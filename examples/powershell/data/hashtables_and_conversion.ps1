# Topic: Hashtables and converting between objects, JSON and CSV.
#
# PowerShell's hashtable is the workhorse for configuration, lookups and
# splatting. Its conversion cmdlets then move data between hashtables,
# PSCustomObjects, JSON and CSV with almost no code -- which is why PowerShell
# is often the shortest path for one-off data wrangling on Windows.
#
# Concepts:
#   - @{} literals, adding/removing keys, and case-insensitive lookup
#   - [ordered]@{} when key order matters (a plain hashtable has none)
#   - Splatting: passing a hashtable as a cmdlet's parameters with @
#   - Hashtable vs PSCustomObject, and why JSON/CSV want the latter
#   - ConvertTo-Json / ConvertFrom-Json, and the -Depth trap
#   - ConvertTo-Csv / ConvertFrom-Csv, and that CSV makes everything a string
#   - Grouping and counting with a hashtable
#
# Validated by running on Windows PowerShell 5.1; also valid on PowerShell 7.

Set-StrictMode -Version Latest

# ---------------------------------------------------------------------------
# 1. Hashtable basics
# ---------------------------------------------------------------------------

$config = @{
    Host    = 'localhost'
    Port    = 8080
    Debug   = $false
}

$config['Timeout'] = 30          # add by index
$config.Retries = 3              # add by property syntax - same thing
$config.Remove('Debug')

Write-Output '-- hashtable basics --'
Write-Output ("  keys    : {0}" -f (($config.Keys | Sort-Object) -join ', '))
Write-Output ("  count   : {0}" -f $config.Count)
Write-Output ("  Port    : {0}" -f $config['Port'])
# Lookup is CASE-INSENSITIVE by default, which surprises people.
Write-Output ("  'port'  : {0}  (case-insensitive)" -f $config['port'])
Write-Output ("  missing : '{0}'  (no error, just null)" -f $config['nope'])
Write-Output ("  ContainsKey('Host') : {0}" -f $config.ContainsKey('Host'))

# A plain hashtable has NO guaranteed order. Use [ordered] when it matters -
# for example when the keys become JSON or CSV columns.
$ordered = [ordered]@{ First = 1; Second = 2; Third = 3 }
Write-Output ("  ordered keys: {0}" -f ($ordered.Keys -join ', '))

# ---------------------------------------------------------------------------
# 2. Splatting - a hashtable AS parameters
# ---------------------------------------------------------------------------
# Instead of a long line of -Parameter value pairs, build a hashtable and
# pass it with @ instead of $. This is the idiomatic way to build a call
# whose parameters vary at runtime.

function Write-Entry {
    param(
        [Parameter(Mandatory)] [string] $Message,
        [ValidateSet('Info', 'Warn', 'Error')] [string] $Level = 'Info',
        [string] $Source = 'app'
    )
    '{0,-5} [{1}] {2}' -f $Level.ToUpper(), $Source, $Message
}

$entryParams = @{
    Message = 'disk usage at 81%'
    Level   = 'Warn'
    Source  = 'monitor'
}

Write-Output '-- splatting --'
Write-Output ("  {0}" -f (Write-Entry @entryParams))       # @ splats
Write-Output ("  {0}" -f (Write-Entry -Message 'started')) # the long way

# ---------------------------------------------------------------------------
# 3. Hashtable vs PSCustomObject
# ---------------------------------------------------------------------------
# A hashtable is a dictionary. A PSCustomObject is a record with properties,
# which is what the pipeline, Format-Table, Export-Csv and ConvertTo-Json
# all expect. Converting is a cast away.

$asObject = [PSCustomObject]$ordered

Write-Output '-- hashtable vs PSCustomObject --'
Write-Output ("  hashtable type : {0}" -f $config.GetType().Name)
Write-Output ("  object type    : {0}" -f $asObject.GetType().Name)
Write-Output ("  object property: {0}" -f $asObject.Second)

# ---------------------------------------------------------------------------
# 4. JSON
# ---------------------------------------------------------------------------

$servers = @(
    [PSCustomObject]@{ Name = 'web-01'; Role = 'web';      Cores = 4; Tags = @('prod', 'uk') }
    [PSCustomObject]@{ Name = 'db-01';  Role = 'database'; Cores = 16; Tags = @('prod') }
    [PSCustomObject]@{ Name = 'web-02'; Role = 'web';      Cores = 4; Tags = @('test') }
)

Write-Output '-- JSON --'
$json = $servers | ConvertTo-Json -Depth 3 -Compress
Write-Output ("  compressed: {0}" -f $json.Substring(0, [Math]::Min(96, $json.Length)) + '...')

$roundTripped = $json | ConvertFrom-Json
Write-Output ("  round-trip count : {0}" -f $roundTripped.Count)
Write-Output ("  first name       : {0}" -f $roundTripped[0].Name)
Write-Output ("  nested array kept: {0}" -f ($roundTripped[0].Tags -join '+'))
Write-Output ("  Cores is still a number: {0}" -f ($roundTripped[0].Cores -is [int]))

# THE DEPTH TRAP: ConvertTo-Json defaults to -Depth 2. Anything nested deeper
# is flattened to its type name instead of being serialised, silently.
$deep = @{ a = @{ b = @{ c = @{ d = 'buried' } } } }
Write-Output ("  default depth: {0}" -f ($deep | ConvertTo-Json -Compress))
Write-Output ("  depth 5      : {0}" -f ($deep | ConvertTo-Json -Depth 5 -Compress))

# ---------------------------------------------------------------------------
# 5. CSV
# ---------------------------------------------------------------------------

Write-Output '-- CSV --'
$csv = $servers | Select-Object Name, Role, Cores | ConvertTo-Csv -NoTypeInformation
foreach ($line in $csv) { Write-Output "  $line" }

$fromCsv = $csv | ConvertFrom-Csv
Write-Output ("  parsed rows      : {0}" -f $fromCsv.Count)
# CSV has no types: EVERYTHING comes back as a string. Cast if you need to
# compute with it. This is the most common CSV surprise.
Write-Output ("  Cores type       : {0}" -f $fromCsv[0].Cores.GetType().Name)
Write-Output ("  '4' + '4' as text: {0}" -f ($fromCsv[0].Cores + $fromCsv[0].Cores))
Write-Output ("  cast to int      : {0}" -f ([int]$fromCsv[0].Cores + [int]$fromCsv[0].Cores))

# ---------------------------------------------------------------------------
# 6. A hashtable as a counter / grouper
# ---------------------------------------------------------------------------

Write-Output '-- counting with a hashtable --'
$byRole = @{}
foreach ($server in $servers) {
    if (-not $byRole.ContainsKey($server.Role)) {
        $byRole[$server.Role] = 0
    }
    $byRole[$server.Role]++
}
foreach ($role in $byRole.Keys | Sort-Object) {
    Write-Output ("  {0,-9} {1}" -f $role, $byRole[$role])
}

# Group-Object does the same in one step and returns objects.
Write-Output '-- the same thing with Group-Object --'
$servers | Group-Object Role | Sort-Object Name | ForEach-Object {
    Write-Output ("  {0,-9} {1}  ({2})" -f $_.Name, $_.Count, ($_.Group.Name -join ', '))
}

# Total cores per role, via a hashtable accumulator.
Write-Output '-- summing into a hashtable --'
$coresByRole = @{}
$servers | ForEach-Object {
    $coresByRole[$_.Role] = ($coresByRole[$_.Role] | ForEach-Object { $_ }) + $_.Cores
}
foreach ($role in $coresByRole.Keys | Sort-Object) {
    Write-Output ("  {0,-9} {1} cores" -f $role, $coresByRole[$role])
}

<#
Expected output:
-- hashtable basics --
  keys    : Host, Port, Retries, Timeout
  count   : 4
  Port    : 8080
  'port'  : 8080  (case-insensitive)
  missing : ''  (no error, just null)
  ContainsKey('Host') : True
  ordered keys: First, Second, Third
-- splatting --
  WARN  [monitor] disk usage at 81%
  INFO  [app] started
-- hashtable vs PSCustomObject --
  hashtable type : Hashtable
  object type    : PSCustomObject
  object property: 2
-- JSON --
  round-trip count : 3
  first name       : web-01
  nested array kept: prod+uk
  Cores is still a number: True
  default depth: {"a":{"b":{"c":"System.Collections.Hashtable"}}}
  depth 5      : {"a":{"b":{"c":{"d":"buried"}}}}
-- CSV --
  "Name","Role","Cores"
  "web-01","web","4"
  ...
  Cores type       : String
  '4' + '4' as text: 44
  cast to int      : 8
-- counting with a hashtable --
  database  1
  web       2
#>
