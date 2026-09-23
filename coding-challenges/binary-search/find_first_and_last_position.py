"""Challenge: Find First and Last Position | Pattern: binary search | Difficulty: Medium

In a sorted list, return the first and last target index or [-1, -1].
Example: [5,7,7,8,8,10], target=8 -> [3,4]. Empty input is allowed.
Hint: find the first index >= target and the first index > target.
Complexity: O(log n) time and O(1) extra space.
"""

import random


def _lower_bound(nums: list[int], target: int) -> int:
    left, right = 0, len(nums)
    while left < right:
        middle = left + (right - left) // 2
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def find_first_and_last(nums: list[int], target: int) -> list[int]:
    first = _lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    return [first, _lower_bound(nums, target + 1) - 1]


def _brute(nums: list[int], target: int) -> list[int]:
    positions = [i for i, value in enumerate(nums) if value == target]
    return [positions[0], positions[-1]] if positions else [-1, -1]


def _tests() -> None:
    assert find_first_and_last([], 8) == [-1, -1]
    assert find_first_and_last([8], 8) == [0, 0]
    assert find_first_and_last([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert find_first_and_last([2, 2, 2], 2) == [0, 2]
    rng = random.Random(24)
    for size in range(30):
        for _ in range(30):
            nums = sorted(rng.randint(-5, 5) for _ in range(size))
            target = rng.randint(-6, 6)
            assert find_first_and_last(nums, target) == _brute(nums, target)
    print("Find First and Last Position: all tests passed")


if __name__ == "__main__":
    _tests()
