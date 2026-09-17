"""
Topic: Binary search — the iterative version.

Concepts:
- Halving the search space each step
- Invariant: answer (if any) is always inside [lo, hi]
- Off-by-one discipline: mid computation and boundary updates
- Returning the insertion point (bisect behavior)

Binary search on a SORTED list finds a target (or proves absence)
in O(log n) instead of O(n) for linear scan.

The classic bugs are the boundary updates:
- found -> return
- too small -> lo = mid + 1   (mid is NOT the answer)
- too big  -> hi = mid - 1     (mid is NOT the answer)
With these, the window shrinks by at least one element per step,
so the loop MUST terminate.

Example:
Input:  [1, 3, 5, 8, 10, 13, 19], target=13
Output: index 5
Input:  same list, target=6
Output: -1 (and insertion point 3)

Time Complexity: O(log n)
Space Complexity: O(1)
"""

from typing import List, Tuple


def binary_search(values: List[int], target: int) -> int:
    """Return the index of target in a sorted list, or -1 if absent."""
    lo, hi = 0, len(values) - 1

    while lo <= hi:
        # (lo + hi) // 2 would overflow in languages with fixed-width
        # ints; the shifted form is the safe habit.
        mid = lo + (hi - lo) // 2

        if values[mid] == target:
            return mid
        elif values[mid] < target:
            lo = mid + 1   # discard everything up to and including mid
        else:
            hi = mid - 1   # discard mid and everything after it

    return -1


def insertion_point(values: List[int], target: int) -> int:
    """Index where target WOULD be inserted to keep the list sorted.

    Same walk, different exit: when the window collapses, `lo` sits
    exactly at the first position >= target.
    """
    lo, hi = 0, len(values)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def binary_search_result(values: List[int], target: int) -> Tuple[int, int]:
    """(found_index_or_-1, insertion_point) in one pass pair."""
    found = binary_search(values, target)
    ins = found if found != -1 else insertion_point(values, target)
    return found, ins


# --- Demo -----------------------------------------------------------------

data = [1, 3, 5, 8, 10, 13, 19]

cases = [
    (13, 5),     # present, middle-right
    (1, 0),      # present, first element
    (19, 6),     # present, last element
    (6, -1),     # absent, between 5 and 8
    (0, -1),     # absent, below all
    (20, -1),    # absent, above all
]

for target, expected in cases:
    found, ins = binary_search_result(data, target)
    status = "ok" if found == expected else "FAIL"
    print(f"target={target:>2}  index={found:>2}  insert_at={ins}  [{status}]")

# Sanity: brute-force cross-check on a bigger random-ish list.
import random
big = sorted(random.sample(range(1000), 500))
for t in range(0, 1001, 10):
    assert binary_search(big, t) == big.index(t) if t in big else -1
print(f"cross-check against list of {len(big)} items: all passed")

# Expected tail output:
# cross-check against list of 500 items: all passed
