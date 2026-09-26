# Pattern: Prefix Sum

Precompute cumulative totals once, then answer any range query in O(1).

## The idea

`prefix[i]` holds the sum of the first `i` elements. The sum of any range is
then one subtraction:

```python
prefix = [0]
for n in nums:
    prefix.append(prefix[-1] + n)

range_sum = prefix[j] - prefix[i]        # sum of nums[i:j], in O(1)
```

Building costs O(n) once; every query afterwards is free. That is the right
trade when you answer many queries over data that does not change.

Note the leading `0`. Without it every query needs an `if i == 0` special
case, which is where the off-by-one bugs live.

## When to reach for it

- **Many range-sum queries** over a static array.
- **"Subarray that sums to k"** — combined with a hash map, this becomes a
  single O(n) pass. That combination is the one worth memorising.
- **Running totals, balances, or differences** between two points.
- **2-D versions**: a rectangle sum via inclusion–exclusion on four corners.
- **Difference arrays**: the inverse trick, where you add to a whole range in
  O(1) and reconstruct at the end.

## The pairing that makes it powerful

Prefix sums alone answer "what is the sum of this range?". Paired with a hash
map of previously-seen prefix values, they answer **"how many ranges sum to
k?"** in one pass:

> If `prefix[j] - prefix[i] == k`, then `prefix[i] == prefix[j] - k`.
> So at each `j`, ask how many earlier prefixes equalled `prefix[j] - k`.

That inversion — from *searching for a range* to *looking up a number* — is
the same move that turns Two Sum from O(n²) into O(n).

## Watch for

- **Seed the map with `{0: 1}`.** A prefix that equals `k` exactly is a valid
  subarray starting at index 0, and it is only counted if the empty prefix is
  already present. This is the single most common bug in the pattern.
- Negative numbers are fine here, unlike with a sliding window — which is
  exactly why you reach for prefix sums when values can be negative.
- Prefix sums assume the array does not change. For updates, use a Fenwick
  (binary indexed) tree or a segment tree instead.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [range_sum_query_2d.py](range_sum_query_2d.py) | Medium | 2D inclusion-exclusion queries |
| [subarray_sum_equals_k.py](subarray_sum_equals_k.py) | 🟡 Medium | Prefix sum + hash map, one pass |
| [subarray_sum_divisible_by_k.py](subarray_sum_divisible_by_k.py) | 🟡 Medium | Prefix residues mod k, count equal pairs |
