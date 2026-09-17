# Recursion and Backtracking

Recursion is how you express "solve a smaller version of this". Backtracking is
recursion that undoes its choices — the standard tool for permutations,
combinations and constraint puzzles.

---

### 🟢 Q. What are the parts of a correct recursive function?

**Answer.** Three, and missing any one is a bug:

1. **A base case** that returns without recursing.
2. **A recursive case** that calls itself on a **strictly smaller** input.
3. **Progress** — every path must move toward the base case.

```python
def factorial(n):
    if n <= 1:          # base case
        return 1
    return n * factorial(n - 1)   # smaller input, guaranteed progress
```

Infinite recursion is almost always a missing base case or a recursive call that
does not shrink the input (`factorial(n)` instead of `factorial(n - 1)`).

---

### 🟢 Q. What actually happens in memory when a function recurses?

**Answer.** Each call pushes a **stack frame** holding that call's parameters,
local variables and return address. Frames are popped as calls return.

That is why recursion costs **O(depth) space** even when it allocates nothing,
and why exceeding the stack limit raises `StackOverflowError` /
`RecursionError`. Python's default limit is 1000 frames — deliberately low, to
turn runaway recursion into a clean error instead of a crash.

The practical consequence: recursion depth proportional to n is fine for a
balanced tree (depth log n) and dangerous for a linked list or a degenerate tree
(depth n).

---

### 🟡 Q. What is tail recursion, and does it help in your language?

**Answer.** A call is in **tail position** when it is the very last thing the
function does — its result is returned directly, with no pending work.

```python
def sum_to(n, acc=0):
    if n == 0:
        return acc
    return sum_to(n - 1, acc + n)     # tail call: nothing waits on it
```

A compiler can reuse the current frame instead of pushing a new one, turning the
recursion into a loop: O(1) space. Scheme and Lua guarantee this; Scala, Kotlin
and most functional languages do it (`@tailrec`); JavaScript engines mostly do
not, despite it being in the spec.

**Python does not do it and will not** — Guido van Rossum has rejected it
deliberately, partly because it destroys the stack traces that make debugging
possible. So in Python, rewriting for tail position buys you nothing. Convert to
an explicit loop instead.

---

### 🟡 Q. When should you convert recursion to iteration?

**Answer.** When depth can be large, or when the recursion is simple enough that
a loop is clearer.

Every recursion can be made iterative with an explicit stack. That does not
reduce total space — it moves it from the limited call stack to the heap, which
is exactly the point when depth is the problem.

Prefer **recursion** for trees, nested structures and divide-and-conquer, where
it mirrors the shape of the data. Prefer **iteration** for linear traversals, and
whenever depth is O(n) on untrusted input.

---

### 🟡 Q. What is backtracking?

**Answer.** Systematic search: make a choice, recurse, then **undo the choice**
before trying the next one. It explores a tree of partial solutions and abandons
a branch as soon as it cannot lead anywhere ("pruning").

The template is the same every time:

```python
def backtrack(state, choices, results):
    if is_complete(state):
        results.append(state.copy())      # copy! state keeps mutating
        return
    for choice in choices:
        if not is_valid(state, choice):
            continue                      # prune
        state.append(choice)              # 1. choose
        backtrack(state, choices, results)# 2. explore
        state.pop()                       # 3. un-choose
    return results
```

Two bugs account for most failures: **forgetting to undo** (state leaks between
branches) and **appending `state` instead of `state.copy()`** (every result is
the same list object, which ends up empty).

---

### 🟡 Q. Generate all permutations of a list.

**Answer.**

```python
def permutations(nums):
    results, used, current = [], [False] * len(nums), []

    def backtrack():
        if len(current) == len(nums):
            results.append(current.copy())
            return
        for i, n in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            current.append(n)
            backtrack()
            current.pop()          # undo
            used[i] = False        # undo
        return

    backtrack()
    return results
```

**O(n × n!) time** — there are n! permutations and copying each costs O(n) — and
**O(n) space** beyond the output.

You cannot beat n! when the output *is* n! items; that is an output-size bound,
not an inefficiency. Say so explicitly, because candidates often apologise for a
complexity that is provably optimal.

---

### 🟡 Q. Subsets vs permutations vs combinations — how do the recursions differ?

**Answer.** All three are the same skeleton with a different loop bound.

| | Count | Key difference |
|---|---|---|
| **Subsets** | 2ⁿ | Every element is take-or-skip; record at **every** node |
| **Permutations** | n! | Order matters; loop over all unused elements |
| **Combinations** (choose k) | C(n,k) | Order does not matter; loop from `start` onward |

The single line that separates permutations from combinations is whether the
recursive call restarts the loop at 0 (permutations) or at `i + 1`
(combinations). Passing a `start` index is what stops `[1,2]` and `[2,1]` both
appearing.

---

### 🔴 Q. How does pruning change backtracking's performance?

**Answer.** It does not improve the worst case, but it is the difference between
usable and useless in practice.

N-Queens is the standard illustration. Brute force places a queen in every square
of every row: 8⁸ ≈ 16.7 million placements for an 8×8 board. Checking validity
*as you place* — abandoning a row the instant a queen is attacked — cuts it to
roughly 15,000 nodes explored, and only 92 solutions exist.

The principle: **check constraints as early as possible**, not at the leaves. A
branch you cut at depth 2 removes everything beneath it. This is also why the
order you try choices matters — trying the most constrained option first
("minimum remaining values") prunes hardest and is the core heuristic in Sudoku
solvers.
