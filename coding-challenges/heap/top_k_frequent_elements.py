"""
Challenge:  Top K Frequent Elements
Pattern:    Heap (min-heap of size k)
Difficulty: Medium

PROBLEM
-------
Given an integer array and an integer k, return the k most frequent elements.
The order of the returned elements does not matter. You may assume the answer
is unique (no ambiguous tie at the k-th position).

EXAMPLES
--------
[1,1,1,2,2,3], k=2  ->  [1, 2]
[1], k=1            ->  [1]
[4,4,4,5,5,6], k=1  ->  [4]

CONSTRAINTS
-----------
- 1 <= k <= number of distinct elements
- Aim to beat O(n log n), which is what sorting by frequency costs.

HINT
----
Two steps, and the second is the interesting one.

1. Count occurrences - a hash map, O(n).
2. Select the k largest counts WITHOUT sorting all of them.

For step 2 the instinct is a max-heap, which is wrong. Use a MIN-heap capped
at size k: its root is the weakest element you are currently keeping, so it is
both the one to compare against and the one to evict.

Sorting the counts is O(d log d) for d distinct values. The heap is
O(d log k), which is better whenever k is much smaller than d - the usual case
when someone asks for "top 10".

COMPLEXITY
----------
Time:  O(n + d log k), n = length, d = distinct values.
       Sorting would be O(n + d log d).
Space: O(d) for the counts plus O(k) for the heap.

There is also an O(n) bucket-sort solution below, since counts are bounded by
n - worth knowing, because it beats the heap asymptotically.
"""

import heapq
from collections import Counter


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)

    # A min-heap of (count, value), capped at k. The root is the least
    # frequent element among those currently kept.
    heap: list[tuple[int, int]] = []
    for value, count in counts.items():
        if len(heap) < k:
            heapq.heappush(heap, (count, value))
        elif count > heap[0][0]:
            # heapreplace = pop then push in one sift, cheaper than doing both.
            heapq.heapreplace(heap, (count, value))

    return [value for count, value in heap]


def top_k_frequent_bucket(nums: list[int], k: int) -> list[int]:
    """O(n) alternative: bucket by frequency.

    A count can never exceed len(nums), so frequencies index directly into a
    list of buckets. Walking it from the back yields elements in descending
    frequency without any comparison sort.
    """
    counts = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for value, count in counts.items():
        buckets[count].append(value)

    out: list[int] = []
    for count in range(len(buckets) - 1, 0, -1):
        for value in buckets[count]:
            out.append(value)
            if len(out) == k:
                return out
    return out


def _tests() -> None:
    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert top_k_frequent([1], 1) == [1]
    assert top_k_frequent([4, 4, 4, 5, 5, 6], 1) == [4]
    assert sorted(top_k_frequent([1, 2], 2)) == [1, 2]
    assert sorted(top_k_frequent([-1, -1, 3], 2)) == [-1, 3]

    # k equal to the number of distinct values returns everything.
    data = [1, 1, 2, 3, 3, 3]
    assert sorted(top_k_frequent(data, 3)) == [1, 2, 3]

    # Both implementations agree, and both match a sort-based reference.
    import random

    def reference(nums: list[int], k: int) -> list[int]:
        counts = Counter(nums)
        return [v for v, _ in counts.most_common(k)]

    random.seed(83)
    for _ in range(400):
        data = [random.randint(0, 8) for _ in range(random.randint(1, 25))]
        distinct = len(set(data))
        k = random.randint(1, distinct)

        want = reference(data, k)
        counts = Counter(data)

        for got in (top_k_frequent(data, k), top_k_frequent_bucket(data, k)):
            assert len(got) == k, (data, k, got)
            assert len(set(got)) == k, (data, k, got)
            # Ties make the exact membership ambiguous, so compare the
            # MULTISET OF COUNTS rather than the values themselves.
            assert sorted(counts[v] for v in got) == sorted(counts[v] for v in want), \
                (data, k, got, want)

    print("top_k_frequent_elements: all tests passed (400 randomised, both variants)")


if __name__ == "__main__":
    _tests()
