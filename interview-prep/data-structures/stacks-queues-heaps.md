# Stacks, Queues and Heaps

Three small structures that unlock a surprising number of problems once you learn
to recognise their signals.

---

### 🟢 Q. Stack vs queue?

**Answer.** Both restrict where you may add and remove; they differ in which end.

- **Stack** — LIFO, last in first out. `push`/`pop` at the same end.
- **Queue** — FIFO, first in first out. Add at the back, remove from the front.

All four operations are O(1) in a good implementation.

Where each shows up:

| Stack | Queue |
|---|---|
| Function call stack | BFS / level-order traversal |
| Undo history | Task and message queues |
| Bracket matching | Print spoolers, request buffers |
| DFS (explicit or via recursion) | Rate limiting, buffering |
| Expression evaluation | Producer–consumer pipelines |

**The rule of thumb:** DFS uses a stack, BFS uses a queue. That one fact decides
a lot of problems.

---

### 🟢 Q. How do you implement a queue efficiently?

**Answer.** Not with a plain array and `pop(0)` — that shifts every element, so
it is O(n) per dequeue and O(n²) overall.

Three correct options:

- **Doubly linked list** — O(1) at both ends, but a pointer per node and poor
  cache behaviour.
- **Circular buffer** — a fixed array with `head` and `tail` indices that wrap via
  modulo. O(1), contiguous, no allocation. Best when capacity is bounded. Worked
  example: [`examples/c/data-structures/circular_queue.c`](../../examples/c/data-structures/circular_queue.c).
- **Deque from the standard library** — `collections.deque`, `ArrayDeque`,
  `std::deque`. Usually a list of fixed-size blocks: O(1) at both ends with
  decent locality. **Use this in an interview unless asked to implement one.**

The classic puzzle — *implement a queue with two stacks* — is worth knowing: push
onto `in`; to pop, if `out` is empty pour all of `in` into it (reversing order)
then pop from `out`. Each element moves at most twice, so it is **O(1)
amortised**.

---

### 🟡 Q. What is a monotonic stack and what does it solve?

**Answer.** A stack kept in sorted order — you pop elements that break the order
before pushing. It answers "for each element, what is the next element greater
(or smaller) than it?" in **O(n)** instead of O(n²).

```python
def next_greater(nums):
    result = [-1] * len(nums)
    stack = []                       # holds indices, values decreasing
    for i, n in enumerate(nums):
        while stack and nums[stack[-1]] < n:
            result[stack.pop()] = n  # n is the answer for that index
        stack.append(i)
    return result

# [2, 1, 3] -> [3, 3, -1]
```

Each index is pushed once and popped once, so despite the inner `while` the total
work is O(n).

**The tell:** "next greater / previous smaller element", "largest rectangle in a
histogram", "daily temperatures", "trapping rain water". If a problem asks you to
relate each element to the nearest element satisfying a comparison, try a
monotonic stack.

---

### 🟢 Q. What is a heap, and what is it good at?

**Answer.** A complete binary tree satisfying the heap property: in a min-heap,
every parent is ≤ its children (so the minimum sits at the root).

It is stored in a **flat array**, not with pointers — for index `i`, children are
at `2i+1` and `2i+2`, parent at `(i-1)//2`. That is why heaps are fast: no
allocation, excellent cache locality.

| Operation | Cost |
|---|---|
| Peek min/max | **O(1)** |
| Insert | O(log n) — sift up |
| Extract min/max | O(log n) — sift down |
| Build from n items | **O(n)**, not O(n log n) |
| Search for arbitrary value | O(n) — no ordering between siblings |

Two points interviewers probe:

- **Building a heap is O(n).** Sifting down from the middle backwards costs less
  at each level because most nodes are near the bottom and barely move.
- **A heap is only partially ordered.** Finding an arbitrary element is O(n), and
  there is no efficient sorted iteration. It is not a substitute for a BST.

---

### 🟡 Q. How do you find the k largest elements in a stream of n items?

**Answer.** A **min-heap of size k**.

```python
import heapq

def k_largest(stream, k):
    heap = []                              # min-heap of the best k so far
    for item in stream:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:               # bigger than the smallest kept
            heapq.heapreplace(heap, item)
    return sorted(heap, reverse=True)
```

**O(n log k) time, O(k) space.**

The counter-intuitive part, and the point of the question: to track the k
*largest* you use a **min**-heap. The root is the weakest of your current
champions, so it is both the cheapest to check against and the right one to
evict.

Why not sort? Sorting is O(n log n) time and **O(n) space** — impossible if the
stream does not fit in memory. When k is small and n is huge, O(n log k) with
O(k) space is the meaningful win.

---

### 🟡 Q. What is a priority queue and how does it differ from a heap?

**Answer.** A **priority queue** is an abstract data type: "give me the
highest-priority item next". A **heap** is the usual concrete implementation.

The distinction matters because other implementations exist with different
trade-offs — a sorted array gives O(1) extraction but O(n) insertion; a Fibonacci
heap gives O(1) amortised insert and decrease-key, which is what makes the
textbook Dijkstra bound O(E + V log V).

In interviews, "priority queue" almost always means "binary heap". It is the
engine inside Dijkstra's algorithm, A*, Huffman coding, and event-driven
simulation.

---

### 🟡 Q. How do you check for balanced brackets?

**Answer.** The canonical stack problem. Push opening brackets; on a closing
bracket, the top of the stack must be its partner.

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def is_balanced(s):
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False           # wrong partner, or nothing open
    return not stack                   # anything left open is unbalanced
```

**O(n) time, O(n) space.** The two edge cases that separate a correct answer from
a nearly-correct one: a closing bracket when the stack is **empty**, and leftover
openers at the **end**. Candidates routinely forget the second and return `True`
for `"((("`.
