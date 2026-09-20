#!/usr/bin/env bash
#
# Topic: Process substitution — <(...) and >(...) give commands file-like
#        endpoints without a temporary file.
#
# Concepts:
#   - <(cmd) behaves like a readable file (/dev/fd/N) holding cmd's output.
#     It is SYNCHRONOUS: by the time the reader reads it, the data is there.
#   - >(cmd) is the writable mirror: what you write to it becomes cmd's
#     stdin. It runs ASYNCHRONOUSLY (bash cannot `wait` on it), so its
#     classic use is "also save this to a file", not "show me its output".
#   - diff / paste / wc all normally read FILES; process substitution lets
#     them read COMMAND OUTPUT instead, with no temp files on disk.
#   - The command inside <(...) runs in a SUBSHELL, so any variable it sets
#     does NOT survive back in the parent shell.
#
# Self-contained: builds its own input files in a temp dir, cleans up after.

set -euo pipefail

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

printf 'apple\nbanana\ncherry\n' > "$workdir/alpha.txt"
printf 'apple\nbanana\ndate\n'   > "$workdir/beta.txt"

echo "=== 1. diff two command outputs, no temp files ==="
# Equivalent to sorting each file then diffing the results.
if diff <(sort "$workdir/alpha.txt") <(sort "$workdir/beta.txt"); then
    echo "identical"
else
    echo "-> differs by one line (cherry vs date)"
fi

echo
echo "=== 2. paste two command streams side by side ==="
paste -d'\t' <(cat "$workdir/alpha.txt") <(cat "$workdir/beta.txt")

echo
echo "=== 3. count lines coming straight from a command ==="
lines=$(wc -l < <(grep . "$workdir/alpha.txt"))
echo "alpha.txt has $lines non-empty lines"

echo
echo "=== 4. the subshell caveat ==="
# The RHS runs in a subshell; a variable it sets never reaches the parent.
count=0
diff <(echo same) <(count=99; echo same) >/dev/null
echo "count in parent is still $count (the 99 was set in a subshell)"

echo
echo "=== 5. >(...) in its safe, common form: also save to a file ==="
# >(...) runs asynchronously (bash cannot `wait` on it), so we don't read
# its stdout for timing — we just wait for the durable side effect: the
# FILE that tee writes. The `until` condition is exempt from `set -e`.
sort "$workdir/alpha.txt" > >(tee "$workdir/sorted.txt" >/dev/null)
i=0
until [ -s "$workdir/sorted.txt" ]; do
    i=$((i + 1))
    [ "$i" -ge 50 ] && break      # give up after ~5s (should never happen)
    sleep 0.1
done
echo "saved via >(tee ...):"
cat "$workdir/sorted.txt"
