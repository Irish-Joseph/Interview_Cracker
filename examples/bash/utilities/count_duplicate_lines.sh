#!/usr/bin/env bash
#
# Topic: Count duplicate lines in one or more text files.
#
# Concepts:
#   - sort + uniq -c pipeline (the classic counting idiom)
#   - awk for filtering only the duplicated lines
#   - Command substitution and argument handling
#   - set -euo pipefail for defensive scripting
#
# Usage:
#   bash count_duplicate_lines.sh <file> [more files...]
#
# The script prints, per file, every line that occurs more than once
# together with its occurrence count, most frequent first.
#
# Time complexity: O(n log n) per file (dominated by the sort).

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: bash count_duplicate_lines.sh <file> [more files...]" >&2
    exit 1
fi

for file in "$@"; do
    if [[ ! -r "$file" ]]; then
        echo "skip: '$file' is not a readable file" >&2
        continue
    fi

    echo "=== $file ==="

    # Step 1: sort puts identical lines together.
    # Step 2: uniq -c prefixes each line with its count.
    # Step 3: awk keeps only lines whose count is greater than 1.
    # Step 4: sort -rn orders duplicates by count, highest first.
    duplicates=$(
        sort -- "$file" \
            | uniq -c \
            | awk '$1 > 1' \
            | sort -rn
    )

    if [[ -z "$duplicates" ]]; then
        echo "  (no duplicate lines)"
    else
        printf '%s\n' "$duplicates" |
            awk '{
                count = $1;
                $1 = "";                       # drop the count field
                sub(/^ /, "", $0);             # drop the leading space
                printf "  %4d x %s\n", count, $0
            }'
    fi
    echo
done

# Example input (for reference):
#
#   apple
#   banana
#   apple
#   cherry
#   banana
#   apple
#
# Expected output for that file:
#   === sample.txt ===
#       3 x apple
#       2 x banana
