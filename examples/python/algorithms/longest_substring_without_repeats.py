"""
Topic: Longest substring without repeating characters.

Concepts:
- Sliding window with two pointers
- Dict as "last seen index" table
- Amortized O(n) without ever shrinking the window backwards

Given a string, find the length of the longest substring that contains
no repeated characters, and return that substring itself.

Example:
Input:  "abcabcbb"
Output: 3, "abc"

Input:  "pwwkew"
Output: 3, "wke"  (not "pkew" — substrings must be contiguous)

Time Complexity:  O(n) — each index is visited at most once
Space Complexity: O(min(n, alphabet_size))
"""

from typing import Dict, Tuple


def longest_unique_substring(s: str) -> Tuple[int, str]:
    last_seen: Dict[str, int] = {}
    start = 0          # left edge of the window
    best_length = 0
    best_start = 0

    for end, char in enumerate(s):
        # If we've seen `char` inside the current window, jump the
        # left edge to just past its previous position. We use max()
        # because the previous occurrence may lie *before* `start`
        # (outside the window), in which case the window stays put.
        if char in last_seen:
            start = max(start, last_seen[char] + 1)

        last_seen[char] = end

        window_length = end - start + 1
        if window_length > best_length:
            best_length = window_length
            best_start = start

    return best_length, s[best_start:best_start + best_length]


# --- Demo -----------------------------------------------------------------

cases = [
    "abcabcbb",   # -> (3, "abc")
    "pwwkew",     # -> (3, "wke")
    "abcdef",     # -> (6, "abcdef")
    "aaaa",       # -> (1, "a")
    "",           # -> (0, "")
    "abcbdaf",    # -> (5, "cbdaf")
]

for case in cases:
    length, substring = longest_unique_substring(case)
    print(f"input={case!r:12} length={length}  substring={substring!r}")

# --- Why the two-pointer trick is O(n) -------------------------------------
#
# A naive approach tries every starting index and scans forward: O(n^2).
# Here the `end` pointer always moves forward, and `start` only ever
# moves forward too (max() guarantees it). Each character is inserted
# into the dict once and read at most a constant number of times, so
# the total work is linear.
