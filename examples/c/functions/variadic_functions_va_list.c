/*
 * Topic: variadic functions - writing your own printf-style code with va_list
 *
 * Concepts:
 *   - A variadic parameter exists at the caller's side; inside the function
 *     there is only a va_list, an opaque cursor into the arguments.
 *     There are no names, no types, no length - you know them from fmt.
 *   - va_start / va_arg / va_end discipline: start after the last named
 *     parameter, read with the right TYPE, end before returning.
 *   - A va_list can only be read forward once. To format the same arguments
 *     twice (measure, then write - the asprintf pattern) use va_copy and
 *     give each list its own va_end.
 *   - The compiler cannot check your fmt against your callers the way it
 *     does for printf itself; a %d reading a double is undefined behaviour
 *     and usually "works" on your machine while corrupting silently.
 *
 * Compile: cc -Wall -o variadic variadic_functions_va_list.c
 * NOTE: validated by inspection (no C toolchain on this host); every literal
 * in the expected output below was computed with Python's matching formats.
 *
 */
#include <stdarg.h>
#include <stdio.h>

/* Forward the caller's arguments to the stdio v-variants. Note what is NOT
 * here: no buffer of arguments, no argument count. Only the cursor. */
static void log_line(const char *level, const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);            /* must name the last fixed parameter */

    printf("[%s] ", level);
    vprintf(fmt, args);             /* vprintf: same as printf, takes a va_list */
    printf("\n");

    va_end(args);                   /* required; the object is opaque */
}

/* The measure-then-write pattern (what asprintf does internally):
 * vsnprintf(NULL, 0, ...) returns the length that WOULD be written,
 * without writing. But it consumes `args`, so the second pass needs
 * a fresh copy - and va_copy costs a second va_end. */
static int build(char *out, size_t cap, const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    va_list args2;
    va_copy(args2, args);

    int len = vsnprintf(NULL, 0, fmt, args);   /* pass 1: measure, no output */
    vsnprintf(out, cap, fmt, args2);           /* pass 2: actually fill */

    va_end(args2);
    va_end(args);
    return len;
}

int main(void)
{
    log_line("INFO", "server started on port %d", 8080);
    log_line("WARN", "%d of %d requests failed", 3, 1200);
    log_line("INFO", "pi to two places: %.2f", 3.14159);

    char buffer[64];
    int len = build(buffer, sizeof buffer, "user %s has %d items", "alice", 7);
    printf("build: needed %d bytes, buffer holds \"%s\"\n", len, buffer);

    /* The danger, commented out because it is UNDEFINED BEHAVIOUR, not a
     * feature:
     *     log_line("BUG", "%d", 3.5);
     * %d reads an int-sized value where a double lives. On x86-64 it will
     * usually print garbage, on some platforms it crashes. The compiler can
     * warn about printf itself (via _format attributes) but not about YOUR
     * function - unless you declare it with the matching format attribute:
     *     __attribute__((format(printf, 2, 3))) void log_line(...);
     * With that attribute, the line above becomes a compiler warning.
     */
    return 0;
}

/*
 * Expected output:
 *
 * [INFO] server started on port 8080
 * [WARN] 3 of 1200 requests failed
 * [INFO] pi to two places: 3.14
 * build: needed 22 bytes, buffer holds "user alice has 7 items"
 */
