"""Challenge: Maximum Depth of a Binary Tree | Pattern: tree DFS | Difficulty: Easy

Return nodes on the longest root-to-leaf path. Empty tree depth is zero.
Hint: a node's depth is one plus its deeper child.
Complexity: O(n) time; O(h) call-stack space for tree height h.
"""

from dataclasses import dataclass
import random


@dataclass
class TreeNode:
    value: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None


def maximum_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + max(maximum_depth(root.left), maximum_depth(root.right))


def _breadth_first_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    level, depth = [root], 0
    while level:
        depth += 1
        level = [child for node in level for child in (node.left, node.right) if child]
    return depth


def _random_tree(rng: random.Random, nodes: int) -> TreeNode | None:
    if nodes == 0:
        return None
    root = TreeNode(0)
    available = [root]
    for value in range(1, nodes):
        while True:
            parent = rng.choice(available)
            side = rng.choice(("left", "right"))
            if getattr(parent, side) is None:
                child = TreeNode(value)
                setattr(parent, side, child)
                available.append(child)
                if parent.left and parent.right:
                    available.remove(parent)
                break
    return root


def _tests() -> None:
    assert maximum_depth(None) == 0
    assert maximum_depth(TreeNode(1)) == 1
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert maximum_depth(root) == 3
    rng = random.Random(24)
    for size in range(40):
        tree = _random_tree(rng, size)
        assert maximum_depth(tree) == _breadth_first_depth(tree)
    print("Maximum Depth of a Binary Tree: all tests passed")


if __name__ == "__main__":
    _tests()
