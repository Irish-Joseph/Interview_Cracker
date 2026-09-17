/*
 * Topic: Reading and writing text files with fopen, fgets, fprintf and fclose.
 *
 * Concepts:
 * - fopen modes: "w" truncates, "a" appends, "r" reads
 * - Checking EVERY call that can fail, and using perror/errno to say why
 * - fgets vs gets: fgets takes a buffer size, so it cannot overflow
 * - Detecting a line that was longer than the buffer
 * - Telling end-of-file apart from a read error (feof vs ferror)
 * - Always fclose, including on the error paths
 *
 * Example output:
 *   wrote 4 lines to notes.txt
 *   1: alpha,3
 *   2: beta,7
 *   3: gamma,1
 *   4: delta,9
 *   read 4 lines, 8 fields total
 *   appended 1 line; file now has 5 lines
 *   expected failure: No such file or directory
 *
 * Compile: gcc -Wall -Wextra -std=c11 read_write_text_file.c -o demo && ./demo
 *
 * NOTE: validated by inspection (no C compiler on authoring host).
 */
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_MAX_LEN 256
#define DEMO_PATH "notes.txt"

/*
 * Write lines to path, one per line.
 *
 * Returns the number of lines written, or -1 on failure. Note that fclose
 * itself can fail: buffered data is flushed there, so a full disk is often
 * only reported by fclose, never by fprintf.
 */
static int write_lines(const char *path, const char *const *lines, int count) {
    FILE *file = fopen(path, "w");  /* "w" truncates an existing file */
    if (file == NULL) {
        /* perror prints the message for errno after the given prefix. */
        perror("fopen for writing");
        return -1;
    }

    for (int i = 0; i < count; i++) {
        if (fprintf(file, "%s\n", lines[i]) < 0) {
            fprintf(stderr, "write failed on line %d: %s\n", i + 1, strerror(errno));
            fclose(file);  /* close even on the error path */
            return -1;
        }
    }

    if (fclose(file) != 0) {
        perror("fclose after writing");
        return -1;
    }
    return count;
}

/*
 * Read path line by line, printing each one and counting comma-separated
 * fields. Returns the number of lines read, or -1 on failure.
 */
static int read_lines(const char *path, int *fields_out) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        perror("fopen for reading");
        return -1;
    }

    char buffer[LINE_MAX_LEN];
    int line_no = 0;
    int fields = 0;

    /* fgets stops at a newline, at size-1 characters, or at EOF, and always
     * NUL-terminates. It returns NULL at EOF *and* on error - hence the
     * ferror check afterwards. */
    while (fgets(buffer, (int)sizeof buffer, file) != NULL) {
        size_t length = strlen(buffer);

        if (length > 0 && buffer[length - 1] == '\n') {
            buffer[length - 1] = '\0';  /* strip the newline fgets kept */
        } else if (!feof(file)) {
            /* No newline and not at EOF means the line did not fit. */
            fprintf(stderr, "line %d longer than %d bytes, truncated\n",
                    line_no + 1, LINE_MAX_LEN - 1);
        }

        line_no++;
        printf("%d: %s\n", line_no, buffer);

        fields++;  /* n commas separate n+1 fields */
        for (const char *cursor = buffer; *cursor != '\0'; cursor++) {
            if (*cursor == ',') {
                fields++;
            }
        }
    }

    bool failed = ferror(file) != 0;
    if (failed) {
        perror("reading");
    }
    fclose(file);

    if (failed) {
        return -1;
    }
    *fields_out = fields;
    return line_no;
}

/* Append one line without touching the existing contents. */
static bool append_line(const char *path, const char *line) {
    FILE *file = fopen(path, "a");  /* "a" always writes at the end */
    if (file == NULL) {
        perror("fopen for appending");
        return false;
    }
    bool ok = fprintf(file, "%s\n", line) >= 0;
    if (fclose(file) != 0) {
        perror("fclose after appending");
        ok = false;
    }
    return ok;
}

/* Count lines without loading the file into memory: read one char at a time. */
static long count_lines(const char *path) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        perror("fopen for counting");
        return -1;
    }

    long lines = 0;
    int ch;
    /* getc returns int, not char, so EOF (-1) stays distinguishable from a
     * valid byte 0xFF. Storing it in a char is a classic bug. */
    while ((ch = getc(file)) != EOF) {
        if (ch == '\n') {
            lines++;
        }
    }

    bool failed = ferror(file) != 0;
    fclose(file);
    return failed ? -1 : lines;
}

int main(void) {
    const char *const rows[] = {"alpha,3", "beta,7", "gamma,1", "delta,9"};
    const int row_count = (int)(sizeof rows / sizeof rows[0]);

    int written = write_lines(DEMO_PATH, rows, row_count);
    if (written < 0) {
        return EXIT_FAILURE;
    }
    printf("wrote %d lines to %s\n", written, DEMO_PATH);

    int fields = 0;
    int lines_read = read_lines(DEMO_PATH, &fields);
    if (lines_read < 0) {
        return EXIT_FAILURE;
    }
    printf("read %d lines, %d fields total\n", lines_read, fields);

    if (!append_line(DEMO_PATH, "epsilon,2")) {
        return EXIT_FAILURE;
    }
    long total = count_lines(DEMO_PATH);
    if (total < 0) {
        return EXIT_FAILURE;
    }
    printf("appended 1 line; file now has %ld lines\n", total);

    /* Opening a file that does not exist is a normal, recoverable situation -
     * not a crash. errno explains it. */
    FILE *missing = fopen("does_not_exist.txt", "r");
    if (missing == NULL) {
        printf("expected failure: %s\n", strerror(errno));
    } else {
        fclose(missing);
    }

    if (remove(DEMO_PATH) != 0) {
        perror("remove");  /* tidy up the demo file */
    }
    return EXIT_SUCCESS;
}
