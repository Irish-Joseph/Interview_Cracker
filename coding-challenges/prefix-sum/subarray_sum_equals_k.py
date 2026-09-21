"""
Challenge:  Subarray Sum Equals K
Pattern:    Prefix sum + hash map
Difficulty: Medium

PROBLEM
-------
Given an integer array and an integer k, return the TOTAL NUMBER of contiguous
subarrays whose sum equals k. Values may be negative.

EXAMPLES
--------
[1,1,1],     k=2  ->  2      ([1,1] at 0..1 and at 1..2 - overlapping counts)
[1,2,3],     k=3  ->  2      ([1,2] and [3])
[1,-1,0],    k=0  ->  3      ([1,-1], [0], [1,-1,0])
[],          k=0  ->  0      (no subarrays at all)

CONSTRAINTS
-----------
- Values can be NEGATIVE, so a sliding window does not work: shrinking the
  window is not guaranteed to reduce the sum.
- Aim for O(n).

HINT
----
Brute force is every start/end pair: O(n^2).

Define prefix[j] as the sum of the first j elements. Then the sum of the
subarray (i, j] is prefix[j] - prefix[i]. You want that to equal k:

    prefix[j] - prefix[i] == k
    =>  prefix[i] == prefix[j] - k

So while scanning, at each j, ask: how many EARLIER prefixes equalled
prefix[j] - k? That is a hash-map lookup, not a search - the same inversion
that turns Two Sum from O(n^2) into O(n).

One detail decides whether this is correct: a subarray starting at index 0 has
prefix[i] == 0, so the map must already contain 0 before the loop starts.

COMPLEXITY
----------
Time:  O(n) - one pass, O(1) average per lookup
Space: O(n) - the map may hold every distinct prefix
"""

from collections import defaultdict


def subarray_sum(nums: list[int], k: int) -> int:
    # seen[p] = how many times prefix sum p has occurred so far.
    # Seeding with {0: 1} accounts for subarrays that start at index 0:
    # without it, [3] with k=3 would return 0 instead of 1.
    seen: dict[int, int] = defaultdict(int)
    seen[0] = 1

    running = 0
    count = 0

    for n in nums:
        running += n
        # Every earlier prefix equal to (running - k) marks the start of a
        # subarray ending here that sums to k.
        count += seen[running - k]
        # Record AFTER counting, so a zero-length subarray is never counted.
        seen[running] += 1

    return count


def _tests() -> None:
    assert subarray_sum([1, 1, 1], 2) == 2
    assert subarray_sum([1, 2, 3], 3) == 2
    assert subarray_sum([1, -1, 0], 0) == 3
    assert subarray_sum([], 0) == 0
    assert subarray_sum([3], 3) == 1            # starts at index 0
    assert subarray_sum([3], 5) == 0
    assert subarray_sum([0, 0, 0], 0) == 6      # every one of the 6 subarrays
    assert subarray_sum([-1, -1, 1], 0) == 1
    assert subarray_sum([1, 2, 1, 2, 1], 3) == 4

    # The {0: 1} seed is load-bearing - prove it.
    def without_seed(nums: list[int], k: int) -> int:
        seen: dict[int, int] = defaultdict(int)     # deliberately NOT seeded
        running = count = 0
        for n in nums:
            running += n
            count += seen[running - k]
            seen[running] += 1
        return count

    assert subarray_sum([3], 3) == 1 and without_seed([3], 3) == 0, \
        "the {0: 1} seed is what counts subarrays starting at index 0"

    # Cross-check against brute force over every start/end pair.
    import random

    def brute(nums: list[int], k: int) -> int:
        total = 0
        for i in range(len(nums)):
            running = 0
            for j in range(i, len(nums)):
                running += nums[j]
                if running == k:
                    total += 1
        return total

    random.seed(89)
    for _ in range(600):
        data = [random.randint(-4, 4) for _ in range(random.randint(0, 14))]
        k = random.randint(-6, 6)
        assert subarray_sum(data, k) == brute(data, k), (data, k)

    print("subarray_sum_equals_k: all tests passed (600 randomised vs brute force)")


if __name__ == "__main__":
    _tests()
