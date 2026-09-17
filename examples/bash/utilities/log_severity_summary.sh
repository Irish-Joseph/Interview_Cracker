#!/usr/bin/env bash
#
# Topic: Summarize log file severity levels with awk.
#
# Concepts:
#   - awk fields ($1, $2, ...) and pattern-action rules
#   - Associative arrays in awk (counts[level]++)
#   - The END block for final output
#   - Sorting output inside a pipeline
#   - Reading from a file argument or stdin
#
# Expected log format (one entry per line):
#   2026-09-06T08:00:01Z ERROR db connection refused
#   2026-09-06T08:00:02Z INFO  api request handled
#
# Usage:
#   bash log_severity_summary.sh <logfile>
#   bash log_severity_summary.sh --demo     (self-test sample)
#   cat app.log | bash log_severity_summary.sh -
#
# Complexity: O(lines) — single pass, no sorting inside awk.

set -euo pipefail

usage() {
    echo "Usage: bash log_severity_summary.sh <logfile|->" >&2
    exit 1
}

[[ $# -eq 1 ]] || usage

input="$1"

# --- Demo mode: generate a sample log, then report on it --------------------

if [[ "$1" == "--demo" ]]; then
    demo_log=$(mktemp)
    trap 'rm -f "$demo_log"' EXIT
    cat <<'EOF' > "$demo_log"
2026-09-06T08:00:01Z ERROR db connection refused
2026-09-06T08:00:02Z INFO api request handled
2026-09-06T08:00:03Z WARN api slow response 1200ms
2026-09-06T08:00:04Z ERROR db timeout after 30s
2026-09-06T08:00:05Z INFO auth login ok
2026-09-06T08:00:06Z DEBUG db query executed
2026-09-06T08:00:07Z CRITICAL db disk full
2026-09-06T08:00:08Z INFO api request handled
this line does not match the format and is ignored
EOF
    input="$demo_log"
fi

# Expected summary for the --demo data:
#   ERROR      2
#   INFO       3
#   WARN       1
#   DEBUG      1
#   CRITICAL   1
#   TOTAL      8

# awk program, explained rule by rule:
#
#   $2 ~ /^(INFO|WARN|ERROR|DEBUG|CRITICAL)$/ { counts[$2]++ }
#       Pattern:  field 2 (the level) must be exactly a known level.
#       Action:   increment that level's counter (awk associative array).
#
#   END { for (level in counts) print counts[level], level }
#       After all input: emit "count level" for every seen level.
#
#   The final sort -rn orders by count, highest first.
read_log() {
    if [[ "$input" == "-" ]]; then
        awk '
            $2 ~ /^(INFO|WARN|ERROR|DEBUG|CRITICAL)$/ { counts[$2]++ }
            END { for (level in counts) print counts[level], level }
        ' | sort -rn
    else
        awk '
            $2 ~ /^(INFO|WARN|ERROR|DEBUG|CRITICAL)$/ { counts[$2]++ }
            END { for (level in counts) print counts[level], level }
        ' "$input" | sort -rn
    fi
}

# --- Report -----------------------------------------------------------------

if [[ "$input" != "-" && ! -r "$input" ]]; then
    echo "error: '$input' is not a readable file" >&2
    exit 1
fi

total=0
counts=$(read_log)
if [[ -z "$counts" ]]; then
    echo "no recognizable log lines found"
    exit 0
fi

# Pretty-print: fixed-width table plus a computed total.
while read -r count level; do
    printf "  %-10s %d\n" "$level" "$count"
    total=$((total + count))
done <<< "$counts"
printf "  %-10s %d\n" "TOTAL" "$total"

