# Sorting and Searching

You will rarely implement a sort in production. You will frequently be asked to
compare them, and binary search is one of the most bug-prone things in computing.

---

### 🟢 Q. Compare the sorting algorithms you know.

**Answer.**

| Algorithm | Best | Average | Worst | Space | Stable? |
|---|---|---|---|---|---|
| Bubble / insertion | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Selection | O(n²) | O(n²) | O(n²) | O(1) | No |
| **Merge sort** | O(n log n) | O(n log n) | **O(n log n)** | O(n) | **Yes** |
| **Quicksort** | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| **Heap sort** | O(n log n) | O(n log n) | **O(n log n)** | **O(1)** | No |
| Counting / radix | O(n + k) | O(n + k) | O(n + k) | O(n + k) | Yes |

The three sentences worth having ready:

- **Merge sort** guarantees O(n log n) and is stable, but needs O(n) scratch space.
- **Quicksort** is usually fastest in practice — great locality, in-place — but
  has an O(n²) worst case.
- **Heap sort** is the only one that is both O(n log n) worst case *and* O(1)
  space, but its cache behaviour makes it slower in practice than quicksort.

---

### 🟡 Q. If quicksort has an O(n²) worst case, why is it the default almost everywhere?

**Answer.** Because the worst case is avoidable and the average case is
excellent.

O(n²) happens when the pivot is consistently the smallest or largest element —
classically, choosing `arr[0]` on already-sorted input, which is depressingly
common in real data. The fixes:

- **Randomised pivot** — an adversary cannot predict it.
- **Median-of-three** — sample first, middle, last.
- **Introsort** — start with quicksort, count recursion depth, and switch to heap
  sort past ~2 log n. This gives quicksort's speed *and* an O(n log n) guarantee.
  It is what C++ `std::sort` does.

Quicksort also wins on constants: it partitions in place with sequential memory
access, so it is very cache-friendly, whereas merge sort writes to a second array.

**The real-world answer:** most standard libraries no longer use plain quicksort.
Python and Java (for objects) use **Timsort**, a stable merge sort that detects
already-sorted runs and is O(n) on nearly-sorted data. Java uses dual-pivot
quicksort for primitives, where stability is meaningless.

---

### 🟡 Q. What does "stable" mean and when does it matter?

**Answer.** A stable sort preserves the relative order of elements that compare
equal.

It matters whenever you sort **more than once**. To sort employees by department,
and by salary within each department, a stable sort lets you do it in two passes:

```python
people.sort(key=lambda p: p.salary)      # secondary key first
people.sort(key=lambda p: p.department)  # primary key second
```

The second sort preserves the salary ordering inside each department — only
because it is stable. With an unstable sort this silently produces wrong output.

Stability is also why Python's `sorted` and Java's `Collections.sort` guarantee
it in their specification: users depend on this pattern.

---

### 🟡 Q. Can you sort faster than O(n log n)?

**Answer.** Not with **comparisons**. There are n! possible orderings, and each
comparison yields one bit, so you need at least log₂(n!) ≈ n log n comparisons.
That is a proven lower bound, not a limitation of current algorithms.

You can beat it by not comparing. **Counting sort** tallies occurrences of each
value into buckets: O(n + k) for values in a range of size k. **Radix sort**
applies counting sort digit by digit: O(d × (n + k)).

The catch is the constraints. Counting sort on 32-bit integers needs a
4-billion-entry array. These are worth it only when the key range is small and
known — sorting ages, exam scores, or fixed-length strings.

If an interviewer asks for better than O(n log n), they are asking you to notice
a constraint on the values.

---

### 🟢 Q. Write binary search. What are the classic bugs?

**Answer.**

```python
def binary_search(arr, target):
    low, high = 0, len(arr) - 1          # inclusive bounds
    while low <= high:                   # <=, not <
        mid = low + (high - low) // 2    # overflow-safe
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1                # must be +1
        else:
            high = mid - 1               # must be -1
    return -1
```

**O(log n) time, O(1) space.** Four bugs live in those eight lines:

1. **`while low < high`** instead of `<=` — misses a one-element range, so the
   last candidate is never checked.
2. **`(low + high) // 2`** — overflows in fixed-width languages (C, Java) when
   both are near `INT_MAX`. This bug was in the JDK for nine years. Python's
   unbounded ints are immune, but write the safe form anyway; interviewers look
   for it.
3. **`low = mid`** instead of `mid + 1` — infinite loop, because the range stops
   shrinking.
4. **Forgetting the array must be sorted.** Binary search on unsorted data
   returns nonsense, not an error.

Test with: empty array, one element, target absent, target at index 0, target at
the last index.

---

### 🟡 Q. How do you find the *first* occurrence of a value in an array with duplicates?

**Answer.** Do not stop at the first match — record it and keep searching left.

```python
def first_occurrence(arr, target):
    low, high = 0, len(arr) - 1
    found = -1
    while low <= high:
        mid = low + (high - low) // 2
        if arr[mid] == target:
            found = mid                  # candidate
            high = mid - 1               # but look further left
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return found
```

Still O(log n). Mirror it (`low = mid + 1` on a match) for the last occurrence.
This "keep searching after you find it" shape is the basis of `bisect_left` /
`lower_bound`, and it generalises to the more important question below.

---

### 🔴 Q. What is "binary search on the answer"?

**Answer.** Binary search does not require an array. It requires a **monotonic
predicate**: a boolean function that is false, false, …, false, true, true, …,
true over the search range. Then you can binary search for the boundary.

This unlocks a whole class of optimisation problems — "minimise the maximum X",
"what is the smallest capacity that works?":

```python
def min_feasible(low, high, works):
    """Smallest value in [low, high] for which works(value) is True."""
    best = -1
    while low <= high:
        mid = low + (high - low) // 2
        if works(mid):
            best = mid
            high = mid - 1               # try to do better
        else:
            low = mid + 1                # not enough
    return best
```

"Ship packages within D days", "minimum eating speed", "split array to minimise
the largest sum" are all this function with a different `works`.

**The tell:** the problem asks for a minimum or maximum value, the answer lies in
a numeric range, and checking "is value V feasible?" is easy even though finding
the best V directly is not. Complexity becomes O(log(range) × cost of `works`).

A worked binary search with insertion points is in
[`python/algorithms/binary_search_iterative.py`](../../python/algorithms/binary_search_iterative.py).
