"""
Challenge:  Combination Sum
Pattern:    Backtracking (with pruning)
Difficulty: Medium

PROBLEM
-------
Given an array of DISTINCT positive integers and a target, return all unique
combinations of the candidates that sum to the target. The SAME candidate may
be chosen any number of times. Two combinations are the same if they contain
the same numbers, regardless of order.

EXAMPLES
--------
candidates=[2,3,6,7], target=7  ->  [[2,2,3], [7]]
candidates=[2,3,5],   target=8  ->  [[2,2,2,2], [2,3,3], [3,5]]
candidates=[2],       target=1  ->  []
candidates=[2,3],     target=0  ->  [[]]     (one way: take nothing)

CONSTRAINTS
-----------
- All candidates are positive and distinct.
- A candidate may be reused without limit.
- [2,2,3] and [2,3,2] are the SAME combination - return it once.

HINT
----
This differs from Subsets in two ways, and each maps to one line.

1. REUSE: after choosing candidates[i], the next choice may be candidates[i]
   again. So recurse with `i`, not `i + 1`. (Recursing with i+1 would forbid
   reuse; recursing from 0 would produce [2,3] and [3,2] as separate answers.)

2. PRUNING: because every candidate is positive, once the remaining target
   goes negative no deeper choice can recover. Stop that branch immediately.

Sorting first lets you prune harder: once candidates[i] exceeds the remaining
target, every later candidate does too, so you can break out of the loop
rather than continue.

COMPLEXITY
----------
Time:  O(n^(target/min_candidate)) in the worst case - the recursion tree is
       as deep as target/min and as wide as n. Pruning cuts this hard in
       practice but does not change the bound.
Space: O(target/min_candidate) for the recursion stack, excluding the output.
"""


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    results: list[list[int]] = []
    current: list[int] = []
    # Sorting enables the `break` below: once one candidate is too big,
    # every later one is too.
    ordered = sorted(candidates)

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            results.append(current.copy())
            return

        for i in range(start, len(ordered)):
            if ordered[i] > remaining:
                break                    # sorted, so no later candidate fits

            current.append(ordered[i])   # choose
            # `i`, not `i + 1`: the same candidate may be reused.
            backtrack(i, remaining - ordered[i])
            current.pop()                # un-choose

    backtrack(0, target)
    return results


def _tests() -> None:
    def norm(result: list[list[int]]) -> list[tuple[int, ...]]:
        return sorted(tuple(sorted(c)) for c in result)

    assert norm(combination_sum([2, 3, 6, 7], 7)) == norm([[2, 2, 3], [7]])
    assert norm(combination_sum([2, 3, 5], 8)) == norm([[2, 2, 2, 2], [2, 3, 3], [3, 5]])
    assert combination_sum([2], 1) == []
    assert combination_sum([2, 3], 0) == [[]]        # take nothing
    assert combination_sum([], 5) == []
    assert norm(combination_sum([1], 3)) == [(1, 1, 1)]
    assert norm(combination_sum([7], 7)) == [(7,)]

    # Every returned combination must actually sum to the target, use only
    # permitted candidates, and appear exactly once.
    import random

    random.seed(73)
    for _ in range(300):
        cands = random.sample(range(2, 12), random.randint(1, 5))
        target = random.randint(0, 20)
        out = combination_sum(cands, target)

        for combo in out:
            assert sum(combo) == target, (cands, target, combo)
            assert all(c in cands for c in combo), (cands, combo)
        assert len(out) == len(set(map(lambda c: tuple(sorted(c)), out))), (cands, target)

    # Cross-check the COUNT against an independent dynamic-programming count of
    # multisets summing to target. This catches both missed and duplicated
    # combinations, which the checks above cannot.
    def count_multisets(cands: list[int], target: int) -> int:
        # ways[t] = number of multisets summing to t, using each candidate in
        # a fixed order so permutations are not counted separately.
        ways = [0] * (target + 1)
        ways[0] = 1
        for c in sorted(cands):
            for t in range(c, target + 1):
                ways[t] += ways[t - c]
        return ways[target]

    random.seed(79)
    for _ in range(300):
        cands = random.sample(range(2, 10), random.randint(1, 4))
        target = random.randint(0, 18)
        assert len(combination_sum(cands, target)) == count_multisets(cands, target), \
            (cands, target)

    print("combination_sum: all tests passed (600 randomised, DP cross-check)")


if __name__ == "__main__":
    _tests()
