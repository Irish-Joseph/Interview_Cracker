# C Interview Questions

---

### 🟢 Q. `malloc`, `calloc`, `realloc` — what does each one do, and what do
they initialize?

**Answer.** `malloc(n)` allocates `n` bytes and returns a suitably aligned
pointer, or NULL — the bytes are **uninitialized** (indeterminate values).
`calloc(n, size)` allocates `n * size` bytes and **zero-fills** them.
`realloc(p, n)` resizes the block pointed to by `p` to `n` bytes, moving it if
necessary, and returns the (possibly new) pointer — `realloc(NULL, n)` is the
same as `malloc(n)`, and `realloc(p, 0)` is implementation-defined.

The follow-ups:

- Check every allocation for NULL *before* using it — the size that made it
  fail may be a one-element request.
- `calloc`'s zero-fill is why it is the right choice for numeric arrays you
  intend to sum, but it is not "faster" in general — it can be slower than
  `malloc` for large blocks.
- The `realloc` trap that loses memory:
  `p = realloc(p, n);` — if `realloc` fails it returns NULL **and `p` still
  points at the old block**, which you have just overwritten. Assign to a
  temporary, check, then commit:
  `q = realloc(p, n); if (q) p = q;`
- The allocation is for **bytes**; `malloc(n * sizeof *p)` (not
  `malloc(n * sizeof p)`) is the idiom that stays correct when `p` changes
  from pointer to array.

---

### 🟢 Q. `char *s = "abc";` versus `char t[] = "abc";` — what is different?

**Answer.** The first points **at** a string literal (read-only storage,
usually in a `.rodata`-style section); the second **copies** the literal into
a new array on the stack that you own. So `t[0] = 'X';` is fine, while
`s[0] = 'X';` is undefined behaviour — and it is the classic "worked on the
old machine, segfaults on the new one" bug, because older toolchains kept
literals in writable memory.

Two more consequences interviewers probe:

- `sizeof("abc")` is 4 and `sizeof t` is 4 (both include the NUL), but
  `sizeof s` is the size of a **pointer** — `sizeof` on a pointer tells you
  nothing about the string.
- `strlen` needs the NUL; an array like `char three[3] = {'x','y','z'};` is
  not a string, and `printf("%s", three)` reads past it.

---

### 🟡 Q. Why is `sizeof(arr)` different inside the function that created the
array from inside the function that received it?

**Answer.** Because in C an array parameter is **not** an array — the
declaration `void f(int a[10])` is adjusted to `void f(int *a)`. This is
called "array-to-pointer decay," and it happens at every function boundary:
the callee receives a pointer, so `sizeof a` is the pointer size, and there is
no length to recover. (It also means `a[3]` works in both places, because
subscripting a pointer and an array is the same operation: `a[3]` is
`*(a + 3)`.)

The practical consequences:

- Functions that take arrays must **also** take the length (or a NUL sentinel
  for strings). The "size is implicit" intuition from other languages is
  simply wrong in C.
- `sizeof` is still useful on the *defining* side:
  `int a[10]; int n = sizeof a / sizeof a[0];` — the division gives the
  element count and survives type changes.
- Variadic `printf` solves the same information-loss problem a different way:
  it does not know the argument types either, so the **format string** is the
  contract — which is why `printf("%d", ptr)` is UB and why `gcc -Wall`
  checks the format against the arguments.

---

### 🟡 Q. What are the `free()` mistakes, and why do people set pointers to
NULL after freeing?

**Answer.** The four: **double free** (`free(p); free(p);` — the allocator's
metadata is corrupt, this is UB and a classic crash/exploit primitive),
**freeing what you did not allocate** (stack variables, sub-objects of a
larger block, or a pointer that was advanced — `free(p + 1)` is UB),
**use after free** (reading or writing through the pointer after the block
went back to the pool — the memory may already belong to someone else), and
**leaks** (losing the only pointer without freeing).

Setting `p = NULL` after `free(p)` does not prevent any of these by itself —
it turns *use after free* and *double free* from "undefined" into "almost
certainly a clean NULL dereference you can find," because `free(NULL)` is a
defined no-op while `free(garbage)` is not. The real defenses are: one
allocation, one free, on one pointer; short pointer lifetimes; and tools
(Valgrind, ASan) that catch all four in the test run rather than in
production.

---

### 🔴 Q. What is undefined behaviour, why does the standard *allow* it, and
which ones are the common offenders?

**Answer.** Undefined behaviour is any program behaviour the standard does not
constrain: nothing is required to happen, including "crash," "print garbage,"
or "work perfectly." The standard gets away with this because compilers are
allowed to **optimize under the assumption that UB never happens in the
program** — code that contains UB may be transformed as if the UB-producing
line could not execute, which is how "harmless" UB becomes a silent logic bug.

The common offenders, and why each is dangerous:

- **Signed integer overflow** (`INT_MAX + 1`). Because it is UB, a compiler
  may assume it cannot happen and delete the "check" you wrote for it — the
  famous case where `if (x + 1 > x)` is optimized away.
- **Out-of-bounds reads/writes** — including one past the end for "convenience"
  (`arr[n]` when valid is `arr[0..n-1]`; even a *read* is UB).
- **Dangling pointers** — use after free, or a pointer to a local after return.
- **Type punning through strict aliasing** — reading an `int` through a
  `float*` (and the reverse) is UB; the portable routes are `memcpy` or a
  union (whose rules were made to allow this in C11).
- **Uninitialized reads** — the value is indeterminate, and using it is UB.
- **Null dereference** — even `if (!p)` is not safe to rely on if `p`'s value
  is itself the product of UB.

The interview-grade framing: UB is not "it probably works." It is "the
compiler may assume your program is a different, well-defined program." The
defenses are the same as for memory bugs — narrow pointer lifetimes, bounds
carried as explicit parameters, and sanitizers/Valgrind in CI.

See also [`examples/c/strings/string_literal_vs_char_array.c`](../../examples/c/strings/string_literal_vs_char_array.c)
and [`examples/c/pointers/dynamic_int_array.c`](../../examples/c/pointers/dynamic_int_array.c).
