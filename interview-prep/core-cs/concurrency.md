# Concurrency

Where correct-looking code is wrong 1% of the time, on a machine you cannot
reproduce.

---

### 🟢 Q. What is a race condition?

**Answer.** When the result depends on the unpredictable timing of concurrent
operations.

The canonical example is that `count += 1` is not one operation. It is three:

```
LOAD  count -> register
ADD   1
STORE register -> count
```

Two threads can both load 5, both compute 6, and both store 6. Two increments,
one net effect — a **lost update**. Worked demonstration:
[`rust/concurrency/threads_and_channels.rs`](../../rust/concurrency/threads_and_channels.rs).

The general term is a **critical section**: a region that must not be entered by
more than one thread at a time.

---

### 🟢 Q. What is a mutex, and how does it differ from a semaphore?

**Answer.** A **mutex** enforces mutual exclusion: one holder at a time, and
ownership matters — the thread that locks it must be the one that unlocks it.

A **semaphore** is a counter permitting **N** concurrent holders. `acquire`
decrements (blocking at zero), `release` increments. A semaphore with N=1
resembles a mutex but has no ownership, so any thread may release it — which
makes it usable as a signal between threads, and easier to misuse.

Use a mutex to protect shared state. Use a semaphore to limit a resource pool
("at most 10 concurrent database connections").

---

### 🟡 Q. What is a deadlock in application code, and how do you avoid it?

**Answer.** Two threads each holding a lock the other needs.

```python
# Thread 1                 # Thread 2
with lock_a:               with lock_b:
    with lock_b:               with lock_a:     # both block forever
        ...                        ...
```

The reliable fix is **consistent lock ordering** — every thread acquires locks in
one global order (say, by object id), which makes a cycle impossible. Also:
prefer a single coarser lock over two fine ones, use timeouts (`tryLock`) so a
deadlock becomes a recoverable error, and never hold a lock across a network call.

---

### 🟡 Q. What does `volatile` / `atomic` mean, and is it enough?

**Answer.** They solve two different problems, and conflating them is the common
error.

**Visibility.** Without synchronisation, a value written by one thread may sit in
a CPU cache or register and never become visible to another. Java's `volatile`
forces reads and writes to go to main memory. It does **not** make compound
operations safe — `volatile int count; count++` is still a race.

**Atomicity.** An atomic operation completes indivisibly.
`AtomicInteger.incrementAndGet()` performs the whole read-modify-write as one
uninterruptible step, usually via a CPU compare-and-swap instruction.

So: `volatile` for a flag one thread writes and others read. **Atomics** for
counters. A **mutex** when you must keep several variables consistent with each
other — atomics protect one variable each, not an invariant across two.

---

### 🟡 Q. Async/await vs threads — when do you use which?

**Answer.** They solve different bottlenecks.

**Threads** give you parallelism across cores. Right for **CPU-bound** work.
Costly: ~1 MB of stack each, plus context switches.

**Async** gives you concurrency on (usually) one thread by suspending a task at
its I/O points so another can run. Right for **I/O-bound** work — thousands of
in-flight requests, each mostly waiting. Cheap: a suspended task is a small heap
object, not a stack.

The rule: **async for waiting, threads for computing.** And the trap that follows
from it — a blocking or CPU-heavy call inside an async function stalls the whole
event loop and every other task on it. Offload that work to a thread pool.

---

### 🟡 Q. What is the difference between a thread pool and creating threads on demand?

**Answer.** A pool creates a fixed set of worker threads once and feeds them
tasks from a queue.

It fixes two problems with thread-per-task: **creation cost** (spawning a thread
is expensive, and doing it per request wastes most of the work) and **unbounded
growth** (10,000 simultaneous requests creating 10,000 threads will exhaust
memory and thrash the scheduler).

The pool size is the tuning knob: roughly the core count for CPU-bound work
(more threads just add switching); much higher for I/O-bound work, since most
threads are blocked. A bounded task queue matters too — an unbounded one converts
an overload into an out-of-memory error instead of applying backpressure.
Worked example: [`go/concurrency/worker_pool.go`](../../go/concurrency/worker_pool.go).

---

### 🔴 Q. What is the producer–consumer problem?

**Answer.** Producers add items to a shared bounded buffer, consumers remove
them. The coordination requirements:

- Producers must **block when the buffer is full** (backpressure).
- Consumers must **block when it is empty**.
- Mutations of the buffer must be mutually exclusive.

Implemented classically with a mutex plus two condition variables, or in modern
code with a **blocking queue** (`BlockingQueue`, `queue.Queue`, a Go channel),
which packages exactly this.

The point of the question is usually backpressure: if producers never block, a
fast producer and a slow consumer grow the buffer until memory runs out. A
bounded queue converts that failure into a slowdown, which is almost always
what you want.

---

### 🟡 Q. What is thread-safety, and how do you achieve it without locks?

**Answer.** Code is thread-safe if it behaves correctly when called concurrently,
with no external synchronisation required.

Locks are one route. The others are usually better:

- **Immutability.** An object that never changes cannot be raced on. This is the
  single most effective technique, and why functional languages have an easier
  time with concurrency.
- **Confinement.** Do not share the state at all — give each thread its own copy
  (thread-local), or pass ownership by message rather than sharing memory. This
  is Go's "share memory by communicating" and Rust's ownership model.
- **Atomics** for single-variable counters and flags.
- **Concurrent collections** — `ConcurrentHashMap` and friends, which lock
  internally at finer granularity than you would.

Rust enforces this at compile time: its borrow checker rejects a data race rather
than letting you find it in production. See
[`rust/ownership/count_word_frequencies_borrowed.rs`](../../rust/ownership/count_word_frequencies_borrowed.rs).
