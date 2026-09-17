# Dynamic Programming

The topic candidates fear most. It is far more learnable than its reputation —
almost every DP problem is the same four steps applied to a different state.

---

### 🟢 Q. What is dynamic programming?

**Answer.** Solving a problem by breaking it into overlapping subproblems and
storing each subproblem's answer so it is computed only once.

Two properties must hold, and naming both is the mark of a real answer:

1. **Optimal substructure** — the optimal solution is built from optimal
   solutions to subproblems. (Shortest path A→C through B uses the shortest A→B.)
2. **Overlapping subproblems** — the same subproblem recurs many times.

If subproblems *don't* overlap, you have divide and conquer (merge sort), not DP.
If there is no optimal substructure, DP does not apply at all.

---

### 🟡 Q. Memoisation vs tabulation?

**Answer.** Two ways to implement the same recurrence.

**Memoisation (top-down)** — ordinary recursion plus a cache.

```python
from functools import cache

@cache
def fib(n):
    return n if n <= 1 else fib(n - 1) + fib(n - 2)
```

**Tabulation (bottom-up)** — fill a table from the base cases up.

```python
def fib(n):
    if n <= 1:
        return n
    prev, curr = 0, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr
```

| | Memoisation | Tabulation |
|---|---|---|
| Written as | Recursion + cache | Loops |
| Computes | Only reachable states | Every state |
| Space | Table + **O(depth) call stack** | Table, often reducible |
| Risk | Stack overflow when deep | None |
| Easier to | Write from the recurrence | Optimise the space of |

Write the memoised version first — it follows directly from the recurrence and is
much harder to get wrong. Convert to tabulation if you need the space
optimisation or are worried about stack depth.

---

### 🟡 Q. How do you recognise a DP problem?

**Answer.** Signals, in rough order of reliability:

- It asks for a **count** of ways, or a **minimum/maximum**, or whether something
  **is possible** — and you cannot just be greedy.
- The brute force is **exponential** and recomputes the same states.
- It involves a **subsequence** (not subarray), or choices of take/skip.
- There are small numeric constraints that look like array dimensions (`n ≤ 1000`
  and `capacity ≤ 10000` is a loud hint at an n × capacity table).

**Counter-signal:** if a locally optimal choice is provably globally optimal, it
is a **greedy** problem, which is simpler. Interval scheduling by earliest finish
time is greedy; the knapsack is not.

---

### 🔴 Q. Walk through solving a DP problem from scratch.

**Answer.** Four steps. Do them in this order, out loud.

**Problem:** climbing stairs, taking 1 or 2 steps at a time — how many distinct
ways to reach step n?

**1. Define the state.** `ways(i)` = the number of distinct ways to reach step i.
Getting this sentence precise is 80% of the work.

**2. Find the recurrence.** You arrive at step i either from `i-1` (a 1-step) or
from `i-2` (a 2-step), and those routes are disjoint:

```
ways(i) = ways(i - 1) + ways(i - 2)
```

**3. Base cases.** `ways(0) = 1` (one way to stand still), `ways(1) = 1`.

**4. Order of evaluation.** `i` depends on smaller `i`, so iterate upward.

```python
def climb(n):
    prev, curr = 1, 1                    # ways(0), ways(1)
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr
```

**O(n) time, O(1) space** — because each state needs only the previous two, the
table collapses to two variables. That collapse is the most common DP
optimisation and interviewers look for it.

---

### 🔴 Q. Explain the 0/1 knapsack.

**Answer.** Given items with weights and values and a capacity, maximise value
without exceeding capacity. Each item is taken at most once — the "0/1".

**State:** `best[i][c]` = the best value using the first `i` items with capacity `c`.

**Recurrence** — for each item, take it or skip it:

```
best[i][c] = max(
    best[i-1][c],                          # skip
    best[i-1][c - weight[i]] + value[i]    # take, if it fits
)
```

```python
def knapsack(weights, values, capacity):
    best = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):    # BACKWARDS
            best[c] = max(best[c], best[c - w] + v)
    return best[capacity]
```

**O(n × capacity) time, O(capacity) space.**

The backwards inner loop is the subtle part. Iterating forwards would let the
same item be used twice, because `best[c - w]` would already have been updated
*in this round*. Forwards gives you the **unbounded** knapsack (unlimited
copies); backwards gives 0/1. Being able to explain that one line is a strong
signal.

**Is it polynomial?** No — this is *pseudo*-polynomial. `capacity` is a numeric
value, not an input size, so the table is exponential in the number of *bits*
used to write the capacity. 0/1 knapsack is NP-hard.

---

### 🟡 Q. What are the standard DP patterns worth recognising?

**Answer.** Most problems are a variation of one of these.

| Pattern | State | Examples |
|---|---|---|
| **Linear** | `dp[i]` from `dp[i-1]`, `dp[i-2]` | Climbing stairs, house robber, max subarray |
| **Two sequences** | `dp[i][j]` over both | Edit distance, longest common subsequence |
| **Knapsack** | `dp[item][capacity]` | Subset sum, coin change, partition |
| **Interval** | `dp[left][right]` | Matrix chain, burst balloons, palindromes |
| **Grid** | `dp[row][col]` | Unique paths, minimum path sum |
| **State machine** | `dp[i][state]` | Stock trading with cooldown or fees |

Naming the pattern early ("this is a two-sequence DP, so I want a 2-D table
indexed by positions in each string") makes the rest follow mechanically.

---

### 🟡 Q. What is the difference between DP and greedy?

**Answer.** Greedy commits to the locally best choice and never reconsiders. DP
explores all choices and keeps the best.

Greedy is faster (usually O(n log n) vs O(n²) or worse) but is only correct when
the problem has the **greedy-choice property** — that a locally optimal choice is
part of some globally optimal solution.

The classic demonstration is coin change. Greedy (take the largest coin that
fits) works for `[1, 5, 10, 25]`: for 30 it gives 25 + 5, which is optimal. It
fails for `[1, 3, 4]`: for 6 it gives 4 + 1 + 1 = **three** coins, but 3 + 3 =
**two** is optimal. Same algorithm, different coin set, wrong answer.

So: if you propose greedy, you owe a justification or a proof sketch. If you
cannot give one, use DP. Never assert greedy works because it passes your two
hand-picked examples.
