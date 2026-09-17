#!/usr/bin/env bash
# Use trap to clean temporary resources on normal exit and common signals.

set -euo pipefail

workspace=""

cleanup() {
    local exit_code=$?

    # Disable the trap first so cleanup cannot recursively trigger itself.
    trap - EXIT INT TERM

    if [[ -n "$workspace" && -d "$workspace" ]]; then
        rm -rf -- "$workspace"
        printf 'Removed temporary workspace: %s\n' "$workspace"
    fi

    exit "$exit_code"
}

trap cleanup EXIT INT TERM

workspace=$(mktemp -d "${TMPDIR:-/tmp}/trap-demo.XXXXXX")
printf 'Workspace: %s\n' "$workspace"

printf '%s\n' alpha beta gamma > "$workspace/input.txt"
tr '[:lower:]' '[:upper:]' < "$workspace/input.txt" > "$workspace/output.txt"

printf 'Processed output:\n'
cat "$workspace/output.txt"

if [[ "${1:-}" == "--fail" ]]; then
    printf 'Simulating a failure after creating temporary files.\n' >&2
    exit 1
fi

printf 'Work completed successfully.\n'

# The EXIT trap runs whether the script succeeds, fails, or receives INT/TERM.
