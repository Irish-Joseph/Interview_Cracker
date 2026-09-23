#!/usr/bin/env bash
# Topic: word splitting and pathname expansion - the two things that make an
#       unquoted $variable a live bug
#
# After parameter expansion, bash does TWO extra things to UNQUOTED results:
#   1. word splitting on $IFS (default: space, tab, newline)
#   2. pathname expansion (globs): * ? [abc]
# Quoting the expansion ("$var") suppresses both. That one habit - always
# double-quote your variables - prevents most classic shell-script bugs.
#
# Concepts:
#   - unquoted $var with spaces splits into many words
#   - a glob in an unquoted variable is expanded against the FILESYSTEM
#   - IFS controls the splitting
#   - set -f disables globbing; an unmatched glob is passed literally (bash)
#   - the safe reading loop: while IFS= read -r (no split, no backslash eat)
#
# Run: bash quoting_word_splitting.sh

tmpdir=$(mktemp -d)
cd "$tmpdir"
trap 'cd / && rm -rf "$tmpdir"' EXIT

echo "== 1. unquoted expansion splits =="
name="Mary Jane Watson"
echo "unquoted: [$name]"          # three words: Mary, Jane, Watson
echo "quoted:   [$name]"          # one word: the whole string
words=($name)
echo "array from unquoted: ${#words[@]} elements: ${words[0]} / ${words[1]} / ${words[2]}"

echo
echo "== 2. an unquoted glob hits the filesystem =="
touch a.txt b.txt c.log
pattern="*.txt"
count_unquoted=$(ls $pattern | wc -l)
count_quoted=$(ls "$pattern" 2>/dev/null | wc -l)
echo "unquoted \$pattern   -> $count_unquoted files (the glob expanded)"
echo "quoted   \\\"$pattern\\\" -> $count_quoted files (literal name, nothing matches)"
empty="does_not_exist_*"
echo "unquoted non-matching glob: [$empty]   (bash passes it literally)"
shopt -s nullglob
arr=($empty)
echo "with nullglob, the same glob vanishes: ${#arr[@]} elements"
shopt -u nullglob

echo
echo "== 3. IFS controls the splitting =="
line="alpha;beta;gamma"
IFS=';' read -ra parts <<< "$line"
echo "split on ';': ${parts[0]} / ${parts[1]} / ${parts[2]}"

echo
echo "== 4. the safe read loop: IFS= read -r =="
printf '  padded line one\nline two with \ backslash\n  line three\n' > rows.txt
n=0
while IFS= read -r row; do
  n=$((n + 1))
  echo "row $n: [$row]"
done < rows.txt
# (IFS= prevents the leading spaces from being stripped; -r keeps the
#  backslash literal - a plain 'read row' would do neither)

echo
echo "== 5. set -f: freeze the globbing =="
set -f
arr=($pattern)
echo "with set -f, *.txt is a literal: ${arr[0]}"
set +f
