# Cache Stampede

### 🔴 Q. What is a cache stampede, and how do you stop one hot key overwhelming the database?

**Answer.** A cache stampede happens when a popular entry expires and many
requests miss together, so they all fetch or recompute the same value and send
a burst to the backing store.

The protections solve different parts of the problem:

- **Request coalescing / single-flight:** one caller refreshes; others wait.
- **Jittered TTLs:** spread expirations so many keys do not fail at once.
- **Stale-while-revalidate:** serve bounded stale data during one refresh.
- **Early refresh:** probabilistically refresh hot data before expiry.

A distributed lock can coordinate hosts, but it needs a short lease and safe
ownership; otherwise it becomes another outage source. Load shedding and
database limits remain the final backstop because no cache strategy can make
the backing service survive arbitrary demand.
