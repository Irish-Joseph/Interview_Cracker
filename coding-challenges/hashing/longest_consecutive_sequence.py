"""
Challenge:  Longest Consecutive Sequence
Pattern:    Hashing (set membership replaces sorting)
Difficulty: Medium

PROBLEM
-------
Given an unsorted array of integers, return the length of the longest
consecutive elements sequence. That is, the longest run of values where
each value is exactly 1 more than the previous (e.g. 9, 10, 11, 12).
The values need not be adjacent in the input.

EXAMPLES
--------
[100, 4, 200, 1, 3, 2]          -> 4   (1, 2, 3, 4)
[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]  -> 9   (0 .. 8)
[]                               -> 0
[1]                              -> 1
[9, 1, 4, 7, 3]                  -> 2   (only 3, 4 are consecutive)

CONSTRAINTS
-----------
- n up to 10^5, values up to 10^9 in magnitude.
- Sorting first would work in O(n log n); the expected solution is O(n).

HINT
----
Put all values in a set. Then only start counting a run from a number x
that is the START of a run (x - 1 is not in the set). Counting from the
middle of a run double-counts work; counting only from starts makes the
total length of all inner while-loops O(n) across the whole algorithm.

COMPLEXITY
----------
Time:  O(n) average - each element is visited by at most one run-count
Space: O(n) - the set
"""


def longest_consecutive(nums: list[int]) -> int:
    values = set(nums)
    best = 0

    for start in values:
        if start - 1 in values:
            continue  # not the beginning of a run; counted elsewhere

        length = 1
        current = start + 1
        while current in values:
            length += 1
            current += 1
        best = max(best, length)

    return best


def _tests() -> None:
    # Empty and single-element inputs.
    assert longest_consecutive([]) == 0
    assert longest_consecutive([1]) == 1
    assert longest_consecutive([42]) == 1

    # Specified examples.
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longest_consecutive([9, 1, 4, 7, 3]) == 2   # only the 3,4 pair
    assert longest_consecutive([9, 1, 7, 5, 3]) == 1   # truly no consecutive pair

    # Duplicates must not inflate the answer.
    assert longest_consecutive([1, 2, 2, 3, 3, 3]) == 3

    # Negatives and runs crossing zero.
    assert longest_consecutive([-2, -1, 0, 1, 3]) == 4
    assert longest_consecutive([-1, -2, -3]) == 3

    # Gaps of exactly one break the run.
    assert longest_consecutive([1, 3]) == 1
    assert longest_consecutive([1, 2, 4, 5]) == 2

    # Cross-check against the O(n log n) reference on randomised inputs.
    import random

    def reference(nums: list[int]) -> int:
        if not nums:
            return 0
        best = current = 1
        for a, b in zip(sorted(set(nums)), sorted(set(nums))[1:]):
            current = current + 1 if b == a + 1 else 1
            best = max(best, current)
        return best

    random.seed(99)
    for _ in range(300):
        n = random.randint(0, 60)
        nums = [random.randint(-15, 15) for _ in range(n)]
        assert longest_consecutive(nums) == reference(nums), nums

    print("longest_consecutive_sequence: all tests passed")


if __name__ == "__main__":
    _tests()
