"""
Challenge:  Sort Colors (the Dutch national flag problem)
Pattern:    Two pointers (read/write with a middle boundary)
Difficulty: Medium

PROBLEM
    Given a list of 0s, 1s and 2s (the "red, white, blue" balls), sort them
    in place so all 0s come first, then 1s, then 2s.

EXAMPLES
    [2, 0, 2, 1, 1, 0] -> [0, 0, 1, 1, 2, 2]
    [1]                -> [1]
    []                 -> []

CONSTRAINTS
    - Sort in place; O(1) extra space (no second array, no sort() call).
    - One pass through the data (O(n) comparisons) - sorting twice or
      partitioning via two separate passes is allowed by most statements,
      but the one-pass version is the point of this problem.

HINT
    Keep three regions with two boundary pointers: [0..lo) are 0s,
    [lo..mid) are 1s, [hi..n) are 2s, and everything mid is looking at
    is unsorted. What do you do when the current element is 1? When it
    is 0? What does the swap with hi do to the element that just moved
    INTO mid's position - do you need to look at it again?

COMPLEXITY
    Time: O(n) - `mid` advances on every step of the loop, and the loop
    stops at `hi`, which only decreases; nothing is ever revisited by mid.
    Space: O(1) - three indices, in place.
"""

from __future__ import annotations

import random


def sort_colors(nums: list[int]) -> None:
    """Sort 0/1/2 in place, one pass.

    Invariant while 0 <= mid <= hi:
        nums[0:lo]   are all 0
        nums[lo:mid] are all 1
        nums[hi+1:]  are all 2
        nums[mid:hi+1] is the unsorted middle
    """
    lo, mid, hi = 0, 0, len(nums) - 1

    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1            # the element swapped in from lo was a 1
        elif nums[mid] == 1:
            mid += 1
        else:                   # nums[mid] == 2: push it to the right end
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
            # mid does NOT advance: the element swapped in from hi is
            # unknown and must be classified on the next iteration.
    assert lo <= len(nums)      # sanity, not part of the algorithm


def _brute_force(nums: list[int]) -> list[int]:
    return sorted(nums)


def _tests() -> None:
    # empty and single element
    empty: list[int] = []
    sort_colors(empty)
    assert empty == []
    single = [1]
    sort_colors(single)
    assert single == [1]

    # the documented example
    nums = [2, 0, 2, 1, 1, 0]
    sort_colors(nums)
    assert nums == [0, 0, 1, 1, 2, 2], nums

    # all one value (the naive two-pointer version often stumbles here)
    for value in (0, 1, 2):
        block = [value] * 7
        sort_colors(block)
        assert block == [value] * 7, (value, block)

    # already sorted, reverse sorted, and 0s next to the hi boundary
    for given in ([0, 1, 2], [2, 1, 0], [2, 2, 0, 1, 2, 0]):
        nums = list(given)
        sort_colors(nums)
        assert nums == sorted(given), (given, nums)

    # in-place: the same list object must be mutated, not replaced
    nums = [2, 0, 1]
    sort_colors(nums)
    assert nums == [0, 1, 2]

    # cross-check against the brute force on randomised inputs
    rng = random.Random(20260922)
    for _ in range(2000):
        expected_input = [rng.randrange(3) for _ in range(rng.randrange(0, 40))]
        nums = list(expected_input)
        sort_colors(nums)
        assert nums == _brute_force(expected_input), expected_input

    print("sort_colors: all tests passed")


if __name__ == "__main__":
    _tests()
