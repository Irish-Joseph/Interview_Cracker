"""Challenge: Permutations | Pattern: backtracking | Difficulty: Medium

Return every ordering of distinct integers. The empty list has one: [[]].
Example: [1,2,3] -> 6 permutations. Hint: fix, recurse, undo the swap.
Complexity: O(n*n!) time to copy answers; O(n) recursion excluding output.
"""

from itertools import permutations as reference_permutations
import random


def permutations(nums: list[int]) -> list[list[int]]:
    values = nums.copy()
    result: list[list[int]] = []

    def visit(first: int) -> None:
        if first == len(values):
            result.append(values.copy())
            return
        for chosen in range(first, len(values)):
            values[first], values[chosen] = values[chosen], values[first]
            visit(first + 1)
            values[first], values[chosen] = values[chosen], values[first]

    visit(0)
    return result


def _normalise(items: list[list[int]]) -> list[tuple[int, ...]]:
    return sorted(map(tuple, items))


def _tests() -> None:
    assert permutations([]) == [[]]
    assert permutations([7]) == [[7]]
    assert len(permutations([1, 2, 3])) == 6
    rng = random.Random(24)
    for size in range(7):
        values = rng.sample(range(-20, 20), size)
        expected = sorted(reference_permutations(values))
        assert _normalise(permutations(values)) == expected
    print("Permutations: all tests passed")


if __name__ == "__main__":
    _tests()
