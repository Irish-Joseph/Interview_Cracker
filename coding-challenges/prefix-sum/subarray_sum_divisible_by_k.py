"""
Challenge:  Subarray Sums Divisible by K
Pattern:    Prefix sum + hashmap of residues (the modular twist)
Difficulty: Medium

PROBLEM
    Given a list of integers (they may be negative) and a positive integer
    k, return the number of contiguous subarrays whose sum is divisible by k.

EXAMPLES
    [4, 5, 0, -2, -3, 1], k = 5  -> 7
    [1, 2, 3], k = 3             -> 3   ([1,2], [3], [1,2,3])
    [5], k = 9                   -> 0
    [0], k = 7                   -> 1   (a single zero is divisible by k)

CONSTRAINTS
    - Up to 10^5 elements, sums can be large, and NEGATIVES are allowed -
      so "the sum" itself is the wrong thing to store; the residue is what
      matters.
    - k >= 1. (k == 1: every subarray qualifies - n*(n+1)/2 of them.)

HINT
    A subarray (i..j] sum is divisible by k exactly when prefix[j] and
    prefix[i] leave the SAME residue mod k - so count pairs of equal
    residues. Store "how many prefixes so far had each residue" in a dict.
    The negative-number trap: in most languages, -1 % 5 is -1, not 4, so
    normalize residues before counting them. (Python's % already does the
    right thing - which is why this file can skip the fixup and just say so.)

COMPLEXITY
    Time: O(n) - one pass, O(1) dict work per element.
    Space: O(min(n, k)) - at most k distinct residues.
"""

from __future__ import annotations

import random
from collections import Counter


def count_subarrays(nums: list[int], k: int) -> int:
    # Python's % returns a non-negative result for positive k, so the
    # residue is already normalised - no fixup needed here. (In C/Java you
    # would write ((prefix % k) + k) % k.)
    counts: Counter[int] = Counter({0: 1})   # the empty prefix has residue 0
    prefix = 0
    result = 0

    for x in nums:
        prefix = (prefix + x) % k
        # Every earlier prefix with this same residue forms a valid subarray.
        result += counts[prefix]
        counts[prefix] += 1

    return result


def _brute_force(nums: list[int], k: int) -> int:
    n = len(nums)
    count = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s % k == 0:
                count += 1
    return count


def _tests() -> None:
    # empty input and k == 1
    assert count_subarrays([], 5) == 0
    assert count_subarrays([1, 2, 3], 1) == 6      # n*(n+1)/2 = 6
    assert count_subarrays([], 1) == 0

    # the documented examples
    assert count_subarrays([4, 5, 0, -2, -3, 1], 5) == 7
    assert count_subarrays([5], 9) == 0
    assert count_subarrays([0], 7) == 1
    assert count_subarrays([1, 2, 3], 3) == 3

    # the negative-number case: -3 is divisible by 3 on its own,
    # and pairs across a negative boundary still count
    assert count_subarrays([-3], 3) == 1
    assert count_subarrays([1, -1, 1], 2) == 2     # [1,-1] and [-1,1] (total is 1)
    assert count_subarrays([-1, -1, -1], 3) == 1   # only the full [-1,-1,-1]

    # cross-check against the brute force on randomised inputs (with negatives)
    rng = random.Random(20260923)
    for _ in range(500):
        n = rng.randrange(0, 30)
        nums = [rng.randrange(-20, 21) for _ in range(n)]
        k = rng.randrange(1, 11)
        assert count_subarrays(nums, k) == _brute_force(nums, k), (nums, k)

    print("count_subarrays: all tests passed")


if __name__ == "__main__":
    _tests()
