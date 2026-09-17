#!/usr/bin/env bash
#
# Topic: Parsing command-line flags with getopts.
#
# Concepts:
#   - getopts: short flags (-v, -o file), combined (-vs)
#   - Required arguments after a colon (-o:), and missing-arg errors
#   - The OPTIND cursor and positional arguments after parsing
#   - -h/--help conventions and usage() text
#   - set -euo pipefail interaction with getopts
#
# A well-behaved CLI tool accepts flags in ANY order, before or
# after positionals (with getopts: flags must come first — a known
# limitation; GNU-style tools use manual parsing for full flexibility).
#
# Usage:
#   bash cli_flags_demo.sh [-v] [-n COUNT] [-o FILE] text...
#
#   -v          verbose: print what the tool does
#   -n COUNT    repeat each word COUNT times (default 1)
#   -o FILE     write output to FILE instead of stdout
#   -h          show help
#
# Example:
#   bash cli_flags_demo.sh -v -n 2 hello world
#   bash cli_flags_demo.sh -o /tmp/out.txt -n 3 alpha beta

set -euo pipefail

# --- Defaults ----------------------------------------------------------------
verbose=0
repeat=1
output_file=""

usage() {
    cat <<'USAGE'
Usage: bash cli_flags_demo.sh [options] word...

Repeats each word N times, optionally writing to a file.

Options:
  -v          verbose: log what the tool does
  -n COUNT    repeat each word COUNT times (default: 1)
  -o FILE     write to FILE instead of stdout
  -h          show this help
USAGE
}

# --- Parse flags ---------------------------------------------------------------
# OPTSTRING: "vn:o:h"
#   v  -> boolean flag
#   n: -> flag requiring an argument (value lands in $opt)
#   o: -> flag requiring an argument
#   h  -> boolean flag
#
# getopts sets $opt to the current flag and advances OPTIND.
# A "?" means an unknown flag; a ":" means a required arg is missing.

while getopts ":vn:o:h" opt; do
    case "$opt" in
        v)  verbose=1 ;;
        n)
            if ! [[ "$OPTARG" =~ ^[1-9][0-9]*$ ]]; then
                echo "error: -n expects a positive integer, got '$OPTARG'" >&2
                exit 1
            fi
            repeat="$OPTARG"
            ;;
        o)  output_file="$OPTARG" ;;
        h)  usage; exit 0 ;;
        :)  echo "error: -${OPTARG} requires an argument" >&2; exit 1 ;;
        \?) echo "error: unknown option -${OPTARG}" >&2; usage >&2; exit 1 ;;
    esac
done

# Shift away the parsed flags; what remains are the positional words.
shift "$((OPTIND - 1))"

if [[ $# -lt 1 ]]; then
    echo "error: at least one word is required" >&2
    usage >&2
    exit 1
fi

log() {
    if [[ "$verbose" -eq 1 ]]; then
        echo "[verbose] $*" >&2   # diagnostics go to stderr, never stdout
    fi
}

# --- Do the work -----------------------------------------------------------------

body=""
for word in "$@"; do
    for ((i = 0; i < repeat; i++)); do
        body+="$word "
    done
done
body="${body% }"   # trim the trailing space

log "repeating $# words $repeat time(s)"
log "words: $*"

if [[ -n "$output_file" ]]; then
    printf '%s\n' "$body" > "$output_file"
    log "wrote $output_file"
    echo "wrote $output_file"
else
    printf '%s\n' "$body"
fi

# --- Error paths to try -------------------------------------------------------------
#   bash cli_flags_demo.sh                 -> missing words error
#   bash cli_flags_demo.sh -n              -> "requires an argument"
#   bash cli_flags_demo.sh -n x hi         -> "positive integer" error
#   bash cli_flags_demo.sh -z hi           -> unknown option + usage
#   bash cli_flags_demo.sh -v -n 2 hi yo   -> works, verbose on stderr
