# Indexing and Transactions

The two database topics that separate "can write a query" from "can run a
system".

---

### 🟢 Q. What is an index and what does it cost?

**Answer.** A separate data structure — almost always a **B+ tree** — that maps
column values to row locations, so the engine can seek instead of scanning every
row.

It turns an O(n) table scan into roughly O(log n).

The costs, which matter as much as the benefit:

- **Writes get slower.** Every `INSERT`, `UPDATE` and `DELETE` must also update
  every affected index.
- **Storage.** An index on a wide column can approach the size of the table.
- **They can be ignored.** If a query would match most of the table, the planner
  correctly decides a sequential scan is cheaper than an index lookup plus
  millions of random row fetches.

So: index columns you filter, join or sort on frequently. Do not index everything.

---

### 🟡 Q. Why a B+ tree rather than a hash index or a binary tree?

**Answer.** Because disk and page size dominate.

A B+ tree node holds hundreds of keys and fills one page, so the tree is very
shallow — three or four levels indexes millions of rows, meaning three or four
page reads. A binary tree with the same data would be ~20 levels deep and each
level is a potential random I/O.

B+ trees also keep all data in the **leaves, linked in sorted order**, which
makes range scans (`WHERE date BETWEEN …`, `ORDER BY`) a straight walk along the
leaf chain.

A **hash index** gives O(1) equality lookup but supports no range queries, no
sorting and no prefix matching. Some engines offer them; the B-tree is the
default because it is good at everything rather than excellent at one thing.

---

### 🟡 Q. What is a composite index, and why does column order matter?

**Answer.** An index on several columns, sorted by the first column, then the
second within that, and so on — like a phone book sorted by surname then forename.

This is the **leftmost prefix rule**. With `INDEX (last_name, first_name)`:

| Query | Uses the index? |
|---|---|
| `WHERE last_name = 'Khan'` | ✅ Yes |
| `WHERE last_name = 'Khan' AND first_name = 'Sara'` | ✅ Yes |
| `WHERE first_name = 'Sara'` | ❌ No |

You cannot look someone up by forename in a phone book; same reason. Put the
column you always filter on first, and the highest-selectivity column early.

---

### 🟡 Q. Name things that stop an index being used.

**Answer.** Mostly, wrapping the indexed column in something:

- **A function on the column.** `WHERE YEAR(created_at) = 2026` cannot use an
  index on `created_at`. Rewrite as a range: `WHERE created_at >= '2026-01-01'
  AND created_at < '2027-01-01'`.
- **A leading wildcard.** `LIKE '%son'` cannot seek; `LIKE 'John%'` can.
- **Implicit type conversion.** Comparing an indexed `VARCHAR` to a number makes
  the engine cast the column, which is a function call.
- **Low selectivity.** An index on a boolean that is 90% true will be skipped.
- **`OR` across different columns.** Often forces a scan; `UNION` of two indexed
  queries can be faster.

Use `EXPLAIN` (or `EXPLAIN ANALYZE`) to check rather than guessing — look for
`Seq Scan` / `type: ALL` where you expected a seek.

---

### 🟢 Q. What does ACID stand for?

**Answer.**

- **Atomicity** — all of a transaction's changes apply, or none do.
- **Consistency** — a transaction moves the database from one valid state to
  another, respecting constraints.
- **Isolation** — concurrent transactions do not see each other's partial work.
- **Durability** — once committed, changes survive a crash (via the write-ahead
  log).

Atomicity is the one people can illustrate: a bank transfer debits one account
and credits another, and a crash in between must not leave money destroyed.

---

### 🔴 Q. Explain the isolation levels and the anomalies they prevent.

**Answer.** Stronger isolation removes more anomalies and costs more concurrency.

| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read uncommitted | possible | possible | possible |
| **Read committed** | prevented | possible | possible |
| **Repeatable read** | prevented | prevented | possible* |
| **Serializable** | prevented | prevented | prevented |

The anomalies:

- **Dirty read** — you read another transaction's uncommitted change, which may
  then roll back.
- **Non-repeatable read** — you read the same **row** twice and get different
  values, because someone committed in between.
- **Phantom read** — you run the same **query** twice and get different *rows*,
  because someone inserted a row matching your filter.

\* PostgreSQL's repeatable read uses snapshot isolation and does prevent
phantoms; the SQL standard does not require this. Defaults differ too —
PostgreSQL and Oracle default to read committed, MySQL/InnoDB to repeatable read.
Knowing that defaults vary is a better answer than reciting one vendor's.

---

### 🟡 Q. What is a deadlock and how do you handle it?

**Answer.** Two transactions each hold a lock the other needs, so neither can
proceed. Transaction A locks row 1 and wants row 2; B locks row 2 and wants row 1.

Databases **detect** deadlocks (a cycle in the wait-for graph) and resolve them
by killing one transaction — the "victim" — which then gets an error and must
retry.

Prevention, in order of usefulness:

1. **Consistent lock ordering.** If every transaction touches rows in ascending
   primary-key order, a cycle cannot form. This is the real fix.
2. **Keep transactions short.** Never hold a lock across a network call or user
   input.
3. **Lower isolation** where the workload permits it.
4. **Retry with backoff.** Deadlocks are normal under load; application code
   should expect and retry them.

---

### 🟡 Q. Optimistic vs pessimistic locking?

**Answer.**

**Pessimistic** — take the lock before reading (`SELECT … FOR UPDATE`) and hold
it until commit. Nobody else can interfere. Correct, but it serialises access and
risks deadlocks. Right when contention is high and conflicts are likely.

**Optimistic** — take no lock. Read a version number with the row, and on write
check the version is unchanged:

```sql
UPDATE accounts SET balance = 500, version = version + 1
WHERE id = 7 AND version = 3;      -- 0 rows updated means someone else won
```

If zero rows are affected, someone else committed first; re-read and retry. Right
when conflicts are rare — no locks, better throughput, at the cost of occasional
wasted work.

---

### 🟡 Q. Normalisation vs denormalisation?

**Answer.** **Normalisation** removes redundancy by splitting data into related
tables. Each fact lives in exactly one place, so updates cannot leave
contradictory copies. The cost is more joins.

**Denormalisation** deliberately duplicates data to avoid those joins — faster
reads, but every copy must be kept in sync, and that synchronisation is where
bugs live.

The practical answer: **normalise by default, denormalise with evidence.** Start
at third normal form, measure, and denormalise the specific read path that is
demonstrably too slow. Analytics and reporting systems (star schemas) are
routinely denormalised because they are read-heavy and loaded in batches.
