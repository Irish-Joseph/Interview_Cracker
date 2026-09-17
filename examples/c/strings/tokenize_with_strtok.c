/*
 * Topic: Splitting strings in C — strtok, strtok_r and a manual splitter.
 *
 * Concepts:
 * - strtok WRITES to the string: it replaces delimiters with '\0'
 * - Why a string literal must never be passed to strtok
 * - The hidden static state, and why strtok is not reentrant
 * - strtok_r (POSIX) / strtok_s (C11 Annex K) with an explicit save pointer
 * - Consecutive delimiters are collapsed — a problem for CSV fields
 * - A manual splitter with strcspn when empty fields must survive
 * - Copying a token safely with snprintf
 *
 * The essential picture. Given "a,b" strtok turns the buffer into:
 *
 *     before:  a  ,  b  \0
 *     after:   a \0  b  \0
 *              ^      ^
 *              |      second call returns this
 *              first call returns this
 *
 * The returned pointers point INTO the original buffer. Nothing is
 * allocated, so nothing needs freeing — but the buffer must outlive
 * every token, and it has been modified in place.
 *
 * Time Complexity: O(n) over the whole string
 *
 * Compile:  gcc -Wall -Wextra -std=c99 -o tokenize tokenize_with_strtok.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

/* strtok_r is POSIX, not ISO C: ask for it before including <string.h>
 * so it stays declared under a strict -std=c99 build. */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <string.h>

#define MAX_FIELDS 16
#define FIELD_LEN 32

/* ---------------------------------------------------------------
 * 1. strtok: the classic, with its two big caveats
 * --------------------------------------------------------------- */
static void demo_strtok(void)
{
    /* MUST be a modifiable array. `char *line = "a,b";` would be a
     * string literal in read-only memory -> undefined behaviour. */
    char line[] = "root:x:0:0:Superuser:/root:/bin/bash";

    printf("1. strtok on: %s\n", line);

    /* First call takes the string, later calls take NULL to mean
     * "continue where you left off" (that state is a hidden static). */
    int index = 0;
    for (char *token = strtok(line, ":"); token != NULL; token = strtok(NULL, ":")) {
        printf("   field %d: %s\n", index++, token);
    }

    /* `line` has been chopped up in place: everything after the first
     * delimiter is now unreachable through `line` itself. */
    printf("   buffer now reads: %s (only the first field remains)\n", line);
}

/* ---------------------------------------------------------------
 * 2. The delimiter-collapsing surprise
 * --------------------------------------------------------------- */
static void demo_empty_fields(void)
{
    char csv[] = "alpha,,gamma,";

    printf("\n2. strtok collapses repeats: %s\n", "alpha,,gamma,");

    int count = 0;
    for (char *token = strtok(csv, ","); token != NULL; token = strtok(NULL, ",")) {
        printf("   token %d: '%s'\n", count++, token);
    }
    /* Prints 2 tokens, not 4: strtok skips runs of delimiters, so the
     * empty field between the commas and the trailing one vanish.
     * For CSV that is data loss — see demo_manual_split. */
    printf("   -> %d tokens (a CSV parser needs 4)\n", count);
}

/* ---------------------------------------------------------------
 * 3. strtok_r: the reentrant version
 * --------------------------------------------------------------- */
static void demo_nested_split(void)
{
    char config[] = "host=localhost;port=8080;debug=true";

    printf("\n3. nested split with strtok_r\n");

    /* Nested strtok loops CANNOT work: the inner loop would clobber the
     * outer loop's hidden state. strtok_r keeps the state in a variable
     * the caller owns, so each loop gets its own. */
    char *outer_save = NULL;
    char *inner_save = NULL;

    for (char *pair = strtok_r(config, ";", &outer_save);
         pair != NULL;
         pair = strtok_r(NULL, ";", &outer_save)) {

        char *key = strtok_r(pair, "=", &inner_save);
        char *value = strtok_r(NULL, "=", &inner_save);

        printf("   %-6s -> %s\n", key ? key : "(none)", value ? value : "(none)");
    }

    /* Portability: strtok_r is POSIX. On MSVC the equivalent is
     * strtok_s(str, delims, &save). A common shim:
     *     #ifdef _WIN32
     *     #define strtok_r strtok_s
     *     #endif                                                     */
}

/* ---------------------------------------------------------------
 * 4. Manual splitting: keeps empty fields, leaves the input intact
 * --------------------------------------------------------------- */

/*
 * Splits `text` on a single delimiter into fixed-size field buffers.
 * Returns the number of fields written (capped at MAX_FIELDS).
 * The source string is NOT modified.
 */
static int manual_split(const char *text, char delim,
                        char fields[][FIELD_LEN], int max_fields)
{
    int count = 0;
    const char *cursor = text;
    const char delim_set[2] = { delim, '\0' };

    while (count < max_fields) {
        /* strcspn returns the length of the run BEFORE the delimiter,
         * or the rest of the string when no delimiter is left. */
        size_t width = strcspn(cursor, delim_set);

        /* snprintf always terminates and never overflows the target;
         * a too-long field is truncated rather than smashing the stack. */
        int needed = snprintf(fields[count], FIELD_LEN, "%.*s", (int)width, cursor);
        if (needed >= FIELD_LEN) {
            printf("   (field %d truncated)\n", count);
        }
        count++;

        cursor += width;
        if (*cursor == '\0') {
            break;      /* consumed the last field */
        }
        cursor++;       /* step over the delimiter and keep going */
    }

    return count;
}

static void demo_manual_split(void)
{
    const char *csv = "alpha,,gamma,";
    char fields[MAX_FIELDS][FIELD_LEN];

    printf("\n4. manual split keeps empty fields: %s\n", csv);

    int count = manual_split(csv, ',', fields, MAX_FIELDS);
    for (int i = 0; i < count; i++) {
        printf("   field %d: '%s'\n", i, fields[i]);
    }
    printf("   -> %d fields, and the source is untouched: %s\n", count, csv);
}

/* ---------------------------------------------------------------
 * 5. Counting words: strtok with a multi-character delimiter set
 * --------------------------------------------------------------- */
static void demo_word_count(void)
{
    char sentence[] = "  the quick\tbrown   fox\njumps  ";
    const char *whitespace = " \t\n\r";

    printf("\n5. word count with a delimiter SET\n");

    /* Every character in the set is a delimiter, and here the collapsing
     * behaviour is exactly what we want: runs of spaces are one break. */
    int words = 0;
    for (char *word = strtok(sentence, whitespace);
         word != NULL;
         word = strtok(NULL, whitespace)) {
        printf("   %d: %s\n", ++words, word);
    }
    printf("   -> %d words\n", words);
}

int main(void)
{
    demo_strtok();
    demo_empty_fields();
    demo_nested_split();
    demo_manual_split();
    demo_word_count();

    /*
     * Choosing a splitter:
     *   strtok      quick one-off parsing of a buffer you own, single thread
     *   strtok_r    anything nested, reentrant, threaded, or library code
     *   strcspn     when empty fields matter or the input must stay const
     *
     * And never: strtok on a string literal, on shared data, or while
     * another strtok loop is still running.
     */
    return 0;
}
