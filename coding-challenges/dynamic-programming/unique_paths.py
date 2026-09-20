"""
Challenge:  Unique Paths
Pattern:    Dynamic programming (2D grid, bottom-up)
Difficulty: Medium

PROBLEM
-------
A robot sits in the top-left cell of an m x n grid and can only move
right or down. How many distinct paths lead it to the bottom-right cell?

EXAMPLES
--------
m = 3, n = 7 -> 28
m = 3, n = 2 -> 3    (RRD, RDR, DRR)
m = 1, n = 1 -> 1    (nowhere to move)
m = 3, n = 3 -> 6

CONSTRAINTS
-----------
- 1 <= m, n <= 100.
- The naive recursion explores the same subgrid exponentially many times;
  the expected solution memoises (or iterates) in O(m*n).

HINT
----
The number of ways to reach a cell is the sum of the ways to reach the
cell above it and the cell to its left. The first row and first column
each have exactly one way in (you can only arrive by moving straight).
Fill the grid row by row.

COMPLEXITY
----------
Time:  O(m * n) - one addition per cell
Space: O(n) - only the previous row is needed (or O(m*n) with a full grid)
"""


def unique_paths(m: int, n: int) -> int:
    # row[j] = ways to reach the current row's j-th column.
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]  # from above (old row[j]) + from left
    return row[-1]


def _tests() -> None:
    # 1 x n and m x 1 grids have exactly one path.
    assert unique_paths(1, 1) == 1
    assert unique_paths(1, 5) == 1
    assert unique_paths(4, 1) == 1

    # The specified examples.
    assert unique_paths(3, 7) == 28
    assert unique_paths(3, 2) == 3
    assert unique_paths(3, 3) == 6

    # Symmetry: the grid transposed has the same count.
    assert unique_paths(3, 7) == unique_paths(7, 3)
    assert unique_paths(100, 1) == 1

    # Cross-check against the closed form: C(m+n-2, m-1).
    import math

    for m in range(1, 13):
        for n in range(1, 13):
            expected = math.comb(m + n - 2, m - 1)
            assert unique_paths(m, n) == expected, (m, n)

    print("unique_paths: all tests passed")


if __name__ == "__main__":
    _tests()
