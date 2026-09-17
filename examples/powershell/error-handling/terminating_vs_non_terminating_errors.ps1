# Topic: PowerShell error handling - terminating vs non-terminating errors.
#
# The single biggest surprise in PowerShell is that try/catch does NOT catch
# most cmdlet failures by default. Cmdlets emit *non-terminating* errors, which
# write to the error stream, append to $Error, and let the pipeline carry on.
# Only a *terminating* error unwinds into catch.
#
# Concepts:
#   - Non-terminating vs terminating errors, and $? / $LASTEXITCODE
#   - -ErrorAction Stop: the switch that makes try/catch work
#   - $ErrorActionPreference and why setting it globally is a blunt instrument
#   - Catching specific exception types, plus finally
#   - -ErrorVariable to collect errors without stopping
#   - throw vs Write-Error
#   - Native executables: exit codes, not exceptions
#
# Run: pwsh -File powershell/error-handling/terminating_vs_non_terminating_errors.ps1
#
# Validated by running on Windows PowerShell 5.1; also valid on PowerShell 7.

Set-StrictMode -Version Latest

# ---------------------------------------------------------------------------
# 1. A non-terminating error does not reach catch
# ---------------------------------------------------------------------------

Write-Output '-- non-terminating (NOT caught) --'
try {
    Get-Item -Path 'C:\definitely\missing\file.txt' -ErrorAction SilentlyContinue
    Write-Output '  the script kept going; catch never ran'
}
catch {
    Write-Output '  this line is unreachable for a non-terminating error'
}

# $? reports whether the LAST command succeeded. It is reset by every command,
# so capture it immediately or it is gone.
Get-Item -Path 'C:\definitely\missing\file.txt' -ErrorAction SilentlyContinue
Write-Output ('  $? after the failed Get-Item: {0}' -f $?)

# ---------------------------------------------------------------------------
# 2. -ErrorAction Stop promotes it to terminating, so catch works
# ---------------------------------------------------------------------------

Write-Output '-- terminating via -ErrorAction Stop --'
try {
    Get-Item -Path 'C:\definitely\missing\file.txt' -ErrorAction Stop
}
catch {
    # $_ is the ErrorRecord, not the exception. The exception is one level in.
    Write-Output ('  caught: {0}' -f $_.Exception.GetType().Name)
    Write-Output ('  message: {0}' -f $_.Exception.Message)
    Write-Output ('  failing command: {0}' -f $_.InvocationInfo.MyCommand)
}
finally {
    Write-Output '  finally always runs'
}

# ---------------------------------------------------------------------------
# 3. Catch specific exception types, most specific first
# ---------------------------------------------------------------------------

function Convert-ToInt {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string] $Value
    )

    try {
        return [int]::Parse($Value)
    }
    catch [System.FormatException] {
        Write-Output ('  "{0}" is not a number' -f $Value)
        return $null
    }
    catch [System.OverflowException] {
        Write-Output ('  "{0}" does not fit in an Int32' -f $Value)
        return $null
    }
    catch {
        # A bare catch is the fallback for everything else. Rethrow with
        # `throw` so the original error record (and its stack) survives.
        throw
    }
}

Write-Output '-- typed catch --'
Write-Output ('  parsed: {0}' -f (Convert-ToInt -Value '42'))
# Called bare: the handlers above report the problem and return $null, and a
# $null on the pipeline displays nothing.
Convert-ToInt -Value 'twelve'
Convert-ToInt -Value '99999999999999999999'

# ---------------------------------------------------------------------------
# 4. -ErrorVariable: keep going, but collect what failed
# ---------------------------------------------------------------------------

Write-Output '-- collect errors without stopping --'
$paths = @('C:\missing\one.txt', 'C:\missing\two.txt')
$found = $paths | ForEach-Object {
    Get-Item -Path $_ -ErrorAction SilentlyContinue -ErrorVariable +itemErrors
}
Write-Output ('  found {0} item(s), {1} error(s)' -f @($found).Count, @($itemErrors).Count)
foreach ($err in $itemErrors) {
    Write-Output ('    - {0}' -f $err.CategoryInfo.Category)
}

# ---------------------------------------------------------------------------
# 5. $ErrorActionPreference: powerful, and easy to misuse
# ---------------------------------------------------------------------------

Write-Output '-- scoped preference --'
function Invoke-StrictBlock {
    # Setting the preference inside a function scopes it to that function,
    # which is far safer than flipping it for the whole script (and much safer
    # than leaving it flipped in a module other people dot-source).
    $ErrorActionPreference = 'Stop'
    try {
        Get-Item -Path 'C:\definitely\missing\file.txt'
        Write-Output '  unreachable'
    }
    catch {
        Write-Output '  caught without -ErrorAction, thanks to the preference'
    }
}
Invoke-StrictBlock

# ---------------------------------------------------------------------------
# 6. throw vs Write-Error
# ---------------------------------------------------------------------------

Write-Output '-- throw vs Write-Error --'

function Test-Positive {
    param([int] $Number)

    if ($Number -le 0) {
        # throw is always terminating: the caller must handle it.
        throw [System.ArgumentOutOfRangeException]::new('Number', 'must be positive')
    }
    $Number
}

# Write-Error emits a non-terminating error: useful when one bad item in a
# pipeline should be reported without abandoning the remaining items.
function Write-Report {
    [CmdletBinding()]   # makes -ErrorAction / -ErrorVariable work on this function
    param([int[]] $Numbers)

    foreach ($number in $Numbers) {
        if ($number -lt 0) {
            Write-Error ('skipping negative value {0}' -f $number)
            continue
        }
        Write-Output ('  value {0}' -f $number)
    }
}

try {
    Test-Positive -Number -5
}
catch [System.ArgumentOutOfRangeException] {
    Write-Output ('  throw was caught: {0}' -f $_.Exception.ParamName)
}

Write-Report -Numbers @(3, -1, 7) -ErrorAction SilentlyContinue -ErrorVariable reportErrors
Write-Output ('  reported {0} problem(s): {1}' -f @($reportErrors).Count, ($reportErrors -join '; '))

# ---------------------------------------------------------------------------
# 7. Native executables report failure with an exit code, not an exception
# ---------------------------------------------------------------------------

Write-Output '-- native exit code --'
# try/catch will never fire for a non-zero exit from an .exe; check
# $LASTEXITCODE (PowerShell 7.3+ can opt in via $PSNativeCommandUseErrorActionPreference).
cmd.exe /c "exit 3" 2>$null
Write-Output ('  $LASTEXITCODE = {0}' -f $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) {
    Write-Output '  treat a non-zero exit code as the failure signal'
}

<#
Expected output:
-- non-terminating (NOT caught) --
  the script kept going; catch never ran
  $? after the failed Get-Item: False
-- terminating via -ErrorAction Stop --
  caught: ItemNotFoundException
  message: Cannot find path 'C:\definitely\missing\file.txt' because it does not exist.
  failing command: Get-Item
  finally always runs
-- typed catch --
  parsed: 42
  "twelve" is not a number
  "99999999999999999999" does not fit in an Int32
-- collect errors without stopping --
  found 0 item(s), 2 error(s)
    - ObjectNotFound
    - ObjectNotFound
-- scoped preference --
  caught without -ErrorAction, thanks to the preference
-- throw vs Write-Error --
  throw was caught: Number
  value 3
  value 7
  reported 1 problem(s): skipping negative value -1
-- native exit code --
  $LASTEXITCODE = 3
  treat a non-zero exit code as the failure signal
#>
