# System Design Fundamentals

System design interviews have no single right answer. They test whether you can
reason about trade-offs out loud, ask about requirements before designing, and
justify choices with numbers.

---

### How to run the interview

1. **Clarify requirements** (5 min). Functional: what must it do? Non-functional:
   how many users, read/write ratio, latency target, consistency needs? **Never
   start drawing before this.** Candidates fail here more than anywhere else.
2. **Estimate scale** (5 min). Get to a rough QPS and storage figure — it decides
   whether you need one server or a thousand.
3. **Sketch the high-level design** (10 min). Boxes and arrows: clients, load
   balancer, services, stores.
4. **Design the data model and API** (10 min).
5. **Go deep** (10 min) on whatever the interviewer pushes on.
6. **Identify bottlenecks** (5 min) and address them.

---

### 🟢 Q. How do you do back-of-the-envelope estimation?

**Answer.** Learn a handful of numbers and round aggressively.

| Quantity | Approximate |
|---|---|
| Seconds in a day | ~86,400, call it 10⁵ |
| 1 million writes/day | ~12 writes/second |
| Memory read | ~100 ns |
| SSD random read | ~100 µs (1000× memory) |
| Disk seek (HDD) | ~10 ms (100× SSD) |
| Same-datacentre round trip | ~0.5 ms |
| Cross-continent round trip | ~150 ms |
| One character (ASCII) | 1 byte |

Example — 100 M daily active users each posting twice:

- Writes: 200 M/day ÷ 10⁵ s ≈ **2,000 writes/second**.
- Peak is typically 2–3× average: **~5,000/s**.
- At 1 KB per post: 200 GB/day, ~**73 TB/year**.

That tells you immediately: one database will not hold a year of this, you need
sharding, and reads will dominate so you need caching.

---

### 🟢 Q. Vertical vs horizontal scaling?

**Answer.** **Vertical** — a bigger machine. Simple, no code changes, but there
is a hard ceiling, it is expensive at the top end, and it leaves a single point
of failure.

**Horizontal** — more machines. Effectively unbounded and fault-tolerant, but it
forces you to handle statelessness, load balancing, data partitioning and
distributed consistency.

The practical answer: **scale vertically until it hurts, then horizontally.**
Horizontal scaling adds real complexity, and a surprising number of systems never
need it. But design stateless services from the start so the option stays open.

---

### 🟡 Q. Where do you put caches, and how do they get stale?

**Answer.** Caching is the highest-leverage optimisation in most designs, because
read traffic usually dominates by 10:1 or more.

Layers: browser → CDN → load balancer → application (in-process) → distributed
cache (Redis/Memcached) → database buffer pool.

**Strategies:**

- **Cache-aside** (most common) — app checks the cache, misses, reads the
  database, populates the cache. Simple; the first request after eviction is slow.
- **Write-through** — write to cache and database together. Consistent, slower
  writes.
- **Write-behind** — write to cache, flush to the database asynchronously. Fast,
  but you can lose data on a crash.

**Eviction:** LRU is the default and usually right. (A worked LRU cache is in
[`examples/cpp/data-structures/lru_cache.cpp`](../../examples/cpp/data-structures/lru_cache.cpp).)

**Invalidation** is the hard part. TTLs are simple but serve stale data for their
duration; explicit invalidation on write is precise but easy to miss a path.
Watch for the **thundering herd** — a popular key expiring makes thousands of
requests hit the database simultaneously. Mitigate with a lock so only one
request refills, or by staggering TTLs.

---

### 🟡 Q. Explain replication and sharding.

**Answer.** They solve different problems and are usually used together.

**Replication** — copies of the same data. Solves read scaling and availability.
Primary–replica is the usual shape: writes go to the primary and propagate to
replicas that serve reads. The catch is **replication lag** — a read right after a
write may hit a replica that has not caught up, so the user does not see their
own change. Fixes: read-your-own-writes routing to the primary, or a version
token.

**Sharding (partitioning)** — splitting *different* data across machines. Solves
write scaling and dataset size.

| Strategy | How | Risk |
|---|---|---|
| Range | Keys A–M here, N–Z there | Hot spots from uneven distribution |
| Hash | `hash(key) % N` | Resharding moves almost everything |
| **Consistent hashing** | Keys and nodes on a ring | Adding a node moves only ~1/N of keys |
| Directory | A lookup service maps key → shard | The directory is a bottleneck/SPOF |

Sharding costs you cross-shard joins and transactions. Choose the shard key so
the common query hits one shard.

---

### 🔴 Q. What is CAP, and what does it actually mean in practice?

**Answer.** In a distributed system you can have at most two of **C**onsistency,
**A**vailability and **P**artition tolerance.

The nuance most candidates miss: **partitions are not optional.** Networks fail,
so P is a given. The real choice is what you do *during* a partition:

- **CP** — refuse requests rather than serve possibly-stale data. Banking,
  inventory, anything where a wrong answer costs money.
- **AP** — keep serving, reconcile later. Social feeds, DNS, shopping carts —
  where being briefly stale beats being down.

**PACELC** extends it usefully: *if Partitioned, choose A or C; Else, choose
Latency or Consistency.* That second half describes normal operation, which is
where systems actually spend their time.

**Eventual consistency** means replicas converge if writes stop. That is weaker
than it sounds, which is why stronger models exist — read-your-writes, monotonic
reads, causal consistency — and naming the specific guarantee you need is a much
better answer than "eventually consistent".

---

### 🟡 Q. When do you add a message queue?

**Answer.** To decouple a producer from a consumer in time.

It buys you:

- **Asynchrony** — return to the user immediately, do the slow work later. (An
  upload responds at once; transcoding happens in the background.)
- **Buffering** — a traffic spike queues up instead of overwhelming the consumer.
- **Retries** — a failed message is redelivered rather than lost.
- **Fan-out** — one event, many independent consumers.

The costs are real: eventual consistency (the work is not done when you reply),
message ordering is hard across partitions, and you must handle **duplicate
delivery** — most queues guarantee at-least-once, not exactly-once. That makes
**idempotent consumers** a requirement, not a nicety.

---

### 🟡 Q. Rate limiting — what algorithms would you use?

**Answer.**

- **Fixed window** — count per calendar minute. Trivial, but allows a 2× burst
  across a window boundary.
- **Sliding window log** — timestamps of every request. Exact, memory-hungry.
- **Sliding window counter** — weighted blend of the current and previous window.
  A good approximation, cheap.
- **Token bucket** — tokens refill at a steady rate; each request spends one.
  Allows controlled bursts, which usually matches what you actually want. Worked
  example: [`examples/go/concurrency/token_bucket_rate_limiter.go`](../../examples/go/concurrency/token_bucket_rate_limiter.go).
- **Leaky bucket** — outflow is perfectly constant. Smooths traffic, no bursts.

In a distributed system the limiter state must be shared (typically Redis), which
adds a network hop to every request — so a common design is a local limiter with
a periodically synchronised global budget.
