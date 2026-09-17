#!/usr/bin/env bash
#
# Topic: Reading a file line by line without breaking on real data.
#
# Concepts:
#   - `while IFS= read -r line` — the safe line-reading loop
#   - What IFS= prevents (stripping of leading/trailing whitespace)
#   - What -r prevents (backslash interpretation)
#   - Handling a final line without a trailing newline (read's exit code)
#   - Why naive `for line in $(cat file)` is wrong
#
# Example output (for a mixed sample file):
#   1|  padded line kept
#   2|tab-start kept
#   3|back\slash kept
#   4|final line without newline kept

set -euo pipefail

sample="$(mktemp)"
trap 'rm -f "$sample"' EXIT

# Build a tricky sample file: padded whitespace, tabs, backslashes,
# and a final line with NO trailing newline.
printf '  padded line kept\n' >"$sample"
printf '\ttab-start kept\n' >>"$sample"
printf 'back\\slash kept\n' >>"$sample"
printf 'final line without newline' >>"$sample"   # note: no \n

echo "--- Safe: while IFS= read -r ---"
n=0
# `|| [ -n "$line" ]` rescues a last line that lacks a trailing newline:
# read returns non-zero at EOF, but still fills $line with the data.
while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    echo "${n}|${line}"
done < "$sample"

echo
echo "--- Unsafe: for line in $(cat) style (word splitting!) ---"
# Demonstrate the failure mode without breaking set -e:
{
    for line in $(cat "$sample"); do
        echo "word: ${line}"
    done
} || true

echo
echo "--- Same loop from a pipe (command output) ---"
printf 'alpha\nbeta beta\n' | while IFS= read -r line; do
    echo "pipe: ${line}"
done
