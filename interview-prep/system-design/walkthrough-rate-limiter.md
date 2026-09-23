# Worked Example: Design an API Rate Limiter

A complete worked answer for "design the rate limiter in front of a public API,"
start to finish. The goal is to show the *shape* of a good answer: clarify,
estimate, pick a data structure on purpose, design the data model, walk the
request path, and name the bottlenecks you would actually hit.

---

## 1. Clarify requirements

- **What is being limited?** Requests from a *client identity* (API key or
  user) to our public API. One global number for everyone is not the real
  problem.
- **What is the limit?** "N requests per rolling window of W seconds, per
  identity." Example: 100 requests / 60 s. (Ask whether it is *fixed* windows
  — simpler, bursty at the boundary — or *rolling* — fairer, harder.)
- **What happens at the limit?** Return `429 Too Many Requests` with a
  `Retry-After` header. We are *rejecting*, not *queuing* — say this out loud,
  because queueing changes the whole design.
- **Where does it run?** In front of the API servers, on the hot path of
  *every* request, so it must be fast (low single-digit ms) and highly
  available — it is now a critical component, and a bug in it can take down
  the whole API.
- **Multi-tenant fairness?** A single misbehaving key must not starve others,
  but we are not doing per-tenant *resource* isolation here — only admission.

The honest scoping line: "I'll design a **fixed-window** counter first because
it is simple and good enough, then show the upgrade to **sliding window** and
**token bucket** and when each is worth it."

---

## 2. Estimate the scale

- 10 M active API keys, 100 M requests/minute peak ≈ **1.7 M req/s**.
- Each decision must take < ~2 ms and touch at most one shard.
- State per key is tiny (a counter, or a few counters). 10 M keys × a few
  hundred bytes ≈ a few GB — fits in memory on a modest cluster.

The key insight: this is a **read-mostly, per-key, low-latency** workload. The
data is small and hot. That argues strongly for an **in-memory, sharded**
design rather than a database on the hot path.

---

## 3. The core data structure

Three algorithms, in increasing order of fairness and cost:

- **Fixed window.** One counter per key, reset every window. `count < limit ?
  admit : reject`. O(1), trivially sharded. The flaw: a client can burst
  `limit` at the end of one window and `limit` at the start of the next — up
  to **2× the limit** across the boundary in 2W of wall time.
- **Sliding window log.** Store every request timestamp per key; admit if
  fewer than `limit` timestamps fall in `(now - W, now]`. Perfectly fair, but
  it stores up to `limit` timestamps per key and is O(log) per check — more
  memory and more work.
- **Sliding window counter (the pragmatic middle).** Keep the *current* and
  *previous* fixed-window counts; estimate the rolling count as
  `prev * overlap + curr`, where `overlap` is the fraction of the previous
  window still in view. O(1) memory, near-fair, no boundary double-burst.
- **Token bucket** (the "smooth rate + allow bursts" variant). Each key has a
  bucket of capacity `B` that refills at `R` tokens/s; a request consumes one
  token. This is the right model when the product says "average rate with
  short bursts allowed," and it is what most real APIs (and the
  [`examples/go/concurrency/token_bucket_rate_limiter.go`](../../examples/go/concurrency/token_bucket_rate_limiter.go)
  example) implement.

**Decision to state out loud:** fixed-window counter for v1 (simple,
shardable, O(1)); token bucket if the spec allows bursts; sliding-window
counter if the boundary burst is a real problem and we want to stay O(1).

---

## 4. Data model

Per key, store the minimum state the chosen algorithm needs:

```
limiter_state  (in memory, sharded by key)
  key           STRING   (API key / user id)  -- partition key
  window_start  TIMESTAMP
  count         INT8/INT32
  -- token bucket variant instead:
  tokens        FLOAT    (current bucket level)
  last_refill   TIMESTAMP
```

State is small and hot → **keep it in memory** on the limiter nodes, sharded
by hash(key). Persistence is a *reliability* concern, not a correctness one:
if a limiter node dies we can lose that shard's counters and briefly
under-count — acceptable for a limiter (failing open for a few seconds beats
failing closed and rejecting everyone). Optionally replicate the hot shard to
a backup node so a failure is a sub-second failover rather than a reset.

---

## 5. The architecture

```
                +------------------+
   request ----> |   edge / LB      |
                +--------+---------+
                         |
                +--------v---------+        shard by hash(key)
                |  rate limiter    |  ---->  [shard 0] [shard 1] ... [shard N]
                |  (stateful,      |         in-memory counters / token buckets
                |   in-memory)     |
                +--------+---------+
                         | admit / 429
                +--------v---------+
                |   API servers    |
                +------------------+
```

- The limiter is a thin, **stateful** layer. Every request hashes its key to a
  shard; that shard holds the counter and makes the admit/reject call in memory.
- Because state is per-shard and the decision is local, there is **no
  cross-node coordination** in the common case — this is the whole point of
  sharding by key.
- `429` responses carry `Retry-After` so well-behaved clients back off.

---

## 6. The request path in detail

1. Edge extracts the identity (API key / auth token) and hashes it → shard.
2. That shard computes the decision:
   - fixed window: if `now` crossed into a new window, reset `count`; then
     `count < limit ? admit : reject`.
   - token bucket: refill `tokens += R * (now - last_refill)` (capped at B),
     then `tokens >= 1 ? (tokens -= 1; admit) : reject`.
3. Admit → forward to the API servers. Reject → return `429` + `Retry-After`
   **without** touching the API servers (that is a feature: the limiter is the
  first line of defence against a flood).

The invariant to name: **the check-and-increment must be atomic per key.**
Within one shard that is a single-threaded or lock-protected counter — no race.
Across shards a key always maps to exactly one shard, so there is no cross-shard
race. This is why "shard by key" is load-bearing, not just a scaling trick.

---

## 7. Bottlenecks and what you would do next

- **Hot keys.** A single abusive key hammers one shard. Mitigations: detect
  and *early-reject* at the edge for keys already known to be over limit
  (a short negative cache: "key X is limited until T"), or temporarily move a
  hot key to a dedicated node.
- **Limiter availability.** It is now on the critical path. Run it as a
  replicated service; if a shard is unreachable, **fail open** (admit) rather
  than fail closed (reject everyone) — a limiter outage should degrade to
  "no limiting," not "no service." Say the trade-off explicitly.
- **Clock skew.** Windows and token refill depend on `now`. Use a shared,
  synchronized time source (NTP); a skewed clock makes windows inconsistent
  across nodes.
- **Burst at window boundary** (fixed window) → the sliding-window-counter or
  token-bucket upgrade from §3.
- **Global limits** ("the whole API gets 5 M req/s") need a *second*,
  coarser counter — per-key limits and a global budget are separate concerns;
  check both, reject if either is exceeded.

---

## 8. What the interviewer is grading

- Did you **clarify** limit semantics (per-key, rolling vs fixed, reject vs
  queue) before designing?
- Did you pick the data structure **on purpose** and name the trade-off
  (fixed window's boundary burst, token bucket's burst allowance)?
- Did you get **sharding by key** and the **atomic per-key counter** right —
  the two things that make it correct under concurrency?
- Did you treat the limiter as a **critical component** (availability, fail
  open/closed, hot keys, clock skew) rather than a trivial counter?
- Did you estimate scale and use it to argue for **in-memory** state?
