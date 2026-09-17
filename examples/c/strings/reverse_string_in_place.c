/*
 * Topic: Reverse a null-terminated string in place using pointers.
 *
 * Concepts:
 * - Pointer arithmetic (s + i, *(s + i) == s[i])
 * - The C string layout: chars + terminating '\0'
 * - Two-pointer in-place swap
 * - strlen() vs manual length scan
 *
 * The algorithm:
 *   1. Find the last character (the '\0' one position before).
 *   2. Walk two pointers inward, swapping, until they meet.
 *
 * Time Complexity: O(n)
 * Space Complexity: O(1) — no extra buffer needed
 *
 * Compile:  gcc -Wall -Wextra -o reverse_string reverse_string_in_place.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stddef.h> /* size_t */
#include <stdio.h>

/* Returns the number of characters before the '\0'. */
static size_t string_length(const char *s)
{
    size_t length = 0;
    while (s[length] != '\0') {
        length++;
    }
    return length;
}

/*
 * Reverses s in place.
 *
 * Uses pure pointer arithmetic (no array-subscript syntax) to make
 * the mechanics explicit:
 *   - left  points at the first character
 *   - right points at the last character
 *   - each step swaps *left and *right, then moves inward.
 */
static void reverse_string(char *s)
{
    char *left = s;                 /* first character          */
    char *right = s + string_length(s) - 1;  /* last character  */

    while (left < right) {
        char temp = *left;
        *left = *right;
        *right = temp;
        left++;
        right--;
    }
    /* No need to touch '\0': it stays at the original end, which is
     * still the end after an in-place reversal. */
}

int main(void)
{
    /* A buffer (not a string literal — literals may be read-only). */
    char message[] = "Daily Code Learning";
    char palindrome[] = "level";
    char empty[] = "";
    char single[] = "a";

    printf("before: %-20s | after: ", message, message);
    reverse_string(message);
    printf("%s\n", message);

    printf("before: %-20s | after: ", palindrome, palindrome);
    reverse_string(palindrome);
    printf("%s\n", palindrome);

    printf("before: %-20s | after: ", empty, empty);
    reverse_string(empty);
    printf("[%s]\n", empty);

    printf("before: %-20s | after: ", single, single);
    reverse_string(single);
    printf("%s\n", single);

    return 0;
}

/* Expected output:
 *
 * before: Daily Code Learning  | after: gninrael eodC yliaD
 * before: level                | after: level
 * before:                      | after: []
 * before: a                    | after: a
 */
