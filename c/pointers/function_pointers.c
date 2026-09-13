/*
 * Topic: Function pointers — passing behavior as a value.
 *
 * Concepts:
 * - The function-pointer type syntax: int (*f)(int, int)
 * - typedef to make it readable
 * - Calling through a pointer: (*f)(a, b)  ==  f(a, b)
 * - Function-pointer parameters (strategy pattern)
 * - Arrays of function pointers (dispatch tables)
 * - Callbacks: your function, called by someone else's
 *
 * Function pointers are how C achieves "higher-order functions"
 * before that term existed: qsort's comparator, signal handlers,
 * plugin systems — all of them are function pointers.
 *
 * Compile:  gcc -Wall -Wextra -std=c99 -o func_ptr function_pointers.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stddef.h> /* size_t */
#include <stdio.h>

/* --- 1. The raw syntax (ugly but you should read it once) ----------------
 *
 * int (*add)(int, int);
 *      ^^^  read "backwards":
 *      - add is a pointer
 *      - to a function
 *      - taking (int, int)
 *      - returning int
 */

int add(int a, int b)  { return a + b; }
int sub(int a, int b)  { return a - b; }
int mul(int a, int b)  { return a * b; }

/* --- 2. typedef: the same type, readable ---------------------------------- */
typedef int BinaryOp(int, int);

int main(void)
{
    /* Assign function names to pointers. The & is optional:
     * function names decay to pointers automatically. */
    BinaryOp *op = add;
    printf("3 op 4 = %d\n", op(3, 4));        /* -> 7  (add) */
    printf("3 op 4 = %d\n", (*op)(3, 4));     /* -> 7  (same, explicit deref) */

    op = sub;
    printf("3 op 4 = %d\n", op(3, 4));        /* -> -1 */
    op = mul;
    printf("3 op 4 = %d\n", op(3, 4));        /* -> 12 */

    /* --- 3. Strategy parameter: the caller picks the behavior ----------------- */

    /* Compute a running result, choosing the operation at runtime. */
    int fold(int start, int n, BinaryOp *combine)
    {
        int acc = start;
        for (int i = 1; i <= n; i++) {
            acc = combine(acc, i);
        }
        return acc;
    }

    printf("sum     1..5 from 0: %d\n", fold(0, 5, add));  /* -> 15  */
    printf("product 1..5 from 1: %d\n", fold(1, 5, mul));  /* -> 120 */

    /* --- 4. Dispatch table: an array of function pointers --------------------- */

    /* A tiny "calculator": symbol -> function. */
    struct Op {
        char symbol;
        BinaryOp *fn;
    };
    struct Op table[] = {
        { '+', add },
        { '-', sub },
        { '*', mul },
    };

    int x = 10, y = 3;
    for (size_t i = 0; i < sizeof table / sizeof table[0]; i++) {
        if (table[i].symbol == '*') {
            printf("10 %c 3 = %d\n", table[i].symbol,
                   table[i].fn(x, y));      /* -> 10 * 3 = 30 */
        }
    }

    /* --- 5. Callbacks: a library calls YOUR function --------------------------- */

    /* A generic "map over an array" — the operation is a callback. */
    void transform(int *data, size_t n, void (*fn)(int *))
    {
        for (size_t i = 0; i < n; i++) {
            fn(&data[i]);   /* hand each element's address to the callback */
        }
    }

    /* Our specific callbacks: */
    void double_it(int *v)  { *v *= 2; }
    void clamp_zero(int *v) { if (*v < 0) *v = 0; }

    int values[] = {1, -2, 3, -4, 5};
    size_t count = sizeof values / sizeof values[0];

    transform(values, count, double_it);
    printf("doubled: ");
    for (size_t i = 0; i < count; i++) printf("%d ", values[i]);
    printf("\n");
    /* -> doubled: 2 -4 6 -8 10 */

    transform(values, count, clamp_zero);
    printf("clamped: ");
    for (size_t i = 0; i < count; i++) printf("%d ", values[i]);
    printf("\n");
    /* -> clamped: 2 0 6 0 10 */

    return 0;
}

/* Expected output:
 *
 * 3 op 4 = 7
 * 3 op 4 = 7
 * 3 op 4 = -1
 * 3 op 4 = 12
 * sum     1..5 from 0: 15
 * product 1..5 from 1: 120
 * 10 * 3 = 30
 * doubled: 2 -4 6 -8 10
 * clamped: 2 0 6 0 10
 */
