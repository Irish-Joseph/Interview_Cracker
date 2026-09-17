/*
 * Topic: Bit manipulation — set, clear, test and toggle individual bits.
 *
 * Concepts:
 * - Bitwise AND (&), OR (|), XOR (^), NOT (~)
 * - Building a bit mask with (1 << position)
 * - Set / clear / test / toggle a single bit without touching the others
 * - Reading flags packed in one integer (a "flags field")
 *
 * A common real-world use: permission or option flags, e.g.
 *   bit 0 = READ, bit 1 = WRITE, bit 2 = EXECUTE
 *
 * Example output:
 *   start              : 0000000000000000
 *   set READ           : 0000000000000001
 *   set WRITE          : 0000000000000011
 *   test READ          : yes
 *   test EXECUTE       : no
 *   toggle WRITE       : 0000000000000001
 *   clear READ         : 0000000000000000
 */
#include <stdio.h>
#include <stdint.h>

#define READ    (1u << 0)   /* bit 0 */
#define WRITE   (1u << 1)   /* bit 1 */
#define EXECUTE (1u << 2)   /* bit 2 */

static void show(const char *label, uint32_t flags)
{
    /* Print the low 16 bits, most significant first. */
    printf("%-20s : ", label);
    for (int i = 15; i >= 0; i--) {
        printf("%d", (flags >> i) & 1u);
    }
    printf("\n");
}

int main(void)
{
    uint32_t perms = 0;

    show("start", perms);

    /* SET a bit: OR with the mask. Bits already set stay set. */
    perms |= READ;
    show("set READ", perms);

    perms |= WRITE;
    show("set WRITE", perms);

    /* TEST a bit: AND with the mask; result is non-zero if set. */
    printf("test READ          : %s\n", (perms & READ) ? "yes" : "no");
    printf("test EXECUTE       : %s\n", (perms & EXECUTE) ? "yes" : "no");

    /* TOGGLE a bit: XOR with the mask flips exactly that bit. */
    perms ^= WRITE;
    show("toggle WRITE", perms);

    /* CLEAR a bit: AND with the INVERTED mask. */
    perms &= ~READ;
    show("clear READ", perms);

    /* Combining several operations is safe because each mask touches
     * only its own bit — the other bits pass through unchanged. */
    perms = READ | EXECUTE;
    printf("combined READ+EXECUTE set? %s\n",
           (perms & (READ | EXECUTE)) == (READ | EXECUTE) ? "yes" : "no");

    return 0;
}
