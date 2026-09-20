# Pattern: Graphs

Many problems are graph problems in disguise: a grid is a graph where each cell
neighbours its four adjacent cells; course prerequisites are a directed graph;
word ladders are a graph of one-letter edits.

## Choosing the traversal

| Use | When |
|---|---|
| **BFS** (queue) | Shortest path / fewest steps in an **unweighted** graph; level-by-level work |
| **DFS** (stack or recursion) | Connectivity, counting components, cycle detection, backtracking |
| **Topological sort** | Dependency ordering; also detects cycles |
| **Dijkstra** | Shortest path with **non-negative weights** |
| **Union–Find** | Dynamic connectivity, Kruskal's MST |

BFS and DFS are both **O(V + E)**. The decisive rule: if the problem says
*shortest*, *fewest* or *minimum steps* and edges are unweighted, use **BFS** —
it reaches every node by the fewest edges, so the first arrival is optimal. DFS
gives no such guarantee.

## Always track visited

A graph can have cycles and multiple paths to the same node. Without a `visited`
set, traversal loops forever or does exponential redundant work.

Mark a node **when you enqueue it**, not when you dequeue it — otherwise the same
node can be queued many times before it is ever processed.

## Grids as graphs

```python
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))     # up, down, left, right
for dr, dc in DIRECTIONS:
    nr, nc = row + dr, col + dc
    if 0 <= nr < rows and 0 <= nc < cols:           # bounds check first
        ...
```

## Challenges

| File | Difficulty | Technique |
|---|---|---|
| [number_of_islands.py](number_of_islands.py) | 🟡 Medium | Grid DFS / flood fill |
| [course_schedule.py](course_schedule.py) | 🟡 Medium | Topological sort (cycle detection) |
| [word_ladder.py](word_ladder.py) | 🔴 Hard | Implicit graph + BFS |
