/*
 * Topic: enum, union and typedef - naming values, sharing storage, and
 *        shortening declarations.
 *
 * Concepts:
 * - enum gives names to integer constants, and how the values auto-increment
 * - typedef removes the need to write `struct Foo` everywhere
 * - union stores ONE of several members in the SAME memory
 * - sizeof(union) is the largest member, not the sum
 * - The tagged union: an enum tag plus a union payload, which is how C models
 *   "one of these" - the same idea as a Rust enum or a C++ std::variant
 * - Why reading a union member you did not write is a bug
 *
 * Compile: gcc -Wall -Wextra -std=c11 enum_union_typedef.c -o demo && ./demo
 *
 * NOTE: validated by inspection (no C compiler on authoring host).
 */
#include <stdio.h>
#include <string.h>

/* ------------------------------------------------------------------------ */
/* 1. enum                                                                    */
/* ------------------------------------------------------------------------ */

/* Values auto-increment from 0 unless you set them. Here: 0, 1, 2, 3. */
typedef enum {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
} LogLevel;

/* You can assign explicitly; unassigned members continue from the last one.
 * So OK=200, CREATED=201, then NOT_FOUND=404, SERVER_ERROR=500. */
typedef enum {
    HTTP_OK = 200,
    HTTP_CREATED,          /* 201 */
    HTTP_NOT_FOUND = 404,
    HTTP_SERVER_ERROR = 500
} HttpStatus;

/* An enum is just an int, so a lookup table keyed by it is idiomatic.
 * Keep the order in step with the enum - that is the maintenance cost. */
static const char *LEVEL_NAMES[] = {"DEBUG", "INFO", "WARN", "ERROR"};

static const char *level_name(LogLevel level) {
    /* Defensive: an enum variable can legally hold a value outside the list.
     * The cast matters: with no negative members gcc gives this enum an
     * UNSIGNED underlying type, so `level < LOG_DEBUG` would be always-false
     * and -Wextra would say so. One unsigned upper-bound test covers both. */
    if ((unsigned) level > (unsigned) LOG_ERROR) {
        return "UNKNOWN";
    }
    return LEVEL_NAMES[level];
}

/* ------------------------------------------------------------------------ */
/* 2. typedef with struct                                                     */
/* ------------------------------------------------------------------------ */

/* Without the typedef you would write `struct Point p;` at every use.
 * With it, `Point p;` is enough. */
typedef struct {
    int x;
    int y;
} Point;

/* ------------------------------------------------------------------------ */
/* 3. union - one block of memory, several interpretations                    */
/* ------------------------------------------------------------------------ */

typedef union {
    int as_int;
    float as_float;
    char as_bytes[4];
} Word;

/* ------------------------------------------------------------------------ */
/* 4. The tagged union: the safe way to use one                               */
/* ------------------------------------------------------------------------ */

typedef enum {
    VALUE_INT,
    VALUE_DOUBLE,
    VALUE_TEXT
} ValueKind;

typedef struct {
    ValueKind kind;            /* the TAG: which member is currently valid */
    union {
        long integer;
        double number;
        char text[32];
    } data;                    /* the PAYLOAD */
} Value;

static Value make_int(long v) {
    Value value;
    value.kind = VALUE_INT;
    value.data.integer = v;
    return value;
}

static Value make_double(double v) {
    Value value;
    value.kind = VALUE_DOUBLE;
    value.data.number = v;
    return value;
}

static Value make_text(const char *v) {
    Value value;
    value.kind = VALUE_TEXT;
    /* strncpy does not always NUL-terminate, so terminate explicitly. */
    strncpy(value.data.text, v, sizeof value.data.text - 1);
    value.data.text[sizeof value.data.text - 1] = '\0';
    return value;
}

/* Always switch on the TAG. Reading the wrong member is undefined behaviour
 * in principle and garbage in practice - the compiler cannot catch it. */
static void print_value(const Value *value) {
    switch (value->kind) {
        case VALUE_INT:
            printf("  int    %ld\n", value->data.integer);
            break;
        case VALUE_DOUBLE:
            printf("  double %.2f\n", value->data.number);
            break;
        case VALUE_TEXT:
            printf("  text   \"%s\"\n", value->data.text);
            break;
        default:
            printf("  <unknown kind>\n");
            break;
    }
}

int main(void) {
    printf("-- enum --\n");
    LogLevel level = LOG_WARN;
    printf("  LOG_WARN  = %d (%s)\n", level, level_name(level));
    printf("  LOG_ERROR = %d (%s)\n", LOG_ERROR, level_name(LOG_ERROR));

    for (LogLevel l = LOG_DEBUG; l <= LOG_ERROR; l++) {
        printf("  %d -> %s\n", l, level_name(l));
    }

    printf("  HTTP_OK=%d HTTP_CREATED=%d HTTP_NOT_FOUND=%d\n",
           HTTP_OK, HTTP_CREATED, HTTP_NOT_FOUND);

    /* An enum is an int: nothing stops an out-of-range value. C enums are
     * NOT the type-safe sum types of newer languages. */
    LogLevel bogus = (LogLevel) 99;
    printf("  out-of-range enum: %d -> %s\n", bogus, level_name(bogus));

    printf("-- typedef --\n");
    Point origin = {0, 0};
    Point target = {.x = 3, .y = 4};     /* designated initialisers, C99+ */
    printf("  origin (%d, %d), target (%d, %d)\n",
           origin.x, origin.y, target.x, target.y);
    printf("  sizeof(Point) = %zu\n", sizeof(Point));

    printf("-- union shares storage --\n");
    Word word;
    word.as_int = 0;
    word.as_float = 1.0f;                /* writing one member overwrites all */
    printf("  after as_float = 1.0f, as_int reads %d\n", word.as_int);
    printf("  (that is the SAME bits reinterpreted, not a conversion)\n");

    word.as_int = 0x41424344;            /* 'A','B','C','D' */
    printf("  as_int = 0x%X, bytes =", word.as_int);
    for (size_t i = 0; i < sizeof word.as_bytes; i++) {
        printf(" %c", word.as_bytes[i]);
    }
    printf("  <- order depends on endianness\n");

    printf("  sizeof(int)=%zu float=%zu char[4]=%zu  =>  sizeof(Word)=%zu\n",
           sizeof(int), sizeof(float), sizeof(char[4]), sizeof(Word));
    printf("  a union is as big as its LARGEST member, not the sum\n");

    printf("-- tagged union --\n");
    Value values[] = {
        make_int(42),
        make_double(3.14159),
        make_text("hello, tagged union"),
    };
    const size_t count = sizeof values / sizeof values[0];

    for (size_t i = 0; i < count; i++) {
        print_value(&values[i]);
    }

    printf("  sizeof(Value) = %zu (tag + largest payload + padding)\n",
           sizeof(Value));

    printf("-- why the tag matters --\n");
    Value v = make_int(1078530011);
    printf("  stored as int: %ld\n", v.data.integer);
    printf("  read as double WITHOUT checking the tag: %g\n", v.data.number);
    printf("  ^ meaningless: those bits were never a double\n");

    return 0;
}

/* Expected output (sizes are typical for a 64-bit build):
-- enum --
  LOG_WARN  = 2 (WARN)
  LOG_ERROR = 3 (ERROR)
  0 -> DEBUG
  1 -> INFO
  2 -> WARN
  3 -> ERROR
  HTTP_OK=200 HTTP_CREATED=201 HTTP_NOT_FOUND=404
  out-of-range enum: 99 -> UNKNOWN
-- typedef --
  origin (0, 0), target (3, 4)
  sizeof(Point) = 8
-- union shares storage --
  after as_float = 1.0f, as_int reads 1065353216
  (that is the SAME bits reinterpreted, not a conversion)
  as_int = 0x41424344, bytes = D C B A  <- little-endian x86
  sizeof(int)=4 float=4 char[4]=4  =>  sizeof(Word)=4
  a union is as big as its LARGEST member, not the sum
-- tagged union --
  int    42
  double 3.14
  text   "hello, tagged union"
  sizeof(Value) = 40 (tag + largest payload + padding)
*/
