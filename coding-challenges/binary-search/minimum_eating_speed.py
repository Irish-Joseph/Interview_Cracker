"""
Challenge:  Minimum Eating Speed (binary search on the answer)
Pattern:    Binary search over a monotonic predicate
Difficulty: Medium

PROBLEM
-------
There are n piles of bananas; piles[i] is the count in pile i. You may eat at a
speed of k bananas per hour: each hour you pick one pile and eat up to k from
it (if the pile has fewer than k left, you finish it and stop for that hour).

Given h hours available, return the minimum integer speed k that finishes all
the bananas within h hours.

EXAMPLES
--------
piles=[3,6,7,11], h=8   -> 4
piles=[30,11,23,4,20], h=5  -> 30
piles=[30,11,23,4,20], h=6  -> 23

CONSTRAINTS
-----------
- 1 <= len(piles) <= h

HINT
----
There is no array to search here - so what are you binary searching?

The ANSWER. Notice that "can I finish at speed k?" is monotonic: if speed k
works, every speed above k also works; if it fails, every speed below also
fails. That gives you  False False False True True True  over k in [1, max(piles)],
and finding the first True is exactly binary search.

Write the feasibility check first, then wrap binary search around it.

COMPLEXITY
----------
Time:  O(n log m), n = number of piles, m = the largest pile
Space: O(1)
"""

import math


def hours_needed(piles: list[int], speed: int) -> int:
    """Hours to clear every pile at `speed`. A partly-eaten pile still costs
    a whole hour, hence the ceiling division."""
    return sum(math.ceil(pile / speed) for pile in piles)


def min_eating_speed(piles: list[int], hours: int) -> int:
    # Speed 1 is always feasible given enough hours; max(piles) always finishes
    # in len(piles) hours, so the answer lies in [1, max(piles)].
    low, high = 1, max(piles)
    best = high

    while low <= high:
        mid = low + (high - low) // 2

        if hours_needed(piles, mid) <= hours:
            best = mid          # feasible - record it, then try slower
            high = mid - 1
        else:
            low = mid + 1       # too slow

    return best


def _tests() -> None:
    assert min_eating_speed([3, 6, 7, 11], 8) == 4
    assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30
    assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23
    assert min_eating_speed([1], 1) == 1
    assert min_eating_speed([1000000000], 2) == 500000000
    assert min_eating_speed([5, 5, 5], 3) == 5          # exactly one hour each

    # The predicate really is monotonic - verify it on a sample.
    piles = [3, 6, 7, 11]
    feasible = [hours_needed(piles, k) <= 8 for k in range(1, 15)]
    assert feasible == sorted(feasible), "predicate must be False... then True..."

    # Cross-check against a linear scan of every candidate speed.
    import random

    random.seed(29)
    for _ in range(200):
        data = [random.randint(1, 30) for _ in range(random.randint(1, 6))]
        hours = random.randint(len(data), len(data) + 12)
        expected = next(k for k in range(1, max(data) + 1)
                        if hours_needed(data, k) <= hours)
        assert min_eating_speed(data, hours) == expected, (data, hours)

    print("minimum_eating_speed: all tests passed (200 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
