# PowerShell pipelines pass structured objects, not formatted text.

$services = @(
    [PSCustomObject]@{ Name = 'api';      Environment = 'prod'; Status = 'Running'; MemoryMB = 420 }
    [PSCustomObject]@{ Name = 'worker';   Environment = 'prod'; Status = 'Stopped'; MemoryMB = 0 }
    [PSCustomObject]@{ Name = 'frontend'; Environment = 'test'; Status = 'Running'; MemoryMB = 180 }
    [PSCustomObject]@{ Name = 'database'; Environment = 'prod'; Status = 'Running'; MemoryMB = 760 }
)

$runningProduction = $services |
    Where-Object { $_.Environment -eq 'prod' -and $_.Status -eq 'Running' } |
    Sort-Object MemoryMB -Descending |
    Select-Object Name, MemoryMB, @{
        Name = 'MemoryGB'
        Expression = { [math]::Round($_.MemoryMB / 1024, 2) }
    }

Write-Output 'Running production services:'
$runningProduction | Format-Table -AutoSize

$totalMemory = $runningProduction |
    Measure-Object -Property MemoryMB -Sum

Write-Output ("Total memory: {0} MB" -f $totalMemory.Sum)

Write-Output 'Count by status:'
$services |
    Group-Object Status |
    Sort-Object Name |
    ForEach-Object {
        # Emit a new object so callers can keep filtering and exporting the data.
        [PSCustomObject]@{
            Status = $_.Name
            Count = $_.Count
        }
    } |
    Format-Table -AutoSize

# Format-Table belongs at the end: it produces display instructions rather than
# the original service objects used by Where-Object, Select-Object, and Measure-Object.
