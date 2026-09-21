"""
Challenge:  Insert Interval
Pattern:    Intervals (sorted sweep, no re-sort needed)
Difficulty: Medium

PROBLEM
-------
Given a list of NON-OVERLAPPING intervals sorted by start time, and one new
interval, insert it and merge where necessary. Return the resulting list,
still sorted and still non-overlapping.

EXAMPLES
--------
[[1,3],[6,9]],                 new=[2,5]   ->  [[1,5],[6,9]]
[[1,2],[3,5],[6,7],[8,10],[12,16]], new=[4,8] ->  [[1,2],[3,10],[12,16]]
[],                            new=[5,7]   ->  [[5,7]]
[[1,5]],                       new=[2,3]   ->  [[1,5]]     (fully contained)
[[1,5]],                       new=[6,8]   ->  [[1,5],[6,8]]

CONSTRAINTS
-----------
- The input is ALREADY sorted and non-overlapping. Use that.
- Touching intervals merge: [1,3] and [3,5] become [1,5].

HINT
----
Merge Intervals sorts first, costing O(n log n). Here the input is already
sorted, so sorting again would waste that - the answer is O(n).

Walk the list once in three phases:

  1. Everything that ends BEFORE the new interval starts -> copy through
     unchanged.
  2. Everything that OVERLAPS -> absorb it, widening the new interval:
        start = min(start, other.start)
        end   = max(end,   other.end)
     Then append the widened interval ONCE, after the phase ends.
  3. Everything that starts AFTER the new interval ends -> copy through.

The `max` in phase 2 is the part people get wrong: the next interval may be
entirely INSIDE the one you are building, and taking its end unconditionally
would shrink the result.

COMPLEXITY
----------
Time:  O(n) - one pass, no sort
Space: O(n) for the output
"""


def insert_interval(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    start, end = new
    i = 0
    n = len(intervals)

    # Phase 1: strictly before the new interval (they do not even touch).
    while i < n and intervals[i][1] < start:
        result.append(list(intervals[i]))
        i += 1

    # Phase 2: everything that overlaps or touches, absorbed into one.
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        # max() matters: intervals[i] may sit entirely inside the range we
        # are building, and taking its end blindly would shrink the result.
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])

    # Phase 3: strictly after.
    while i < n:
        result.append(list(intervals[i]))
        i += 1

    return result


def _tests() -> None:
    assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert insert_interval(
        [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]
    ) == [[1, 2], [3, 10], [12, 16]]
    assert insert_interval([], [5, 7]) == [[5, 7]]
    assert insert_interval([[1, 5]], [2, 3]) == [[1, 5]]        # contained
    assert insert_interval([[1, 5]], [6, 8]) == [[1, 5], [6, 8]]
    assert insert_interval([[1, 5]], [0, 0]) == [[0, 0], [1, 5]]  # before all
    assert insert_interval([[1, 5]], [0, 9]) == [[0, 9]]         # swallows all
    assert insert_interval([[3, 5]], [1, 3]) == [[1, 5]]         # touching
    assert insert_interval([[1, 3]], [3, 6]) == [[1, 6]]         # touching
    assert insert_interval([[1, 2], [5, 6]], [3, 4]) == [[1, 2], [3, 4], [5, 6]]

    # The caller's data must not be mutated.
    original = [[1, 3], [6, 9]]
    insert_interval(original, [2, 5])
    assert original == [[1, 3], [6, 9]], "must not mutate the input"

    # Cross-check: the result must cover exactly the same integer points as
    # the input plus the new interval, and be sorted and non-overlapping.
    import random

    random.seed(101)
    for _ in range(500):
        # Build a genuinely non-overlapping, sorted input.
        intervals: list[list[int]] = []
        cursor = random.randint(0, 3)
        for _ in range(random.randint(0, 6)):
            start = cursor + random.randint(1, 3)
            end = start + random.randint(0, 3)
            intervals.append([start, end])
            cursor = end + random.randint(1, 2)     # gap guarantees no overlap

        new_start = random.randint(0, 20)
        new = [new_start, new_start + random.randint(0, 6)]

        out = insert_interval(intervals, new)

        covered_before = set()
        for s, e in intervals + [new]:
            covered_before.update(range(s, e + 1))
        covered_after = set()
        for s, e in out:
            covered_after.update(range(s, e + 1))
        assert covered_before == covered_after, (intervals, new, out)

        for earlier, later in zip(out, out[1:]):
            # Sorted, and strictly disjoint (touching would have merged).
            assert earlier[1] < later[0], (intervals, new, out)
        for s, e in out:
            assert s <= e, (intervals, new, out)

    print("insert_interval: all tests passed (500 randomised coverage checks)")


if __name__ == "__main__":
    _tests()
