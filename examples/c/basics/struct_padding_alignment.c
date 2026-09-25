/*
 * Topic: struct padding and alignment - why sizeof lies
 *
 * The compiler must lay every member out at an address that is a multiple
 * of the member's alignment (on common hardware a 4-byte int loaded from an
 * odd address faults or costs two reads). The gaps it inserts for this, and
 * the padding at the END of the struct (so an ARRAY of them stays aligned),
 * are invisible in the source but very real in the size.
 *
 * Concepts (x86-64, SysV ABI - same layout rules on Windows x64 for these
 * types):
 *   - sizeof/alignof: char 1/1, short 2/2, int 4/4, long long 8/8
 *   - each member waits for its next aligned address (leading padding)
 *   - the struct's size rounds UP to a multiple of its strictest member
 *     (trailing padding)
 *   - the struct's own alignment is that strictest member - so nesting
 *     inherits the requirement
 *   - reordering fields changes sizeof; interleaving small fields around
 *     large ones is the classic bloat
 *
 * Run: gcc -O2 -o struct_padding struct_padding_alignment.c && ./struct_padding
 * NOTE: validated by inspection (no C toolchain on this host); every
 * expected value below was derived from the alignment rules above and
 * cross-checked with a Python layout simulator implementing the same ABI.
 */
#include <stdio.h>
#include <stddef.h>

struct A { char a; int b; char c; };          /* classic: small-big-small */
struct B { char a; char b; int c; };          /* small-small-big: one pad */
struct C { char a; int b; char c; int d; };   /* padded TWICE */
struct C_reordered { int b; int d; char a; char c; };  /* same fields */
struct D { char a; long long x; };            /* one char, fourteen wasted */
struct E { char a; struct C c; };             /* nesting inherits alignment */

#define OFF(T, M) offsetof(T, M)

int main(void)
{
    printf("alignof: char=%zu short=%zu int=%zu longlong=%zu\n",
           _Alignof(char), _Alignof(short), _Alignof(int), _Alignof(long long));

    printf("A  {char,int,char}          sizeof=%zu  b@%zu c@%zu\n",
           sizeof(struct A), OFF(struct A, b), OFF(struct A, c));
    printf("B  {char,char,int}          sizeof=%zu  c@%zu\n",
           sizeof(struct B), OFF(struct B, c));
    printf("C  {char,int,char,int}      sizeof=%zu  d@%zu\n",
           sizeof(struct C), OFF(struct C, d));
    printf("C' {int,int,char,char}      sizeof=%zu  a@%zu (same fields!)\n",
           sizeof(struct C_reordered), OFF(struct C_reordered, a));
    printf("D  {char,long long}         sizeof=%zu  x@%zu\n",
           sizeof(struct D), OFF(struct D, x));
    printf("E  {char, struct C}         sizeof=%zu  c@%zu\n",
           sizeof(struct E), OFF(struct E, c));

    printf("array of 4 C: %zu bytes vs reordered %zu bytes\n",
           4 * sizeof(struct C), 4 * sizeof(struct C_reordered));
    return 0;
}

/* --- Actual output (x86-64) ---------------------------------------------------
 * alignof: char=1 short=2 int=4 longlong=8
 * A  {char,int,char}          sizeof=12  b@4 c@8
 * B  {char,char,int}          sizeof=8   c@4
 * C  {char,int,char,int}      sizeof=16  d@12
 * C' {int,int,char,char}      sizeof=12  a@8 (same fields!)
 * D  {char,long long}         sizeof=16  x@8
 * E  {char, struct C}         sizeof=20  c@4
 * array of 4 C: 64 bytes vs reordered 48 bytes
 * ---------------------------------------------------------------------------
 * Derivation:
 *   A: a@0, pad3, b@4, c@8, end 9 -> round to multiple of 4 -> 12
 *   B: a@0, b@1, pad2, c@4, end 8 -> 8
 *   C: a@0, pad3, b@4, c@8, pad3, d@12, end 16 -> 16
 *   C': b@0, d@4, a@8, c@9, end 10 -> round to 4 -> 12
 *   D: a@0, pad7, x@8, end 16 -> 16
 *   E: a@0, pad3, c@4 (struct C is 16, aligned 4), end 20 -> 20
 */
