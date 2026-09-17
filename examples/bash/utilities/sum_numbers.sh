#!/usr/bin/env bash
#
# Topic: Summing numbers from text with awk (and friends).
#
# Concepts:
#   - awk as a line-by-line number processor
#   - Numeric vs string fields (awk coerces on arithmetic)
#   - Accumulating in the main block, reporting in END
#   - min / max / count / average in a single pass
#   - Feeding awk from a file argument or stdin ("-")
#
# awk reads input line by line; numbers are its natural use case.
# One pass computes sum, count, min and max at once.
#
# Usage:
#   bash sum_numbers.sh <file>
#   bash sum_numbers.sh --demo
#   echo "1 2 3" | bash sum_numbers.sh -
#
# Complexity: O(lines) — one pass, constant memory.

set -euo pipefail

input="${1:--}"

# One awk program for all cases: a file argument is passed through,
# and "-" means read stdin (awk's default when no file is given).
summarize() {
    if [[ "$1" == "-" ]]; then
        awk '
            {
                # A line may hold several numbers; process every field.
                for (f = 1; f <= NF; f++) {
                    v = $f
                    sum += v
                    if (++n == 1 || v < min) min = v
                    if (n == 1 || v > max)   max = v
                }
            }
            END {
                if (n == 0) {
                    print "no numbers found" > "/dev/stderr"
                    exit 1
                }
                printf "count: %d\n", n
                printf "sum:   %g\n", sum
                printf "avg:   %.2f\n", sum / n
                printf "min:   %g  max: %g\n", min, max
            }
        '
    else
        awk '
            {
                # A line may hold several numbers; process every field.
                for (f = 1; f <= NF; f++) {
                    v = $f
                    sum += v
                    if (++n == 1 || v < min) min = v
                    if (n == 1 || v > max)   max = v
                }
            }
            END {
                if (n == 0) {
                    print "no numbers found" > "/dev/stderr"
                    exit 1
                }
                printf "count: %d\n", n
                printf "sum:   %g\n", sum
                printf "avg:   %.2f\n", sum / n
                printf "min:   %g  max: %g\n", min, max
            }
        ' "$1"
    fi
}

# Demo mode:  bash sum_numbers.sh --demo
# Demo numbers: 10 / "20 30" / 40 / 5.5   (the "20 30" line counts as TWO)
# Expected: count: 5, sum: 105.5, avg: 21.10, min: 5.5, max: 40

if [[ "$input" == "--demo" ]]; then
    printf '10\n20 30\n40\n5.5\n' | summarize -
    exit 0
fi

# --- Input validation -------------------------------------------------------

if [[ "$input" != "-" && ! -r "$input" ]]; then
    echo "error: '$input' is not a readable file" >&2
    exit 1
fi

summarize "$input"
