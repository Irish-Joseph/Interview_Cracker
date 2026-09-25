"""
Challenge:  Kth Largest Element in an Array
Pattern:    Heap (min-heap of size k - the "weakest champion" sits at the root)
Difficulty: Medium

PROBLEM
-------
Given an array of integers and k (1-based), return the kth LARGEST element,
counting duplicates (so in [3, 3, 1] the 2nd largest is 3, not 1).

EXAMPLES
--------
[3, 2, 1, 5, 6, 4], k = 2                      -> 5
[3, 2, 3, 1, 2, 3, 5, 7, 2, 7, 4, 7], k = 3    -> 7   (duplicates count)
[1], k = 1                                      -> 1

CONSTRAINTS
-----------
- 1 <= k <= len(nums) <= 10**5.
- The array is unsorted and not modified in place (a copy is fine).
- Beat the full sort (O(n log n)) when k << n.

HINT
----
You do not need the whole array ordered - only a window of the k best so far.
Keep a MIN-heap of size k: its root is the *weakest* of the current champions,
so any newcomer bigger than the root evicts it. Why a min-heap for "largest"?
A max-heap would put the strongest at the root and tell you nothing to drop.

COMPLEXITY
----------
Time:  O(n log k) - each element costs at most one sift in a heap of size k
Space: O(k)       - the window itself (k is often far smaller than n)
       vs a full sort: O(n log n) time, O(n) space
"""

import heapq


def kth_largest(nums, k: int):
    # window holds the k largest seen so far, as a MIN-heap:
    # window[0] is the smallest of them - the eviction candidate.
    window = []
    for n in nums:
        if len(window) < k:
            heapq.heappush(window, n)
        elif n > window[0]:
            heapq.heapreplace(window, n)   # pop root + push, one sift

    return window[0]


def _tests() -> None:
    # Single element (k = 1 = n at once).
    assert kth_largest([1], 1) == 1

    # k = 1 is the max; k = n is the min.
    assert kth_largest([3, 2, 1, 5, 6, 4], 1) == 6
    assert kth_largest([3, 2, 1, 5, 6, 4], 6) == 1
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5

    # The case that defeats "deduplicate first": duplicates count,
    # so the 2nd largest of [3, 3, 1] is 3, not 1 - and in the long
    # array below the three 7s already occupy the top three places.
    assert kth_largest([3, 3, 1], 2) == 3
    assert kth_largest([3, 2, 3, 1, 2, 3, 5, 7, 2, 7, 4, 7], 3) == 7
    assert kth_largest([3, 2, 3, 1, 2, 3, 5, 7, 2, 7, 4, 7], 4) == 5

    # All equal: every k lands on the same value.
    assert kth_largest([7, 7, 7, 7], 3) == 7

    # Two elements, both orders of k.
    assert kth_largest([1, 2], 1) == 2
    assert kth_largest([1, 2], 2) == 1

    # Cross-check against the full-sort reference on randomised inputs,
    # with heavy duplication to stress the "duplicates count" rule.
    import random
    random.seed(25)
    for _ in range(300):
        n = random.randint(1, 12)
        nums = [random.randint(0, 6) for _ in range(n)]
        k = random.randint(1, n)
        expected = sorted(nums, reverse=True)[k - 1]
        assert kth_largest(nums, k) == expected, (nums, k)

    print("kth_largest_element: all tests passed")


if __name__ == "__main__":
    _tests()
