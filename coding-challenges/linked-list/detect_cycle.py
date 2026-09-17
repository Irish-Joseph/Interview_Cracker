"""
Challenge:  Linked List Cycle (detect it, and find where it starts)
Pattern:    Floyd's tortoise and hare
Difficulty: Medium

PROBLEM
-------
Given the head of a linked list, determine whether it contains a cycle. If it
does, return the node where the cycle begins; otherwise return None.

EXAMPLES
--------
3 -> 2 -> 0 -> -4
     ^___________|     -> cycle starts at the node holding 2

1 -> 2 -> None         -> None

CONSTRAINTS
-----------
- Solve it in O(1) extra space (a visited set is O(n) and is the easy answer).

HINT
----
Move one pointer one step at a time and another two steps at a time. If there
is a cycle they must eventually meet, because once both are inside the loop the
fast pointer closes the gap by exactly one position per iteration - so it can
never jump over the slow one.

For the second half (WHERE the cycle starts): after they meet, reset one pointer
to the head and advance both ONE step at a time. They meet at the entrance.

Why that works: let L be head->entrance, and let the meeting point be M steps
into the cycle. When they meet, slow has walked L+M and fast has walked
2(L+M), so the extra distance fast covered, L+M, is a whole number of laps.
That means walking L more steps from the meeting point lands exactly on the
entrance - which is also L steps from the head.

COMPLEXITY
----------
Time:  O(n)
Space: O(1)
"""

from __future__ import annotations


class Node:
    def __init__(self, value: int, next: Node | None = None) -> None:
        self.value = value
        self.next = next


def has_cycle(head: Node | None) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next            # 1 step
        fast = fast.next.next       # 2 steps
        if slow is fast:            # identity, not equality
            return True
    return False                    # fast reached the end - no cycle


def cycle_start(head: Node | None) -> Node | None:
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # Phase 2: both now move one step at a time.
            finder = head
            while finder is not slow:
                finder = finder.next
                slow = slow.next
            return finder

    return None


def build_with_cycle(values: list[int], cycle_index: int | None) -> Node | None:
    """Build a list; if cycle_index is not None, link the tail back to it."""
    if not values:
        return None
    nodes = [Node(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if cycle_index is not None:
        nodes[-1].next = nodes[cycle_index]
    return nodes[0]


def _tests() -> None:
    # No cycle
    assert has_cycle(None) is False
    assert has_cycle(build_with_cycle([1], None)) is False
    assert has_cycle(build_with_cycle([1, 2], None)) is False
    assert has_cycle(build_with_cycle([1, 2, 3, 4, 5], None)) is False
    assert cycle_start(build_with_cycle([1, 2, 3], None)) is None

    # Cycles at various positions
    head = build_with_cycle([3, 2, 0, -4], 1)
    assert has_cycle(head) is True
    start = cycle_start(head)
    assert start is not None and start.value == 2

    head = build_with_cycle([1, 2], 0)
    assert has_cycle(head) is True
    assert cycle_start(head).value == 1

    head = build_with_cycle([1], 0)            # single node pointing at itself
    assert has_cycle(head) is True
    assert cycle_start(head).value == 1

    head = build_with_cycle([1, 2, 3, 4, 5], 4)  # tail loops to itself
    assert has_cycle(head) is True
    assert cycle_start(head).value == 5

    # Exhaustive: every cycle entry point for lists up to length 8.
    for size in range(1, 9):
        values = list(range(size))
        for entry in range(size):
            head = build_with_cycle(values, entry)
            assert has_cycle(head) is True, (size, entry)
            assert cycle_start(head).value == entry, (size, entry)
        assert has_cycle(build_with_cycle(values, None)) is False

    print("detect_cycle: all tests passed (exhaustive over entry points up to n=8)")


if __name__ == "__main__":
    _tests()
