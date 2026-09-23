# Virtual Memory Faults

### 🟡 Q. What is the difference between a page fault and a segmentation fault?

**Answer.** A **page fault** is a CPU trap because a virtual page is not
currently mapped as usable; it is often normal and recoverable. A
**segmentation fault** is the process-visible failure after the OS determines
that the access is invalid and cannot be satisfied.

On a valid page fault, the kernel may load a file-backed page, allocate a fresh
zero page, or perform copy-on-write, update the page table, and restart the
instruction. A major fault needs storage I/O; a minor fault can be resolved
from memory.

If the address is outside mapped regions, violates permissions, or cannot be
loaded, the kernel signals the process. The memorable distinction is:
**page fault is the mechanism; segmentation fault is one possible outcome.**
