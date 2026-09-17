# Pattern: Hashing

Trade memory for time: replace an inner search loop with an O(1) lookup.

## When to reach for it

The clearest signal is **you are searching inside a loop**. Any time you write
"for each element, look through the array for …", a hash map or set removes the
inner loop and turns O(n²) into O(n).

Also reach for it when you need to:

- **Count** occurrences → `Counter` / `defaultdict(int)`
- **Group** items by a computed key → `defaultdict(list)`
- Test **membership** or **seen-before** → `set`
- Detect **duplicates** in one pass
- Build an **index** from a value back to its position

## The two shapes

**Seen-so-far** — one pass, checking the map before adding to it. This is what
makes Two Sum O(n): by the time you reach the second element of a pair, the first
is already in the map.

```python
seen = {}
for i, n in enumerate(nums):
    if complement(n) in seen:
        return [seen[complement(n)], i]
    seen[n] = i
```

**Canonical key** — map each item to a normalised form, then group items sharing
that form. Sorted letters for anagrams, a frozenset for unordered collections, a
tuple for a composite key.

## What to watch for

- **Keys must be hashable** — in Python, that means immutable. A `list` cannot be
  a key; a `tuple` can.
- O(1) is **average**, not worst case — see
  [`interview-prep/data-structures/hash-tables.md`](../../interview-prep/data-structures/hash-tables.md).
- Hash maps have **no ordering**. If you need sorted output, sort at the end.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [two_sum.py](two_sum.py) | 🟢 Easy | Seen-so-far |
| [group_anagrams.py](group_anagrams.py) | 🟡 Medium | Canonical key |
