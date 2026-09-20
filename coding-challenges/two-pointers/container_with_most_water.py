"""
Challenge:  Container With Most Water
Pattern:    Two pointers (converging)
Difficulty: Medium

PROBLEM
-------
Given n non-negative integers h[0..n-1], where each value is a vertical
line at position i with top at (i, h[i]). Choose two lines that, together
with the x-axis, form a container holding the most water. Return that
maximum area. You may not tilt the container.

EXAMPLES
--------
[1, 8, 6, 2, 5, 4, 8, 3, 7] -> 49   (lines at i=1 and i=8: 7 * min(8,7))
[1, 1]                      -> 1
[4, 3, 2, 1, 4]             -> 16   (the two 4s: 4 * 4)

CONSTRAINTS
-----------
- n >= 2.
- The brute force checks all n(n-1)/2 pairs; do better.

HINT
----
Start with the outermost pair — the widest possible container. Then move
the pointer under the SHORTER line inward: the area is bounded by the
shorter line, so keeping it can never increase the area, and the width
only shrinks. Which pointer must move when both lines are equal?

COMPLEXITY
----------
Time:  O(n) - each step moves a pointer inward
Space: O(1)
"""


def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0

    while left < right:
        width = right - left
        best = max(best, width * min(height[left], height[right]))

        # The shorter line cannot improve the area if kept: any new
        # container with it would be at least as short AND narrower.
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return best


def _tests() -> None:
    # Single-valid-container inputs (n == 2).
    assert max_area([1, 1]) == 1
    assert max_area([0, 5]) == 0
    assert max_area([9, 2]) == 2     # width 1, bounded by the short line

    # Specified examples.
    assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_area([4, 3, 2, 1, 4]) == 16

    # Peak in the middle: the naive "move the taller" variant behaves the
    # same, but this stresses the equal-heights tie (either pointer may
    # move, the proof still holds).
    assert max_area([3, 3, 3, 3]) == 9
    assert max_area([1, 2, 1]) == 2

    # Wide beats tall: the two 100s (width 2) give 200, which beats
    # any pair involving the 1s, but a greedy "tallest line" pick would
    # miss that width matters too.
    assert max_area([1, 100, 1, 100]) == 200

    # Cross-check against brute force on randomised inputs.
    import random

    random.seed(11)
    for _ in range(200):
        n = random.randint(2, 30)
        h = [random.randint(0, 20) for _ in range(n)]
        expected = max(
            (j - i) * min(h[i], h[j]) for i in range(n) for j in range(i + 1, n)
        )
        assert max_area(h) == expected, h

    print("container_with_most_water: all tests passed")


if __name__ == "__main__":
    _tests()
