"""
Challenge:  House Robber
Pattern:    Dynamic programming (two-state, rolling variables)
Difficulty: Medium

PROBLEM
-------
You have the money in a row of houses. You cannot rob two ADJACENT houses
(their alarms trip together). Return the maximum total you can steal.

EXAMPLES
--------
[2, 7, 9, 3, 1] -> 12   (2 + 9 + 1: skip house 2, take 1, 3, 5)
[2, 1, 1, 2]    -> 4    (the two ends)
[2, 1, 4, 1, 1] -> 7    (the "take the biggest first" reading gives only 6)

CONSTRAINTS
-----------
- 0 <= len(houses) <= 10**4, each amount >= 0.
- O(n) time, O(1) space.

HINT
----
At house i you have exactly one real choice: rob it (then the best you can
do is the best up to house i-2, plus its money) or skip it (then the best
is simply the best up to house i-1). Two rolling variables are enough -
which one is "up to i-1" and which is "up to i-2" is the whole state.

COMPLEXITY
----------
Time:  O(n) - one pass, constant work per house
Space: O(1) - only the two rolling totals (the O(n) table is not needed,
       because house i only ever looks back at i-1 and i-2)
"""


def rob(houses):
    # skip = best total using houses up to the previous one WITHOUT robbing it
    # rob  = best total using houses up to the previous one WITH robbing it
    skip, take = 0, 0

    for amount in houses:
        # From each house's perspective the previous "take" is forbidden
        # (adjacent), so a new "take" builds only on the old "skip".
        skip, take = max(skip, take), skip + amount

    return max(skip, take)


def _brute_force(houses):
    """Try every subset of non-adjacent houses (exponential; test sizes only)."""
    best = 0

    def visit(i, running):
        nonlocal best
        if i >= len(houses):
            best = max(best, running)
            return
        visit(i + 1, running)            # skip house i
        visit(i + 2, running + houses[i])  # rob it, jump over the next

    visit(0, 0)
    return best


def _tests() -> None:
    # Empty and single house.
    assert rob([]) == 0
    assert rob([5]) == 5

    # Two houses: take the bigger, nothing else.
    assert rob([2, 3]) == 3
    assert rob([0, 0]) == 0

    # The case that defeats "take the biggest first": grabbing 4 first
    # leaves only 2+1 = 6, while 2 + 4 + 1 = 7.
    assert rob([2, 1, 4, 1, 1]) == 7

    # The two ends are the answer; all-equal; the documented examples.
    assert rob([2, 1, 1, 2]) == 4
    assert rob([3, 3, 3, 3]) == 6
    assert rob([2, 7, 9, 3, 1]) == 12

    # Cross-check against the exhaustive reference on randomised inputs.
    import random
    random.seed(25)
    for _ in range(300):
        n = random.randint(0, 10)
        houses = [random.randint(0, 9) for _ in range(n)]
        assert rob(houses) == _brute_force(houses), houses

    print("house_robber: all tests passed")


if __name__ == "__main__":
    _tests()
