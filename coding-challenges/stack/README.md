# Pattern: Stack

Last in, first out. Use it when the **most recent** unresolved thing is the one
you need next.

## When to reach for it

- **Matching pairs** — brackets, tags, nested structures. The most recent opener
  is the one a closer must match.
- **"Next greater / next smaller element"** — the monotonic stack (below).
- **Undo / history**, expression evaluation, DFS without recursion.

## The monotonic stack

A stack kept in sorted order: before pushing, pop everything that breaks the
order. Those popped elements have just found their answer.

```python
stack = []                              # holds indices; values decreasing
for i, n in enumerate(nums):
    while stack and nums[stack[-1]] < n:
        result[stack.pop()] = n         # n is the next greater element
    stack.append(i)
```

This is O(n), not O(n²): each index is pushed exactly once and popped at most
once, so the inner `while` runs at most n times *in total* across the whole loop.

**The tell:** "for each element, find the nearest element to its right/left that
is bigger/smaller". Daily temperatures, largest rectangle in a histogram,
trapping rain water, stock span.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [valid_parentheses.py](valid_parentheses.py) | 🟢 Easy | Matching pairs |
| [daily_temperatures.py](daily_temperatures.py) | 🟡 Medium | Monotonic stack |
