"""
Challenge:  Number of Islands
Pattern:    Grid traversal / flood fill
Difficulty: Medium

PROBLEM
-------
Given a 2-D grid of '1' (land) and '0' (water), count the islands. An island is
land connected horizontally or vertically (NOT diagonally), surrounded by water.

EXAMPLES
--------
  1 1 0 0 0
  1 1 0 0 0        -> 3
  0 0 1 0 0
  0 0 0 1 1

  1 1 1
  0 1 0            -> 1   (all connected)
  1 1 1

CONSTRAINTS
-----------
- The grid may be empty.
- Diagonal neighbours do NOT connect.

HINT
----
Scan every cell. When you find land you have not seen before, you have found a
new island - so increment the count, then flood-fill outwards to mark that
entire island as visited, so its other cells do not each count again.

The flood fill can be DFS or BFS; either works, since you only need connectivity,
not shortest paths.

COMPLEXITY
----------
Time:  O(rows * cols) - every cell is examined a constant number of times
Space: O(rows * cols) worst case - the visited set, plus the DFS stack for a
       grid that is entirely land
"""

DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))     # no diagonals


def count_islands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    islands = 0

    def flood(start_row: int, start_col: int) -> None:
        """Iterative DFS - avoids a stack overflow on a large all-land grid."""
        stack = [(start_row, start_col)]
        while stack:
            row, col = stack.pop()
            for delta_row, delta_col in DIRECTIONS:
                next_row, next_col = row + delta_row, col + delta_col
                if (0 <= next_row < rows and 0 <= next_col < cols
                        and grid[next_row][next_col] == "1"
                        and (next_row, next_col) not in visited):
                    visited.add((next_row, next_col))   # mark on PUSH
                    stack.append((next_row, next_col))

    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == "1" and (row, col) not in visited:
                islands += 1                 # a cell no island has claimed
                visited.add((row, col))
                flood(row, col)

    return islands


def to_grid(text: str) -> list[list[str]]:
    return [list(line.strip()) for line in text.strip().splitlines() if line.strip()]


def _tests() -> None:
    assert count_islands(to_grid("""
        11000
        11000
        00100
        00011
    """)) == 3

    assert count_islands(to_grid("""
        111
        010
        111
    """)) == 1

    assert count_islands([]) == 0
    assert count_islands([[]]) == 0
    assert count_islands(to_grid("0")) == 0
    assert count_islands(to_grid("1")) == 1
    assert count_islands(to_grid("000\n000")) == 0
    assert count_islands(to_grid("111\n111")) == 1

    # Diagonals must NOT connect.
    assert count_islands(to_grid("10\n01")) == 2

    # A checkerboard: every land cell is its own island.
    assert count_islands(to_grid("101\n010\n101")) == 5

    # Cross-check against a union-find implementation.
    import random

    def reference(grid: list[list[str]]) -> int:
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        parent: dict[tuple[int, int], tuple[int, int]] = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1":
                    parent[(r, c)] = (r, c)
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != "1":
                    continue
                for dr, dc in ((1, 0), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                        parent[find((r, c))] = find((nr, nc))
        return len({find(cell) for cell in parent})

    random.seed(43)
    for _ in range(300):
        rows, cols = random.randint(1, 6), random.randint(1, 6)
        grid = [[random.choice("01") for _ in range(cols)] for _ in range(rows)]
        assert count_islands(grid) == reference(grid), grid

    print("number_of_islands: all tests passed (300 randomised cross-checks)")


if __name__ == "__main__":
    _tests()
