# Linked Lists

Rarely the right choice in production, reliably popular in interviews — because
they test pointer manipulation and careful edge-case handling with no library to
hide behind.

---

### 🟢 Q. What is a linked list and how does it differ from an array?

**Answer.** A chain of nodes, each holding a value and a reference to the next
node. Nodes live anywhere in memory; the links impose the order.

| | Array | Linked list |
|---|---|---|
| Access by index | **O(1)** | O(n) — must walk |
| Insert/delete at head | O(n) | **O(1)** |
| Insert/delete at a known node | O(n) | **O(1)** |
| Memory per element | value only | value + pointer(s) |
| Cache locality | **Excellent** | Poor |
| Size | grows by reallocation | grows one node at a time |

The honest summary: linked lists win only when you are inserting or deleting at a
position you already hold a reference to, and never index. In practice, cache
locality means an array often wins even then — a linear scan of a contiguous
array can outrun pointer-chasing by an order of magnitude.

---

### 🟢 Q. Singly vs doubly linked — what does the extra pointer buy?

**Answer.** A `prev` pointer costs one word per node and buys:

- **Backwards traversal.**
- **O(1) deletion given only the node** — a singly linked list needs the
  *predecessor*, so it must scan from the head (O(n)).
- **O(1) append with a tail pointer** — also possible singly, but removing the
  last element needs `prev`.

This is why an LRU cache uses a doubly linked list: it must move an arbitrary
node to the front in O(1), which requires unlinking it, which requires `prev`.

---

### 🟡 Q. How do you detect a cycle in a linked list?

**Answer.** **Floyd's tortoise and hare.** Two pointers, one moving one step per
iteration and one moving two. If there is a cycle they must eventually meet; if
there is not, the fast pointer reaches the end.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

**O(n) time, O(1) space.** The hash-set alternative (store every visited node) is
also O(n) time but O(n) space — mention both, then say why you would pick Floyd.

**Why they must meet:** once both are inside the cycle, the fast pointer gains
exactly one position per iteration, so it closes any gap of size k in k steps. It
cannot "jump over" the slow pointer.

**The follow-up — find where the cycle starts.** After they meet, reset one
pointer to the head and advance both one step at a time. They meet at the cycle
entrance. (The distance from head to entrance equals the distance from the
meeting point to the entrance, going forward around the loop.)

---

### 🟡 Q. Reverse a singly linked list.

**Answer.** Three pointers, walking once and flipping each link as you pass.

```python
def reverse(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next    # save it BEFORE overwriting
        curr.next = prev         # flip
        prev = curr              # advance
        curr = next_node
    return prev                  # new head
```

**O(n) time, O(1) space.** The whole problem is saving `curr.next` before you
destroy it — do that in the wrong order and you lose the rest of the list.

The recursive version is elegant but **O(n) space** from the call stack, which is
a real downside worth naming rather than presenting it as equally good.

---

### 🟡 Q. Find the middle of a linked list in one pass.

**Answer.** Same fast/slow trick. When the fast pointer reaches the end, the slow
pointer is at the middle.

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

For even lengths this returns the *second* of the two middles. If you need the
first, stop when `fast.next and fast.next.next`. Interviewers often care which
one you return — say out loud which convention you chose.

---

### 🟡 Q. Why does so much linked-list code use a dummy head node?

**Answer.** Because it removes the "what if the head changes?" special case.

Without a dummy, deleting the first node or inserting before it needs separate
branching, and that branch is where the bug always is. With a sentinel node in
front, every node has a predecessor and one uniform code path handles all of
them:

```python
def remove_all(head, target):
    dummy = Node(None)
    dummy.next = head
    prev = dummy
    while prev.next:
        if prev.next.value == target:
            prev.next = prev.next.next   # works even for the real head
        else:
            prev = prev.next
    return dummy.next                    # not `head` — it may be gone
```

Reaching for a dummy node unprompted signals real experience.

---

### 🔴 Q. Merge two sorted linked lists. What is the complexity, and why is it nicer than for arrays?

**Answer.** Walk both with a pointer each, always taking the smaller head, and
splice it onto a result list built behind a dummy node.

**O(n + m) time, O(1) extra space** — and that O(1) is the interesting part. The
array version of merge needs an O(n + m) output buffer, because you cannot make
room in a contiguous block without copying. A linked list merge just re-points
existing nodes, allocating nothing.

This is the one place linked lists genuinely beat arrays, and it is why merge
sort on a linked list is O(1)-space while merge sort on an array is O(n)-space.

A worked implementation is in
[`examples/java/algorithms/merge_two_sorted_lists.java`](../../examples/java/algorithms/merge_two_sorted_lists.java)
and [`examples/c/data-structures/linked_list.c`](../../examples/c/data-structures/linked_list.c).

---

### 🟡 Q. What edge cases must linked-list code handle?

**Answer.** Interviewers grade heavily on these, and they are the same four every
time:

1. **Empty list** (`head is None`).
2. **Single node** (`head.next is None`) — many loops never execute.
3. **Operating on the head** — does your code return the right new head?
4. **Operating on the tail** — is `next` set to `None`, or did you leave a
   dangling link?

Walk through a 0-node, 1-node and 2-node list out loud before you say you are
done. It takes twenty seconds and catches most bugs.
