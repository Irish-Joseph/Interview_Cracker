"""
Challenge:  Number of Provinces
Pattern:    Union-Find (count the connected components of an undirected graph)
Difficulty: Easy

PROBLEM
    n cities, some pairs connected by a direct road (the matrix is symmetric
    with zeros on the diagonal). Two cities are in the same "province" if
    there is a road path between them. Return the number of provinces.

EXAMPLES
    [[1, 1, 0],
     [1, 1, 0],
     [0, 0, 1]]            -> 2   ({0,1} and {2})
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 1]]         -> 4   (no roads at all)
    [[1]]                  -> 1

CONSTRAINTS
    - 1 <= n <= 200, matrix is symmetric, matrix[i][i] == 0.
    - Only the UPPER triangle carries information (i < j); the diagonal is
      self-loops and must be skipped or it unions a city with itself.

HINT
    Each city starts as its own component. For every road (i, j) with i < j,
    union the two cities. The answer is how many DISTINCT roots remain -
    equivalently, how many unions actually merged two different components.

COMPLEXITY
    Time: O(n^2 / alpha(n)) ~= O(n^2) - we must read the n x n matrix anyway.
    Space: O(n) for parent and rank.
"""

from __future__ import annotations

import random


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        # Path HALVING: each hop pulls the node up two levels, so the tree
        # stays flat without a separate compression pass.
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """Return True if this merged two previously separate components."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def number_of_provinces(matrix: list[list[int]]) -> int:
    n = len(matrix)
    uf = UnionFind(n)
    provinces = n                          # every city starts alone

    for i in range(n):
        for j in range(i + 1, n):          # upper triangle only: i < j
            if matrix[i][j] == 1 and uf.union(i, j):
                provinces -= 1             # a real merge: one province fewer

    return provinces


def _flood_count(matrix: list[list[int]]) -> int:
    """Brute-force reference: BFS the adjacency matrix per unvisited city."""
    n = len(matrix)
    seen = [False] * n
    count = 0
    for start in range(n):
        if seen[start]:
            continue
        count += 1
        stack = [start]
        seen[start] = True
        while stack:
            u = stack.pop()
            for v in range(n):
                if matrix[u][v] == 1 and not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return count


def _random_symmetric(n: int, rng: random.Random) -> list[list[int]]:
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.4:
                m[i][j] = m[j][i] = 1
    return m


def _tests() -> None:
    # single city (the "n=1" edge), no roads, and the documented example
    assert number_of_provinces([[1]]) == 1
    assert number_of_provinces([[1, 0], [0, 1]]) == 2
    assert number_of_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
    identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    assert number_of_provinces(identity) == 4

    # fully connected: one province
    full = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    assert number_of_provinces(full) == 1

    # a chain 0-1-2-3: transitivity must collapse four cities to one
    chain = [[0, 1, 0, 0],
             [1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0]]
    assert number_of_provinces(chain) == 1

    # the input must not be mutated
    snapshot = [row[:] for row in chain]
    number_of_provinces(chain)
    assert chain == snapshot

    # cross-check against the flood-fill brute force on random symmetric graphs
    rng = random.Random(20260923)
    for _ in range(500):
        n = rng.randrange(1, 30)
        m = _random_symmetric(n, rng)
        assert number_of_provinces(m) == _flood_count(m), m

    print("number_of_provinces: all tests passed")


if __name__ == "__main__":
    _tests()
