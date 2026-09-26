"""Challenge: Non-overlapping Intervals | Pattern: greedy intervals | Difficulty: Medium

Return the fewest intervals to remove so the remainder do not overlap.
Hint: keep the compatible interval that finishes earliest.
Complexity: O(n log n) sorting time and O(n) space for the sorted copy.
"""
from itertools import combinations
import random

def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    removed, end = 0, None
    for start, finish in sorted(intervals, key=lambda item: item[1]):
        if end is not None and start < end: removed += 1
        else: end = finish
    return removed

def _brute(intervals: list[list[int]]) -> int:
    for kept in range(len(intervals), -1, -1):
        for subset in combinations(intervals, kept):
            ordered = sorted(subset)
            if all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1)):
                return len(intervals) - kept
    raise AssertionError("unreachable")

def _tests() -> None:
    assert erase_overlap_intervals([]) == 0
    assert erase_overlap_intervals([[1, 2]]) == 0
    assert erase_overlap_intervals([[1, 2], [2, 3]]) == 0
    assert erase_overlap_intervals([[1, 2], [1, 3], [2, 4], [3, 5]]) == 2
    rng = random.Random(26)
    for size in range(8):
        for _ in range(50):
            values = []
            for _ in range(size):
                start = rng.randint(-4, 4); values.append([start, start + rng.randint(1, 4)])
            assert erase_overlap_intervals(values) == _brute(values)
    print("Non-overlapping Intervals: all tests passed")

if __name__ == "__main__": _tests()
