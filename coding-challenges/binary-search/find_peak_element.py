"""
Challenge:  Find Peak Element
Pattern:    Binary search (decision by slope, not by value)
Difficulty: Medium

PROBLEM
-------
A peak element is an element strictly greater than its neighbours. Given an
array nums where nums[i] != nums[i+1], find a peak element and return its
index. If several peaks exist, returning any one is correct.

You may imagine nums[-1] = nums[n] = -infinity, so an element at either end
can be a peak.

EXAMPLES
--------
[1, 2, 3, 1]          -> 2     (3 is a peak)
[1, 2, 1, 3, 5, 6, 4] -> 1 or 5   (both 2 and 6 are peaks; either is valid)
[1]                   -> 0

CONSTRAINTS
-----------
- n == 1 is allowed and is itself a peak.
- Adjacent values are never equal.
- Expected: better than scanning the whole array.

HINT
----
Look at the MIDPOINT's slope. If nums[mid] < nums[mid + 1], the array is
climbing to the right — since the array ends (and the imagined neighbour
beyond the edge is -infinity), the climb must turn over at some peak to the
right of mid. Discard the left half. Which half survives when
nums[mid] > nums[mid + 1]?

COMPLEXITY
----------
Time:  O(log n) - half the search space is discarded each step
Space: O(1)
"""


def find_peak(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1

    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
            # Climbing up: a peak lies at mid+1 or further right.
            left = mid + 1
        else:
            # At or above the right neighbour: mid itself is a valid
            # candidate, so it stays in the search space.
            right = mid

    # left == right is a peak by construction.
    return left


def is_peak(nums: list[int], i: int) -> bool:
    left_ok = i == 0 or nums[i] > nums[i - 1]
    right_ok = i == len(nums) - 1 or nums[i] > nums[i + 1]
    return left_ok and right_ok


def _tests() -> None:
    # Single element: trivially a peak.
    assert find_peak([1]) == 0
    assert find_peak([-5]) == 0

    # The two specified examples. Either peak index is acceptable.
    assert find_peak([1, 2, 3, 1]) == 2
    assert is_peak([1, 2, 1, 3, 5, 6, 4], find_peak([1, 2, 1, 3, 5, 6, 4]))

    # Endpoints can be peaks (imagined -infinity neighbours).
    assert find_peak([3, 2, 1]) == 0
    assert find_peak([1, 2, 3]) == 2

    # Multiple peaks: the answer just has to be A peak, not THE peak.
    for case in ([1, 2, 1, 3, 5, 6, 4], [5, 4, 3, 4, 5], [2, 1, 2, 1, 2]):
        assert is_peak(case, find_peak(case)), case

    # Strictly monotone and V-shaped inputs.
    assert is_peak([1, 2, 3, 4, 5], find_peak([1, 2, 3, 4, 5]))
    assert is_peak([5, 4, 3, 2, 1], find_peak([5, 4, 3, 2, 1]))
    assert is_peak([9, 7, 5, 3, 5, 7, 9], find_peak([9, 7, 5, 3, 5, 7, 9]))

    # Cross-check on randomised inputs: result must always be a real peak.
    import random

    random.seed(7)
    for _ in range(300):
        n = random.randint(1, 40)
        nums = random.sample(range(-100, 100), n)  # unique -> no equal neighbours
        idx = find_peak(nums)
        assert is_peak(nums, idx), (nums, idx)

    print("find_peak_element: all tests passed")


if __name__ == "__main__":
    _tests()
