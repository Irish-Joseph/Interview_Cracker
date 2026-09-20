/*
 * Topic: Passing 2D arrays to functions — the three shapes that actually work.
 *
 * Concepts:
 * - A `double a[3][4]` argument in a prototype DECAYS to "pointer to array
 *   of 4 doubles": `double (*a)[4]`. The COLUMN count is part of the type.
 * - Why `double a[][4]` compiles but `double a[][]` does not
 * - The flat-array alternative for dynamic widths: a[row * cols + col]
 * - Pointer arithmetic: a + 1 advances by a whole row (4 doubles)
 *
 * Validated by inspection (no C compiler on the authoring machine).
 *
 * Example output:
 *   row0sum 10  row1sum 26  row2sum 42
 *   first_of_row2 = 5
 *   col0 15
 *   col1 18
 *   col2 21
 *   col3 24
 *   flat [1][2] = 7
 *   flat_row_sum row1 = 26
 */
#include <stdio.h>

/* Shape 1: classic. The column count MUST be a literal (or macro) —
 * the compiler needs it to compute the stride between rows. */
static int row_sum(const double a[3][4], int row)
{
    int sum = 0;
    for (int c = 0; c < 4; c++) {
        sum += (int)a[row][c];
    }
    return sum;
}

/* Same type spelled explicitly: a is a POINTER to an array of 4 doubles.
 * (a + 1) therefore skips 4 doubles, i.e. one full row. */
static double first_of_row2(const double (*a)[4])
{
    return a[1][0];  /* == (* (a + 1) )[0] */
}

/* Shape 2: flat array for dynamically-sized grids. The row count is
 * passed at runtime; indexing is manual: flat[row * cols + col]. */
static int flat_row_sum(const double *flat, int cols, int row)
{
    int sum = 0;
    for (int c = 0; c < cols; c++) {
        sum += (int)flat[row * cols + c];
    }
    return sum;
}

int main(void)
{
    double grid[3][4] = {
        { 1, 2, 3, 4 },
        { 5, 6, 7, 8 },
        { 9, 10, 11, 12 },
    };

    /* The 2D array is not "copied" — it decays to a pointer to its
     * first row. The whole grid lives in one contiguous block. */
    printf("row0sum %d  row1sum %d  row2sum %d\n",
           row_sum(grid, 0), row_sum(grid, 1), row_sum(grid, 2));
    printf("first_of_row2 = %g\n", first_of_row2(grid));

    /* Column sums: a[i] (row i) itself decays to double* when indexed. */
    for (int c = 0; c < 4; c++) {
        int s = 0;
        for (int r = 0; r < 3; r++) {
            s += (int)grid[r][c];
        }
        printf("col%d %d\n", c, s);
    }

    /* Shape 2: the SAME memory viewed flat. &grid[0][0] has type
     * double* and walks the whole block in row-major order. */
    const double *flat = &grid[0][0];
    printf("flat [1][2] = %d\n", (int)flat[1 * 4 + 2]);
    printf("flat_row_sum row1 = %d\n", flat_row_sum(flat, 4, 1));

    return 0;
}
