"""Challenge: Sliding Window Maximum | Pattern: monotonic deque | Difficulty: Hard

Return the maximum in every contiguous window of size k.
Example: [1,3,-1,-3,5,3,6,7], k=3 -> [3,3,5,5,6,7].
Constraints: empty input returns []; otherwise 1 <= k <= len(nums).
Hint: keep only indices that can still become a future maximum.
Complexity: O(n) time (each index enters/leaves once), O(k) space.
"""

from collections import deque
import random


def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    if not nums:
        return []
    if k < 1 or k > len(nums):
        raise ValueError("k must be between 1 and len(nums)")
    candidates: deque[int] = deque()
    result: list[int] = []
    for right, value in enumerate(nums):
        left = right - k + 1
        if candidates and candidates[0] < left:
            candidates.popleft()
        while candidates and nums[candidates[-1]] <= value:
            candidates.pop()
        candidates.append(right)
        if left >= 0:
            result.append(nums[candidates[0]])
    return result


def _brute(nums: list[int], k: int) -> list[int]:
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def _tests() -> None:
    assert sliding_window_maximum([], 1) == []
    assert sliding_window_maximum([8], 1) == [8]
    assert sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert sliding_window_maximum([9, 8, 7, 6], 2) == [9, 8, 7]
    rng = random.Random(24)
    for size in range(1, 20):
        for _ in range(30):
            nums = [rng.randint(-10, 10) for _ in range(size)]
            k = rng.randint(1, size)
            assert sliding_window_maximum(nums, k) == _brute(nums, k)
    print("Sliding Window Maximum: all tests passed")


if __name__ == "__main__":
    _tests()
