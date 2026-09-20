"""
Challenge:  Remove Nth Node From End of List
Pattern:    Linked list (fast and slow pointers)
Difficulty: Medium

PROBLEM
-------
Given the head of a singly-linked list, remove the nth node from the end
of the list and return its head. Do it in a single pass.

EXAMPLES
--------
[1,2,3,4,5], n = 2  -> [1,2,3,5]   (the 4, second from the end, is gone)
[1], n = 1          -> []          (removing the only node)
[1,2], n = 2        -> [2]         (removing the head)

CONSTRAINTS
-----------
- 1 <= length <= 30, 1 <= n <= length, so a node to remove always exists.
- One pass over the list: a second pass to count the length first is the
  naive approach this pattern exists to avoid.

HINT
----
The gap you need is n+1, not n. Start a slow pointer n+1 steps behind a
fast pointer (use a dummy node before the head so removing the real head
needs no special case). Move both until fast reaches the end: slow now
sits on the node just BEFORE the one to delete.

COMPLEXITY
----------
Time:  O(L) - single pass, where L is the list length
Space: O(1)
"""

from typing import Optional


class ListNode:
    def __init__(self, value: int = 0, next: "Optional[ListNode]" = None):
        self.value = value
        self.next = next


def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    # The dummy handles "remove the head" without a separate branch:
    # slow ends up on the dummy, and dummy.next is re-pointed.
    dummy = ListNode(0, head)

    # Advance fast n+1 steps so the slow/fast gap becomes n+1 nodes.
    fast = dummy
    for _ in range(n + 1):
        fast = fast.next

    slow = dummy
    while fast is not None:
        slow = slow.next
        fast = fast.next

    # slow.next is the nth node from the end; splice it out.
    slow.next = slow.next.next
    return dummy.next


def to_list(node: Optional[ListNode]) -> list[int]:
    out = []
    while node:
        out.append(node.value)
        node = node.next
    return out


def build(values: list[int]) -> Optional[ListNode]:
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def _tests() -> None:
    # Single node removed -> empty list.
    assert to_list(remove_nth_from_end(build([1]), 1)) == []

    # Removing the head (n == length).
    assert to_list(remove_nth_from_end(build([1, 2]), 2)) == [2]
    assert to_list(remove_nth_from_end(build([7]), 1)) == []

    # The specified example: middle removal.
    assert to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]

    # Removing the tail (n == 1).
    assert to_list(remove_nth_from_end(build([1, 2, 3]), 1)) == [1, 2]

    # Removing from a two-element list, both positions.
    assert to_list(remove_nth_from_end(build([9, 8]), 1)) == [9]
    assert to_list(remove_nth_from_end(build([9, 8]), 2)) == [8]

    # Cross-check against a length-counting reference on random inputs.
    import random

    def reference(values: list[int], n: int) -> list[int]:
        length = len(values)
        index_to_remove = length - n  # 0-based position
        return values[:index_to_remove] + values[index_to_remove + 1:]

    random.seed(3)
    for _ in range(300):
        length = random.randint(1, 15)
        values = [random.randint(0, 9) for _ in range(length)]
        n = random.randint(1, length)
        result = to_list(remove_nth_from_end(build(values), n))
        assert result == reference(values, n), (values, n, result)

    print("remove_nth_from_end: all tests passed")


if __name__ == "__main__":
    _tests()
