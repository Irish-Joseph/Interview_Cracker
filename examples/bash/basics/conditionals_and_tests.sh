#!/usr/bin/env bash
#
# Topic: Conditionals - [[ ]] vs [ ], and the tests worth memorising.
#
# Concepts:
#   - Why [[ ]] is the right default in bash, and when you still need [ ]
#   - Unquoted variables: safe inside [[ ]], dangerous inside [ ]
#   - String tests: = == != -z -n, and pattern matching with ==
#   - Numeric tests: -eq -ne -lt -le -gt -ge, and the (( )) alternative
#   - File tests: -e -f -d -r -w -x -s
#   - Combining with && || and ! ; the exit-status view of true/false
#   - case, and why it often reads better than a chain of elifs
#
# Run: bash bash/basics/conditionals_and_tests.sh

set -uo pipefail     # note: NOT -e, because we deliberately run failing tests

# ---------------------------------------------------------------------------
# 1. [[ ]] vs [ ]
# ---------------------------------------------------------------------------
# [ is an ordinary COMMAND (a synonym for `test`), so the shell splits and
# globs its arguments first. [[ is shell SYNTAX, parsed before expansion,
# which is why it is safer and more capable.

name="two words"

echo "-- quoting --"
if [[ $name == "two words" ]]; then           # unquoted $name is fine here
    echo "  [[ ]] handles an unquoted variable containing spaces"
fi

if [ "$name" = "two words" ]; then            # quotes are MANDATORY here
    echo "  [ ] needs the quotes; without them it sees 3 arguments and errors"
fi

# An empty or unset variable is the classic [ ] failure:
empty=""
if [ -z "$empty" ]; then echo "  [ -z ] with quotes: empty detected"; fi
if [[ -z $empty ]]; then echo "  [[ -z ]] without quotes: also fine"; fi

# ---------------------------------------------------------------------------
# 2. String tests
# ---------------------------------------------------------------------------
echo "-- strings --"
file="report-2026-09.csv"

[[ -n $file ]]              && echo "  -n : non-empty"
[[ $file == *.csv ]]        && echo "  == : glob pattern match (*.csv)"
[[ $file == report-* ]]     && echo "  == : prefix match"
[[ $file != *.tsv ]]        && echo "  != : negated match"
[[ $file =~ ^report-[0-9]{4}-[0-9]{2}\.csv$ ]] && echo "  =~ : regex match"

# Inside [[ ]] the right-hand side of == is a PATTERN unless you quote it.
[[ $file == "*.csv" ]] || echo '  quoting the pattern makes it a literal (no match)'

# Lexicographic comparison uses < and > inside [[ ]] (escape them in [ ]).
[[ "apple" < "banana" ]] && echo "  < : apple sorts before banana"

# ---------------------------------------------------------------------------
# 3. Numeric tests
# ---------------------------------------------------------------------------
echo "-- numbers --"
count=7

[[ $count -gt 5 ]] && echo "  -gt : 7 > 5"
[[ $count -eq 7 ]] && echo "  -eq : equals 7"
(( count > 5 ))    && echo "  (( )) : arithmetic context, use plain > and <"
(( count % 2 ))    && echo "  (( )) : non-zero is TRUE, so this tests oddness"

# The trap: = and == compare STRINGS, so "07" != "7" but they are -eq.
[[ "07" == "7" ]] || echo '  "07" == "7"  is false (string comparison)'
[[ "07" -eq "7" ]] && echo '  "07" -eq "7" is true  (numeric comparison)'

# ---------------------------------------------------------------------------
# 4. File tests
# ---------------------------------------------------------------------------
echo "-- files --"
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT          # clean up however the script exits

printf 'row\n' > "$workdir/data.csv"
: > "$workdir/empty.log"               # create a zero-byte file
mkdir -p "$workdir/archive"

[[ -e $workdir/data.csv ]]  && echo "  -e : exists (file OR directory)"
[[ -f $workdir/data.csv ]]  && echo "  -f : is a regular file"
[[ -d $workdir/archive ]]   && echo "  -d : is a directory"
[[ -s $workdir/data.csv ]]  && echo "  -s : exists and is NON-empty"
[[ -s $workdir/empty.log ]] || echo "  -s : empty.log is empty, so -s is false"
[[ -r $workdir/data.csv ]]  && echo "  -r : readable"
[[ -w $workdir/data.csv ]]  && echo "  -w : writable"
[[ -x $workdir/data.csv ]]  || echo "  -x : not executable"
[[ ! -e $workdir/missing ]] && echo "  !  : negation, missing file"

# "newer than" is handy for build scripts and caches.
sleep 0.01
printf 'newer\n' > "$workdir/rebuilt"
[[ $workdir/rebuilt -nt $workdir/data.csv ]] && echo "  -nt : rebuilt is newer than data.csv"

# ---------------------------------------------------------------------------
# 5. Combining conditions
# ---------------------------------------------------------------------------
echo "-- combining --"
extension=csv
size=1200

if [[ $extension == csv && $size -gt 1000 ]]; then
    echo "  && inside [[ ]] : both true"
fi

if [[ $extension == tsv || $extension == csv ]]; then
    echo "  || inside [[ ]] : either true"
fi

# Grouping needs parentheses, which [[ ]] understands directly.
if [[ ( $extension == csv || $extension == tsv ) && $size -gt 0 ]]; then
    echo "  ( ) : grouping works inside [[ ]]"
fi

# Every command returns an exit status; 0 means success/true. `if` simply
# runs a command and branches on that status -- there is no boolean type.
if grep -q "row" "$workdir/data.csv"; then
    echo "  if runs a COMMAND and branches on its exit status"
fi

# && and || between commands are short-circuit operators, not syntax:
[[ -f $workdir/data.csv ]] && echo "  short-circuit: file exists" || echo "  unreachable"

# ---------------------------------------------------------------------------
# 6. case - usually clearer than a chain of elifs
# ---------------------------------------------------------------------------
echo "-- case --"
classify() {
    local path=$1
    case $path in
        *.csv|*.tsv)  echo "  $path -> delimited text" ;;
        *.json)       echo "  $path -> json" ;;
        *.log)        echo "  $path -> log" ;;
        .*)           echo "  $path -> hidden file" ;;
        *)            echo "  $path -> unknown" ;;   # the default arm
    esac
}

for candidate in report.csv data.tsv config.json app.log .bashrc mystery.bin; do
    classify "$candidate"
done

# Expected output:
#   -- quoting --
#     [[ ]] handles an unquoted variable containing spaces
#     [ ] needs the quotes; without them it sees 3 arguments and errors
#     [ -z ] with quotes: empty detected
#     [[ -z ]] without quotes: also fine
#   -- strings --
#     -n : non-empty
#     == : glob pattern match (*.csv)
#     ...
#   -- case --
#     report.csv -> delimited text
#     data.tsv -> delimited text
#     config.json -> json
#     app.log -> log
#     .bashrc -> hidden file
#     mystery.bin -> unknown
