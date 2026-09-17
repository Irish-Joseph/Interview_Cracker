# Topic: Function parameters - binding, validation and pipeline input.
#
# PowerShell's parameter binder does a surprising amount of work for you:
# type coercion, mandatory prompting, validation, tab-completion of allowed
# values, and wiring a function into the pipeline. Declaring parameters well
# means you write almost no argument-checking code.
#
# Concepts:
#   - [CmdletBinding()] and what it turns on (-Verbose, -ErrorAction, ...)
#   - Mandatory, Position, and named vs positional arguments
#   - Validation attributes: ValidateSet, ValidateRange, ValidatePattern,
#     ValidateNotNullOrEmpty, ValidateScript
#   - Default values, [switch] parameters, and typed arrays
#   - Pipeline input: ValueFromPipeline and the begin/process/end blocks
#
# Validated by running on Windows PowerShell 5.1; also valid on PowerShell 7.

Set-StrictMode -Version Latest

# ---------------------------------------------------------------------------
# 1. A well-declared function
# ---------------------------------------------------------------------------

function Get-Report {
    [CmdletBinding()]
    param(
        # Mandatory + Position=0 means it can be passed positionally or named.
        [Parameter(Mandatory, Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string] $Name,

        # ValidateSet restricts the value AND gives tab-completion for free.
        # An invalid value fails at BINDING time, before your code runs.
        [Parameter()]
        [ValidateSet('csv', 'json', 'text')]
        [string] $Format = 'text',

        # ValidateRange rejects out-of-bounds numbers with a clear message.
        [ValidateRange(1, 100)]
        [int] $Limit = 10,

        # A switch is $false unless present; never pass -Force $true.
        [switch] $Force
    )

    # Write-Verbose only prints when -Verbose is passed. This works because
    # of [CmdletBinding()] -- without it there is no -Verbose parameter.
    Write-Verbose "building report for $Name"

    [PSCustomObject]@{
        Name   = $Name
        Format = $Format
        Limit  = $Limit
        Forced = [bool] $Force
    }
}

# ---------------------------------------------------------------------------
# 2. Validation that runs your own code
# ---------------------------------------------------------------------------

function Import-DataFile {
    [CmdletBinding()]
    param(
        # ValidateScript runs an expression; $_ is the candidate value.
        # Throwing a clear message beats returning $false, which produces
        # a generic "did not pass the validation script" error.
        [Parameter(Mandatory)]
        [ValidateScript({
            if (-not (Test-Path -LiteralPath $_)) {
                throw "file not found: $_"
            }
            $true
        })]
        [string] $Path,

        # ValidatePattern applies a regular expression.
        [ValidatePattern('^[a-z][a-z0-9_]*$')]
        [string] $TableName = 'imported_rows'
    )

    [PSCustomObject]@{
        Path      = (Split-Path -Leaf $Path)
        TableName = $TableName
        SizeBytes = (Get-Item -LiteralPath $Path).Length
    }
}

# ---------------------------------------------------------------------------
# 3. Accepting pipeline input
# ---------------------------------------------------------------------------

function Measure-Word {
    [CmdletBinding()]
    param(
        # ValueFromPipeline lets values stream in one at a time.
        [Parameter(Mandatory, ValueFromPipeline)]
        [string[]] $Word,

        [ValidateRange(1, 50)]
        [int] $MinimumLength = 1
    )

    # begin runs ONCE before any input arrives - set up state here.
    begin {
        $seen = 0
        $kept = [System.Collections.Generic.List[string]]::new()
    }

    # process runs once PER pipeline item. Putting the work in the wrong
    # block is the most common mistake: code in begin/end sees only the
    # last bound value, not every item.
    process {
        foreach ($item in $Word) {
            $seen++
            if ($item.Length -ge $MinimumLength) {
                $kept.Add($item)
            }
        }
    }

    # end runs ONCE after the pipeline is exhausted - emit the summary here.
    end {
        [PSCustomObject]@{
            Seen    = $seen
            Kept    = $kept.Count
            Longest = ($kept | Sort-Object Length -Descending | Select-Object -First 1)
        }
    }
}

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

Write-Output '-- positional vs named --'
Get-Report 'sales' | Format-List | Out-String | ForEach-Object { $_.Trim() }
Write-Output ''
Write-Output '-- named, with a switch and a validated set --'
(Get-Report -Name 'stock' -Format json -Limit 25 -Force) |
    ForEach-Object { "  Name=$($_.Name) Format=$($_.Format) Limit=$($_.Limit) Forced=$($_.Forced)" }

Write-Output '-- validation rejects bad values at BINDING time --'
try {
    Get-Report -Name 'sales' -Format xml
}
catch {
    Write-Output "  ValidateSet: $($_.Exception.Message.Split([Environment]::NewLine)[0])"
}

try {
    Get-Report -Name 'sales' -Limit 999
}
catch {
    Write-Output "  ValidateRange: $($_.Exception.Message.Split([Environment]::NewLine)[0])"
}

try {
    Get-Report -Name ''
}
catch {
    Write-Output "  ValidateNotNullOrEmpty: rejected the empty string"
}

Write-Output '-- ValidateScript with a useful message --'
try {
    Import-DataFile -Path 'C:\definitely\missing\data.csv'
}
catch {
    Write-Output "  $($_.Exception.Message.Split([Environment]::NewLine)[0])"
}

$temp = New-TemporaryFile
Set-Content -LiteralPath $temp -Value "a,b,c" -Encoding utf8
(Import-DataFile -Path $temp -TableName 'staging_rows') |
    ForEach-Object { "  imported $($_.TableName) from $($_.Path)" }

try {
    Import-DataFile -Path $temp -TableName '9bad-name'
}
catch {
    Write-Output '  ValidatePattern: rejected "9bad-name"'
}
Remove-Item -LiteralPath $temp -Force

Write-Output '-- pipeline input, process block --'
'alpha', 'be', 'gamma', 'xi', 'epsilon' |
    Measure-Word -MinimumLength 3 |
    ForEach-Object { "  Seen=$($_.Seen) Kept=$($_.Kept) Longest=$($_.Longest)" }

Write-Output '-- -Verbose comes free with [CmdletBinding()] --'
Get-Report -Name 'audit' -Verbose 4>&1 |
    Where-Object { $_ -is [System.Management.Automation.VerboseRecord] } |
    ForEach-Object { "  VERBOSE: $($_.Message)" }

<#
Expected output:
-- positional vs named --
Name   : sales
Format : text
Limit  : 10
Forced : False

-- named, with a switch and a validated set --
  Name=stock Format=json Limit=25 Forced=True
-- validation rejects bad values at BINDING time --
  ValidateSet: Cannot validate argument on parameter 'Format'. ...
  ValidateRange: Cannot validate argument on parameter 'Limit'. ...
  ValidateNotNullOrEmpty: rejected the empty string
-- ValidateScript with a useful message --
  Cannot validate argument on parameter 'Path'. file not found: C:\definitely\missing\data.csv
  imported staging_rows from tmpXXXX.tmp
  ValidatePattern: rejected "9bad-name"
-- pipeline input, process block --
  Seen=5 Kept=3 Longest=epsilon
-- -Verbose comes free with [CmdletBinding()] --
  VERBOSE: building report for audit
#>
