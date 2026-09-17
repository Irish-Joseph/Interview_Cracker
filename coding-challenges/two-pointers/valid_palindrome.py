"""
Challenge:  Valid Palindrome
Pattern:    Two pointers (converging)
Difficulty: Easy

PROBLEM
-------
Given a string, decide whether it reads the same forwards and backwards,
considering only alphanumeric characters and ignoring case.

EXAMPLES
--------
"A man, a plan, a canal: Panama"  -> True   (amanaplanacanalpanama)
"race a car"                      -> False
" "                               -> True   (no alphanumeric characters)

CONSTRAINTS
-----------
- The string may contain letters, digits, spaces and punctuation.
- Aim for O(1) extra space.

HINT
----
Cleaning the string first ("".join(filter(str.isalnum, s.lower()))) works and is
O(n), but it allocates a whole second string. Can you compare in place by
walking inwards from both ends and skipping characters you do not care about?

COMPLEXITY
----------
Time:  O(n) - each pointer crosses the string at most once
Space: O(1) - no copy of the input
"""


def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1

    while left < right:
        # Skip anything that is not alphanumeric, from either end.
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True


def _tests() -> None:
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome(" ") is True
    assert is_palindrome("") is True
    assert is_palindrome("a") is True
    assert is_palindrome("ab") is False
    assert is_palindrome("aa") is True
    assert is_palindrome("0P") is False          # digit vs letter, not equal
    assert is_palindrome(".,!") is True          # no alphanumerics at all
    assert is_palindrome("Was it a car or a cat I saw?") is True

    # Cross-check against the simple reference implementation.
    def reference(text: str) -> bool:
        cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
        return cleaned == cleaned[::-1]

    for case in ["", " ", "a", "ab", "0P", "No lemon, no melon", "Hello"]:
        assert is_palindrome(case) == reference(case), case

    print("valid_palindrome: all tests passed")


if __name__ == "__main__":
    _tests()
