r"""
Challenge:  Lowest Common Ancestor of a Binary Search Tree
Pattern:    Trees (BST property beats traversal)
Difficulty: Medium

PROBLEM
-------
Given a binary search tree and two nodes p and q that are guaranteed to
exist in it, return their lowest common ancestor (LCA): the deepest node
that is an ancestor of both. A node is considered an ancestor of itself.

EXAMPLES
--------
        6                    2 and 8  -> 6
      /   \
     2     8          2 and 4  -> 2    (2 is an ancestor of itself)
    / \   / \
   0   4 7   9      7 and 9  -> 8
      / \
     3   5

CONSTRAINTS
-----------
- p and q are always present in the tree, and p != q.
- Naive approach (collect ancestor paths and intersect them) is O(h)
  space; the BST property allows O(1) space.

HINT
----
In a BST, everything left of a node is smaller and everything right is
bigger. If p and q are on OPPOSITE sides of the current node, it must be
their LCA. If both are smaller, the LCA is below-and-left; if both are
bigger, below-and-right. Walk down, never branching.

COMPLEXITY
----------
Time:  O(h) - one pass from the root, h = tree height
Space: O(1) iterative (O(h) stack if written recursively)
"""

from typing import Optional


class TreeNode:
    def __init__(self, value: int, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def lowest_common_ancestor(root: TreeNode, p: int, q: int) -> int:
    node = root
    while True:
        if p < node.value and q < node.value:
            node = node.left          # both targets are in the left subtree
        elif p > node.value and q > node.value:
            node = node.right         # both targets are in the right subtree
        else:
            return node.value         # split point — or node is p/q itself


def _tests() -> None:
    # Build the classic example tree:
    #        6
    #      /   \
    #     2     8
    #    / \   / \
    #   0   4 7   9
    #      / \
    #     3   5
    root = TreeNode(6,
                    TreeNode(2,
                             TreeNode(0),
                             TreeNode(4, TreeNode(3), TreeNode(5))),
                    TreeNode(8, TreeNode(7), TreeNode(9)))

    # The specified examples.
    assert lowest_common_ancestor(root, 2, 8) == 6
    assert lowest_common_ancestor(root, 2, 4) == 2   # ancestor of itself
    assert lowest_common_ancestor(root, 7, 9) == 8
    assert lowest_common_ancestor(root, 3, 5) == 4
    assert lowest_common_ancestor(root, 0, 5) == 2

    # Symmetry: argument order must not matter.
    assert lowest_common_ancestor(root, 8, 2) == 6
    assert lowest_common_ancestor(root, 5, 3) == 4

    # Skewed tree (a sorted list): every ancestor query collapses to the
    # smaller of the two values.
    chain = TreeNode(1, None, TreeNode(2, None, TreeNode(3, None, TreeNode(4))))
    assert lowest_common_ancestor(chain, 1, 4) == 1
    assert lowest_common_ancestor(chain, 2, 4) == 2
    assert lowest_common_ancestor(chain, 3, 4) == 3

    # Single-child tree.
    assert lowest_common_ancestor(TreeNode(5, TreeNode(3)), 3, 5) == 5

    # Cross-check against an ancestor-path reference on a random BST.
    import random

    def make_bst(values):
        node = None
        for v in values:
            if node is None:
                node = TreeNode(v)
                continue
            cur = node
            while True:
                if v < cur.value:
                    if cur.left is None:
                        cur.left = TreeNode(v)
                        break
                    cur = cur.left
                else:
                    if cur.right is None:
                        cur.right = TreeNode(v)
                        break
                    cur = cur.right
        return node

    def ancestors(root, target, path=()):
        """Ordered root->target path as a tuple."""
        if root is None:
            return None
        if root.value == target:
            return path + (root.value,)
        child = root.left if target < root.value else root.right
        sub = ancestors(child, target, path + (root.value,))
        return sub

    random.seed(17)
    for _ in range(200):
        values = random.sample(range(1, 60), random.randint(2, 25))
        tree = make_bst(values)
        p, q = random.sample(values, 2)
        path_p = set(ancestors(tree, p))
        # Walk the q-path from the root; the last node that is also an
        # ancestor of p is the deepest (lowest) common ancestor.
        expected = next(
            v for v in reversed(ancestors(tree, q)) if v in path_p
        )
        got = lowest_common_ancestor(tree, p, q)
        assert got == expected, (values, p, q, got, expected)

    print("lowest_common_ancestor_bst: all tests passed")


if __name__ == "__main__":
    _tests()
