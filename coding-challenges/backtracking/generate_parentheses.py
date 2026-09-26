"""Challenge: Generate Parentheses | Pattern: constrained backtracking | Difficulty: Medium

Return every well-formed string containing n pairs of parentheses.
Hint: never close more pairs than have been opened.
Complexity: O(Cn*n) output time and O(n) recursion, where Cn is Catalan(n).
"""

def generate_parentheses(n: int) -> list[str]:
    result, path = [], []
    def visit(opened: int, closed: int) -> None:
        if len(path) == 2 * n:
            result.append("".join(path)); return
        if opened < n:
            path.append("("); visit(opened + 1, closed); path.pop()
        if closed < opened:
            path.append(")"); visit(opened, closed + 1); path.pop()
    visit(0, 0)
    return result

def _is_valid(value: str) -> bool:
    balance = 0
    for char in value:
        balance += 1 if char == "(" else -1
        if balance < 0: return False
    return balance == 0

def _tests() -> None:
    assert generate_parentheses(0) == [""]
    assert generate_parentheses(1) == ["()"]
    assert set(generate_parentheses(3)) == {"((()))", "(()())", "(())()", "()(())", "()()()"}
    for n, expected in enumerate([1, 1, 2, 5, 14, 42, 132]):
        values = generate_parentheses(n)
        assert len(values) == len(set(values)) == expected
        assert all(len(value) == 2 * n and _is_valid(value) for value in values)
    print("Generate Parentheses: all tests passed")

if __name__ == "__main__": _tests()
