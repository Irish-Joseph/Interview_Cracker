# Pattern: Linked List

Pointer rewiring. There is no library to hide behind, so these problems test
care with edge cases more than cleverness.

## The techniques

**Dummy head node.** A sentinel in front of the real head means every node has a
predecessor, so inserting or deleting the first node needs no special case. Reach
for it whenever the head might change — and remember to return `dummy.next`, not
`head`.

**Three-pointer reversal.** `prev`, `curr`, `next`. Always save `curr.next`
*before* you overwrite it.

**Fast and slow pointers.** One moves two steps per iteration. Finds the middle,
detects a cycle, finds the kth node from the end — all in one pass with O(1)
space.

## The four edge cases

Every linked-list answer is graded on these. Walk through them out loud:

1. Empty list (`head is None`).
2. Single node (`head.next is None`) — many loops never run.
3. Operating on the **head** — did you return the correct new head?
4. Operating on the **tail** — is `next` set to `None`, or dangling?

## Challenges

| File | Difficulty | Technique |
|---|---|---|
| [reverse_linked_list.py](reverse_linked_list.py) | 🟢 Easy | Three pointers |
| [detect_cycle.py](detect_cycle.py) | 🟡 Medium | Floyd's fast/slow |
