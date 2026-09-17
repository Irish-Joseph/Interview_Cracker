#!/usr/bin/env bash
#
# Topic: Parameter expansion — string surgery without sed, awk or cut.
#
# Concepts:
#   ${var:-default}   fallback when unset/empty
#   ${var:=default}   fallback AND assign
#   ${var:?message}   fail fast when a required variable is missing
#   ${#var}           length
#   ${var:offset:len} substring
#   ${var#pat} ${var##pat}   strip shortest/longest match from the FRONT
#   ${var%pat} ${var%%pat}   strip shortest/longest match from the BACK
#   ${var/old/new} ${var//old/new}   replace first / all
#   ${var^^} ${var,,}        upper / lower case (bash 4+)
#
# Why it matters: every one of these is a shell builtin. No subprocess, no
# pipe, no quoting surprises — and noticeably faster inside a loop than
# calling sed once per line.
#
# Run: bash string_manipulation.sh

set -euo pipefail

section() { printf '\n== %s ==\n' "$1"; }

# --- Defaults and required values -----------------------------------------

section "defaults"

unset GREETING || true
printf 'unset with :-      -> %s\n' "${GREETING:-hello}"     # hello
printf 'GREETING is still  -> %s\n' "${GREETING:-<unset>}"   # :- does not assign

printf 'unset with :=      -> %s\n' "${GREETING:=hola}"      # hola, and assigns
printf 'GREETING is now    -> %s\n' "$GREETING"              # hola

NAME="world"
printf 'set value wins     -> %s\n' "${NAME:-fallback}"      # world

# ${var:?msg} aborts with that message when the variable is missing. Use it
# at the top of a script for required inputs:
#     : "${API_HOST:?API_HOST must be set}"
# Shown in a subshell here so this script survives the failure:
if ( : "${MISSING_VAR:?is required}" ) 2>/dev/null; then
    printf 'unreachable\n'
else
    printf ':? aborted as expected for MISSING_VAR\n'
fi

# Watch the colon: ${var-default} fires only when var is UNSET, while
# ${var:-default} also fires when it is set but EMPTY.
EMPTY=""
printf 'empty with :-      -> %s\n' "${EMPTY:-fallback}"     # fallback
printf 'empty with -       -> [%s]\n' "${EMPTY-fallback}"    # [] — set, so kept

# --- Length and substrings -------------------------------------------------

section "length and substring"

path="/var/log/nginx/access.log"
printf 'value              -> %s\n' "$path"
printf 'length             -> %d\n' "${#path}"
printf 'chars 0..3         -> %s\n' "${path:0:4}"      # /var
printf 'from index 9       -> %s\n' "${path:9}"        # nginx/access.log
printf 'last 8 chars       -> %s\n' "${path: -8}"      # cess.log (space before -8)

# --- Trimming prefixes and suffixes: the dirname/basename pair ------------

section "trimming"

# '#' and '##' cut from the FRONT, '%' and '%%' cut from the BACK.
# One symbol = shortest match, doubled = longest match.
printf 'basename  ${p##*/} -> %s\n' "${path##*/}"      # access.log
printf 'dirname   ${p%%/*} -> %s\n' "${path%/*}"       # /var/log/nginx
printf 'drop .log ${p%%.log} -> %s\n' "${path%.log}"   # /var/log/nginx/access
printf 'top dir   ${p#/*/} -> %s\n' "${path#/*/}"      # log/nginx/access.log

file="archive.tar.gz"
printf 'shortest back  %%.* -> %s\n' "${file%.*}"      # archive.tar
printf 'longest  back %%%%.* -> %s\n' "${file%%.*}"    # archive
printf 'shortest front #*. -> %s\n' "${file#*.}"       # tar.gz
printf 'longest  front ##*. -> %s\n' "${file##*.}"     # gz  (the extension)

# --- Replacement -----------------------------------------------------------

section "replacement"

csv="alpha,beta,gamma,beta"
printf 'first  ${v/beta/X}  -> %s\n' "${csv/beta/X}"     # alpha,X,gamma,beta
printf 'all    ${v//beta/X} -> %s\n' "${csv//beta/X}"    # alpha,X,gamma,X
printf 'delete ${v//,/}     -> %s\n' "${csv//,/}"        # alphabetagammabeta
printf 'to spaces           -> %s\n' "${csv//,/ }"       # alpha beta gamma beta

# Anchored replacement: '#' matches only at the start, '%' only at the end.
version="v2.11.4"
printf 'strip leading v     -> %s\n' "${version/#v/}"    # 2.11.4

# --- Case conversion (bash 4+) --------------------------------------------

section "case"

env_name="production"
loud="${env_name^^}"
printf 'upper ${v^^}       -> %s\n' "$loud"              # PRODUCTION
printf 'first ${v^}        -> %s\n' "${env_name^}"       # Production
printf 'lower ${v,,}       -> %s\n' "${loud,,}"          # production

# --- Putting it together: a tiny filename normaliser ----------------------

section "practical: normalise filenames"

# Turn "Report Final (2024).CSV" into a safe slug using builtins only.
for original in "Report Final (2024).CSV" "Sales Q1 (draft).TXT" "notes.md"; do
    name="${original%.*}"                 # everything before the last dot
    ext="${original##*.}"                 # the extension
    slug="${name,,}"                      # lowercase
    slug="${slug//[()]/}"                 # drop parentheses
    slug="${slug// /_}"                   # spaces -> underscores
    printf '%-26s -> %s.%s\n' "$original" "$slug" "${ext,,}"
done

# --- Why not sed? ----------------------------------------------------------

section "cost"

# Both loops extract the same basename 100 times. The builtin version
# spawns no processes at all; the sed version forks twice per iteration,
# which is why it takes visibly longer (dramatically so on Windows).
start=$SECONDS
for _ in {1..100}; do value="${path##*/}"; done
builtin_time=$((SECONDS - start))

start=$SECONDS
for _ in {1..100}; do value="$(printf '%s' "$path" | sed 's|.*/||')"; done
sed_time=$((SECONDS - start))

printf '100x parameter expansion: %ds\n' "$builtin_time"
printf '100x sed subprocess:      %ds\n' "$sed_time"
printf 'last value computed:      %s\n' "$value"
