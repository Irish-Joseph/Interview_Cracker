/*
Topic: Flexible array members for one-allocation variable-sized structs.
Concepts: sizeof excludes payload, overflow-safe allocation, contiguous data.
Run: cc -std=c11 -Wall -Wextra flexible_array_member.c -o demo && ./demo
NOTE: validated by inspection (no C toolchain on this host).
Expected output: count=4 sum=26
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

struct IntBuffer {
    size_t count;
    int values[]; /* Must be last; contributes zero to sizeof(struct). */
};

static struct IntBuffer *buffer_create(size_t count) {
    if (count > (SIZE_MAX - sizeof(struct IntBuffer)) / sizeof(int)) {
        return NULL; /* Prevent size_t overflow before malloc. */
    }

    size_t bytes = sizeof(struct IntBuffer) + count * sizeof(int);
    struct IntBuffer *buffer = malloc(bytes);
    if (buffer == NULL) {
        return NULL;
    }

    buffer->count = count;
    return buffer;
}

static long sum(const struct IntBuffer *buffer) {
    long total = 0;
    for (size_t i = 0; i < buffer->count; ++i) {
        total += buffer->values[i];
    }
    return total;
}

int main(void) {
    struct IntBuffer *buffer = buffer_create(4);
    if (buffer == NULL) {
        fputs("allocation failed\n", stderr);
        return EXIT_FAILURE;
    }

    int input[] = {5, 6, 7, 8};
    for (size_t i = 0; i < buffer->count; ++i) {
        buffer->values[i] = input[i];
    }

    printf("count=%zu sum=%ld\n", buffer->count, sum(buffer));
    free(buffer); /* Header and payload belong to the same allocation. */
    return EXIT_SUCCESS;
}
