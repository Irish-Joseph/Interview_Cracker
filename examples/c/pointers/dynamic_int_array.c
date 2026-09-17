/*
 * Topic: A growable int array (dynamic array) using malloc/realloc.
 *
 * Concepts:
 * - Heap allocation with malloc / realloc / free
 * - Separating "length" from "capacity"
 * - Geometric (x2) growth for amortized O(1) push
 * - Ownership: exactly one free per allocation
 * - Why realloc can move memory (and the classic temp-variable bug)
 *
 * Amortized analysis: the array doubles when full, so over n pushes
 * the total work copying elements is 1+2+4+...+n < 2n, i.e. O(n)
 * total -> O(1) average per push.
 *
 * Compile:  gcc -Wall -Wextra -o dynamic_array dynamic_int_array.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;      /* backing storage on the heap        */
    size_t length;  /* number of elements actually stored */
    size_t capacity;/* number of elements data[] can hold */
} IntArray;

/* Creates an empty array with initial capacity 4. */
static IntArray int_array_new(void)
{
    IntArray arr;
    arr.data = malloc(4 * sizeof(int));
    if (arr.data == NULL) {
        fprintf(stderr, "malloc failed\n");
        exit(1);
    }
    arr.length = 0;
    arr.capacity = 4;
    return arr;
}

/* Appends value, growing the buffer (x2) when full. */
static void int_array_push(IntArray *arr, int value)
{
    if (arr->length == arr->capacity) {
        size_t new_capacity = arr->capacity * 2;
        int *grown = realloc(arr->data, new_capacity * sizeof(int));
        if (grown == NULL) {
            /* Original block is still valid on realloc failure. */
            fprintf(stderr, "realloc failed\n");
            exit(1);
        }
        arr->data = grown;         /* may be a DIFFERENT address */
        arr->capacity = new_capacity;
    }
    arr->data[arr->length++] = value;
}

/* Frees the backing storage and zeroes the struct. */
static void int_array_free(IntArray *arr)
{
    free(arr->data);
    arr->data = NULL;
    arr->length = 0;
    arr->capacity = 0;
}

int main(void)
{
    IntArray numbers = int_array_new();

    /* Push 10 values: forces growth 4 -> 8 -> 16. */
    for (int i = 1; i <= 10; i++) {
        int_array_push(&numbers, i * i);   /* squares: 1 4 9 ... 100 */
    }

    printf("length=%zu capacity=%zu\n", numbers.length, numbers.capacity);
    /* -> length=10 capacity=16 */

    for (size_t i = 0; i < numbers.length; i++) {
        printf("%d ", numbers.data[i]);
    }
    printf("\n");
    /* -> 1 4 9 16 25 36 49 64 81 100 */

    int_array_free(&numbers);
    return 0;
}

/*
 * The classic realloc bug this example avoids:
 *
 *     arr->data = realloc(arr->data, new_size);
 *
 * looks safe, but if realloc FAILS it returns NULL and the pointer
 * to the OLD block is overwritten — a memory leak. The safe pattern
 * is always to use a temporary variable first:
 *
 *     int *grown = realloc(arr->data, new_size);
 *     if (grown == NULL) { /* handle error, old block intact */ }
 *     arr->data = grown;
 */
