#!/usr/bin/env bash
#
# Topic: Find the largest files in a directory tree.
#
# Concepts:
#   - find for recursive file discovery
#   - du for disk usage per file
#   - Sorting numerically in reverse
#   - head to keep only the top N
#   - printf for aligned output
#
# Usage:
#   bash find_largest_files.sh <directory> [top N]
#
# Example:
#   bash find_largest_files.sh /var/log 5
#
# Prints the N largest files under <directory>, biggest first,
# with human-readable sizes.
#
# Complexity: O(files in tree) — find + du each visit every file.

set -euo pipefail

usage() {
    echo "Usage: bash find_largest_files.sh <directory> [top N]" >&2
    exit 1
}

[[ $# -ge 1 ]] || usage

directory="$1"
top_n="${2:-5}"

# Basic validation before doing any work.
if [[ ! -d "$directory" ]]; then
    echo "error: '$directory' is not a directory" >&2
    exit 1
fi

if ! [[ "$top_n" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: top N must be a positive integer, got '$top_n'" >&2
    exit 1
fi

# Pipeline, step by step:
#   find   - only regular files, print NUL-separated (safe for spaces)
#   du -h  - human-readable size per file
#   sort   - numeric reverse sort on the size column (field 1)
#   head   - keep only the top N lines
#
# du's output looks like:  4.0K\t/tmp/some/file.txt
#
# We use -z / --null-data so filenames with spaces or newlines
# don't break the pipeline.
find "$directory" -type f -print0 \
    | du -h --files0-from=- 2>/dev/null \
    | sort -rh \
    | head -n "$top_n" \
    | awk -F'\t' '{
        # Humanize the size a little and align the columns.
        printf "  %-10s %s\n", $1, $2
    }'

# ---------------------------------------------------------------------------
# Note on `du -h --files0-from=-`:
#   - reads a NUL-separated file list from stdin
#   - -h  human-readable sizes (K/M/G)
#
# Portability: --files0-from is GNU coreutils. On macOS/BSD use:
#   find "$directory" -type f -exec du -h {} + | sort -rh | head -n "$top_n"
# ---------------------------------------------------------------------------
