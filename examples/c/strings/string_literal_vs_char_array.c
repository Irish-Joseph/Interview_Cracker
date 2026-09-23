/*
 * Topic: "abc" vs {'a','b','c','\0'} - a string literal is not a char array
 *
 * The most common C "why is my code crashing" confusion: the difference
 * between a string literal and a character array, and where each one lives.
 *
 * Concepts:
 *   - "abc" is a string literal of type "array of 4 const char" (the '\0'
 *     counts in sizeof). Its storage is usually in a read-only section.
 *   - {'a','b','c','\0'} (or a char s[] = "abc") is a real, writable array
 *     - typically on the stack for locals, in .bss/.data for statics.
 *   - char *p = "abc"; makes p writable-looking but the POINTS AT literal is
 *     not: p[0] = 'X' is undefined behaviour (it works on many old systems
 *     and fails on modern ones with a segfault - the classic "it worked on
 *     my machine" bug).
 *   - char s[] = "abc"; copies the literal into a new array you own.
 *   - String "concatenation" at compile time: "foo " "bar" is "foo bar"
 *     (adjacent literals merge), which is why long strings get split.
 *   - sizeof("abc") is 4, strlen("abc") is 3 - the NUL is real storage.
 *
 * Compile: cc -Wall -o literal_vs_array literal_vs_array.c
 * NOTE: validated by inspection (no C toolchain on this host); the expected
 * output uses only sizeof/strlen on fixed literals, so every number below is
 * computed, and the mutation cases are the two legal ones plus the UB one
 * shown commented out (never "demonstrating" UB by running it).
 */
#include <stdio.h>
#include <string.h>

int main(void)
{
    /* The literal: read-only storage, type "const char[4]" */
    printf("sizeof(\"abc\")      = %zu   (the NUL counts)\n", sizeof("abc"));
    printf("strlen(\"abc\")      = %zu   (stops at the NUL)\n", strlen("abc"));

    /* char *p = "abc";   p points AT the literal.
     * p[0] = 'X';        <- UNDEFINED BEHAVIOUR: writing to a literal.
     * Commented out on purpose: it may "work" on an old toolchain and segfault
     * on a modern one, which is exactly why it must be learned, not tried. */

    /* char s[] = "abc";  copies the literal into a writable array you own. */
    char s[] = "abc";
    printf("sizeof(s)          = %zu\n", sizeof(s));
    s[0] = 'X';                         /* legal: s is your storage */
    printf("after s[0]='X': %s\n", s);

    /* The brace-initialised form is the same object, spelled out. */
    char t[] = {'a', 'b', 'c', '\0'};
    printf("t (explicit NUL)   = %s\n", t);
    t[1] = 'B';
    printf("after t[1]='B': %s\n", t);

    /* An array WITHOUT a terminator is not a string - strlen would wander. */
    char three[3] = {'x', 'y', 'z'};
    printf("sizeof(three)      = %zu   (no NUL: not a string)\n", sizeof(three));
    printf("three[0..2]        = %c%c%c\n", three[0], three[1], three[2]);

    /* Adjacent literals merge at COMPILE time: one literal, one NUL. */
    long_string:
    {
        const char *msg = "this is a long "
                          "enough line to "
                          "be worth splitting";
        printf("merged literal len = %zu\n", strlen(msg));
    }

    return 0;
}

/*
 * Expected output:
 *
 * sizeof("abc")      = 4   (the NUL counts)
 * strlen("abc")      = 3   (stops at the NUL)
 * sizeof(s)          = 4
 * after s[0]='X': Xbc
 * t (explicit NUL)   = abc
 * after t[1]='B': aBc
 * sizeof(three)      = 3   (no NUL: not a string)
 * three[0..2]        = xyz
 * merged literal len = 48
 */
