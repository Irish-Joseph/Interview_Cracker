"""
Challenge:  Longest Common Subsequence (length)
Pattern:    Dynamic programming (two sequences)
Difficulty: Medium

PROBLEM
    Given two sequences, return the length of their longest common
    subsequence - a sequence obtainable from both by deleting elements,
    without reordering.

EXAMPLES
    "abcde", "ace"          -> 3   (the subsequence is "ace")
    "abc", "abc"            -> 3
    "abc", "def"            -> 0   (no common characters at all)
    "", "anything"          -> 0

CONSTRAINTS
    - Lengths up to ~1000, so the O(m*n) table is the intended size.
    - This file returns the LENGTH. Returning the subsequence itself is a
      standard follow-up (walk the table back from (m, n)).

HINT
    State: `dp[i][j]` is the LCS length of the first i characters of the
    first string and the first j of the second. If the two current
    characters match, you can take one plus the smaller state; if they
    differ, the best answer is the better of dropping one character from
    either side - try both and keep the max.

COMPLEXITY
    Time: O(m*n) - every cell of the table is filled once, in constant work.
    Space: O(m*n) for the table; O(min(m, n)) if you keep only the previous
    row (the table only ever looks one row up and one cell left).
"""

from __future__ import annotations

import random


def lcs_length(a: str, b: str) -> int:
    """Length of the longest common subsequence of `a` and `b`."""
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0

    # dp[i][j] = LCS length of a[:i] and b[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def _brute_force(a: str, b: str) -> int:
    """Exponential reference: try take/skip at every position pair."""
    import functools

    @functools.cache
    def rec(i: int, j: int) -> int:
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + rec(i + 1, j + 1)
        return max(rec(i + 1, j), rec(i, j + 1))

    return rec(0, 0)


def _tests() -> None:
    # empty and single-character inputs
    assert lcs_length("", "") == 0
    assert lcs_length("", "abc") == 0
    assert lcs_length("abc", "") == 0
    assert lcs_length("a", "a") == 1
    assert lcs_length("a", "b") == 0
    assert lcs_length("ab", "a") == 1

    # the documented examples
    assert lcs_length("abcde", "ace") == 3
    assert lcs_length("abc", "abc") == 3
    assert lcs_length("abc", "def") == 0

    # the case that breaks "only count adjacent matches":
    # the match at positions 0 and 2 must be counted, not skipped
    assert lcs_length("abca", "a") == 1
    # matches are not required to be adjacent or in a block:
    assert lcs_length("a*b*c*d", "abcd") == 4
    # and one where the common letters appear in a different order:
    assert lcs_length("abc", "cab") == 2     # "ab" appears in both
    # while this one genuinely collapses to a single letter:
    assert lcs_length("abc", "cba") == 1

    # cross-check against the exponential reference on small random inputs
    rng = random.Random(20260922)
    for _ in range(300):
        a = "".join(rng.choice("abcd") for _ in range(rng.randrange(0, 12)))
        b = "".join(rng.choice("abcd") for _ in range(rng.randrange(0, 12)))
        assert lcs_length(a, b) == _brute_force(a, b), (a, b)

    print("lcs_length: all tests passed")


if __name__ == "__main__":
    _tests()
