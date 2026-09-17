# Worked Example: Design a URL Shortener

A complete answer, start to finish, in the order you should actually deliver it.
The point is the *shape* of the answer — the same structure works for any design
question.

---

## 1. Clarify requirements

Ask before designing. Suggested questions and the answers assumed here:

**Functional**
- Shorten a long URL into a short one, and redirect from short to long. ✅
- Custom aliases? *Yes, optional.*
- Expiry? *Yes, optional TTL.*
- Analytics on clicks? *Basic counts, not real-time.*
- User accounts, editing, deletion? *Out of scope for now.*

**Non-functional**
- Scale? *100 M new URLs per day.*
- Read/write ratio? *100:1 — redirects vastly outnumber creations.*
- Latency? *Redirect under 100 ms at p99.*
- Availability? *Highly available. A redirect failing is worse than a creation
  failing.*
- Consistency? *A newly created link should work immediately; analytics may lag.*

That last pair is the important trade: **AP for reads, with read-your-writes for
the creator.**

---

## 2. Estimate the scale

```
Writes:   100 M/day ÷ 10⁵ s     ≈ 1,000 URLs/second
Reads:    100 × writes           ≈ 100,000 redirects/second
Peak:     ~2× average            ≈ 200,000 redirects/second

Storage per record:
  short code      7 bytes
  long URL      ~500 bytes
  metadata      ~100 bytes  (created_at, expiry, owner, counter)
  ------------------------
  ~600 bytes, round to 1 KB

  100 M/day × 1 KB = 100 GB/day ≈ 36 TB/year
```

**What these numbers tell us immediately:**
- 200 K reads/second cannot come from a database → **cache is mandatory**.
- 36 TB/year does not fit one node → **sharding required**.
- Reads dominate 100:1 → optimise the read path above everything else.

---

## 3. How long must the short code be?

With 62 characters (`a–z A–Z 0–9`):

| Length | Combinations |
|---|---|
| 5 | 62⁵ ≈ 916 M |
| 6 | 62⁶ ≈ 56 B |
| **7** | **62⁷ ≈ 3.5 trillion** |

At 100 M/day we use 36.5 B/year. Six characters is exhausted in about 18 months;
**seven characters gives roughly 95 years of headroom.** Choose 7.

---

## 4. API

```
POST /api/v1/urls
  { "long_url": "https://…", "custom_alias": "sale", "ttl_days": 30 }
  -> 201 { "short_url": "https://sho.rt/aB3dE7x", "expires_at": "…" }

GET /{code}
  -> 301 or 302 to the long URL
  -> 404 if unknown or expired
```

**301 vs 302 is a real decision.** 301 (permanent) is cached by the browser, so
subsequent visits never reach your servers — cheaper and faster, but you lose
click analytics and cannot ever change the target. **302** keeps every click
flowing through you. Given the analytics requirement: **302**.

---

## 5. Generating the code

Three options, and the trade-off is the answer:

**(a) Hash the URL** — `base62(md5(url))[:7]`. Deterministic, so the same URL
gives the same code. But collisions must be detected and resolved by rehashing
with a salt, which costs a read before every write.

**(b) Random generation** — pick 7 random characters, retry on collision. At 3.5
trillion possibilities and billions of records, collisions are rare, but you
still need a uniqueness check.

**(c) Counter + base62 encoding** ✅ — maintain a distributed counter and encode
it. **Collision-free by construction**, no read before write, and short codes.
The downsides: codes are sequential and therefore guessable and enumerable, and
the counter is a coordination point.

**Chosen: (c), with mitigations.** Use a ticket service (or Redis `INCR`, or
ZooKeeper) handing out **ranges** of 1,000 IDs to each application server, so
servers only coordinate once per thousand URLs rather than per request. Then
XOR/permute the counter before encoding so codes are not obviously sequential.

---

## 6. Data model

A key–value workload: look up one row by primary key, no joins, no complex
queries. That points at a NoSQL store (DynamoDB, Cassandra) rather than a
relational one, though a sharded relational database is entirely defensible.

```
urls
  code        VARCHAR(7)  PRIMARY KEY / partition key
  long_url    TEXT
  created_at  TIMESTAMP
  expires_at  TIMESTAMP   NULL
  owner_id    VARCHAR     NULL
```

**Shard by `code`** using consistent hashing. Every read is by code, so every
read hits exactly one shard — no scatter-gather.

---

## 7. The architecture

```
                    ┌──────────────┐
   client ────────► │     CDN      │  (static assets only)
                    └──────────────┘
                           │
                    ┌──────▼───────┐
                    │ Load balancer│
                    └──────┬───────┘
              ┌───────────┴────────────┐
       ┌──────▼──────┐          ┌──────▼──────┐
       │ Read service│          │Write service│
       │ (redirects) │          │ (shorten)   │
       └──────┬──────┘          └──────┬──────┘
              │                        │
       ┌──────▼──────┐          ┌──────▼──────┐
       │ Redis cache │          │Ticket server│
       │  (LRU, hot) │          │ (ID ranges) │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              └────────┬───────────────┘
                 ┌─────▼──────┐     ┌──────────────┐
                 │  Sharded   │     │ Click events │
                 │  KV store  │     │  → queue →   │
                 └────────────┘     │  analytics   │
                                    └──────────────┘
```

Read and write paths are separate services because their load differs by 100×
and they should scale — and fail — independently.

---

## 8. The read path in detail

1. Request arrives at the read service.
2. Look up `code` in Redis. **Expect ~90% hit rate**: link popularity follows a
   power law, so a small hot set serves most traffic.
3. On a miss, read the shard, populate the cache, return.
4. Emit a click event to a queue (fire-and-forget) — **never** let analytics
   block the redirect.

Cache sizing: if 20% of URLs are hot, that is 20 M × 1 KB = **20 GB**, which fits
comfortably in a small Redis cluster.

---

## 9. Bottlenecks and what you would do next

| Risk | Mitigation |
|---|---|
| Cache stampede on a viral link | Single-flight refill; never expire hot keys mid-spike |
| Ticket server is a SPOF | Replicate it; servers hold a local range so a brief outage is invisible |
| Hot shard | Consistent hashing with virtual nodes |
| Abuse (malware, phishing) | Reputation check on creation, blocklist on redirect |
| Expired-record cleanup | TTL in the store, or a background sweeper |

---

## 10. What the interviewer is grading

Not the diagram. They want to see that you:

- **asked about requirements before designing** — the most common failure;
- **used numbers** to justify the cache, the shard count and the code length;
- **named trade-offs explicitly** (301 vs 302, counter vs hash) rather than
  presenting one option as obviously correct;
- **separated read and write paths** once you knew the ratio;
- **knew what you had not solved** and could say so.

Saying "I'd choose X because of Y, though Z would be better if the requirement
were W" is worth more than any particular architecture.
