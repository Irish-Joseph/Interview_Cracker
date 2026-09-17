# Arrays and Strings

The most common interview substrate. Most "easy" and "medium" problems are an
array or a string with a pattern applied to it.

---

### 🟢 Q. What is the difference between an array and a dynamic array?

**Answer.** A **static array** is a fixed-size, contiguous block of memory. Its
size is decided at creation and never changes. `int[10]` in C or Java.

A **dynamic array** wraps a static array and grows it when it fills up, by
allocating a larger block and copying. Python `list`, Java `ArrayList`, C++
`vector`, Go slice, JavaScript `Array`.

Both give O(1) indexed access, because the address of element `i` is just
`base + i × element_size` — one multiplication and one addition, no traversal.

| Operation | Cost | Why |
|---|---|---|
| Access by index | O(1) | Direct address arithmetic |
| Append | O(1) amortised | Occasional doubling + copy |
| Insert/delete at front or middle | O(n) | Everything after must shift |
| Search (unsorted) | O(n) | No structure to exploit |
| Search (sorted) | O(log n) | Binary search |

---

### 🟢 Q. Why is inserting at the front of an array O(n) but appending O(1)?

**Answer.** Because arrays are contiguous. Inserting at index 0 means every
existing element must move one slot to the right to make room — n moves.
Appending writes into already-reserved space at the end — one move.

This is the single most useful performance fact about arrays, and it is why:

- `list.pop(0)` is a performance bug in a loop; use `collections.deque`.
- Building a result by `insert(0, x)` is O(n²); append and reverse at the end.

---

### 🟡 Q. Why are strings immutable in Python, Java and JavaScript?

**Answer.** Several reasons reinforce each other:

- **Safe sharing.** An immutable string can be passed around, cached and shared
  between threads with no defensive copying and no locking.
- **Hashability.** A string's hash can be computed once and cached. If strings
  could change, every string used as a map key would be a latent bug (see the
  equals/hashCode contract).
- **Interning.** Identical literals can share one object, saving memory.
- **Security.** A filename or URL validated and then passed to the OS cannot be
  mutated in between by another thread.

The cost is that every "modification" allocates. Concatenating in a loop is
O(n²); use a builder (`StringBuilder`, `"".join`, array + `join`) instead.

---

### 🟡 Q. What does "in-place" mean, and what is the space complexity of an in-place algorithm?

**Answer.** In-place means the algorithm transforms the input using only O(1)
extra space — a few variables, no second array proportional to n.

```python
def reverse_in_place(arr):          # O(1) extra space
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
```

Two honest caveats interviewers probe for:

- You cannot do this to a string in Python/Java — strings are immutable, so you
  necessarily produce a new one. In C or C++ (`char[]`) you can.
- O(log n) stack space from recursion is usually still called "in-place" by
  convention (quicksort is described as in-place), which is a slight abuse.

---

### 🟡 Q. What is the two-pointer technique and when does it apply?

**Answer.** Two indices moving through the array under a rule, replacing a nested
loop — turning O(n²) into O(n).

Three shapes:

**Converging** (from both ends) — needs a **sorted** array or a symmetry:
```python
left, right = 0, len(arr) - 1
while left < right:
    total = arr[left] + arr[right]
    if total == target: return (left, right)
    if total < target:  left += 1      # need bigger
    else:               right -= 1     # need smaller
```
This works only because sorting guarantees which direction increases the sum.

**Fast/slow** — cycle detection, finding the middle of a linked list.

**Same direction (read/write)** — in-place filtering, deduplication:
```python
write = 0
for read in range(len(arr)):
    if keep(arr[read]):
        arr[write] = arr[read]
        write += 1
return write        # new logical length
```

**The tell:** the array is sorted, or you are looking for a pair/triplet, or you
must filter in place.

---

### 🟡 Q. What is the sliding window technique?

**Answer.** A window `[left, right]` over a contiguous run, where `right` expands
and `left` contracts to restore a constraint. Each element enters and leaves at
most once, so the whole scan is O(n) despite the nested-looking loops.

```python
def longest_unique(s):
    last_seen = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1      # contract past the duplicate
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best
```

**The tell:** "longest/shortest/maximum **contiguous** subarray or substring
satisfying X". If the problem says *subsequence* (non-contiguous), a window does
not apply — that is usually dynamic programming.

---

### 🟡 Q. How do you find a duplicate in an array? Give three approaches.

**Answer.** The interviewer wants to see you trade time against space.

1. **Brute force** — compare every pair. O(n²) time, O(1) space.
2. **Sort first** — duplicates become adjacent. O(n log n) time, O(1) extra space
   if you may modify the input.
3. **Hash set** — one pass, check membership. O(n) time, O(n) space.

Then the constrained follow-up: *values are in `1..n` and you may not modify the
input or use extra space.* That is Floyd's cycle detection applied to the array
as an implicit linked list (`i → arr[i]`), giving O(n) time and O(1) space.

Say all three and name the trade-off explicitly — that is the answer they want,
not just the fastest one.

---

### 🟢 Q. What is the difference between a subarray, a subsequence and a subset?

**Answer.** A distinction that changes which algorithm applies, so get it right:

| Term | Contiguous? | Order kept? | Count for n elements |
|---|---|---|---|
| **Subarray / substring** | Yes | Yes | n(n+1)/2 |
| **Subsequence** | No | Yes | 2ⁿ |
| **Subset** | No | No | 2ⁿ |

For `[1, 2, 3]`: `[2, 3]` is a subarray; `[1, 3]` is a subsequence but not a
subarray; `{3, 1}` is a subset.

**Why it matters:** subarray problems usually yield to a sliding window or prefix
sums (O(n)). Subsequence problems usually need dynamic programming, because there
are exponentially many.

---

### 🟡 Q. What is a prefix sum and what is it for?

**Answer.** A precomputed array where `prefix[i]` is the sum of the first `i`
elements. It makes any range sum O(1):

```python
prefix = [0]
for n in nums:
    prefix.append(prefix[-1] + n)

# sum of nums[i:j] in O(1)
range_sum = prefix[j] - prefix[i]
```

Build cost O(n) once, then unlimited O(1) range queries — the right trade when
you answer many queries over a static array. Combined with a hash table of seen
prefix sums it solves "count subarrays summing to k" in one pass.

Worked examples: [`coding-challenges/two-pointers/`](../../coding-challenges/two-pointers/)
and [`coding-challenges/sliding-window/`](../../coding-challenges/sliding-window/).
