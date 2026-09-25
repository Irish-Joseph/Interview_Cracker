#!/usr/bin/env bash
# Topic: set -e (errexit) - the failures it does NOT die on
#
# The misconception: "set -e makes the script die on any error."
# What it actually does: exit on a failed command whose status is NOT about
# to be inspected. errexit is suspended exactly where the shell is going to
# CHECK the result:
#
#   1. the condition of if / while / until
#   2. any command in a && or || list EXCEPT the last
#   3. EVERY command inside a function that was called from either of those
#      contexts (this is the big one: the whole function body is exempt)
#
# Plus two friends with their own traps:
#   - without `set -o pipefail`, `false | true` exits 0
#   - `set -u` turns undefined variables into errors (escape: ${var:-def})
#
# Each demo below runs in a `bash -c` child so the parent script stays alive
# to report what happened.
#
# Run: bash examples/bash/basics/set_e_pitfalls.sh
# Expected output: at the bottom of this file (stdout only; the one
# unbound-variable message from demo 7 goes to stderr).

echo "=== 1. bare failing command: the script exits ==="
bash -c 'set -e
false
echo "never reached"'
echo "child exited with $?"

echo "=== 2. failure in an if condition: expected, no exit ==="
bash -c 'set -e
if false; then
  echo "then branch"
else
  echo "else branch (script continues)"
fi
echo "still alive"'
echo "child exited with $?"

echo "=== 3. && and || lists: only the list RESULT counts ==="
bash -c 'set -e
false && echo "then-part of a failed && never runs"
echo "still alive after the && list"
false || echo "|| body ran because the left side failed"
echo "still alive after the || list"'
echo "child exited with $?"

echo "=== 4. the big one: function called from a condition ==="
bash -c 'set -e
risky() {
  echo "step one"
  false                     # a real failure...
  echo "step three (ran anyway - errexit was off for the whole body)"
}
if risky; then
  echo "condition said: success"
else
  echo "condition said: failure"
fi
echo "still alive"'
echo "child exited with $?"
echo "# NOTE: because the LAST command in risky() succeeded, its status is"
echo "# 0 and the condition even reports success. The failure vanished."

echo "=== 5. the SAME function in a normal context: exits ==="
bash -c 'set -e
boom() { false; }
boom
echo "never reached"'
echo "child exited with $?"

echo "=== 6. pipelines hide the left side without pipefail ==="
bash -c 'set -e
false | true
echo "pipeline survived without pipefail"'
echo "child exited with $?"
bash -c 'set -e
set -o pipefail
false | true
echo "never reached"'
echo "with pipefail, child exited with $?"

echo "=== 7. set -u: undefined variables are errors ==="
bash -c 'set -euo pipefail
echo "${UNDEFINED_VAR:-fallback}"'
bash -c 'set -u
echo "$UNDEFINED_VAR2"' 2>/dev/null
echo "child exited with $? (unbound variable message went to stderr; 127 on this bash)"

echo "=== takeaway ==="
echo "# Put 'set -euo pipefail' at the top of scripts. Then remember:"
echo "#  - commands you WANT to ignore a failure from belong in if/||/&&"
echo "#  - a failed step inside a function used as a condition is silent:"
echo "#    check its status explicitly (if risky; then ... else fail)"

# --- Actual output ---------------------------------------------------------
# === 1. bare failing command: the script exits ===
# child exited with 1
# === 2. failure in an if condition: expected, no exit ===
# else branch (script continues)
# still alive
# child exited with 0
# === 3. && and || lists: only the list RESULT counts ===
# still alive after the && list
# || body ran because the left side failed
# still alive after the || list
# child exited with 0
# === 4. the big one: function called from a condition ===
# step one
# step three (ran anyway - errexit was off for the whole body)
# condition said: success
# still alive
# child exited with 0
# # NOTE: because the LAST command in risky() succeeded, its status is
# # 0 and the condition even reports success. The failure vanished.
# === 5. the SAME function in a normal context: exits ===
# child exited with 1
# === 6. pipelines hide the left side without pipefail ===
# pipeline survived without pipefail
# child exited with 0
# with pipefail, child exited with 1
# === 7. set -u: undefined variables are errors ===
# fallback
# child exited with 127 (unbound variable message went to stderr; 127 on this bash)
# === takeaway ===
# # Put 'set -euo pipefail' at the top of scripts. Then remember:
# #  - commands you WANT to ignore a failure from belong in if/||/&&
# #  - a failed step inside a function used as a condition is silent:
# #    check its status explicitly (if risky; then ... else fail)
