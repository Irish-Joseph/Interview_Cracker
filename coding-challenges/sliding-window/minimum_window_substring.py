"""
Challenge:  Minimum Window Substring
Pattern:    Sliding window (dynamic, character-frequency driven)
Difficulty: Hard

PROBLEM
-------
Given two strings s and t, return the minimum-length substring of s that
contains every character of t (including duplicates). If no such
substring exists, return "".

EXAMPLES
--------
s = "ADOBECODEBANC", t = "ABC" -> "BANC"
s = "a",           t = "a"     -> "a"
s = "a",           t = "aa"    -> ""    (one 'a' cannot cover two)
s = "aab",         t = "b"     -> "b"

CONSTRAINTS
-----------
- 1 <= len(s), len(t) <= 10^5; uppercase and lowercase letters only.
- The straightforward "scan every start position and count characters"
  solution is O(n * m) — too slow at these sizes. Aim for O(n).

HINT
----
Grow a window's right edge until it covers t's character counts, then
shrink the left edge while it still does — recording the best length in
between. You need a running tally of how many distinct character
requirements are currently satisfied, not a full recount per step.

COMPLEXITY
----------
Time:  O(n) - each pointer only moves right, together at most 2n steps
Space: O(1) - fixed-size frequency tables (alphabet, not input)
"""

from collections import Counter


def min_window(s: str, t: str) -> str:
    needed = Counter(t)
    still_needed = len(needed)  # distinct characters not yet satisfied

    best = (float("inf"), 0)    # (length, start index)
    counts: dict[str, int] = {}
    left = 0

    for right, ch in enumerate(s):
        if ch in needed:
            counts[ch] = counts.get(ch, 0) + 1
            if counts[ch] == needed[ch]:
                still_needed -= 1

        # Shrink while the window still covers t completely.
        while still_needed == 0:
            window = right - left + 1
            if window < best[0]:
                best = (window, left)

            removed = s[left]
            if removed in needed:
                counts[removed] -= 1
                if counts[removed] < needed[removed]:
                    still_needed += 1
            left += 1

    length, start = best
    return s[start:start + length] if length != float("inf") else ""


def _tests() -> None:
    # No match / trivial matches.
    assert min_window("a", "aa") == ""
    assert min_window("a", "a") == "a"
    assert min_window("abc", "xyz") == ""
    assert min_window("aa", "a") == "a"

    # The classic example, and a duplicate-letter requirement.
    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("aab", "b") == "b"
    assert min_window("WANKIND", "ANK") == "ANK"
    assert min_window("ab", "ba") == "ab"        # order in t does not matter
    assert min_window("aabbcc", "abc") == "abbc"   # smallest window holding all three

    # Case that breaks the naive "first valid window is best" approach:
    # the answer appears only after the window has grown and shrunk.
    assert min_window("bba", "ab") == "ba"

    # Cross-check against brute force on randomised inputs.
    import random

    def brute(s: str, t: str) -> str:
        best = ""
        for i in range(len(s)):
            for j in range(i + len(t), len(s) + 1):
                if Counter(s[i:j]) >= Counter(t):
                    if not best or len(s[i:j]) < len(best):
                        best = s[i:j]
                    break  # longer j only gets bigger
        return best

    random.seed(42)
    alphabet = "ab"
    for _ in range(300):
        s = "".join(random.choice(alphabet) for _ in range(random.randint(1, 12)))
        t = "".join(random.choice(alphabet) for _ in range(random.randint(1, 4)))
        assert min_window(s, t) == brute(s, t), (s, t, min_window(s, t), brute(s, t))

    print("minimum_window_substring: all tests passed")


if __name__ == "__main__":
    _tests()
