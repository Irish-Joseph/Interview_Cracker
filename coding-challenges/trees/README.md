# Pattern: Trees

Trees are recursive by definition, so most tree solutions are naturally
recursive: solve the children, combine the results.

## The two modes

**Depth-first (recursion).** Ask "what do I need from my children?" and combine.
Space is O(h) for the call stack — O(log n) balanced, O(n) degenerate.

```python
def depth(node):
    if node is None:
        return 0
    return 1 + max(depth(node.left), depth(node.right))
```

**Breadth-first (a queue).** Use it whenever the problem mentions **levels**,
depth, or the shortest path. Process the queue one full level at a time by
capturing `len(queue)` before the inner loop.

## Facts worth memorising

- **In-order traversal of a BST yields sorted order.** "Validate a BST" and "kth
  smallest" are both that observation.
- BST operations are **O(h)**, which is O(log n) *only if balanced*.
- Validating a BST requires an inherited **range**, not a local comparison — see
  the challenge.

## Challenges

| File | Difficulty | Mode |
|---|---|---|
| [level_order_traversal.py](level_order_traversal.py) | 🟡 Medium | BFS |
| [validate_bst.py](validate_bst.py) | 🟡 Medium | DFS with bounds |
