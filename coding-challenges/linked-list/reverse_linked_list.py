"""
Challenge:  Reverse a Linked List
Pattern:    Three-pointer rewiring
Difficulty: Easy

PROBLEM
-------
Reverse a singly linked list and return the new head.

EXAMPLES
--------
1 -> 2 -> 3 -> None   becomes   3 -> 2 -> 1 -> None
None                  becomes   None
1 -> None             becomes   1 -> None

CONSTRAINTS
-----------
- Do it in O(1) extra space (so: iteratively).

HINT
----
Walk the list once, flipping each `next` pointer to point backwards.

The whole difficulty is in one ordering detail: the moment you set
`curr.next = prev`, you have destroyed your only reference to the rest of the
list. Save it first.

When the loop ends, `curr` is None - so which variable holds the new head?

COMPLEXITY
----------
Time:  O(n)
Space: O(1)  (the recursive version is O(n) from the call stack)
"""

from __future__ import annotations


class Node:
    def __init__(self, value: int, next: Node | None = None) -> None:
        self.value = value
        self.next = next


def reverse(head: Node | None) -> Node | None:
    prev: Node | None = None
    curr = head

    while curr:
        next_node = curr.next    # save BEFORE overwriting
        curr.next = prev         # flip the link
        prev = curr              # advance both pointers
        curr = next_node

    return prev                  # curr is None; prev is the last node visited


def reverse_recursive(head: Node | None) -> Node | None:
    """Same result, O(n) stack space. Included for comparison."""
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head        # make the next node point back at us
    head.next = None             # and break the old forward link
    return new_head


def build(values: list[int]) -> Node | None:
    head: Node | None = None
    for value in reversed(values):
        head = Node(value, head)
    return head


def to_list(head: Node | None) -> list[int]:
    out: list[int] = []
    while head:
        out.append(head.value)
        head = head.next
    return out


def _tests() -> None:
    for values in ([], [1], [1, 2], [1, 2, 3], [1, 2, 3, 4, 5], [7, 7, 7]):
        assert to_list(reverse(build(values))) == values[::-1], values
        assert to_list(reverse_recursive(build(values))) == values[::-1], values

    # Reversing twice returns the original order.
    assert to_list(reverse(reverse(build([1, 2, 3])))) == [1, 2, 3]

    # The new tail must terminate, not dangle.
    head = reverse(build([1, 2, 3]))
    assert head is not None and head.value == 3
    tail = head
    while tail.next:
        tail = tail.next
    assert tail.value == 1 and tail.next is None

    print("reverse_linked_list: all tests passed (iterative and recursive)")


if __name__ == "__main__":
    _tests()
