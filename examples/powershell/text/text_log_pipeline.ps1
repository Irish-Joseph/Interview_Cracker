# Topic: analysing text logs with the pipeline - Select-String, Group-Object, Measure-Object
#
# PowerShell turns "grep, awk, wc" into three pipeline verbs. Instead of
# writing a parser loop, you stream lines through a filter, group them, and
# aggregate - which is why it is the fastest way to interrogate a log file
# you did not write.
#
# Concepts:
#   - Select-String is grep: it returns MatchInfo objects, not raw lines,
#     so you can pull groups out of the match afterwards
#   - Group-Object counts for free: the Count property is the histogram
#   - Measure-Object -Sum/-Average/-Maximum does the arithmetic
#   - the -Raw flag: read a whole file as one string when line-splitting is
#     the thing you want to AVOID
#   - pipeline vs cmdlet: Get-Content -ReadCount batches lines for large files
#
# Run: powershell -ExecutionPolicy Bypass -File <this file>
# (a .ps1 extension is required for -File)
#
# Validated by running on Windows PowerShell 5.1 (cp1252 console, ASCII output).

$logPath = Join-Path $env:TEMP "pipeline_demo.log"
$lines = @(
    "2026-09-23 10:00:01 INFO  [web]  request completed in 12 ms",
    "2026-09-23 10:00:02 ERROR [db]   connection pool exhausted",
    "2026-09-23 10:00:03 WARN  [web]  slow request in 340 ms",
    "2026-09-23 10:00:04 INFO  [web]  request completed in 8 ms",
    "2026-09-23 10:00:05 ERROR [db]   deadlock detected",
    "2026-09-23 10:00:06 INFO  [auth] user login ok",
    "2026-09-23 10:00:07 WARN  [web]  slow request in 501 ms",
    "2026-09-23 10:00:08 ERROR [web]  upstream timeout"
)
Set-Content -Path $logPath -Value $lines -Encoding ASCII

Write-Host "== Select-String: filter, then extract a group =="
# The pattern captures the component in [brackets]; .Matches[0].Groups gives it.
$components = Select-String -Path $logPath -Pattern '\[(?<comp>[a-z]+)\]' |
    ForEach-Object { $_.Matches[0].Groups['comp'].Value }
Write-Host ("distinct components seen: {0}" -f (($components | Sort-Object -Unique) -join ', '))

Write-Host ""
Write-Host "== Group-Object: a histogram with no loops =="
# (A plain -split "\s+" is the trap: the double space before [comp] makes
# an EMPTY field, so "field 2" is blank. Match the level directly instead.)
$byLevel = Get-Content $logPath |
    ForEach-Object { [regex]::Match($_, "(INFO|WARN|ERROR)").Value } |
    Group-Object
foreach ($g in ($byLevel | Sort-Object Name)) {
    Write-Host ("{0,-6} {1}" -f $g.Name, $g.Count)
}

Write-Host ""
Write-Host "== Measure-Object: arithmetic over the pipeline =="
$latencies = Select-String -Path $logPath -Pattern 'in (\d+) ms' |
    ForEach-Object { [int]$_.Matches[0].Groups[1].Value }
$m = $latencies | Measure-Object -Sum -Average -Maximum
Write-Host ("requests with latency: {0}" -f $latencies.Count)
Write-Host ("total ms  : {0}" -f $m.Sum)
Write-Host ("average ms: {0:N1}" -f $m.Average)
Write-Host ("max ms    : {0}" -f $m.Maximum)

Write-Host ""
Write-Host "== -Raw: one string, no line objects =="
$raw = Get-Content $logPath -Raw
Write-Host ("file is one string of {0} chars, {1} newlines" -f $raw.Length, ([regex]::Matches($raw, "`n").Count))

Remove-Item $logPath

<#
Expected output (Windows PowerShell 5.1):

== Select-String: filter, then extract a group ==
distinct components seen: auth, db, web

== Group-Object: a histogram with no loops ==
ERROR  3
INFO   3
WARN   2

== Measure-Object: arithmetic over the pipeline ==
requests with latency: 4
total ms  : 861
average ms: 215.3
max ms    : 501

== -Raw: one string, no line objects ==
file is one string of 446 chars, 8 newlines
#>
