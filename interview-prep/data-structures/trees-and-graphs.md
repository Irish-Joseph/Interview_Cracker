# Trees and Graphs

The highest-yield topic after hash tables. Most "hard" interview problems are a
graph problem wearing a costume.

---

### 🟢 Q. What is a binary search tree, and what is its complexity?

**Answer.** A binary tree where, for every node, all keys in the left subtree are
smaller and all keys in the right subtree are larger. That invariant makes search
a series of "left or right?" decisions.

Search, insert and delete are **O(h)** where h is the height — **not** O(log n).
The two coincide only when the tree is balanced:

- Balanced: h ≈ log n → **O(log n)**.
- Degenerate (insert already-sorted data): h = n → **O(n)**, a linked list with
  extra pointers.

That degeneration is the entire reason self-balancing trees exist. Saying "O(h),
which is O(log n) only if balanced" is a much stronger answer than "O(log n)".

---

### 🟢 Q. What are the tree traversals and when do you use each?

**Answer.** Three depth-first orders, defined by when you visit the node relative
to its children, plus one breadth-first order.

```
        4
      /   \
     2     6
    / \   / \
   1   3 5   7
```

| Traversal | Order | Result | Use |
|---|---|---|---|
| **In-order** | left, **node**, right | 1 2 3 4 5 6 7 | **Sorted output from a BST** |
| **Pre-order** | **node**, left, right | 4 2 1 3 6 5 7 | Copying/serialising a tree |
| **Post-order** | left, right, **node** | 1 3 2 5 7 6 4 | Deleting; computing from children up |
| **Level-order (BFS)** | by depth | 4 2 6 1 3 5 7 | Shortest path; level-by-level work |

The fact worth memorising: **in-order traversal of a BST yields sorted order.**
"Validate a BST" and "find the kth smallest" are both just that observation.

---

### 🟡 Q. How do you validate a binary search tree?

**Answer.** The trap: checking only `left < node < right` locally is **wrong**.
It passes trees that are not BSTs:

```
    5
   / \
  3   7
     / \
    2   8     <- 2 < 5, so it violates the BST property,
              but locally 2 < 7 looks fine
```

Every node must fall inside a range inherited from its ancestors:

```python
def is_bst(node, low=float("-inf"), high=float("inf")):
    if node is None:
        return True
    if not (low < node.value < high):
        return False
    return (is_bst(node.left, low, node.value) and
            is_bst(node.right, node.value, high))
```

Equivalently: do an in-order traversal and check the output is strictly
increasing. Both are O(n) time, O(h) space.

---

### 🟡 Q. Which balanced trees should I know, and what balances them?

**Answer.** You need the idea, not the rotation code.

- **AVL** — strictly balanced; heights of sibling subtrees differ by at most 1.
  Faster lookups, more rotations on write.
- **Red–black** — loosely balanced via colour rules; the longest path is at most
  twice the shortest. Fewer rotations, so better for write-heavy work. This is
  what `TreeMap`, `std::map` and most standard libraries use.
- **B-tree / B+ tree** — high branching factor, so the tree is very shallow. Used
  by databases and filesystems because each node is one disk/page read; a
  three-level B+ tree can index millions of rows. Discussed further in
  [`databases/indexing-and-transactions.md`](../databases/indexing-and-transactions.md).

All give **O(log n)** worst case. The distinction is the constant factor and the
read/write balance.

---

### 🟢 Q. BFS or DFS — how do you choose?

**Answer.**

| | BFS | DFS |
|---|---|---|
| Structure | Queue | Stack (or recursion) |
| Visits | Nearest first | Deepest first |
| Finds shortest path | **Yes**, in an unweighted graph | No |
| Space | O(width) — can be huge | O(depth) |
| Natural for | Levels, shortest hops, "minimum steps" | Cycles, topological sort, connectivity, backtracking |

Both are **O(V + E)** time.

**The decisive rule:** if the question says *shortest*, *fewest*, or *minimum
number of steps* in an unweighted graph, use **BFS**. BFS reaches every node by
the fewest edges, so the first time it arrives is the shortest way. DFS gives no
such guarantee — it may find a long path first.

If edges are weighted, neither works: use **Dijkstra** (non-negative weights) or
**Bellman–Ford** (negative weights allowed).

---

### 🟡 Q. How do you represent a graph, and which representation should you pick?

**Answer.** Two options, chosen by density.

**Adjacency list** — map each vertex to its neighbours.
```python
graph = {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}
```
Space O(V + E). Iterating a vertex's neighbours is O(degree). **The default.**

**Adjacency matrix** — a V×V grid where `m[i][j]` marks an edge.
Space O(V²) regardless of edge count. Edge lookup is O(1); listing neighbours is
O(V).

Pick the matrix when the graph is **dense** (E approaches V²), when you need
constant-time "is there an edge?", or for matrix algorithms like Floyd–Warshall.
Pick the list otherwise — real graphs are almost always sparse, and O(V²) space
for a million vertices is a terabyte.

---

### 🟡 Q. Why must graph traversal track visited nodes when tree traversal need not?

**Answer.** Because a tree is by definition acyclic and each node has exactly one
parent — you cannot arrive anywhere twice. A general graph can have cycles and
multiple paths to the same node, so without a `visited` set traversal loops
forever or does exponential redundant work.

```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)
    for neighbour in graph[node]:
        dfs(graph, neighbour, visited)
```

Mark a node **when you enqueue/visit it**, not when you dequeue it — otherwise
the same node can be queued many times before it is ever processed.

---

### 🔴 Q. What is a topological sort and when is it impossible?

**Answer.** A linear ordering of a directed graph's vertices such that every edge
points forward — every task appears after everything it depends on. Build
systems, task schedulers and course prerequisites all need it.

**It is impossible exactly when the graph contains a cycle**, since a cycle means
a set of tasks that each depend on the other. So a topological sort doubles as a
cycle detector, which is often the real question.

Kahn's algorithm, O(V + E):

1. Compute every vertex's in-degree.
2. Enqueue all vertices with in-degree 0.
3. Pop one, append it to the output, and decrement its neighbours' in-degrees;
   enqueue any that reach 0.
4. If the output holds fewer than V vertices, **there is a cycle**.

A recursive example over a hierarchy is in
[`examples/sql/recursive-ctes/org_chart_tree_traversal.sql`](../../examples/sql/recursive-ctes/org_chart_tree_traversal.sql).

---

### 🟡 Q. What is a trie and why use one over a hash table?

**Answer.** A tree keyed by character, where a word's letters spell out the path
from the root. Shared prefixes share nodes.

Lookup is **O(k)** for a key of length k — independent of how many words are
stored, and with no hashing and no collisions.

The reason to choose it over a hash map is **prefix queries**. "All words
starting with `pre`" is one walk to the `pre` node followed by a subtree
traversal. A hash map cannot do this at all without scanning every key, because
hashing deliberately destroys the relationship between similar keys.

That makes tries the structure behind autocomplete, spell-checkers and IP routing
tables. The cost is memory: a node per character per distinct prefix.
