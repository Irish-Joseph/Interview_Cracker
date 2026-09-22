"""
Challenge:  Search a 2D Matrix
Pattern:    Binary search (a 2D matrix is a sorted list wearing a costume)
Difficulty: Easy

PROBLEM
    Given a matrix of m rows and n columns where the elements in each row
    are sorted left-to-right and the first element of each row is greater
    than the last element of the previous row, return whether `target` is
    in the matrix.

EXAMPLES
    [[1,  3,  5,  7],
     [10, 11, 16, 20],
     [23, 30, 34, 60]], target 3  -> True
    same matrix, target 13       -> False
    [[1]], target 1              -> True
    [[1]], target 0              -> False

CONSTRAINTS
    - 1 <= m, n <= 100, so O(m*n) linear scan is "fine" for the sizes -
      the point is the O(log(m*n)) search and the index translation.
    - Read-only; the matrix is not modified.

HINT
    The rows are sorted AND every row starts after the previous row ends,
    so the matrix is one long sorted sequence of m*n values in disguise.
    Run binary search over the range [0, m*n) and translate a flat index
    back into a row and column with two arithmetic operations.

COMPLEXITY
    Time: O(log(m*n)) - classic binary search over m*n virtual positions.
    Space: O(1) - only lo, hi and mid.
"""

from __future__ import annotations

import random

Matrix = list[list[int]]


def search(matrix: Matrix, target: int) -> bool:
    if not matrix or not matrix[0]:
        return False

    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols - 1          # inclusive bounds, over the FLAT range

    while lo <= hi:
        mid = lo + (hi - lo) // 2
        value = matrix[mid // cols][mid % cols]   # flat index -> (row, col)
        if value == target:
            return True
        if value < target:
            lo = mid + 1                # +1, or the range stops shrinking
        else:
            hi = mid - 1
    return False


def _linear(matrix: Matrix, target: int) -> bool:
    """Brute-force reference: check every cell."""
    return any(target in row for row in matrix)


def _random_matrix(rng: random.Random, rows: int, cols: int) -> Matrix:
    """Build a matrix with the required global ordering."""
    values = sorted(rng.randrange(-50, 50) for _ in range(rows * cols))
    return [values[i * cols:(i + 1) * cols] for i in range(rows)]


def _tests() -> None:
    # empty input
    assert search([], 5) is False
    assert search([[]], 5) is False

    # single element, present and absent
    assert search([[1]], 1) is True
    assert search([[1]], 0) is False
    assert search([[1]], 2) is False

    # the classic shape
    matrix: Matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60],
    ]
    assert search(matrix, 3) is True
    assert search(matrix, 13) is False

    # the boundary positions are the ones off-by-one bugs live in:
    flat = [1, 3, 5, 7, 10, 11, 16, 20, 23, 30, 34, 60]
    assert search(matrix, flat[0]) is True          # very first
    assert search(matrix, flat[-1]) is True         # very last
    assert search(matrix, flat[7]) is True          # first cell of row 2
    assert search(matrix, flat[6]) is True          # last cell of row 1
    assert search(matrix, flat[0] - 1) is False     # below the range
    assert search(matrix, flat[-1] + 1) is False    # above the range

    # cross-check against the brute force on randomised matrices
    rng = random.Random(20260922)
    for _ in range(300):
        m, n = rng.randrange(1, 8), rng.randrange(1, 8)
        mat = _random_matrix(rng, m, n)
        target = rng.randrange(-60, 61)
        assert search(mat, target) is _linear(mat, target), (mat, target)

    print("search_2d_matrix: all tests passed")


if __name__ == "__main__":
    _tests()
