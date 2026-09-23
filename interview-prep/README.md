# Interview Prep

Question banks with **written answers**, organised by subject. Every answer aims
to be the explanation you would give out loud in an interview — not a definition
copied from a textbook.

## How each file is laid out

Every question follows the same shape:

```markdown
### Q. The question

**Answer.** The direct answer first, in one or two sentences.

Then the reasoning, an example, and the follow-up the interviewer will ask next.
```

Questions are tagged by difficulty:

- 🟢 **Foundational** — you are expected to answer these without hesitation.
- 🟡 **Intermediate** — the bulk of a typical screen.
- 🔴 **Advanced** — senior roles, or a deliberate depth probe.

---

## Subjects

### Data structures
| File | Covers |
|---|---|
| [arrays-and-strings.md](data-structures/arrays-and-strings.md) | Dynamic arrays, amortised growth, string immutability, in-place work |
| [linked-lists.md](data-structures/linked-lists.md) | Singly/doubly linked, cycle detection, when a list beats an array |
| [stacks-queues-heaps.md](data-structures/stacks-queues-heaps.md) | LIFO/FIFO, monotonic stacks, priority queues, heap operations |
| [hash-tables.md](data-structures/hash-tables.md) | Hashing, collisions, load factor, why O(1) is *average* not worst |
| [trees-and-graphs.md](data-structures/trees-and-graphs.md) | BSTs, balancing, traversals, BFS/DFS, representations |
| [tries.md](data-structures/tries.md) | Prefix trees, prefix enumeration, trie vs hash set, longest-prefix query |

### Algorithms
| File | Covers |
|---|---|
| [complexity-analysis.md](algorithms/complexity-analysis.md) | Big-O, amortised vs average, space complexity, common mistakes |
| [sorting-and-searching.md](algorithms/sorting-and-searching.md) | Comparison sorts, stability, binary search and its edge cases |
| [selection-algorithms.md](algorithms/selection-algorithms.md) | Quickselect vs heaps vs sorting for kth-element queries |
| [recursion-and-backtracking.md](algorithms/recursion-and-backtracking.md) | Base cases, call stack, memoisation, pruning |
| [dynamic-programming.md](algorithms/dynamic-programming.md) | Recognising DP, state design, top-down vs bottom-up |
| [number-theory-and-math.md](algorithms/number-theory-and-math.md) | GCD, modular arithmetic, primality/sieve, bit tricks, big-number overflow |

### Databases
| File | Covers |
|---|---|
| [sql-query-questions.md](databases/sql-query-questions.md) | Joins, grouping, window functions, the NULL traps |
| [indexing-and-transactions.md](databases/indexing-and-transactions.md) | B-tree indexes, query plans, ACID, isolation levels, deadlocks |
| [covering-indexes.md](databases/covering-indexes.md) | Index-only scans and their read/write trade-offs |
| [database-normalization.md](databases/database-normalization.md) | Functional dependencies, 1NF-3NF/BCNF, anomalies, when to denormalize |

### Core computer science
| File | Covers |
|---|---|
| [operating-systems.md](core-cs/operating-systems.md) | Processes vs threads, scheduling, memory, virtual memory, deadlock |
| [virtual-memory-faults.md](core-cs/virtual-memory-faults.md) | Page faults, demand paging, and segmentation faults |
| [networking.md](core-cs/networking.md) | TCP/UDP, HTTP, DNS, TLS, what happens when you type a URL |
| [concurrency.md](core-cs/concurrency.md) | Race conditions, locks, atomics, async vs threads |
| [cryptography-and-security.md](core-cs/cryptography-and-security.md) | Symmetric vs asymmetric, hash vs MAC vs signature, password storage, TLS |

### System design
| File | Covers |
|---|---|
| [fundamentals.md](system-design/fundamentals.md) | Load balancing, caching, replication, sharding, CAP, queues |
| [walkthrough-url-shortener.md](system-design/walkthrough-url-shortener.md) | A complete worked answer, start to finish |
| [walkthrough-rate-limiter.md](system-design/walkthrough-rate-limiter.md) | A complete worked answer: rate limiter, fixed window vs token bucket, sharding by key |
| [cache-stampede.md](system-design/cache-stampede.md) | Single-flight, TTL jitter, and stale-while-revalidate |

### Language-specific
| File | Covers |
|---|---|
| [python.md](languages/python.md) | GIL, mutability, generators, decorators, `is` vs `==` |
| [javascript.md](languages/javascript.md) | Event loop, closures, `this`, prototypes, promises |
| [java.md](languages/java.md) | JVM memory, collections, equals/hashCode, generics erasure |
| [rust.md](languages/rust.md) | Ownership and moves, borrowing/lifetimes, Option/Result/`?`, Box/Rc/RefCell |
| [go.md](languages/go.md) | Goroutines vs threads, channel blocking, error values, interfaces, goroutine leaks |
| [c.md](languages/c.md) | malloc/calloc/realloc, literals vs arrays, array decay, free() mistakes, undefined behaviour |
| [cpp.md](languages/cpp.md) | RAII, smart pointers and cycles, move semantics, virtual/vtable traps, rule of zero |
| [csharp.md](languages/csharp.md) | Value vs reference types, `==` vs Equals, async/await and the async-void trap, Task vs ValueTask |

### Behavioural
| File | Covers |
|---|---|
| [star-stories.md](behavioral/star-stories.md) | The STAR structure, the questions that recur, how to prepare stories |

---

## Study plans

These are deliberately conservative. A plan you actually finish beats an
ambitious one you abandon on day three.

### One week (a screen is coming up)

| Day | Focus |
|---|---|
| 1 | `complexity-analysis.md` + `arrays-and-strings.md`, then the two-pointers and sliding-window challenges |
| 2 | `hash-tables.md` + the hashing challenges |
| 3 | `trees-and-graphs.md` + the tree and graph challenges |
| 4 | `sorting-and-searching.md` + binary-search challenges |
| 5 | Your language file + `concurrency.md` |
| 6 | `sql-query-questions.md` or `system-design/fundamentals.md`, whichever the role needs |
| 7 | Re-attempt every challenge you got wrong, from a blank file |

### Four weeks (building real depth)

| Week | Focus |
|---|---|
| 1 | All of **Data structures**, one challenge pattern per day |
| 2 | All of **Algorithms**, including dynamic programming |
| 3 | **Databases** + **Core CS** + your language file |
| 4 | **System design**, behavioural stories, and full mock attempts under time |

### How to practise a challenge properly

1. Read only the problem statement. Cover the solution.
2. Give yourself 20 minutes. If you are stuck at 20, read *only* the hint.
3. Write the code before running it. Interviewers watch you reason, not iterate.
4. Compare against the provided solution — including its complexity section.
5. Note the *pattern*, not the problem. That is what transfers.

---

## A note on honesty

Nothing here is labelled "asked at company X". Those claims circulate widely and
are almost never verifiable, and preparing for a specific company's rumoured list
is worse practice than understanding the underlying topic. The questions here are
the ones that genuinely recur across the field, grouped by subject.
