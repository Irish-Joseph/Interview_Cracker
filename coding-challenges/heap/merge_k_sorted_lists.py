"""
Challenge:  Merge K Sorted Lists
Pattern:    Heap (k-way merge with a min-heap of size k)
Difficulty: Medium

PROBLEM
    Given a list of k already-sorted lists of integers, return one sorted
    list containing every element.

EXAMPLES
    [[1, 4, 5], [1, 2, 3], [2, 6]]  -> [1, 1, 2, 2, 3, 4, 5, 6]
    [[1]]                            -> [1]
    []                               -> []
    [[], [3], []]                    -> [3]

CONSTRAINTS
    - Each inner list is sorted; together they may hold up to 10^5 elements
      and k may be up to 10^4, so concatenating and re-sorting everything
      (O(N log N)) is allowed by most statements but not the point.
    - The intended solution touches each element exactly once and keeps only
      k candidates in memory at a time.

HINT
    The answer's next smallest element must be the head of one of the k
    lists. Keep exactly those k heads in a min-heap; pop the smallest,
    append it, and push that list's NEXT element. Stop when the heap is
    empty. (Heapify once, then k pops and at most N pushes.)

COMPLEXITY
    Time: O(N log k) where N is the total number of elements - each of the
          N elements is pushed and popped once, each heap op costs log k.
    Space: O(k) for the heap (plus O(N) for the output).
"""

from __future__ import annotations

import heapq
import random


def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int]] = []    # (value, list_index)

    # Seed with each list's head. The list index in the tuple is the tie-
    # breaker: two equal values would otherwise compare their (absent) second
    # element - with the index present, the tuple is always fully ordered.
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))   # (value, list_idx, pos)

    result: list[int] = []
    while heap:
        value, i, pos = heapq.heappop(heap)
        result.append(value)
        if pos + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][pos + 1], i, pos + 1))
    return result


def _tests() -> None:
    # empty input and single-list input
    assert merge_k_sorted([]) == []
    assert merge_k_sorted([[1, 2, 3]]) == [1, 2, 3]
    assert merge_k_sorted([[]]) == []

    # the documented example, plus lists that are empty in the middle
    assert merge_k_sorted([[1, 4, 5], [1, 2, 3], [2, 6]]) == [1, 1, 2, 2, 3, 4, 5, 6]
    assert merge_k_sorted([[], [3], []]) == [3]
    assert merge_k_sorted([[5], [], [1]]) == [1, 5]

    # duplicates across lists (the tie-breaker path), and one huge list
    assert merge_k_sorted([[2, 2, 2], [2, 2], [2]]) == [2] * 6
    assert merge_k_sorted([[100, 200], [1]]) == [1, 100, 200]

    # cross-check against the (deliberately simple) brute force on random inputs
    rng = random.Random(20260923)
    for _ in range(500):
        k = rng.randrange(0, 8)
        lists = [
            sorted(rng.randrange(0, 30) for _ in range(rng.randrange(0, 10)))
            for _ in range(k)
        ]
        expected = sorted(x for lst in lists for x in lst)
        assert merge_k_sorted(lists) == expected, (lists, expected)

    print("merge_k_sorted: all tests passed")


if __name__ == "__main__":
    _tests()
