#!/usr/bin/env bash
# Topic: bash arithmetic - $(( )), (( )), and the traps in between
#
# Concepts:
#   - $(( expr )) is a WORD: it evaluates and substitutes a number
#   - (( expr )) is a COMMAND: the expression's VALUE becomes the exit
#     status, so (( 0 )) FAILS (exit 1) - the exact opposite of what
#     "the test passed" intuition says
#   - bash arithmetic is INTEGER ONLY: 7/2 is 3; 0.5 is a syntax error
#   - numbers with a leading 0 are OCTAL: 010 is 8, and 08 is a syntax
#     error. Force base 10 with 10#
#   - the set -e killer: (( --x )) when x is 1 evaluates to 0 and exits
#     with status 1
#
# Run: bash arithmetic_traps.sh

echo '== $(( )) is a word: it produces a number =='
echo "$(( 2 + 3 ))"            # 5
echo "7/2 = $(( 7 / 2 ))"     # 3 - integer division, no fraction
echo "7%2 = $(( 7 % 2 ))"     # 1 - the remainder, as a value
echo "$(( 2 ** 10 ))"          # 1024 - ** is exponentiation

echo
echo "== (( )) is a command: the value becomes the exit status =="
(( 1 + 1 ))  ; echo "(( 1+1 ))  exit: $?"   # 0 (value 2, nonzero -> success)
(( 0 ))      ; echo "(( 0 ))    exit: $?"   # 1 (value 0 -> FAILURE, like test -z)
(( 5 == 5 )) ; echo "(( 5==5 )) exit: $?"   # 0 (true  -> value 1 -> success)
(( 5 == 6 )) ; echo "(( 5==6 )) exit: $?"   # 1 (false -> value 0 -> failure)

echo
echo "== the set -e killer: pre-decrement to zero =="
x=1
if (( --x )); then
  echo "decrement produced nonzero, x is now $x"
else
  echo "x was 1, --x is 0 -> (( )) exited 1 -> under 'set -e' the script would die here"
fi

echo
echo "== base: leading zero means octal =="
echo "010   = $(( 010 ))"     # 8
echo "017   = $(( 017 ))"     # 15
echo "020   = $(( 020 ))"     # 16
echo "10#10 = $(( 10#10 ))"   # 10 - force base 10
echo "0x10  = $(( 0x10 ))"    # 16 - hex is fine
# echo "$(( 08 ))"            # uncomment: '08: value too great for base'

echo
echo "== strings and variables =="
word="5"
echo "word=5 -> word+1 = $(( word + 1 ))"   # 6
bad="08"
if ( echo "$(( bad + 1 ))" ) >/dev/null 2>&1; then
  echo "bad=08 expanded fine"
else
  echo "bad=08 -> raw expansion fails: '08' is not a valid octal number"
fi
echo "bad=08 -> forced base 10: $(( 10#$bad + 1 ))"   # 9
