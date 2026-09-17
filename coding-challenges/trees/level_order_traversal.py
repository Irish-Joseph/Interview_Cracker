"""
Challenge:  Binary Tree Level Order Traversal
Pattern:    Breadth-first search with a queue
Difficulty: Medium

PROBLEM
-------
Return the values of a binary tree's nodes level by level, left to right, as a
list of lists - one inner list per level.

EXAMPLES
--------
      3
     / \
    9   20
        / \
       15  7      -> [[3], [9, 20], [15, 7]]

None               -> []

CONSTRAINTS
-----------
- Each level must be its own list.

HINT
----
A queue gives you breadth-first order, but a plain BFS loop flattens everything
into one list - it does not tell you where one level ends.

The trick: before processing, record how many nodes are currently in the queue.
That count IS the size of the current level, because nothing else has been added
yet. Process exactly that many, and everything you enqueue meanwhile belongs to
the next level.

COMPLEXITY
----------
Time:  O(n) - every node enqueued and dequeued once
Space: O(w) where w is the widest level; for a complete tree that is ~n/2
"""

from __future__ import annotations

from collections import deque


class Node:
    def __init__(self, value: int, left: Node | None = None, right: Node | None = None) -> None:
        self.value = value
        self.left = left
        self.right = right


def level_order(root: Node | None) -> list[list[int]]:
    if root is None:
        return []

    levels: list[list[int]] = []
    queue: deque[Node] = deque([root])

    while queue:
        # Snapshot the level's size BEFORE adding this level's children.
        level_size = len(queue)
        level: list[int] = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        levels.append(level)

    return levels


def build(values: list[int | None]) -> Node | None:
    """Build a tree from a level-order list, using None for absent children."""
    if not values or values[0] is None:
        return None
    root = Node(values[0])
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        if index < len(values) and values[index] is not None:
            node.left = Node(values[index])
            queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right = Node(values[index])
            queue.append(node.right)
        index += 1
    return root


def _tests() -> None:
    assert level_order(build([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
    assert level_order(None) == []
    assert level_order(build([1])) == [[1]]
    assert level_order(build([1, 2])) == [[1], [2]]
    assert level_order(build([1, None, 2])) == [[1], [2]]

    # A left-leaning chain: one node per level.
    chain = Node(1, Node(2, Node(3, Node(4))))
    assert level_order(chain) == [[1], [2], [3], [4]]

    # A full three-level tree.
    assert level_order(build([1, 2, 3, 4, 5, 6, 7])) == [[1], [2, 3], [4, 5, 6, 7]]

    # The flattened result must match a plain BFS order.
    tree = build([3, 9, 20, None, None, 15, 7])
    flat = [value for level in level_order(tree) for value in level]
    assert flat == [3, 9, 20, 15, 7]

    print("level_order_traversal: all tests passed")


if __name__ == "__main__":
    _tests()
