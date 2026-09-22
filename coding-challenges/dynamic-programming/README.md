# Pattern: Dynamic Programming

Overlapping subproblems solved once and reused.

## When to reach for it

- The problem asks for a **count of ways**, a **minimum/maximum**, or whether
  something **is possible** — and greedy does not provably work.
- The brute force is exponential and **recomputes the same states**.
- It involves a **subsequence** (not a contiguous subarray) or take/skip choices.

## The four steps

Do these in order, out loud. Getting step 1 precise is most of the work.

1. **Define the state.** Write the sentence: "`dp[i]` is the … using the first
   i …". If you cannot write it cleanly, you do not have the right state yet.
2. **Find the recurrence.** How does this state follow from smaller ones?
3. **Base cases.** The smallest inputs, answered directly.
4. **Evaluation order.** Bottom-up loops, or top-down recursion with a cache.

## Memoise first

Write the recursive version with `@functools.cache` first — it follows directly
from the recurrence and is much harder to get wrong. Convert to a bottom-up table
only if you need the space optimisation or are worried about stack depth.

## The space collapse

If `dp[i]` depends only on `dp[i-1]` and `dp[i-2]`, you never need the whole
table — two variables suffice, turning O(n) space into O(1). Interviewers look
for this.

## Challenges

| File | Difficulty | Pattern |
|---|---|---|
| [climbing_stairs.py](climbing_stairs.py) | 🟢 Easy | Linear, with the space collapse |
| [coin_change.py](coin_change.py) | 🟡 Medium | Unbounded knapsack |
| [unique_paths.py](unique_paths.py) | 🟡 Medium | 2D grid, row collapse |
| [longest_common_subsequence.py](longest_common_subsequence.py) | 🟡 Medium | Two sequences, take/skip |
