# Pattern: Two Pointers

Two indices moving through a sequence under a rule, replacing a nested loop and
turning O(n²) into O(n).

## When to reach for it

- The array is **sorted** (or you can afford to sort it).
- You are looking for a **pair or triplet** that satisfies a condition.
- You must **filter or deduplicate in place** with O(1) extra space.
- You are comparing a sequence against itself from both ends (palindromes).

## The three shapes

**Converging** — start at both ends and move inward. Requires sorted input,
because you must know which direction increases the value.

```python
left, right = 0, len(arr) - 1
while left < right:
    total = arr[left] + arr[right]
    if total == target: return (left, right)
    if total < target:  left += 1     # need a bigger sum
    else:               right -= 1    # need a smaller sum
```

**Fast and slow** — one pointer moves twice as fast. Cycle detection, finding a
midpoint.

**Read and write** — both move forward; `write` lags behind `read` and only
advances for kept elements. In-place filtering.

## Why it is O(n)

Each pointer only ever moves in one direction and never resets, so together they
take at most 2n steps — even though the code looks like it might be quadratic.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [valid_palindrome.py](valid_palindrome.py) | 🟢 Easy | Converging |
| [three_sum.py](three_sum.py) | 🟡 Medium | Sort + converging inside a loop |
