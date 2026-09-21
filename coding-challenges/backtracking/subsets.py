"""
Challenge:  Subsets (the power set)
Pattern:    Backtracking
Difficulty: Medium

PROBLEM
-------
Given an array of DISTINCT integers, return all possible subsets (the power
set). The solution must not contain duplicate subsets; the order of the
subsets, and of elements within them, does not matter.

EXAMPLES
--------
[1, 2, 3]  ->  [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
[0]        ->  [[], [0]]
[]         ->  [[]]          <- the empty set is a subset of itself

CONSTRAINTS
-----------
- Elements are distinct.
- There are exactly 2^n subsets, so n is small in practice (n <= 20 or so).

HINT
----
Each element is a binary decision: in, or out. That is 2^n combinations, and
it maps directly onto a recursion tree where each level decides one element.

Unlike most backtracking problems, there is no "is it complete?" test to pass
before recording - EVERY node of the tree is a valid subset, including the
root (the empty set). So record on entry, not at the leaves.

Passing a `start` index is what prevents [1,2] and [2,1] both appearing.

COMPLEXITY
----------
Time:  O(n * 2^n) - 2^n subsets, and copying each costs up to O(n).
       You cannot beat 2^n when the output IS 2^n items.
Space: O(n) for the recursion stack and the working list,
       excluding the output itself.
"""


def subsets(nums: list[int]) -> list[list[int]]:
    results: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int) -> None:
        # Every node is a valid subset, so record immediately. The .copy() is
        # essential: `current` keeps mutating, so appending it directly would
        # leave every result pointing at the same (eventually empty) list.
        results.append(current.copy())

        for i in range(start, len(nums)):
            current.append(nums[i])      # choose
            backtrack(i + 1)             # explore, from the NEXT index onward
            current.pop()                # un-choose

    backtrack(0)
    return results


def subsets_bitmask(nums: list[int]) -> list[list[int]]:
    """Iterative alternative: treat each integer 0..2^n-1 as a membership mask.

    Bit i of the mask decides whether nums[i] is included. Often faster and
    with no recursion, but the backtracking version generalises to problems
    where you need to prune.
    """
    n = len(nums)
    out: list[list[int]] = []
    for mask in range(1 << n):
        out.append([nums[i] for i in range(n) if mask & (1 << i)])
    return out


def _tests() -> None:
    def norm(result: list[list[int]]) -> list[tuple[int, ...]]:
        """Order is unspecified, so compare as a sorted set of tuples."""
        return sorted(tuple(s) for s in result)

    assert norm(subsets([1, 2, 3])) == norm([
        [], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]
    ])
    assert norm(subsets([0])) == [(), (0,)]
    assert subsets([]) == [[]]                    # the empty set, not []
    assert len(subsets([1, 2, 3, 4])) == 16       # 2^4

    # No duplicates, ever.
    for data in ([1, 2, 3], [5], [], [1, 2, 3, 4, 5]):
        result = subsets(data)
        assert len(result) == len(set(map(tuple, result))), data
        assert len(result) == 2 ** len(data), data

    # Results must be independent objects, not aliases of the working list.
    result = subsets([1, 2])
    result[0].append(99)
    assert subsets([1, 2])[0] == [], "results must be copies"

    # Both implementations must agree, on many random inputs.
    import random

    random.seed(71)
    for _ in range(200):
        data = random.sample(range(-9, 10), random.randint(0, 8))
        assert norm(subsets(data)) == norm(subsets_bitmask(data)), data

    # Cross-check against itertools, the reference for combinations.
    import itertools

    for data in ([1, 2, 3], [4, 5, 6, 7], []):
        expected = []
        for size in range(len(data) + 1):
            expected.extend(list(c) for c in itertools.combinations(data, size))
        assert norm(subsets(data)) == norm(expected), data

    print("subsets: all tests passed (200 randomised, both variants)")


if __name__ == "__main__":
    _tests()
