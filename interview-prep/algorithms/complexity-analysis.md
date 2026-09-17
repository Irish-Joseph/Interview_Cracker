# Complexity Analysis

If you get one subject right, make it this one. Every other answer you give will
be followed by "and what's the complexity?"

---

### 🟢 Q. What does Big-O actually describe?

**Answer.** An upper bound on how the cost of an algorithm *grows* as the input
grows, ignoring constant factors and lower-order terms.

It deliberately throws away detail. `O(n)` says "doubling the input roughly
doubles the work". It does not say the algorithm is fast — an `O(n)` algorithm
with a huge constant can lose to an `O(n log n)` one at every realistic size.

The three you will be asked to distinguish:

- **O** — upper bound ("no worse than").
- **Ω** — lower bound ("no better than").
- **Θ** — both, a tight bound.

In practice interviewers say "Big-O" but mean Θ. Answer with the tight bound and
you will never be wrong.

---

### 🟢 Q. Order these from fastest-growing to slowest: O(n log n), O(1), O(2ⁿ), O(n²), O(log n), O(n)

**Answer.** From slowest-growing (best) to fastest-growing (worst):

```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)
```

A rough feel for what each survives, at roughly a second of compute:

| Complexity | Largest practical n |
|---|---|
| O(log n) | effectively unbounded |
| O(n) | ~100,000,000 |
| O(n log n) | ~5,000,000 |
| O(n²) | ~10,000 |
| O(2ⁿ) | ~25 |
| O(n!) | ~11 |

This table is the real reason constraints appear in problem statements. If the
input is 10⁵, an O(n²) solution will not pass and you should stop and look for
an O(n log n) one.

---

### 🟡 Q. What is amortised complexity, and why is appending to a dynamic array O(1)?

**Answer.** Amortised complexity is the average cost per operation across a
*worst-case sequence* of operations — not the average over random inputs.

A dynamic array (Python `list`, Java `ArrayList`, Go slice, C++ `vector`) keeps
spare capacity. Appending is normally a write to a free slot: O(1). When capacity
runs out it allocates a bigger block — usually double — and copies everything,
which is O(n).

The doubling is what makes it work. To reach n elements the copies cost
`1 + 2 + 4 + … + n`, which sums to less than `2n`. Spread across n appends that
is O(1) each.

**The follow-up:** *what if it grew by a constant 10 instead of doubling?* Then
reaching n costs `10 + 20 + 30 + …`, an arithmetic series that sums to O(n²), so
each append is O(n) amortised. Geometric growth is the whole trick.

---

### 🟡 Q. What is the difference between amortised, average-case and worst-case?

**Answer.** They answer different questions:

- **Worst case** — the most expensive single input. Hash table lookup: O(n),
  when every key collides.
- **Average case** — expected cost over a distribution of inputs. Hash table
  lookup: O(1), assuming a reasonable hash.
- **Amortised** — guaranteed average across a sequence, with no probability
  involved. Dynamic array append: O(1), always.

The distinction that catches people out: amortised is a *guarantee*, average is a
*statistical expectation*. A quicksort's O(n log n) is average-case — an
adversary can still force O(n²). A dynamic array's O(1) append is amortised — no
adversary can break it.

---

### 🟢 Q. How do you analyse nested loops?

**Answer.** Multiply the iteration counts, but read the bounds carefully.

```python
for i in range(n):          # n
    for j in range(n):      # n
        work()              # O(1)
# O(n²)
```

The one that trips people up:

```python
for i in range(n):
    for j in range(i, n):   # shrinking inner loop
        work()
```

That is `n + (n-1) + … + 1 = n(n+1)/2`, which is still **O(n²)**. Halving the
work does not change the growth class.

And the one that looks quadratic but is not:

```python
for i in range(n):
    j = 1
    while j < n:
        j *= 2              # log n iterations, not n
```

That is **O(n log n)**.

---

### 🟡 Q. What is the complexity of this, and why?

```python
def f(s):
    result = ""
    for ch in s:
        result += ch
    return result
```

**Answer.** **O(n²)** in languages with immutable strings (Python, Java, C#,
JavaScript).

`result += ch` cannot extend the existing string — strings are immutable, so it
allocates a new string and copies every character across. Doing that n times
copies `1 + 2 + … + n` characters, which is O(n²).

The fix is to collect the pieces and join once, which is O(n):

```python
return "".join(s)          # Python
# StringBuilder in Java/C#, array.push + join in JavaScript
```

This is a genuinely common interview trap, because the O(n²) version looks like
a simple linear loop.

---

### 🟡 Q. How do you reason about the complexity of a recursive function?

**Answer.** Count the nodes in the recursion tree, then multiply by the work done
per node.

**Fibonacci, naive:**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

Each call spawns two, to a depth of n, so roughly 2ⁿ nodes with O(1) work each:
**O(2ⁿ) time, O(n) space** (the deepest path of the call stack).

**Merge sort:** the tree has log n levels, and every level touches all n elements
during the merges: **O(n log n)**.

**Binary search:** one child per call, log n deep, O(1) per node: **O(log n)**.

For divide-and-conquer, the Master Theorem formalises this, but the recursion
tree gets you there and is easier to explain out loud.

---

### 🟡 Q. What is space complexity, and does the call stack count?

**Answer.** Space complexity is the *extra* memory an algorithm needs beyond its
input — and yes, the call stack counts.

A recursive function that is O(n) deep uses O(n) space even if it allocates
nothing, which is exactly why deep recursion causes stack overflow. Converting to
iteration with an explicit stack does not reduce the space, but it does move it
from the (small, fixed) stack to the (large) heap.

Common values worth memorising:

| Algorithm | Time | Space |
|---|---|---|
| Merge sort | O(n log n) | O(n) |
| Quicksort | O(n log n) avg | O(log n) stack |
| Heap sort | O(n log n) | O(1) |
| BFS / DFS on a graph | O(V + E) | O(V) |
| Binary search, iterative | O(log n) | O(1) |

Heap sort being the only O(1)-space O(n log n) comparison sort is a favourite
follow-up.
