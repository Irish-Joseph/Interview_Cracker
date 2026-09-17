"""
Challenge:  Two Sum
Pattern:    Hashing (seen-so-far)
Difficulty: Easy

PROBLEM
-------
Given an array of integers and a target, return the indices of the two numbers
that add up to the target. Assume exactly one solution exists, and the same
element may not be used twice.

EXAMPLES
--------
[2, 7, 11, 15], target=9  -> [0, 1]   (2 + 7)
[3, 2, 4],      target=6  -> [1, 2]   (2 + 4)
[3, 3],         target=6  -> [0, 1]

CONSTRAINTS
-----------
- Return the indices, not the values.
- Duplicate values are allowed.

HINT
----
Brute force checks every pair: O(n^2). For each number x, you are really asking
"have I already seen target - x?" - which is a membership question, and
membership questions belong in a hash map.

Store each value as you pass it, mapped to its index. Check BEFORE you store,
so an element cannot pair with itself.

COMPLEXITY
----------
Time:  O(n) - one pass, O(1) average lookup per element
Space: O(n) - the map may hold every element
"""


def two_sum(nums: list[int], target: int) -> list[int] | None:
    seen: dict[int, int] = {}          # value -> index where we saw it

    for index, value in enumerate(nums):
        complement = target - value

        # Check first: `seen` holds only EARLIER elements, so a number can
        # never pair with itself, and duplicates work correctly.
        if complement in seen:
            return [seen[complement], index]

        seen[value] = index

    return None


def _tests() -> None:
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert two_sum([3, 3], 6) == [0, 1]              # duplicate values
    assert two_sum([-1, -2, -3, -4], -6) == [1, 3]   # negatives
    assert two_sum([0, 4, 3, 0], 0) == [0, 3]        # zeroes

    # No solution, and inputs too small to have one
    assert two_sum([1, 2, 3], 100) is None
    assert two_sum([], 0) is None
    assert two_sum([1], 2) is None                   # must not pair with itself

    # Cross-check against brute force.
    import itertools
    import random

    random.seed(17)
    for _ in range(300):
        data = [random.randint(-10, 10) for _ in range(random.randint(0, 10))]
        target = random.randint(-10, 10)
        expected = next(
            ([i, j] for i, j in itertools.combinations(range(len(data)), 2)
             if data[i] + data[j] == target),
            None,
        )
        actual = two_sum(data, target)
        if expected is None:
            assert actual is None, (data, target, actual)
        else:
            # Any valid pair is acceptable, so verify the answer rather than
            # demanding the same indices as the brute-force scan.
            assert actual is not None, (data, target)
            i, j = actual
            assert i != j and data[i] + data[j] == target, (data, target, actual)

    print("two_sum: all tests passed (300 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
