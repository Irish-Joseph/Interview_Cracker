<#
Topic: Advanced pipeline functions with begin/process/end.
Concepts: one-time setup, one call per input object, aggregation in end.
Run: powershell -File examples/powershell/functions/pipeline_begin_process_end.ps1
#>

function Measure-RunningTotal {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [int] $Value
    )

    begin {
        $total = 0
        $count = 0
    }

    process {
        $total += $Value
        $count += 1
    }

    end {
        [pscustomobject]@{
            Count = $count
            Total = $total
            Average = if ($count) { $total / $count } else { 0 }
        }
    }
}

$result = 2, 4, 9 | Measure-RunningTotal
if ($result.Count -ne 3 -or $result.Total -ne 15 -or $result.Average -ne 5) {
    throw 'Unexpected aggregation result'
}

$result | Format-List Count, Total, Average
