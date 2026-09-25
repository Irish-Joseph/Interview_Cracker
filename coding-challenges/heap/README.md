# Pattern: Heap / Top-K

A heap gives you the smallest (or largest) element in O(1) and maintains that
property in O(log n) per insert or removal. Reach for it when you repeatedly
need the extreme element of a changing collection.

## When to reach for it

- **Top K / Kth largest / K closest** — the clearest signal. The word "K" in
  a problem statement should make you think heap.
- **A running median**, or any statistic over a stream (two heaps).
- **Merging k sorted sequences** — the next element is always the smallest
  head.
- **Scheduling**: always take the task that finishes soonest, or starts next.
- Dijkstra and A*, where the frontier is a priority queue.

## The counter-intuitive part

**To track the K LARGEST elements, use a MIN-heap of size K.**

The root is then the *weakest* of your current champions — exactly the one to
compare against and evict. Keeping a max-heap would put the strongest at the
root, which tells you nothing about what to drop.

```python
import heapq

heap = []                          # min-heap of the best K so far
for item in stream:
    if len(heap) < k:
        heapq.heappush(heap, item)
    elif item > heap[0]:           # better than the weakest kept
        heapq.heapreplace(heap, item)
```

**O(n log k) time, O(k) space.** Compare with sorting: O(n log n) time and
O(n) space. When k is small and n is huge — or n does not fit in memory — that
difference is the whole point.

## Python specifics

`heapq` is a **min-heap only**. For a max-heap, push negated values and negate
on the way out. For tuples, it compares element by element, so
`(priority, item)` sorts by priority — but a tie then compares `item`, which
raises `TypeError` if the items are not comparable. Insert a unique counter as
a tiebreaker: `(priority, count, item)`.

| Operation | Cost |
|---|---|
| `heap[0]` (peek) | O(1) |
| `heappush` / `heappop` | O(log n) |
| `heapreplace` (pop then push) | O(log n), one sift |
| `heapify(list)` | **O(n)**, not O(n log n) |
| find an arbitrary element | O(n) — a heap is only partially ordered |

## Do not confuse a heap with a sorted structure

A heap knows its minimum and nothing else. It cannot iterate in order, cannot
do range queries, and cannot find an arbitrary element quickly. If you need
those, use a balanced tree.

## Challenges

| File | Difficulty | Shape |
|---|---|---|
| [top_k_frequent_elements.py](top_k_frequent_elements.py) | 🟡 Medium | Count, then min-heap of size k |
| [merge_k_sorted_lists.py](merge_k_sorted_lists.py) | 🟡 Medium | K-way merge, heap of size k |
| [kth_largest_element.py](kth_largest_element.py) | 🟡 Medium | Min-heap of size k, evict the weakest |
