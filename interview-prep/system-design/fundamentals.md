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

---

### 🟡 Q. Your service must call a payment provider over the network and retry
on failure. How do you make sure a retry does not charge the customer twice?

**Answer.** You make the operation **idempotent** so that sending it once or
five times has the same effect as sending it once. In practice that means
giving the *logical* operation a stable **idempotency key** that you generate
once (before the first attempt) and send with every attempt; the provider
stores the result of the first key it has seen and returns that stored result
for every repeat, instead of performing the charge again.

The reasoning, and the traps:

- **The key identifies the operation, not the attempt.** You generate it
  before the first try (e.g. a UUID or a business id like the order number)
  and reuse the *same* key on every retry. If you generate a fresh key per
  retry, each retry looks like a new operation and you are back to double
  charges.
- **Retries happen because you cannot tell "failed" from "slow".** The
  classic ambiguity: you sent the charge, the connection timed out, so did the
  provider process it? Without idempotency you must guess, and guessing wrong
  in either direction is costly. With an idempotency key you simply resend and
  the provider's deduplication resolves the ambiguity.
- **Idempotency is a property of the receiver, triggered by the sender.** The
  client supplying the key is necessary but not sufficient — the provider must
  actually deduplicate on it (typically: store `key -> result` atomically,
  e.g. an insert that fails if the key exists). A provider that ignores the key
  gives you no protection.
- **Scope the key to the thing you want to repeat.** "Charge order 1234" gets
  one key; "charge order 1234 again for a genuinely new, separate purchase"
  must get a *different* key. Get this wrong and you either double-charge or,
  worse, silently skip a legitimate second charge.

The trade-off worth stating: idempotency keys make **at-least-once delivery
safe**, which is almost always what you want over "at-most-once" (drop on
failure). The cost is that the receiver keeps a deduplication record with a
retention window, and the key space must be chosen so that legitimate
repeat-able operations collide intentionally while distinct operations never
do. This is also why HTTP distinguishes `POST` (not idempotent by default)
from `PUT`/`DELETE` (idempotent) — a client can safely retry the latter.

### 🟡 Q. Your load balancer fronts 10 replicas. How do you find out when one
stops working — and what do you do about it?

**Answer.** Health checks, in two flavours: **active** (the LB itself probes
each replica — an HTTP GET on a `/healthz` endpoint, or a TCP connect — on a
schedule, and removes replicas that fail N times in a row) and **passive**
(the LB watches real traffic: if requests routed to a replica start failing
or timing out, it stops routing to it). Production systems use both: active
checks catch a replica that is *up but broken* even before traffic would have
hit it, and passive checks react instantly to failures that active checks'
poll interval cannot see.

The parts an interviewer is looking for next:

- **The probe must be a liveness probe, not a dependency probe.** If
  `/healthz` checks the database too, a DB blip removes *every* replica at
  once and the "recovery" is a full-service failure. The right split is:
  *liveness* = "can this process serve at all" (used for removal);
  *readiness* = "are my dependencies ready to take traffic right now"
  (used to keep a just-started replica out of rotation until it is warm).
- **Hysteresis in both directions.** Removal should require a few consecutive
  failures (one GC pause must not bounce a replica), and re-addition should
  require a few consecutive successes (otherwise a flapping replica oscillates
  in and out and every recovery takes a cold start).
- **Ejection beats polling-only.** Passive ejection is the fastest signal you
  have — real users are already getting errors, so react in one failed request,
  not in the next 10-second poll.
- **The trap: removing a sick replica shifts its load to the healthy ones.**
  With 10 replicas, losing one means the other nine each take +11%. If they
  were running at 80%, they now take 90% and may start failing too — a
  cascading failure. This is why health-check design must be discussed
  together with load headroom, rate limits, and circuit breakers, not in
  isolation.

**Follow-up.** "Replicas are flapping: healthy, unhealthy, healthy, every
minute. What do you do?" Expected: lengthen the failure streak and/or add
hysteresis delay, look for a resource cliff (memory pressure, connection
pool exhaustion, a dependency at its limit), and if the cause is external,
prefer keeping the replica in and shedding load (circuit breaker) over
churning the pool.
