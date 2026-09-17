"""
Challenge:  Valid Parentheses
Pattern:    Stack (matching pairs)
Difficulty: Easy

PROBLEM
-------
Given a string containing only '(', ')', '{', '}', '[' and ']', determine
whether the brackets are correctly balanced and correctly nested.

EXAMPLES
--------
"()"      -> True
"()[]{}"  -> True
"(]"      -> False
"([)]"    -> False   (overlapping, not nested)
"{[]}"    -> True

CONSTRAINTS
-----------
- The empty string is valid.

HINT
----
Counting brackets is not enough: "([)]" has the right counts but is invalid.
Nesting means the most RECENT unclosed opener is the one a closer must match -
and "most recent" is exactly what a stack gives you.

Two edge cases decide whether your answer is right:
  - a closer arriving when nothing is open
  - openers still on the stack when the string ends

COMPLEXITY
----------
Time:  O(n)
Space: O(n) - all openers, e.g. "((((("
"""

PAIRS = {")": "(", "]": "[", "}": "{"}


def is_valid(s: str) -> bool:
    stack: list[str] = []

    for char in s:
        if char in "([{":
            stack.append(char)
        elif char in PAIRS:
            # Nothing open, or the wrong opener on top -> invalid.
            if not stack or stack.pop() != PAIRS[char]:
                return False

    # Anything still open at the end is unbalanced.
    return not stack


def _tests() -> None:
    assert is_valid("()") is True
    assert is_valid("()[]{}") is True
    assert is_valid("(]") is False
    assert is_valid("([)]") is False            # overlapping, not nested
    assert is_valid("{[]}") is True
    assert is_valid("") is True                 # vacuously balanced
    assert is_valid("(") is False               # leftover opener
    assert is_valid(")") is False               # closer with nothing open
    assert is_valid("(((((") is False
    assert is_valid(")))))") is False
    assert is_valid("({[]})") is True
    assert is_valid("()(") is False

    # Cross-check against repeated removal of adjacent pairs.
    import random

    def reference(text: str) -> bool:
        previous = None
        while previous != text:
            previous = text
            for pair in ("()", "[]", "{}"):
                text = text.replace(pair, "")
        return text == ""

    random.seed(31)
    for _ in range(500):
        text = "".join(random.choices("()[]{}", k=random.randint(0, 10)))
        assert is_valid(text) == reference(text), text

    print("valid_parentheses: all tests passed (500 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
