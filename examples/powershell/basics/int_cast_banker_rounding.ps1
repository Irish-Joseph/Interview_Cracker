# Topic: [int] casts in PowerShell round to even (banker's rounding), not half-up
#
# If you expect [int]2.5 to be 3, this file shows why it is 2, and how to get
# the schoolbook "half-up" rule when you really want it.
#
# Concepts:
#   - [int]3.5 is 4 but [int]2.5 is 2 -- .NET rounds midpoints to the
#     nearest EVEN number, which keeps the average error over many
#     roundings at zero
#   - [math]::Floor / Ceiling / Truncate when you want no rounding at all
#   - [math]::Round with explicit MidpointRounding for half-up behaviour
#   - Failed parses: [int]"abc" gives $null plus a non-terminating error;
#     -as [int] gives $null quietly. Neither is a clean "parse or error"
#     story -- [int]::TryParse is
#
# Run:
#   powershell -ExecutionPolicy Bypass -File int_cast_banker_rounding.ps1
#
# Validated by running on Windows PowerShell (console is cp1252, so output
# below is plain ASCII).

function Show([object]$value) {
    if ($null -eq $value) { return '$null' }
    return "$value"
}

Write-Host "== [int] cast: banker's rounding (round to even)"
Write-Host ("[int] 3.5  -> {0}  (4 is even)"      -f [int]3.5)
Write-Host ("[int] 2.5  -> {0}  (2 is even)"      -f [int]2.5)
Write-Host ("[int] 4.5  -> {0}  (4 is even)"      -f [int]4.5)
Write-Host ("[int] -2.5 -> {0}  (-2 is even)"     -f [int]-2.5)
Write-Host ("[int] 3.75 -> {0}  (not a midpoint)" -f [int]3.75)

Write-Host ""
Write-Host "== explicit control"
Write-Host ("[math]::Floor(3.75)   -> {0}" -f [math]::Floor(3.75))
Write-Host ("[math]::Ceiling(3.25) -> {0}" -f [math]::Ceiling(3.25))
Write-Host ("[math]::Truncate(3.75)-> {0}  (drops the fraction, no rounding)" -f [math]::Truncate(3.75))
Write-Host ("Round 2.5 ToEven         -> {0}" -f [math]::Round(2.5, 0, [MidpointRounding]::ToEven))
Write-Host ("Round 2.5 AwayFromZero   -> {0}  (the 'schoolbook' half-up rule)" -f [math]::Round(2.5, 0, [MidpointRounding]::AwayFromZero))

Write-Host ""
Write-Host "== failed parses: cast vs -as"
$ErrorActionPreference = "SilentlyContinue"
$bad = [int]"abc"
Write-Host ("[int]'abc'     -> {0}  (null value, plus a non-terminating error)" -f (Show $bad))
$ErrorActionPreference = "Stop"
$bad2 = "abc" -as [int]
Write-Host ("-as [int]      -> {0}  (same null, but no error raised)" -f (Show $bad2))
$good = "42" -as [int]
Write-Host ("'42' -as [int] -> {0}  (parsing succeeded)" -f (Show $good))

<#
Expected output:

== [int] cast: banker's rounding (round to even)
[int] 3.5  -> 4  (4 is even)
[int] 2.5  -> 2  (2 is even)
[int] 4.5  -> 4  (4 is even)
[int] -2.5 -> -2  (-2 is even)
[int] 3.75 -> 4  (not a midpoint)

== explicit control
[math]::Floor(3.75)   -> 3
[math]::Ceiling(3.25) -> 4
[math]::Truncate(3.75)-> 3  (drops the fraction, no rounding)
Round 2.5 ToEven         -> 2
Round 2.5 AwayFromZero   -> 3  (the 'schoolbook' half-up rule)

== failed parses: cast vs -as
[int]'abc'     -> $null  (null value, plus a non-terminating error)
-as [int]      -> $null  (same null, but no error raised)
'42' -as [int] -> 42  (parsing succeeded)
#>
