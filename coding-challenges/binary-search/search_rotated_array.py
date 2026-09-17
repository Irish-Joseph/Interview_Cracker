"""
Challenge:  Search in a Rotated Sorted Array
Pattern:    Binary search (modified)
Difficulty: Medium

PROBLEM
-------
A sorted array of distinct integers was rotated at some unknown pivot, e.g.
[0,1,2,4,5,6,7] became [4,5,6,7,0,1,2]. Given the rotated array and a target,
return the target's index, or -1.

EXAMPLES
--------
[4,5,6,7,0,1,2], target=0  -> 4
[4,5,6,7,0,1,2], target=3  -> -1
[1],             target=1  -> 0

CONSTRAINTS
-----------
- All values are distinct.
- Must run in O(log n) - a linear scan does not count.

HINT
----
You cannot compare against the midpoint alone, because the array is not fully
sorted. But here is the key observation: when you split a rotated sorted array
at any midpoint, AT LEAST ONE of the two halves is properly sorted.

Work out which half is sorted (compare nums[low] with nums[mid]), then check
whether the target lies inside that sorted half's range. If it does, search
there; otherwise search the other half.

COMPLEXITY
----------
Time:  O(log n)
Space: O(1)
"""


def search_rotated(nums: list[int], target: int) -> int:
    low, high = 0, len(nums) - 1

    while low <= high:
        mid = low + (high - low) // 2

        if nums[mid] == target:
            return mid

        # Exactly one side is guaranteed sorted. Identify it, then decide
        # whether the target falls within its known range.
        if nums[low] <= nums[mid]:
            # Left half [low..mid] is sorted.
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            # Right half [mid..high] is sorted.
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1

    return -1


def _tests() -> None:
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 4) == 0
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 2) == 6
    assert search_rotated([1], 1) == 0
    assert search_rotated([1], 0) == -1
    assert search_rotated([], 1) == -1
    assert search_rotated([1, 3], 3) == 1
    assert search_rotated([3, 1], 1) == 1
    assert search_rotated([1, 2, 3, 4, 5], 4) == 3      # not rotated at all

    # Exhaustive check: every rotation of every size, every target.
    for size in range(1, 12):
        base = list(range(size))
        for rotation in range(size):
            rotated = base[rotation:] + base[:rotation]
            for target in range(-1, size + 1):
                index = search_rotated(rotated, target)
                if target in rotated:
                    assert index != -1 and rotated[index] == target, (rotated, target)
                else:
                    assert index == -1, (rotated, target, index)

    print("search_rotated_array: all tests passed (exhaustive over all rotations)")


if __name__ == "__main__":
    _tests()
