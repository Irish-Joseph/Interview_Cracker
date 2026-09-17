"""
Challenge:  Longest Substring Without Repeating Characters
Pattern:    Sliding window (variable size)
Difficulty: Medium

PROBLEM
-------
Given a string, find the length of the longest substring that contains no
repeated characters.

EXAMPLES
--------
"abcabcbb"  -> 3   ("abc")
"bbbbb"     -> 1   ("b")
"pwwkew"    -> 3   ("wke" - note "pwke" is a subsequence, not a substring)
""          -> 0

CONSTRAINTS
-----------
- Any characters, not just lowercase letters.

HINT
----
Keep a window that is always valid (no repeats). When the character at `right`
is already inside the window, the window must shrink from the left until it is
not.

The naive shrink moves `left` one step at a time. But if you store the last
index at which you saw each character, you can jump `left` straight past the
previous occurrence in one step.

Careful: the stored index may be *behind* the current window, from a character
that already left. Check before you jump.

COMPLEXITY
----------
Time:  O(n) - one pass, each character processed once
Space: O(min(n, alphabet)) for the index map
"""


def longest_unique_substring(s: str) -> int:
    last_seen: dict[str, int] = {}     # character -> most recent index
    left = 0
    best = 0

    for right, char in enumerate(s):
        # Only jump if the previous sighting is inside the current window.
        # Without the `>= left` guard, a stale index would drag `left`
        # backwards and let duplicates back into the window.
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1

        last_seen[char] = right
        best = max(best, right - left + 1)

    return best


def _tests() -> None:
    assert longest_unique_substring("abcabcbb") == 3
    assert longest_unique_substring("bbbbb") == 1
    assert longest_unique_substring("pwwkew") == 3
    assert longest_unique_substring("") == 0
    assert longest_unique_substring("a") == 1
    assert longest_unique_substring("abcdef") == 6
    assert longest_unique_substring("tmmzuxt") == 5      # "mzuxt"
    assert longest_unique_substring("dvdf") == 3         # "vdf" - the stale-index case
    assert longest_unique_substring("  ") == 1           # spaces count
    assert longest_unique_substring("a!a!b") == 3        # "a!b"

    # Cross-check against brute force over all substrings.
    import random
    import string

    def reference(text: str) -> int:
        best = 0
        for i in range(len(text)):
            seen: set[str] = set()
            for j in range(i, len(text)):
                if text[j] in seen:
                    break
                seen.add(text[j])
                best = max(best, j - i + 1)
        return best

    random.seed(13)
    for _ in range(400):
        text = "".join(random.choices(string.ascii_lowercase[:4], k=random.randint(0, 12)))
        assert longest_unique_substring(text) == reference(text), text

    print("longest_substring_without_repeats: all tests passed (400 randomised cases)")


if __name__ == "__main__":
    _tests()
