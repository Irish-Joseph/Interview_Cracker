#!/usr/bin/env bash
#
# Topic: Indexed and associative arrays in Bash.
#
# Concepts:
#   - Declaring arrays, and why "${arr[@]}" needs both the quotes and the @
#   - "${arr[@]}" (one word per element) vs "${arr[*]}" (one joined word)
#   - Appending, slicing, indices, length, deleting an element
#   - declare -A for associative arrays (Bash 4+), and iterating their keys
#   - Counting and grouping without awk
#   - Passing an array to a function safely
#   - mapfile/readarray to load lines into an array
#
# Run: bash bash/arrays/indexed_and_associative_arrays.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Indexed arrays
# ---------------------------------------------------------------------------

# Literal assignment. Elements with spaces must be quoted individually.
fruits=("apple" "granny smith" "pear")

fruits+=("plum")                 # append
fruits[10]="fig"                 # arrays are sparse: indices need no gaps

echo "count:   ${#fruits[@]}"    # 5 elements, even though the top index is 10
echo "first:   ${fruits[0]}"
echo "last:    ${fruits[-1]}"    # negative indexes count from the end
echo "indices: ${!fruits[*]}"    # 0 1 2 3 10

echo "-- \"\${fruits[@]}\": one word per element --"
for fruit in "${fruits[@]}"; do
    echo "  [$fruit]"
done

# Unquoted ${fruits[@]} would split "granny smith" into two words, and
# "${fruits[*]}" joins everything with the first character of IFS instead.
echo "-- \"\${fruits[*]}\": a single joined word --"
for fruit in "${fruits[*]}"; do
    echo "  [$fruit]"
done

echo "slice 1..2: ${fruits[*]:1:2}"

unset 'fruits[10]'               # quote the name so globbing cannot touch it
echo "after unset: ${#fruits[@]} elements"

# ---------------------------------------------------------------------------
# 2. Associative arrays (Bash 4+)
# ---------------------------------------------------------------------------

declare -A stock=(
    [apple]=12
    [pear]=0
    ["granny smith"]=7
)

stock[plum]=3                    # add a key
stock[apple]=$(( stock[apple] + 5 ))   # arithmetic context needs no $

echo "-- stock --"
# Key order is unspecified (it is a hash), so sort when output must be stable.
# Read the sorted keys back into an array: an unquoted $(...) would word-split
# "granny smith" into two bogus keys.
mapfile -t sorted_keys < <(printf '%s\n' "${!stock[@]}" | sort)
for key in "${sorted_keys[@]}"; do
    printf '  %-13s %s\n' "$key" "${stock[$key]}"
done

# -v tests for key existence, which is not the same as "value is non-empty".
if [[ -v stock[pear] ]]; then
    echo "pear is stocked (quantity ${stock[pear]})"
fi
if [[ ! -v stock[kiwi] ]]; then
    echo "kiwi is not a known product"
fi

# ---------------------------------------------------------------------------
# 3. Counting and grouping - the classic use for an associative array
# ---------------------------------------------------------------------------

count_levels() {
    local -A counts=()
    local line level
    while IFS= read -r line; do
        level=${line%% *}                     # first word
        counts[$level]=$(( ${counts[$level]:-0} + 1 ))
    done
    local -a sorted=()
    mapfile -t sorted < <(printf '%s\n' "${!counts[@]}" | sort)
    for level in "${sorted[@]}"; do
        printf '  %-5s %d\n' "$level" "${counts[$level]}"
    done
}

echo "-- log levels --"
count_levels <<'LOG'
INFO service started
WARN disk at 81%
INFO request handled
ERROR upstream timeout
INFO request handled
WARN disk at 88%
LOG

# ---------------------------------------------------------------------------
# 4. Passing arrays to functions
# ---------------------------------------------------------------------------

# An array does not survive "$@" as one argument, so expand it and let the
# function take the elements as positional parameters.
join_with() {
    local sep=$1
    shift
    local result=$1
    shift
    local item
    for item in "$@"; do
        result+="${sep}${item}"
    done
    printf '%s\n' "$result"
}

echo "joined: $(join_with ' | ' "${fruits[@]}")"

# Bash 4.3+ can take the array by *name* with a nameref, avoiding the copy.
describe_array() {
    local -n ref=$1                           # ref is an alias for the caller's array
    printf 'array %s has %d elements, first=%s\n' "$1" "${#ref[@]}" "${ref[0]}"
}
describe_array fruits

# ---------------------------------------------------------------------------
# 5. mapfile: read lines straight into an array
# ---------------------------------------------------------------------------

# -t strips the trailing newline from each element.
mapfile -t lines <<'TEXT'
first line
  indented line
last line
TEXT

echo "-- mapfile --"
echo "read ${#lines[@]} lines; second is [${lines[1]}]"

# Expected output:
#   count:   5
#   first:   apple
#   last:    fig
#   indices: 0 1 2 3 10
#   ...
#   -- log levels --
#     ERROR 1
#     INFO  3
#     WARN  2
#   joined: apple | granny smith | pear | plum
#   array fruits has 4 elements, first=apple
#   -- mapfile --
#   read 3 lines; second is [  indented line]
