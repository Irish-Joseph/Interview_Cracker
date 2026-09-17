# Pattern: Sliding Window

A window `[left, right]` over a **contiguous** run. `right` expands to include
new elements; `left` contracts to restore a constraint.

## When to reach for it

The problem asks for the **longest / shortest / maximum / minimum contiguous
subarray or substring** satisfying some condition.

The word that decides it: **contiguous**. If the problem says *subsequence*
(elements need not be adjacent), a window does not apply — that is usually
dynamic programming.

## Fixed vs variable window

**Fixed size k** — slide by adding the entering element and removing the leaving
one, so each step is O(1) instead of recomputing the whole window:

```python
window = sum(arr[:k])
best = window
for right in range(k, len(arr)):
    window += arr[right] - arr[right - k]
    best = max(best, window)
```

**Variable size** — expand always, contract while the constraint is violated:

```python
left = 0
for right in range(len(arr)):
    add(arr[right])
    while violates_constraint():
        remove(arr[left])
        left += 1
    best = max(best, right - left + 1)
```

## Why it is O(n) despite the nested loop

`left` only ever moves forward and never passes `right`. Every element enters the
window once and leaves at most once, so the total work across the whole run is
2n — the inner `while` does not make it quadratic.

## Challenges

| File | Difficulty | Window |
|---|---|---|
| [max_sum_subarray_of_size_k.py](max_sum_subarray_of_size_k.py) | 🟢 Easy | Fixed |
| [longest_substring_without_repeats.py](longest_substring_without_repeats.py) | 🟡 Medium | Variable |
