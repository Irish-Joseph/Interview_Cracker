# Hash Tables

The most useful data structure in interviews. A very large fraction of "optimise
this O(n²) solution" problems are solved by adding a hash table.

---

### 🟢 Q. How does a hash table work?

**Answer.** It stores key–value pairs in an array, and uses a hash function to
compute which slot a key belongs in.

1. `hash(key)` produces an integer.
2. That integer is reduced to an index, usually `hash % capacity`.
3. The pair is stored at that index.

Lookup repeats the same computation, so it goes straight to the slot instead of
scanning — O(1) average instead of O(n).

The whole structure rests on one assumption: that the hash function spreads keys
roughly evenly. Everything that goes wrong with hash tables is that assumption
failing.

---

### 🟢 Q. What is a collision, and how are collisions resolved?

**Answer.** A collision is two different keys mapping to the same slot. They are
unavoidable — there are more possible keys than slots (the pigeonhole principle).

Two families of solution:

**Separate chaining.** Each slot holds a list of entries. On collision, append.
Lookup scans that one short list. Simple, degrades gracefully, but costs a
pointer per entry and scatters memory. Used by Java's `HashMap` (which upgrades a
long chain to a balanced tree) and most C++ `unordered_map` implementations.

**Open addressing.** Everything lives in the array itself. On collision, probe
for another free slot — linearly, quadratically, or via a second hash. Better
cache behaviour, no per-entry allocation, but deletion is awkward (you must leave
a tombstone, or later probes stop too early) and it degrades badly when full.
Used by Python's `dict` and Go's maps.

---

### 🟡 Q. Hash table lookup is "O(1)". When is it not?

**Answer.** O(1) is the *average* case. The worst case is **O(n)**, when every
key hashes to the same slot and the table degenerates into a linked list.

This matters in practice in two ways:

- **Bad hash functions.** If you write `hashCode()` as `return 1`, every lookup
  becomes a linear scan. Correct but catastrophic.
- **Hash-flooding attacks.** If an attacker can choose your keys and knows your
  hash function, they can deliberately force collisions and turn an O(1) endpoint
  into an O(n²) one. The defence is a randomly seeded hash per process — which is
  why Python's string hashes differ between runs unless you set `PYTHONHASHSEED`.

Java 8+ mitigates it differently: a bucket whose chain exceeds 8 entries converts
to a red–black tree, capping the worst case at O(log n).

---

### 🟡 Q. What is the load factor and why does it trigger a resize?

**Answer.** Load factor = entries ÷ capacity. It measures how full the table is.

As it rises, collisions rise, and average probe length rises with it. Past
roughly 0.7 the performance falls off sharply, so implementations resize — double
the capacity and **rehash every entry**, because the index depends on capacity.

That rehash is O(n), which makes a single insert occasionally O(n) — but
amortised O(1) across all inserts, for exactly the same geometric-growth reason a
dynamic array append is.

Practical consequence: if you know you will insert a million entries, pre-size
the map. You avoid about 20 rehashes.

---

### 🟡 Q. What makes a good hash function?

**Answer.** Three properties:

1. **Deterministic** — the same key always hashes to the same value. Within one
   process run, at minimum.
2. **Uniform** — outputs spread evenly across the range, so no slot is favoured.
3. **Fast** — it runs on every single operation.

Note that cryptographic strength is *not* required and usually not wanted; SHA-256
is uniform but far too slow for a hash table.

---

### 🔴 Q. What is the contract between equals and hashCode?

**Answer.** **If two objects are equal, they must have the same hash code.** The
converse is not required — unequal objects may share a hash code, that is just a
collision.

Break it and hash tables break silently:

```java
Set<Point> set = new HashSet<>();
set.add(new Point(1, 2));
set.contains(new Point(1, 2));   // false, if hashCode() was not overridden
```

The lookup hashes to a different slot and never finds the entry, even though
`equals` would have said yes.

The other half of the contract: **a key's hash must not change while it is in the
table.** Mutating a field that feeds `hashCode` strands the entry in the wrong
slot — it is in the table but unreachable, and it will not even be removed by
`remove()`. This is why immutable keys are strongly preferred, and why Python
simply refuses to hash a `list`.

---

### 🟡 Q. When would you *not* use a hash table?

**Answer.** Four cases:

- **You need ordering.** Hash tables have none. Use a balanced BST (`TreeMap`,
  `std::map`) for sorted iteration or range queries like "all keys between X and Y".
- **You need the worst case bounded.** Real-time systems cannot accept an
  occasional O(n) rehash pause; a balanced tree's guaranteed O(log n) is better.
- **The dataset is tiny.** For five entries, a linear scan of an array is faster
  and uses less memory — no hashing, perfect cache locality.
- **Keys are not hashable.** Mutable or unorderable keys.

---

### 🟡 Q. What is the difference between a HashMap, a HashSet and a HashTable?

**Answer.**

- **Map** — key → value. The core structure.
- **Set** — keys only. Almost always implemented as a map with a dummy value.
- **Hashtable** (the legacy Java class, capital-T) — a synchronised, slower
  predecessor of `HashMap` that also forbids null keys and values. Do not use it;
  if you need thread safety, use `ConcurrentHashMap`, which locks per-bucket
  rather than locking the whole table.

---

### 🟡 Q. How do you use a hash table to turn O(n²) into O(n)?

**Answer.** The pattern: **replace an inner search loop with a lookup**, trading
memory for time.

Two Sum is the canonical example. The brute force checks every pair:

```python
for i in range(len(nums)):              # O(n²)
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
```

The hash table version asks, for each number, "have I already seen the value that
completes this pair?" — a lookup instead of a scan:

```python
seen = {}                               # value -> index
for i, n in enumerate(nums):            # O(n) time, O(n) space
    if target - n in seen:
        return [seen[target - n], i]
    seen[n] = i
```

Recognising this — *"I am searching inside a loop, so I should index instead"* —
is worth more than memorising any individual solution. Worked examples are in
[`coding-challenges/hashing/`](../../coding-challenges/hashing/).

### 🟡 Q. How can an attacker make my hash table slow, and what do
implementations do about it?

**Answer.** A **hash-flooding (hash-collision) DoS**: the attacker supplies
many inputs that hash to the *same* bucket. If the table resolves collisions
by chaining, that one bucket becomes an O(n) linked list, and every lookup
degrades from average O(1) to O(n) — a request that costs microseconds now
costs milliseconds, multiplied across the fleet. (The older variant targeted
`String.hashCode()` in Java, which is public and predictable; the
vulnerability was knowing the function and inverting it.)

The mitigations, in the order they matter:

1. **Make the hash unpredictable.** Randomize it per process start: a secret
   salt/seed mixed into the hash (SipHash in Rust and Python's `hash()`,
   a random multiplier in many Java implementations). The attacker can no
   longer compute colliding inputs *after* the process starts. This is why
   Python's `hash(str)` differs between runs — it is a defence, not a bug.
2. **Switch to tree buckets at the sign of trouble.** JDK 8+ converts a chain
   longer than 8 entries into a balanced tree, capping the worst case at
   O(log n) even if the attacker wins step 1.
3. **Limit the blast radius.** Caps on key length and on map size per
   request turn "one adversarial payload" into "at most N·log N work".

The conceptual point: `O(1)` was always *average*; the attack makes the
adversary control the distribution, so the fix is to remove the adversary's
knowledge (randomization), not to claim a worst case the structure cannot
provide.

**Follow-up.** "Randomizing the hash breaks anything?" Expected: yes — the
hash is no longer stable across processes, so you cannot persist `hash()`
values to disk or compare them between processes; equality must remain defined
by the value, and anything needing a *stable* digest (caches, content
addressing) uses a cryptographic hash, not the table's hasher.
