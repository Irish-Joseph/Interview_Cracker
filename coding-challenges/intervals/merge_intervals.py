"""
Challenge:  Merge Intervals
Pattern:    Sort by start, then sweep
Difficulty: Medium

PROBLEM
-------
Given a list of intervals [start, end], merge all overlapping intervals and
return the non-overlapping intervals that cover the same total range.

EXAMPLES
--------
[[1,3],[2,6],[8,10],[15,18]] -> [[1,6],[8,10],[15,18]]
[[1,4],[4,5]]                -> [[1,5]]      (touching counts as overlapping)
[[1,4],[2,3]]                -> [[1,4]]      (fully contained)

CONSTRAINTS
-----------
- The input is not sorted.
- Touching intervals ([1,4] and [4,5]) DO merge here.

HINT
----
Unsorted, any interval can overlap any other, so you would need to compare all
pairs. Sort by start time and that collapses: an interval can now only overlap
the one you are currently building.

Walk through the sorted list keeping one "current" interval. Either the next
interval extends it, or it starts a new one.

Watch the case where the next interval sits entirely INSIDE the current one -
the end must not move backwards.

COMPLEXITY
----------
Time:  O(n log n) - dominated by the sort; the sweep is O(n)
Space: O(n) for the output
"""


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda interval: interval[0])
    merged = [list(ordered[0])]          # copy: do not mutate the caller's data

    for start, end in ordered[1:]:
        last_end = merged[-1][1]

        if start <= last_end:
            # Overlaps (or touches) the interval we are building - extend it.
            # max() is essential: [2,3] inside [1,4] must not shrink the end.
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])

    return merged


def _tests() -> None:
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]        # touching
    assert merge_intervals([[1, 4], [2, 3]]) == [[1, 4]]        # contained
    assert merge_intervals([]) == []
    assert merge_intervals([[1, 4]]) == [[1, 4]]
    assert merge_intervals([[1, 4], [5, 6]]) == [[1, 4], [5, 6]]   # disjoint
    assert merge_intervals([[5, 6], [1, 4]]) == [[1, 4], [5, 6]]   # unsorted input
    assert merge_intervals([[1, 4], [0, 4]]) == [[0, 4]]
    assert merge_intervals([[1, 1], [2, 2]]) == [[1, 1], [2, 2]]   # zero-length
    assert merge_intervals([[1, 10], [2, 3], [4, 5], [6, 7]]) == [[1, 10]]

    # The caller's input must not be mutated.
    original = [[1, 3], [2, 6]]
    merge_intervals(original)
    assert original == [[1, 3], [2, 6]]

    # Cross-check: the merged set must cover exactly the same integer points,
    # and must itself be sorted and non-overlapping.
    import random

    random.seed(59)
    for _ in range(300):
        data = []
        for _ in range(random.randint(0, 8)):
            start = random.randint(0, 20)
            data.append([start, start + random.randint(0, 6)])

        merged = merge_intervals(data)

        covered_before = set()
        for start, end in data:
            covered_before.update(range(start, end + 1))
        covered_after = set()
        for start, end in merged:
            covered_after.update(range(start, end + 1))
        assert covered_before == covered_after, (data, merged)

        for earlier, later in zip(merged, merged[1:]):
            assert earlier[1] < later[0], (data, merged)   # disjoint and ordered

    print("merge_intervals: all tests passed (300 randomised coverage checks)")


if __name__ == "__main__":
    _tests()
