"""
Challenge:  Maximum Sum Subarray of Size K
Pattern:    Sliding window (fixed size)
Difficulty: Easy

PROBLEM
-------
Given an array of integers and a number k, find the maximum sum of any
contiguous subarray of exactly k elements.

EXAMPLES
--------
[2, 1, 5, 1, 3, 2], k=3  -> 9   ([5, 1, 3])
[2, 3, 4, 1, 5],    k=2  -> 7   ([3, 4])

CONSTRAINTS
-----------
- Return None if k is larger than the array, or k <= 0.
- Values may be negative.

HINT
----
The obvious solution recomputes the sum of every window from scratch: O(n*k).
But consecutive windows overlap in k-1 elements. When the window slides one
step right, what is the *only* thing that changes about its sum?

COMPLEXITY
----------
Time:  O(n) - each element is added once and subtracted once
Space: O(1)
"""


def max_sum_subarray(nums: list[int], k: int) -> int | None:
    if k <= 0 or k > len(nums):
        return None

    window = sum(nums[:k])          # the first window, computed once
    best = window

    for right in range(k, len(nums)):
        # Slide: one element enters on the right, one leaves on the left.
        window += nums[right] - nums[right - k]
        best = max(best, window)

    return best


def _tests() -> None:
    assert max_sum_subarray([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_sum_subarray([2, 3, 4, 1, 5], 2) == 7
    assert max_sum_subarray([1], 1) == 1
    assert max_sum_subarray([-1, -2, -3], 2) == -3      # all negative
    assert max_sum_subarray([5, 5, 5], 3) == 15

    # Edge cases
    assert max_sum_subarray([], 1) is None
    assert max_sum_subarray([1, 2], 3) is None          # k larger than input
    assert max_sum_subarray([1, 2], 0) is None
    assert max_sum_subarray([1, 2], -1) is None

    # Cross-check against the naive O(n*k) version.
    import random

    random.seed(5)
    for _ in range(300):
        data = [random.randint(-20, 20) for _ in range(random.randint(1, 12))]
        k = random.randint(1, len(data))
        expected = max(sum(data[i:i + k]) for i in range(len(data) - k + 1))
        assert max_sum_subarray(data, k) == expected, (data, k)

    print("max_sum_subarray_of_size_k: all tests passed (300 randomised cases)")


if __name__ == "__main__":
    _tests()
