"""
Challenge:  Redundant Connection
Pattern:    Union-Find (cycle detection in an undirected graph)
Difficulty: Medium

PROBLEM
-------
You start with a tree of n nodes labelled 1..n (n-1 edges, no cycles), then
ONE extra edge is added. Return the edge that can be removed so the result is
a tree again. If several answers exist, return the one that appears LAST in
the input.

EXAMPLES
--------
[[1,2],[1,3],[2,3]]                  ->  [2,3]
[[1,2],[2,3],[3,4],[1,4],[1,5]]      ->  [1,4]

CONSTRAINTS
-----------
- The graph is UNDIRECTED and connected, with exactly one extra edge.
- Node labels are 1-based.

HINT
----
Adding an edge between two nodes that are ALREADY connected is precisely what
creates a cycle. So process the edges in order and ask, for each one: are
these two endpoints already in the same component?

That question - "already connected?" - asked repeatedly while edges keep
arriving, is what union-find exists for. A DFS would work but would have to
re-search after every edge.

Because you scan in input order, the FIRST edge that fails to merge is also
the LAST one needed to break the cycle, which is what the problem asks for.

COMPLEXITY
----------
Time:  O(n * alpha(n)), effectively O(n)
Space: O(n) for the parent and rank arrays
"""


class DSU:
    """Disjoint Set Union with path compression and union by rank."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            # Path compression: point x at its grandparent as we climb.
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """Merge the groups. Returns False if they were ALREADY joined."""
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False                 # already connected -> this closes a cycle

        # Union by rank: hang the shorter tree under the taller one.
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True


def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    # Nodes are 1-based, so size n+1 and index 0 goes unused.
    dsu = DSU(len(edges) + 1)

    for a, b in edges:
        if not dsu.union(a, b):
            # These were already connected, so this edge closes the cycle.
            # Scanning in input order means this is also the last such edge.
            return [a, b]

    return []                            # unreachable for well-formed input


def _tests() -> None:
    assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
    assert find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
    assert find_redundant_connection([[1, 2], [2, 3], [1, 3]]) == [1, 3]

    # Smallest possible case: two nodes, a duplicated edge.
    assert find_redundant_connection([[1, 2], [1, 2]]) == [1, 2]

    # The cycle-closing edge is the LAST of the tied candidates.
    assert find_redundant_connection([[1, 2], [1, 3], [1, 4], [3, 4]]) == [3, 4]

    # DSU behaviour in isolation.
    dsu = DSU(5)
    assert dsu.union(1, 2) is True
    assert dsu.union(2, 3) is True
    assert dsu.union(1, 3) is False, "1 and 3 are already connected"
    assert dsu.find(1) == dsu.find(3)
    assert dsu.find(1) != dsu.find(4)

    # Path compression must not change which group a node belongs to.
    deep = DSU(50)
    for i in range(1, 49):
        deep.union(i, i + 1)
    root = deep.find(1)
    assert all(deep.find(i) == root for i in range(1, 50)), "all one component"

    # Cross-check: removing the returned edge must leave a valid tree -
    # connected, and with exactly n-1 edges.
    import random

    def is_tree(n: int, edges: list[list[int]]) -> bool:
        if len(edges) != n - 1:
            return False
        adjacency: dict[int, list[int]] = {i: [] for i in range(1, n + 1)}
        for a, b in edges:
            adjacency[a].append(b)
            adjacency[b].append(a)
        seen = {1}
        stack = [1]
        while stack:
            node = stack.pop()
            for nxt in adjacency[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return len(seen) == n            # connected and acyclic => a tree

    random.seed(103)
    for _ in range(400):
        n = random.randint(3, 9)
        # Build a random tree, then add exactly one extra edge.
        labels = list(range(1, n + 1))
        random.shuffle(labels)
        edges = [[labels[i], labels[random.randint(0, i - 1)]] for i in range(1, n)]

        existing = {frozenset(e) for e in edges}
        candidates = [
            [a, b] for a in labels for b in labels
            if a < b and frozenset((a, b)) not in existing
        ]
        if not candidates:
            continue
        edges.append(random.choice(candidates))
        random.shuffle(edges)

        answer = find_redundant_connection(edges)
        assert answer in edges or list(reversed(answer)) in edges, (edges, answer)

        remaining = list(edges)
        remaining.remove(answer)
        assert is_tree(n, remaining), (edges, answer)

    print("redundant_connection: all tests passed (400 randomised trees)")


if __name__ == "__main__":
    _tests()
