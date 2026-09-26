/*
Topic: restrict pointers as an optimization contract, not a runtime check.
Concepts: non-aliasing promise, undefined behavior on violation, vectorization.
Run: cc -std=c11 -O2 -Wall restrict_aliasing_contract.c -o demo && ./demo
NOTE: validated by inspection (no C toolchain on this host).
Expected output: 11 22 33 44
*/

#include <stddef.h>
#include <stdio.h>

void add_arrays(size_t count,
                const int *restrict left,
                const int *restrict right,
                int *restrict output) {
    for (size_t i = 0; i < count; ++i) {
        output[i] = left[i] + right[i];
    }
}

int main(void) {
    const int left[] = {1, 2, 3, 4};
    const int right[] = {10, 20, 30, 40};
    int output[4] = {0};

    add_arrays(4, left, right, output);
    for (size_t i = 0; i < 4; ++i) {
        printf("%d%s", output[i], i == 3 ? "\n" : " ");
    }

    // Passing `output` as both an input and output would violate this
    // function's restrict contract. The compiler does not diagnose it; the
    // resulting behavior is undefined because optimization assumes no alias.
    return 0;
}
