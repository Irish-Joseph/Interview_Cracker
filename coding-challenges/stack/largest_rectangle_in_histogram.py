"""
Challenge:  Largest Rectangle in Histogram
Pattern:    Monotonic stack (stack of indices with increasing heights)
Difficulty: Hard

PROBLEM
    Given a histogram as a list of bar heights (each bar has width 1),
    return the area of the largest axis-aligned rectangle contained in it.

EXAMPLES
    [2, 1, 2]              -> 3   (the bar of height 1 across all three bars)
    [2, 4]                 -> 4   (the right bar alone)
    [6, 2, 5, 4, 5, 1, 6]  -> 12  (4 and 5 form width-3 at height 4)
    []                     -> 0

CONSTRAINTS
    - Heights are non-negative; length up to 10^5, so O(n^2)
      (trying every bar as the height) is too slow.
    - Read-only: the input list is not modified.

HINT
    A rectangle of height h can extend left and right until a shorter bar
    appears. Instead of checking that for every bar, push indices onto a
    stack kept in increasing height order; when a shorter bar arrives, the
    bars popped from the stack have just found their right boundary - and
    the new top of the stack is their left boundary.

COMPLEXITY
    Time: O(n) - every index is pushed exactly once and popped at most once.
    Space: O(n) for the stack.
"""

from __future__ import annotations

import random


def largest_rectangle(heights: list[int]) -> int:
    best = 0
    stack: list[int] = []               # indices, heights increasing

    # A sentinel height of 0 at the end forces every remaining bar to pop,
    # so the loop below needs no special case for the tail of the input.
    for right, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            height = heights[top]
            # Left boundary: the index now on top, or -1 if the stack is
            # empty, meaning this bar was the shortest seen so far and its
            # rectangle runs to the start of the histogram.
            left = stack[-1] if stack else -1
            width = right - left - 1
            best = max(best, height * width)
        if right < len(heights):
            stack.append(right)
    return best


def _brute_force(heights: list[int]) -> int:
    """Exhaustive reference: every (left, right) window, running minimum.

    Note why the tempting "for each bar, extend right" version is WRONG:
    a rectangle's height is set by its shortest bar, which does not have to
    sit at the rectangle's left edge - [2, 1, 2] gives 3, which no bar's
    right-extension produces.
    """
    best = 0
    for left in range(len(heights)):
        minimum = float("inf")
        for right in range(left, len(heights)):
            minimum = min(minimum, heights[right])
            best = max(best, minimum * (right - left + 1))
    return best


def _tests() -> None:
    # empty input
    assert largest_rectangle([]) == 0

    # single bar
    assert largest_rectangle([5]) == 5
    assert largest_rectangle([0]) == 0

    # the documented examples
    assert largest_rectangle([2, 1, 2]) == 3
    assert largest_rectangle([2, 4]) == 4
    assert largest_rectangle([6, 2, 5, 4, 5, 1, 6]) == 12

    # the case that breaks the "tallest bar wins" intuition:
    # the answer is the short wide rectangle, not any single bar
    assert largest_rectangle([3, 3, 3, 3]) == 12
    # ...and its opposite, where the tall single bar wins
    assert largest_rectangle([1, 100, 1]) == 100

    # all zeros and an increasing run (where the tail handling matters)
    assert largest_rectangle([0, 0, 0]) == 0
    assert largest_rectangle([1, 2, 3, 4]) == 6    # 2 high across the last three
    assert largest_rectangle([4, 3, 2, 1]) == 6    # symmetric: also 2 high, width 3

    # input must not be modified
    original = [6, 2, 5, 4, 5, 1, 6]
    snapshot = list(original)
    largest_rectangle(original)
    assert original == snapshot

    # cross-check against the brute force on randomised inputs
    rng = random.Random(20260922)
    for _ in range(500):
        heights = [rng.randrange(0, 10) for _ in range(rng.randrange(0, 12))]
        assert largest_rectangle(heights) == _brute_force(heights), heights

    print("largest_rectangle: all tests passed")


if __name__ == "__main__":
    _tests()
