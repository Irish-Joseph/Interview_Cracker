# Pattern: Binary Search

Halve the search space each step: O(log n).

## When to reach for it

- The input is **sorted** (or rotated-sorted, or sorted by some property).
- Or — the more powerful case — you can define a **monotonic predicate** over a
  numeric range: `works(v)` is false, false, …, false, true, true, …, true. Then
  you can binary search for the boundary even with no array at all. The signal is
  "find the minimum/maximum value such that …", where checking a candidate is
  easy but finding the best directly is not.

## The template

```python
low, high = 0, len(arr) - 1          # inclusive bounds
while low <= high:                   # <= , so a 1-element range is examined
    mid = low + (high - low) // 2    # overflow-safe form
    if arr[mid] == target:
        return mid
    if arr[mid] < target:
        low = mid + 1                # + 1, or the range stops shrinking
    else:
        high = mid - 1
return -1
```

## The four classic bugs

1. `while low < high` — skips the final single-element range.
2. `(low + high) // 2` — integer overflow in C/Java. (This bug was in the JDK's
   binary search for nine years.)
3. `low = mid` instead of `mid + 1` — infinite loop.
4. Forgetting the input must be **sorted** — you get a wrong answer, not an error.

Always test: empty, one element, target absent, target first, target last.

## Challenges

| File | Difficulty | Variant |
|---|---|---|
| [search_rotated_array.py](search_rotated_array.py) | 🟡 Medium | Sorted-but-rotated input |
| [minimum_eating_speed.py](minimum_eating_speed.py) | 🟡 Medium | Binary search on the answer |
