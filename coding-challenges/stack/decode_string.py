"""
Challenge:  Decode String
Pattern:    Stack (explicit stack of (context, multiplier) frames)
Difficulty: Medium

PROBLEM
-------
Given an encoded string, return the decoded form. The grammar is:
    S := ( digit+ '[' S ']' ) | non-digits   , repeated
That is, "3[ab]" means "ababab" and encodings nest: "2[a3[b]]" -> "abbbabbb".

EXAMPLES
--------
"3[a2[bc]]"      -> "abcbcabcbcabcbc"   (inner decodes first)
"2[a3[b]]"       -> "abbbabbb"
"10[a]"          -> "aaaaaaaaaa"        (multi-digit multiplier)
"xyz"            -> "xyz"               (no brackets at all)

CONSTRAINTS
-----------
- 0 <= len(s) <= 30; the input is always a valid encoding.
- Digits may be multi-digit; brackets are always well balanced.
- Aim for a single left-to-right pass (an explicit stack, not recursion).

HINT
----
A '[' freezes the current state: everything decoded so far and the pending
multiplier become the "outside" of this bracket. On ']' you pop that frame
and the text you have just built inside is repeated by its multiplier, then
appended back to the outside. What data structure holds "the outside"?

COMPLEXITY
----------
Time:  O(L * K) worst case where L is the input length and K the nesting
       multiplication factor - the OUTPUT can be exponentially larger than
       the input, so no algorithm can beat the size of the answer
Space: O(L + K) - the stack of frames plus the output being built
"""


def decode(s: str) -> str:
    stack = []      # frames of (text_before_bracket, multiplier)
    cur = ""        # text decoded since the most recent '['
    num = 0

    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)          # multi-digit counts accumulate
        elif ch == "[":
            stack.append((cur, num))          # freeze the outside context
            cur, num = "", 0
        elif ch == "]":
            prev, k = stack.pop()             # close the context
            cur = prev + cur * k
        else:
            cur += ch

    return cur


def _reference(s: str, i: int = 0):
    """Recursive brute force: returns (decoded_text, index_after_construction)."""
    out = []
    while i < len(s) and s[i] != "]":
        if s[i].isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            k = int(s[i:j])
            assert s[j] == "["
            inner, i = _reference(s, j + 1)   # returns at the matching ']'
            out.append(inner * k)
            i += 1                            # skip ']'
        else:
            out.append(s[i])
            i += 1
    return "".join(out), i


def _tests() -> None:
    # Empty input and no brackets: identity.
    assert decode("") == ""
    assert decode("xyz") == "xyz"

    # Single element and single construction.
    assert decode("3[a]") == "aaa"
    assert decode("2[abc]3[cd]ef") == "abcabccdcdcdef"

    # The case that breaks a flat (non-stack) approach: nesting.
    assert decode("2[a3[b]]") == "abbbabbb"
    assert decode("3[a2[bc]]") == "abcbcabcbcabcbc"

    # Multi-digit multiplier.
    assert decode("10[a]") == "a" * 10

    # Cross-check against the recursive reference on random valid encodings.
    import random
    random.seed(25)

    def gen(depth: int) -> str:
        parts = []
        for _ in range(random.randint(1, 3)):
            if depth > 0 and random.random() < 0.6:
                parts.append(f"{random.randint(1, 2)}[{gen(depth - 1)}]")
            else:
                parts.append(random.choice("abc"))
        return "".join(parts)

    for _ in range(200):
        s = gen(3)
        expected, end = _reference(s, 0)
        assert decode(s) == expected, (s, expected, decode(s))
        assert end == len(s), s

    print("decode_string: all tests passed")


if __name__ == "__main__":
    _tests()
