"""
Challenge:  3Sum
Pattern:    Sort, then two pointers inside a loop
Difficulty: Medium

PROBLEM
-------
Given an array of integers, return all unique triplets [a, b, c] such that
a + b + c == 0. The result must not contain duplicate triplets.

EXAMPLES
--------
[-1, 0, 1, 2, -1, -4]  -> [[-1, -1, 2], [-1, 0, 1]]
[0, 1, 1]              -> []
[0, 0, 0]              -> [[0, 0, 0]]

CONSTRAINTS
-----------
- The same element may not be used twice in one triplet.
- [-1, 0, 1] and [0, 1, -1] are the SAME triplet - return it once.

HINT
----
Brute force is three nested loops, O(n^3). Sort the array first: then fix one
element and the problem reduces to "find a pair summing to -x in a sorted
array", which is the converging two-pointer scan.

The hard part is not the search - it is skipping duplicates, in two places.

COMPLEXITY
----------
Time:  O(n^2) - an O(n) scan for each of n fixed elements; the O(n log n) sort
       is dominated by it
Space: O(1) beyond the output (ignoring the sort's internal space)
"""


def three_sum(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    triplets: list[list[int]] = []

    for i in range(len(nums) - 2):
        # Once the smallest value is positive, no triplet can reach zero.
        if nums[i] > 0:
            break

        # Skip a repeated first element: it would regenerate the same triplets.
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]

            if total < 0:
                left += 1           # need a bigger sum
            elif total > 0:
                right -= 1          # need a smaller sum
            else:
                triplets.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # Skip repeats of the value we just used, or we emit duplicates.
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1

    return triplets


def _tests() -> None:
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum([0, 1, 1]) == []
    assert three_sum([0, 0, 0]) == [[0, 0, 0]]
    assert three_sum([]) == []
    assert three_sum([1, 2]) == []
    assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
    assert three_sum([-2, 0, 1, 1, 2]) == [[-2, 0, 2], [-2, 1, 1]]

    # Cross-check against brute force on random inputs.
    import itertools
    import random

    random.seed(11)
    for _ in range(200):
        data = [random.randint(-6, 6) for _ in range(random.randint(0, 9))]
        expected = sorted({
            tuple(sorted(combo))
            for combo in itertools.combinations(data, 3)
            if sum(combo) == 0
        })
        actual = sorted(tuple(t) for t in three_sum(data))
        assert actual == expected, (data, actual, expected)

    print("three_sum: all tests passed (200 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
