/*
 * Topic: Structs in C — definition, initialization and operations.
 *
 * Concepts:
 * - Defining a struct type
 * - Designated initializers (C99)
 * - Accessing members with the . and -> operators
 * - Structs by value vs. through pointers
 * - A small struct-based "record" with helper functions
 *
 * A struct bundles related values into one named type — C's basic
 * unit of data modeling. Functions either take structs by value
 * (a copy) or by pointer (shared, use ->).
 *
 * Compile:  gcc -Wall -Wextra -std=c99 -o person_ops person_structs.c
 *
 * NOTE: validated by inspection (no C toolchain on authoring host).
 */

#include <stdio.h>
#include <string.h>

typedef struct {
    char first[32];
    char last[32];
    int  age;
} Person;

/* By value: p is a COPY. Mutations do not affect the caller. */
static void print_person_by_value(Person p)
{
    printf("  (by value)    %s %s, age %d\n", p.first, p.last, p.age);
}

/* By pointer: shared. The idiomatic choice for big structs —
 * avoids copying, and allows mutation via the -> operator. */
static void print_person_by_pointer(const Person *p)
{
    printf("  (by pointer)  %s %s, age %d\n", p->first, p->last, p->age);
}

/* Helper: full name length, showing dot/arrow on each access style. */
static size_t full_name_length(const Person *p)
{
    /* . works on a local copy; -> works on the pointer. Both are
     * the same access, different syntax for the same thing. */
    Person local = *p;               /* copy out of the pointer */
    return strlen(local.first) + 1 + strlen(p->last);
}

/* Age-up in place via pointer. */
static void birthday(Person *p)
{
    p->age++;
}

int main(void)
{
    /* C99 designated initializers: set fields by name, any order. */
    Person alice = {
        .age  = 30,
        .first = "Alice",
        .last  = "Smith",
    };

    /* Plain positional initializer (also valid). */
    Person bob = { "Bob", "Jones", 25 };

    print_person_by_value(alice);
    print_person_by_pointer(&alice);

    /* Mutate through the pointer; both views now see the change. */
    birthday(&alice);
    print_person_by_pointer(&alice);

    printf("alice's full name is %zu chars (incl. space)\n",
           full_name_length(&alice));
    /* "Alice Smith" -> 11 */

    printf("bob: %s %s, age %d\n", bob.first, bob.last, bob.age);

    /* Struct copy: assignment copies the whole struct (shallow). */
    Person bob_copy = bob;
    bob_copy.age = 99;
    printf("after copying bob and bumping the copy:\n");
    printf("  bob      age=%d\n", bob.age);       /* 25, unchanged */
    printf("  bob_copy age=%d\n", bob_copy.age);  /* 99 */

    return 0;
}

/* Expected output:
 *
 *   (by value)    Alice Smith, age 30
 *   (by pointer)  Alice Smith, age 30
 *   (by pointer)  Alice Smith, age 31
 * alice's full name is 11 chars (incl. space)
 * bob: Bob Jones, age 25
 * after copying bob and bumping the copy:
 *   bob      age=25
 *   bob_copy age=99
 */
