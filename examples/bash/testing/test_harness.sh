#!/usr/bin/env bash
#
# Topic: A tiny test harness — expected vs actual with diff.
#
# Concepts:
#   - Table-driven tests in a shell script
#   - Command substitution capturing actual output
#   - diff for readable expected/actual comparison
#   - Exit codes as the test protocol (0 = pass, 1 = fail)
#   - set -u and careful error handling (NOT -e: failures are data)
#
# This is the shell equivalent of a unit test: feed input, capture
# output, compare against the expected string, report pass/fail.
# No frameworks required — just diff and discipline.
#
# Usage:  bash test_harness.sh
# Exit code: 0 if all tests pass, 1 otherwise.

set -u

PASS=0
FAIL=0
FAILED_NAMES=()

# expect <test-name> <expected-output> <actual-output>
expect() {
    local name="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        printf "PASS  %s\n" "$name"
        PASS=$((PASS + 1))
    else
        printf "FAIL  %s\n" "$name"
        # Readable comparison: show the two sides, then a real diff.
        printf "      expected: %s\n" "$expected"
        printf "      actual:   %s\n" "$actual"
        diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") \
            | sed 's/^/      /' || true
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
    fi
}

# The function under test: clamp a number into [lo, hi].
clamp() {
    local n="$1" lo="$2" hi="$3"
    if (( n < lo )); then echo "$lo"
    elif (( n > hi )); then echo "$hi"
    else echo "$n"
    fi
}

# The function under test 2: pluralize.
pluralize() {
    local word="$1" count="$2"
    if (( count == 1 )); then echo "$word"
    else echo "${word}s"
    fi
}

# --- Tests: clamp --------------------------------------------------------
expect "clamp: within range"  "5"  "$(clamp 5 0 10)"
expect "clamp: below range"   "0"  "$(clamp -3 0 10)"
expect "clamp: above range"   "10" "$(clamp 42 0 10)"
expect "clamp: equal to lo"   "0"  "$(clamp 0 0 10)"
expect "clamp: equal to hi"   "10" "$(clamp 10 0 10)"

# --- Tests: pluralize ------------------------------------------------------
# (pluralize adds "s" for anything except exactly 1 — it does NOT know
#  about irregular forms; the tests assert the function's real contract.)
expect "plural: one"    "child"  "$(pluralize child 1)"
expect "plural: many"   "cats"   "$(pluralize cat 3)"
expect "plural: zero"   "boxs"   "$(pluralize box 0)"

# --- Tests: pipeline behavior (grep counts) ---------------------------------
input=$'alpha\nbeta\nalpha\nbeta\nbeta\n'
expect "grep -c counts matches" "3" "$(printf '%s' "$input" | grep -c beta)"
expect "awk unique count" "2" "$(printf '%s' "$input" | awk '!seen[$0]++' | wc -l | tr -d ' ')"

# --- Tests: deliberate failure demo (commented out) ---------------------------
# expect "this should fail" "x" "y"   # uncomment to see a FAIL + diff

# --- Summary -------------------------------------------------------------------
echo
printf "%d passed, %d failed\n" "$PASS" "$FAIL"

if [[ $FAIL -gt 0 ]]; then
    printf "failed tests:\n"
    for name in "${FAILED_NAMES[@]}"; do
        printf "  - %s\n" "$name"
    done
    exit 1
fi
exit 0

# Expected output:
# PASS  clamp: within range
# PASS  clamp: below range
# PASS  clamp: above range
# PASS  clamp: equal to lo
# PASS  clamp: equal to hi
# PASS  plural: one
# PASS  plural: many
# PASS  plural: zero
# PASS  grep -c counts matches
# PASS  awk unique count
#
# 10 passed, 0 failed
