# Pattern: Intervals

Problems about ranges `[start, end]` that may overlap: meeting rooms, calendar
bookings, merging ranges, resource allocation.

## The first move is almost always: sort

Sort by **start** time for merging and overlap detection. Sort by **end** time
for "maximum non-overlapping intervals" (the classic greedy — always keep the
one that frees up soonest).

Sorting costs O(n log n) and that usually dominates the whole solution.

## Overlap in one line

Two intervals `a` and `b` overlap when:

```python
a.start < b.end and b.start < a.end
```

It is easier to reason about the negation: they do **not** overlap when one ends
before the other starts. Decide up front whether touching endpoints (`[1,2]` and
`[2,3]`) count as overlapping — interviewers ask, and it flips a `<` to a `<=`.

## The merge template

```python
intervals.sort(key=lambda i: i[0])
merged = [intervals[0]]
for start, end in intervals[1:]:
    if start <= merged[-1][1]:                  # overlaps the last kept one
        merged[-1][1] = max(merged[-1][1], end) # extend it
    else:
        merged.append([start, end])             # disjoint, start a new one
```

The `max` matters: the next interval may be entirely *inside* the current one,
and without it you would shrink the range.

## Challenges

| File | Difficulty | Sort by |
|---|---|---|
| [merge_intervals.py](merge_intervals.py) | 🟡 Medium | Start |
| [meeting_rooms.py](meeting_rooms.py) | 🟡 Medium | Start, with a min-heap |
