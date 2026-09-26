"""Challenge: Range Sum Query 2D | Pattern: 2D prefix sum | Difficulty: Medium

Preprocess a matrix, then answer inclusive rectangle-sum queries in O(1).
Hint: inclusion-exclusion over the four prefix corners.
Complexity: O(rows*cols) build, O(1) query, O(rows*cols) space.
"""
import random

class NumMatrix:
    def __init__(self, matrix: list[list[int]]) -> None:
        rows, cols = len(matrix), len(matrix[0]) if matrix else 0
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
        for row in range(rows):
            running = 0
            for col in range(cols):
                running += matrix[row][col]
                self.prefix[row + 1][col + 1] = self.prefix[row][col + 1] + running

    def sum_region(self, top: int, left: int, bottom: int, right: int) -> int:
        p = self.prefix
        return p[bottom + 1][right + 1] - p[top][right + 1] - p[bottom + 1][left] + p[top][left]

def _brute(matrix: list[list[int]], top: int, left: int, bottom: int, right: int) -> int:
    return sum(matrix[r][c] for r in range(top, bottom + 1) for c in range(left, right + 1))

def _tests() -> None:
    assert NumMatrix([]).prefix == [[0]]
    assert NumMatrix([[7]]).sum_region(0, 0, 0, 0) == 7
    matrix = [[3, 0, 1, 4], [5, 6, 3, 2], [1, 2, 0, 1]]
    assert NumMatrix(matrix).sum_region(0, 1, 2, 3) == 19
    rng = random.Random(26)
    for _ in range(100):
        matrix = [[rng.randint(-5, 5) for _ in range(5)] for _ in range(4)]
        table = NumMatrix(matrix)
        top, bottom = sorted(rng.sample(range(4), 2)); left, right = sorted(rng.sample(range(5), 2))
        assert table.sum_region(top, left, bottom, right) == _brute(matrix, top, left, bottom, right)
    print("Range Sum Query 2D: all tests passed")

if __name__ == "__main__": _tests()
