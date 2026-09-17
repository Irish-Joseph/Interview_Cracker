/*
 * Topic: Reading command-line arguments with argc and argv.
 *
 * Concepts:
 * - What argc counts, and why argv[0] is the program name, not the first option
 * - argv is NULL-terminated: argv[argc] == NULL
 * - Parsing flags (-v), options with values (-n 5) and positional arguments
 * - Converting text to numbers SAFELY with strtol, not atoi
 * - Reporting usage and returning a non-zero exit code on bad input
 *
 * Why not atoi: atoi("abc") returns 0 with no way to tell it apart from
 * atoi("0"), and overflow is undefined behaviour. strtol reports both.
 *
 * Example session:
 *   $ ./demo
 *   usage: demo [-v] [-n COUNT] NAME...
 *
 *   $ ./demo -v -n 3 alpha beta
 *   verbose: on
 *   count:   3
 *   names:   2
 *     [0] alpha
 *     [1] beta
 *     repeat 1: alpha beta
 *     repeat 2: alpha beta
 *     repeat 3: alpha beta
 *
 *   $ ./demo -n oops alpha
 *   error: -n expects a number, got "oops"
 *
 * Compile: gcc -Wall -Wextra -std=c11 command_line_arguments.c -o demo
 *
 * NOTE: validated by inspection (no C compiler on authoring host).
 */
#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Parse a whole number from text.
 *
 * Returns true on success and writes the value to *out. strtol tells us
 * three things atoi cannot: where parsing stopped, whether anything was
 * parsed at all, and whether the value overflowed.
 */
static bool parse_int(const char *text, long *out) {
    errno = 0;
    char *end = NULL;
    long value = strtol(text, &end, 10);

    if (end == text) {
        return false;          /* no digits at all */
    }
    if (*end != '\0') {
        return false;          /* trailing junk, e.g. "12abc" */
    }
    if (errno == ERANGE || value < INT_MIN || value > INT_MAX) {
        return false;          /* out of range */
    }

    *out = value;
    return true;
}

static void print_usage(const char *program) {
    fprintf(stderr, "usage: %s [-v] [-n COUNT] NAME...\n", program);
}

int main(int argc, char *argv[]) {
    /* argc counts the program name too, so "./demo -v" gives argc == 2.
     * argv[0] is the program name as invoked; argv[argc] is guaranteed NULL. */
    const char *program = (argc > 0 && argv[0] != NULL) ? argv[0] : "demo";

    bool verbose = false;
    long count = 1;

    int index = 1;             /* start at 1: skip the program name */
    for (; index < argc; index++) {
        const char *arg = argv[index];

        if (strcmp(arg, "--") == 0) {
            index++;           /* everything after "--" is positional */
            break;
        }
        if (arg[0] != '-' || arg[1] == '\0') {
            break;             /* not a flag (a lone "-" means stdin) */
        }

        if (strcmp(arg, "-v") == 0) {
            verbose = true;
        } else if (strcmp(arg, "-n") == 0) {
            /* An option that takes a value must check the value EXISTS. */
            if (index + 1 >= argc) {
                fprintf(stderr, "error: -n requires a value\n");
                print_usage(program);
                return EXIT_FAILURE;
            }
            if (!parse_int(argv[++index], &count) || count < 1) {
                fprintf(stderr, "error: -n expects a number, got \"%s\"\n",
                        argv[index]);
                return EXIT_FAILURE;
            }
        } else {
            fprintf(stderr, "error: unknown option \"%s\"\n", arg);
            print_usage(program);
            return EXIT_FAILURE;
        }
    }

    int name_count = argc - index;
    if (name_count <= 0) {
        print_usage(program);
        return EXIT_FAILURE;
    }

    printf("verbose: %s\n", verbose ? "on" : "off");
    printf("count:   %ld\n", count);
    printf("names:   %d\n", name_count);

    for (int i = 0; i < name_count; i++) {
        printf("  [%d] %s\n", i, argv[index + i]);
    }

    for (long repeat = 1; repeat <= count; repeat++) {
        printf("  repeat %ld:", repeat);
        for (int i = 0; i < name_count; i++) {
            printf(" %s", argv[index + i]);
        }
        printf("\n");
    }

    /* Proof that argv is NULL-terminated - this is guaranteed by the standard
     * and is how execv-style functions know where the list ends. */
    if (verbose) {
        printf("argv[%d] is %s\n", argc, argv[argc] == NULL ? "NULL" : "not NULL");
    }

    return EXIT_SUCCESS;
}
