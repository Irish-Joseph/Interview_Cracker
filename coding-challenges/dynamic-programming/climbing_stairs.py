"""
Challenge:  Climbing Stairs
Pattern:    Linear DP (and the O(1)-space collapse)
Difficulty: Easy

PROBLEM
-------
You are climbing a staircase of n steps. Each move takes either 1 or 2 steps.
How many distinct ways can you reach the top?

EXAMPLES
--------
n=2 -> 2    (1+1, 2)
n=3 -> 3    (1+1+1, 1+2, 2+1)
n=4 -> 5

CONSTRAINTS
-----------
- n >= 0. There is exactly one way to climb zero steps: do nothing.

HINT
----
Work backwards from the top. To arrive at step n you took your last move from
either step n-1 (a 1-step) or step n-2 (a 2-step) - and those two sets of routes
are disjoint, so you can just add them.

That gives you a familiar recurrence. Once you have it, notice that step i only
ever needs the two values before it - so you do not need to keep the whole table.

COMPLEXITY
----------
Time:  O(n)
Space: O(1) for the iterative version below
       (naive recursion is O(2^n) time; memoised it is O(n) time, O(n) space)
"""

from functools import cache


def climb_stairs(n: int) -> int:
    if n < 0:
        return 0
    if n <= 1:
        return 1                     # ways(0) = 1 (stand still), ways(1) = 1

    previous, current = 1, 1         # ways(0), ways(1)
    for _ in range(n - 1):
        previous, current = current, previous + current
    return current


@cache
def climb_stairs_memoised(n: int) -> int:
    """Top-down version - closer to the recurrence, O(n) stack space."""
    if n < 0:
        return 0
    if n <= 1:
        return 1
    return climb_stairs_memoised(n - 1) + climb_stairs_memoised(n - 2)


def _tests() -> None:
    assert climb_stairs(0) == 1
    assert climb_stairs(1) == 1
    assert climb_stairs(2) == 2
    assert climb_stairs(3) == 3
    assert climb_stairs(4) == 5
    assert climb_stairs(5) == 8
    assert climb_stairs(-1) == 0

    # It is the Fibonacci sequence, shifted.
    assert [climb_stairs(n) for n in range(10)] == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

    # Both implementations must agree.
    for n in range(0, 60):
        assert climb_stairs(n) == climb_stairs_memoised(n), n

    # Cross-check small n against exhaustive enumeration of move sequences.
    def enumerate_ways(n: int) -> int:
        if n < 0:
            return 0
        if n == 0:
            return 1
        return enumerate_ways(n - 1) + enumerate_ways(n - 2)

    for n in range(0, 18):
        assert climb_stairs(n) == enumerate_ways(n), n

    # Large input must be instant, which the naive recursion would not be.
    assert climb_stairs(90) == 4660046610375530309

    print("climbing_stairs: all tests passed (iterative, memoised, exhaustive)")


if __name__ == "__main__":
    _tests()
