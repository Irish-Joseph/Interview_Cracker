# Operating Systems

Asked in almost every interview that touches backend or systems work.

---

### 🟢 Q. Process vs thread?

**Answer.** A **process** is a running program with its own address space. A
**thread** is an execution path inside a process; threads of one process share
that address space.

| | Process | Thread |
|---|---|---|
| Memory | Isolated | **Shared** (heap, globals, files) |
| Own stack | Yes | Yes |
| Creation cost | High | Low |
| Communication | IPC (pipes, sockets, shared memory) | Shared variables |
| Crash blast radius | Contained | **Takes down the process** |

The shared address space is the entire trade-off: threads communicate cheaply,
and that same sharing is what makes race conditions possible. Chrome uses a
process per tab precisely so one crashed tab cannot take the browser with it.

---

### 🟡 Q. What is a context switch and why is it expensive?

**Answer.** Saving the CPU state of one thread (registers, program counter, stack
pointer) and restoring another's, so the CPU can run something else.

The direct cost — copying registers — is small, a microsecond or so. The real
cost is indirect: the new thread's data is not in the CPU caches, so it runs
slowly until they refill, and a process switch also flushes the TLB because the
page tables change.

This is why thread-per-request servers stop scaling around a few thousand
connections, and why async I/O exists — one thread multiplexing thousands of
sockets never context-switches between them.

---

### 🟡 Q. What is virtual memory?

**Answer.** An abstraction giving each process its own contiguous address space,
which the MMU translates to physical addresses via **page tables**.

It provides three things at once:

- **Isolation** — a process cannot name another process's memory, so it cannot
  corrupt it.
- **More memory than you have** — pages not in use can be evicted to disk and
  faulted back in on access.
- **Simplicity** — every program is compiled as if it owns all of memory; the
  kernel handles fragmentation.

A **page fault** is the CPU trapping to the kernel because a page is not resident.
A *minor* fault is resolved from memory (the page is already cached); a *major*
fault requires disk I/O and is thousands of times slower. Sustained major faults
are **thrashing** — the system spends all its time paging instead of working.

---

### 🟢 Q. Stack vs heap?

**Answer.**

| | Stack | Heap |
|---|---|---|
| Allocation | Move a pointer — very fast | Search a free list — slower |
| Lifetime | Automatic, at scope exit | Manual or garbage-collected |
| Size | Small and fixed (~1–8 MB) | Large |
| Fragmentation | None | Possible |
| Thread sharing | Private per thread | **Shared** |

Local variables and call frames go on the stack; anything outliving its scope, or
whose size is not known at compile time, goes on the heap. "Stack overflow" is
deep recursion exhausting that small fixed region.

---

### 🟡 Q. Explain the conditions for deadlock.

**Answer.** Four conditions must hold **simultaneously** (Coffman conditions);
break any one and deadlock is impossible.

1. **Mutual exclusion** — a resource cannot be shared.
2. **Hold and wait** — a process holds one resource while waiting for another.
3. **No preemption** — resources cannot be forcibly taken back.
4. **Circular wait** — a cycle of processes each waiting on the next.

In practice you break **circular wait** by imposing a global lock ordering: every
piece of code acquires locks in the same order, so a cycle cannot form. That is
the answer to give — it is the one that is cheap and actually used.

**Livelock** is the related trap: threads are not blocked but keep reacting to
each other and make no progress, like two people stepping aside in the same
direction repeatedly.

---

### 🟡 Q. What is the difference between concurrency and parallelism?

**Answer.** **Concurrency** is dealing with many things at once — a structure
that lets tasks make progress in overlapping time periods. **Parallelism** is
doing many things at once — literally simultaneous execution on multiple cores.

Concurrency is about program structure; parallelism is about hardware execution.
A single-core machine can be concurrent (interleaving) but never parallel. An
async web server is concurrent without necessarily being parallel.

The practical consequence: concurrency helps with **I/O-bound** work (waiting on
network or disk), parallelism helps with **CPU-bound** work. Adding threads to a
CPU-bound task on a single core makes it slower, not faster.

---

### 🟡 Q. How does the kernel decide what runs next?

**Answer.** A scheduler balances throughput, latency and fairness. The approaches
worth naming:

- **Round robin** — each ready thread gets a time slice in turn. Fair, simple,
  ignores priority.
- **Priority scheduling** — highest priority first; risks **starvation** of low
  priority work, mitigated by *aging* (raising priority the longer a task waits).
- **Multi-level feedback queue** — several queues; a task that uses its whole
  slice drops to a lower-priority queue, one that blocks early stays high. This
  automatically favours interactive work over batch work, which is why your
  editor stays responsive during a compile.

Linux's CFS aims to give each runnable task an equal share of CPU time, tracking
how much each has had and running whichever is furthest behind.

---

### 🟡 Q. What is a system call?

**Answer.** The controlled entry point from user space into the kernel — the only
way a program can do I/O, allocate memory or create processes.

Normal code runs in **user mode**, which cannot touch hardware or other
processes' memory. A syscall traps into **kernel mode**, which can. The CPU
enforces this boundary, which is what makes process isolation real rather than a
convention.

Syscalls cost far more than a function call (a mode switch, argument validation,
cache effects), which is why I/O is buffered — `printf` accumulates output and
issues one `write` instead of one per character, and why `sendfile` exists to
copy a file to a socket without crossing the boundary repeatedly.

---

### 🟡 Q. What is a zombie process, why can it not be killed, and what is an
orphan process?

**Answer.** A **zombie** is a process that has exited but still has an entry
in the process table because its parent has not yet called `wait()` to read
its exit status. It is already dead — it holds no memory, no CPU, no file
descriptors — so there is nothing to kill; the entry exists only to hold the
exit code until the parent collects it. An **orphan** is the mirror case: a
process whose parent died first; it is *alive* and simply gets adopted by
`init`/PID 1, which waits on it so it does not become a zombie when it
exits.

Why zombies happen and what they mean:

- When a process exits, it must report **how** it exited (code or signal) to
  its parent. That report has nowhere to live except the process-table
  entry, which is why the entry lingers instead of vanishing.
- `kill` does not work on a zombie — there is no running code to receive the
  signal. The only fix is on the *parent's* side: the parent calls `wait()`,
  or the parent itself dies (then init reaps it).
- A single zombie is harmless (a few hundred bytes of table space). The
  failure mode is a **parent that spawns many children and never waits** —
  each one leaves a zombie, and the table has a finite size, at which point
  the parent cannot create new processes at all.

The practical rules you end with:

- Servers that fork workers should call `wait()` promptly, or set
  `SIGCHLD` to `SIG_IGN`, or install a handler that reaps — any of these
  prevents zombie accumulation.
- `init` (PID 1) exists partly to be the reaping backstop: every orphan is
  reparented to it, and init waits on all its children, so the system as a
  whole can never be clogged with unreaped exits.
- The classic confusion, stated out loud: **zombie = dead but uncollected
  (entry lingers); orphan = alive but parentless (gets adopted)**. They are
  independent properties — a process can be an orphan and never a zombie, and
  a zombie is never "running", so "killing a zombie" is a category error.
