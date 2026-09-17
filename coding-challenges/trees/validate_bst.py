"""
Challenge:  Validate a Binary Search Tree
Pattern:    DFS carrying inherited bounds
Difficulty: Medium

PROBLEM
-------
Given the root of a binary tree, decide whether it is a valid binary search
tree: every node's left subtree holds only smaller values, every node's right
subtree holds only larger values, and both subtrees are themselves valid BSTs.

EXAMPLES
--------
    2
   / \
  1   3        -> True

    5
   / \
  3   7
     / \
    2   8      -> False   (2 is in the right subtree of 5, but 2 < 5)

CONSTRAINTS
-----------
- Values are distinct; equal values are NOT allowed on either side.

HINT
----
The tempting solution - check node.left.value < node.value < node.right.value at
each node - is WRONG. The second example above passes every local check: 3 < 5,
7 > 5, 2 < 7, 8 > 7. Yet 2 sits in 5's right subtree, which breaks the BST
property.

The reason is that the constraint is inherited from ALL ancestors, not just the
parent. Every node lives inside a (low, high) range that narrows as you descend.

There is a second solution worth knowing: in-order traversal of a valid BST
produces strictly increasing values. Both are implemented below.

COMPLEXITY
----------
Time:  O(n) - each node visited once
Space: O(h) - the call stack; O(log n) balanced, O(n) degenerate
"""

from __future__ import annotations


class Node:
    def __init__(self, value: int, left: Node | None = None, right: Node | None = None) -> None:
        self.value = value
        self.left = left
        self.right = right


def is_valid_bst(node: Node | None,
                 low: float = float("-inf"),
                 high: float = float("inf")) -> bool:
    if node is None:
        return True                      # an empty tree is a valid BST

    if not low < node.value < high:      # violates a bound set by an ancestor
        return False

    # Descending left tightens the upper bound; descending right tightens
    # the lower bound.
    return (is_valid_bst(node.left, low, node.value)
            and is_valid_bst(node.right, node.value, high))


def is_valid_bst_inorder(root: Node | None) -> bool:
    """Alternative: in-order traversal must be strictly increasing."""
    previous: float = float("-inf")
    stack: list[Node] = []
    node = root

    while stack or node:
        while node:                      # walk as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()
        if node.value <= previous:       # not strictly increasing
            return False
        previous = node.value
        node = node.right

    return True


def _tests() -> None:
    valid = Node(2, Node(1), Node(3))
    assert is_valid_bst(valid) is True

    # The case that defeats a naive local check.
    sneaky = Node(5, Node(3), Node(7, Node(2), Node(8)))
    assert is_valid_bst(sneaky) is False

    assert is_valid_bst(None) is True                       # empty
    assert is_valid_bst(Node(1)) is True                    # single node
    assert is_valid_bst(Node(1, Node(1))) is False          # duplicates invalid
    assert is_valid_bst(Node(1, None, Node(1))) is False
    assert is_valid_bst(Node(2, Node(3), None)) is False     # left child too big
    assert is_valid_bst(Node(2, None, Node(1))) is False     # right child too small

    # A valid larger tree.
    big = Node(8,
               Node(4, Node(2, Node(1), Node(3)), Node(6, Node(5), Node(7))),
               Node(12, Node(10), Node(14)))
    assert is_valid_bst(big) is True

    # A left-leaning chain is a valid (degenerate) BST.
    chain = Node(5, Node(4, Node(3, Node(2))))
    assert is_valid_bst(chain) is True

    # Both implementations must always agree.
    for tree in (valid, sneaky, None, Node(1), big, chain,
                 Node(1, Node(1)), Node(2, Node(3), None)):
        assert is_valid_bst(tree) == is_valid_bst_inorder(tree)

    # Randomised: build from a shuffled list via BST insertion (always valid),
    # then corrupt one node and expect invalidity.
    import random

    def insert(root: Node | None, value: int) -> Node:
        if root is None:
            return Node(value)
        if value < root.value:
            root.left = insert(root.left, value)
        else:
            root.right = insert(root.right, value)
        return root

    random.seed(41)
    for _ in range(200):
        values = random.sample(range(100), random.randint(1, 12))
        root: Node | None = None
        for value in values:
            root = insert(root, value)
        assert is_valid_bst(root) is True, values
        assert is_valid_bst_inorder(root) is True, values

    print("validate_bst: all tests passed (200 randomised trees, both variants)")


if __name__ == "__main__":
    _tests()
