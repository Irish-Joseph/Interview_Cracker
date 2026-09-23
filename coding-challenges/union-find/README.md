# Pattern: Union-Find (Disjoint Set Union)

Track which elements belong to the same group, while groups keep merging.
Two operations, both effectively O(1):

- `find(x)` — which group is x in?
- `union(a, b)` — merge the two groups

## When to reach for it

- **Dynamic connectivity**: edges arrive one at a time and you must answer
  "are these two connected *yet*?" after each one.
- **Cycle detection in an UNDIRECTED graph**: an edge whose endpoints are
  already in the same group closes a cycle.
- **Counting connected components** as they merge.
- **Kruskal's MST**, where you add the cheapest edge that does not form a cycle.
- Grouping by an equivalence relation: accounts sharing an email, equations
  like `a == b`.

## Union-find or DFS/BFS?

Both find connected components, so the distinction is worth having ready:

| | Union-Find | DFS / BFS |
|---|---|---|
| Edges arrive **incrementally** | ✅ natural | ✗ must re-run each time |
| Graph is **fixed** up front | works | usually simpler |
| Needs the actual **path** | ✗ cannot | ✅ gives it |
| Detects a cycle **as it forms** | ✅ | after the fact |
| Cost | ~O(E·α(n)), α < 5 always | O(V + E) per run |

**Rule of thumb:** if the problem streams edges and asks about connectivity
along the way, use union-find. If it hands you the whole graph and asks for a
path, traverse.

## The implementation, and why both optimisations matter

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n                  # tree depth, for union by rank

    def find(self, x):
        while self.parent[x] != x:
            # Path compression: point x straight at its grandparent, halving
            # the path on the way up. Costs nothing, flattens the tree.
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                     # already joined -> a cycle
        # Union by rank: hang the shorter tree off the taller one, so depth
        # grows as slowly as possible.
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
```

Without either optimisation, a union chain degenerates into a linked list and
`find` becomes O(n). With both, the amortised cost is O(α(n)) — the inverse
Ackermann function, which is below 5 for any input that fits in the universe.
Treat it as constant, but know the name.

**`union` returning a boolean is the useful part.** `False` means "already
connected", which is exactly a cycle — so cycle detection falls out for free
rather than needing a second pass.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [redundant_connection.py](redundant_connection.py) | 🟡 Medium | Cycle detection as edges arrive |
| [number_of_provinces.py](number_of_provinces.py) | 🟢 Easy | Count connected components |
