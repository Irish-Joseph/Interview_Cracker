/*
 * Topic: 2D arrays in C — indexing, pointer traversal and row pointers.
 *
 * Concepts:
 * - How a 2D array is laid out in memory (row-major)
 * - arr[i][j] vs (*(*arr + i) + j): same address, two syntaxes
 * - Passing 2D arrays to functions (row count must be known)
 * - Row pointers: arr[i] is an int* to the row's first element
 * - Column-major iteration and cache behavior (brief note)
 *
 * Memory layout of int grid[3][4]:
 *   [row0: 4 ints] [row1: 4 ints] [row2: 4 ints]
 * grid[i][j] lives at  &grid[0][0] + (i*4 + j)*sizeof(int).
 *
 * Time Complexity: O(rows * cols) for full traversals
 *
 * Compile:  gcc -Wall -Wextra -std=c99 -o grid2d grid_traversal.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stdio.h>

#define ROWS 3
#define COLS 4

/* Pass a 2D array: the first dimension may be elided, the row
 * length (COLS) must be a constant expression the compiler knows. */
static void print_grid(const int grid[ROWS][COLS])
{
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            printf("%3d ", grid[i][j]);
        }
        printf("\n");
    }
}

/* Same traversal written with pure pointer arithmetic.
 *
 * grid            : int (*)[COLS]  (pointer to an array of COLS ints)
 * grid + i        : pointer to row i
 * *(grid + i)     : the row itself, which decays to int*
 * *(grid + i) + j : address of element (i, j)
 * *(*(grid+i)+j)  : the element value
 */
static void print_with_pointers(const int grid[ROWS][COLS])
{
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            printf("%3d ", *(*(grid + i) + j));
        }
        printf("\n");
    }
}

/* Row pointer idiom: each row can be handed around as a plain int*. */
static int row_max(const int grid[ROWS][COLS], int row)
{
    const int *r = grid[row];   /* r points at the row's first element */
    int best = r[0];
    for (int j = 1; j < COLS; j++) {
        if (r[j] > best) best = r[j];
    }
    return best;
}

int main(void)
{
    int grid[ROWS][COLS] = {
        { 1,  5,  2,  8},
        { 9,  3,  7,  4},
        { 6, 10,  1, 11},
    };

    printf("subscript syntax:\n");
    print_grid(grid);

    printf("\npointer syntax (identical values):\n");
    print_with_pointers(grid);

    printf("\nrow maxes:");
    for (int i = 0; i < ROWS; i++) {
        printf(" %d", row_max(grid, i));
    }
    printf("\n");
    /* -> row maxes: 8 9 11 */

    /* Demonstrate the flat address formula directly: */
    int *flat = &grid[0][0];           /* treat the whole array as flat */
    int i = 1, j = 2;
    printf("grid[1][2] via flat offset: %d\n", flat[i * COLS + j]);
    /* -> 7 (same cell, reached the arithmetic way) */

    return 0;
}

/* Expected output:
 *
 * subscript syntax:
 *   1  5  2  8
 *   9  3  7  4
 *   6 10  1 11
 *
 * pointer syntax (identical values):
 *   1  5  2  8
 *   9  3  7  4
 *   6 10  1 11
 *
 * row maxes: 8 9 11
 * grid[1][2] via flat offset: 7
 */
