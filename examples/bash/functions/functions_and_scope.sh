#!/usr/bin/env bash
#
# Topic: Functions - arguments, return values, and variable scope.
#
# Bash functions do NOT return values the way other languages do. `return`
# sets an EXIT STATUS (0-255), not a result. To hand data back you either
# print it and let the caller capture stdout, or write into a named variable.
# Getting this distinction right is most of what separates working shell
# scripts from mysterious ones.
#
# Concepts:
#   - Declaring functions, and why $1 $2 "$@" replace named parameters
#   - return = exit status (0 = success), NOT a value
#   - Returning data via stdout and $( ), and why that spawns a subshell
#   - `local` and dynamic scoping - and what happens without it
#   - local -n namerefs to write into a caller's variable (bash 4.3+)
#   - Default values for missing arguments
#   - Recursion, and that $FUNCNAME knows where it is
#
# Run: bash bash/functions/functions_and_scope.sh

set -uo pipefail

# ---------------------------------------------------------------------------
# 1. Arguments are positional
# ---------------------------------------------------------------------------
# There are no named parameters. $1..$9 are the arguments, $# is the count,
# "$@" is all of them as separate words, and $0 is the SCRIPT name (not the
# function name - use $FUNCNAME for that).

greet() {
    local name=$1
    local greeting=${2:-Hello}          # default when $2 is unset or empty
    printf '%s, %s!\n' "$greeting" "$name"
}

describe_args() {
    printf '  function : %s\n' "$FUNCNAME"
    printf '  count    : %d\n' "$#"
    printf '  all ("$@"): '
    local arg
    for arg in "$@"; do
        printf '[%s] ' "$arg"
    done
    printf '\n'
}

echo "-- arguments --"
greet "Ada"
greet "Grace" "Good morning"
describe_args one "two words" three

# ---------------------------------------------------------------------------
# 2. return is an EXIT STATUS, not a value
# ---------------------------------------------------------------------------

is_even() {
    # 0 means success/true in shell. This is inverted from most languages.
    (( $1 % 2 == 0 ))
}

file_is_big() {
    local path=$1 threshold=${2:-100}
    local size
    size=$(wc -c < "$path")
    (( size > threshold ))
}

echo "-- return = exit status --"
if is_even 4; then echo "  4 is even (function returned 0)"; fi
if ! is_even 7; then echo "  7 is odd  (function returned non-zero)"; fi

# The trap: `return 42` does NOT give you 42 as a value.
answer() { return 42; }
answer
echo "  after 'return 42', \$? is $? - an exit status, not a result"
echo "  and values above 255 wrap around, so never use return for data"

# ---------------------------------------------------------------------------
# 3. Returning DATA: print it, capture it
# ---------------------------------------------------------------------------

full_name() {
    local first=$1 last=$2
    printf '%s %s' "$first" "$last"     # printf, not echo: no trailing newline
}

sum_numbers() {
    local total=0 n
    for n in "$@"; do
        (( total += n ))
    done
    printf '%d' "$total"
}

echo "-- returning data via stdout --"
name=$(full_name "Ada" "Lovelace")      # $( ) captures stdout
echo "  captured: $name"
echo "  sum 1..5: $(sum_numbers 1 2 3 4 5)"

# ---------------------------------------------------------------------------
# 4. Scope: local, and what happens without it
# ---------------------------------------------------------------------------
# Bash variables are GLOBAL by default. A function that forgets `local`
# silently clobbers the caller's variable - a classic source of action-at-a-
# distance bugs in long scripts.

counter="caller's value"

leaky() {
    counter="overwritten by leaky"      # no local: this is the GLOBAL
}

tidy() {
    local counter="only inside tidy"    # shadows the global
    printf '  inside tidy : %s\n' "$counter"
}

echo "-- scope --"
printf '  before      : %s\n' "$counter"
tidy
printf '  after tidy  : %s  (unchanged)\n' "$counter"
leaky
printf '  after leaky : %s  (clobbered!)\n' "$counter"

# Bash scoping is DYNAMIC, not lexical: a local is visible to functions that
# this function CALLS, which surprises people coming from other languages.
outer() {
    local secret="set in outer"
    inner                                # inner can see $secret
}
inner() {
    printf '  inner sees outer local: %s\n' "${secret:-<unset>}"
}
counter="caller's value"                 # restore for clarity
outer
printf '  but at top level: %s\n' "${secret:-<unset>}"

# ---------------------------------------------------------------------------
# 5. Writing into the caller's variable with a nameref (bash 4.3+)
# ---------------------------------------------------------------------------
# $( ) runs the function in a SUBSHELL, which costs a fork and means the
# function cannot change anything in the caller. A nameref avoids both.

split_path() {
    local path=$1
    local -n dir_ref=$2                  # ref is an ALIAS for the caller's var
    local -n file_ref=$3
    dir_ref=${path%/*}
    file_ref=${path##*/}
}

populate_array() {
    local -n out_ref=$1
    shift
    out_ref=()
    local item
    for item in "$@"; do
        out_ref+=("${item^^}")           # ^^ upper-cases
    done
}

echo "-- namerefs write into the caller --"
split_path "/var/log/app/server.log" directory filename
printf '  directory: %s\n' "$directory"
printf '  filename : %s\n' "$filename"

populate_array shouty alpha beta gamma
printf '  array    : %s\n' "${shouty[*]}"

# ---------------------------------------------------------------------------
# 6. Recursion
# ---------------------------------------------------------------------------

factorial() {
    local n=$1
    if (( n <= 1 )); then
        printf '1'
        return 0
    fi
    printf '%d' "$(( n * $(factorial $(( n - 1 ))) ))"
}

countdown() {
    local n=$1
    (( n < 0 )) && return 0
    printf '%d ' "$n"
    countdown $(( n - 1 ))
}

echo "-- recursion --"
printf '  factorial 6 : %s\n' "$(factorial 6)"
printf '  countdown 5 : '
countdown 5
printf '\n'

# ---------------------------------------------------------------------------
# 7. Guidelines
# ---------------------------------------------------------------------------
echo "-- rules of thumb --"
echo "  1. Declare every function variable 'local' - always."
echo "  2. Use return ONLY for success/failure, never for data."
echo "  3. Print data to stdout and capture with \$( ), or use a nameref."
echo "  4. Quote \"\$@\" (not \$*) to preserve arguments containing spaces."
echo "  5. Keep diagnostics on stderr so they do not pollute captured output."

# Expected output:
#   -- arguments --
#   Hello, Ada!
#   Good morning, Grace!
#     function : describe_args
#     count    : 3
#     all ("$@"): [one] [two words] [three]
#   -- return = exit status --
#     4 is even (function returned 0)
#     7 is odd  (function returned non-zero)
#     after 'return 42', $? is 42 - an exit status, not a result
#   -- scope --
#     before      : caller's value
#     inside tidy : only inside tidy
#     after tidy  : caller's value  (unchanged)
#     after leaky : overwritten by leaky  (clobbered!)
#     inner sees outer local: set in outer
#     but at top level: <unset>
#   -- namerefs write into the caller --
#     directory: /var/log/app
#     filename : server.log
#     array    : ALPHA BETA GAMMA
#   -- recursion --
#     factorial 6 : 720
#     countdown 5 : 5 4 3 2 1 0
