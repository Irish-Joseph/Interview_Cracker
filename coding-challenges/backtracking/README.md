# Pattern: Backtracking

Build a candidate one choice at a time, and **undo the choice** before trying
the next. It explores a tree of partial solutions and abandons a branch the
moment it cannot lead anywhere.

## When to reach for it

- The problem asks for **all** solutions, not one: every subset, every
  permutation, every valid board.
- You are making a **sequence of choices** where an early choice constrains
  later ones.
- The answer is a **combination of elements** satisfying a constraint.
- Brute force is exponential and you need to prune, not just enumerate.

The tell: the words *all*, *every*, *generate*, or *count the ways* applied to
arrangements rather than to a single optimum. If the problem wants one optimal
value rather than every arrangement, think dynamic programming instead.

## The template

Every backtracking solution is this shape:

```python
def backtrack(state, start):
    if is_complete(state):
        results.append(state.copy())     # copy! state keeps mutating
        return
    for choice in choices_from(start):
        if not is_valid(state, choice):
            continue                     # prune
        state.append(choice)             # 1. choose
        backtrack(state, next_start)     # 2. explore
        state.pop()                      # 3. un-choose
```

## The two bugs that account for most failures

1. **Appending `state` instead of `state.copy()`.** Every result ends up being
   the same list object, so the output is N copies of whatever `state` held
   last — usually empty.
2. **Forgetting to undo.** The `pop()` must mirror the `append()` exactly. If
   you also set a flag or mark a cell, undo that too.

## Subsets vs permutations vs combinations

All three are the same skeleton; only the loop bound differs.

| | Count | Loop starts at | Order matters |
|---|---|---|---|
| **Subsets** | 2ⁿ | `start` | no |
| **Combinations** (choose k) | C(n,k) | `start` | no |
| **Permutations** | n! | 0, skipping used | yes |

Passing a `start` index is what stops `[1,2]` and `[2,1]` both appearing.
Looping from 0 over unused elements is what makes them both appear.

## Complexity

Bounded by the size of the output. Generating 2ⁿ subsets cannot beat O(2ⁿ) —
that is an output-size bound, not an inefficiency, and it is worth saying so
rather than apologising for it. Pruning does not improve the worst case, but it
is routinely the difference between milliseconds and hours.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [subsets.py](subsets.py) | 🟡 Medium | Take-or-skip, record at every node |
| [combination_sum.py](combination_sum.py) | 🟡 Medium | Reuse allowed, prune on the running total |
