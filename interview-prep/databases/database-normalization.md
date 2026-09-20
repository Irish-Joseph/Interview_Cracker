# Database Normalization

Normalization is about arranging tables so that each **fact** is stored in
exactly one place. The payoff is not academic purity — it is the elimination
of update, insertion, and deletion **anomalies**, where one logical change
has to be written to (or breaks) several rows.

---

### 🟢 Q. What is a functional dependency, and why is it the root of
normalization?

**Answer.** A functional dependency `X → Y` means the value of `X`
determines the value of `Y` — two rows with the same `X` must have the same
`Y`. Normalization is the process of splitting tables so that every
non-key attribute depends on the **whole key**, **nothing but the key**,
and **nothing but the key** (the 3NF slogan). Every normal form is a rule
about which dependencies are allowed to live in a table.

```python
# An unnormalized "enrollment" table where the teacher is repeated per row.
rows = [
    ("S1", "Math", "Alice"),
    ("S1", "Bio",  "Bob"),
    ("S2", "Math", "Alice"),   # "Math is taught by Alice" stored TWICE
]
teachers_for_math = [r[2] for r in rows if r[1] == "Math"]
assert teachers_for_math == ["Alice", "Alice"]   # redundant copies
```

The fact "Math is taught by Alice" depends only on `course`, not on the
`(student, course)` key — that is the dependency that normalization will
eventually force out of the table.

---

### 🟡 Q. Walk through 1NF, 2NF, and 3NF, and name the anomaly each one
removes.

**Answer.**

- **1NF** — atomic values only, no repeating groups / nested arrays.
  Removes the "column is a list" problem.
- **2NF** — 1NF + no *partial* dependency: every non-key attribute depends
  on the **whole** primary key, not just part of it. Removes anomalies
  where you can't add a course with a known teacher unless a student is
  already enrolled in it.
- **3NF** — 2NF + no *transitive* dependency: non-key attributes depend on
  the key directly, not via another non-key attribute. Removes the
  **update anomaly** — changing a teacher requires updating many rows and
  invites inconsistent copies.

```python
import sqlite3

con = sqlite3.connect(":memory:")
cur = con.cursor()
# Unnormalized: (student, course) key, teacher transitively dependent.
cur.execute(
    "CREATE TABLE enrollment "
    "(id INTEGER PRIMARY KEY, student TEXT, course TEXT, teacher TEXT)"
)
cur.executemany(
    "INSERT INTO enrollment (student, course, teacher) VALUES (?,?,?)",
    [("S1", "Math", "Alice"), ("S1", "Bio", "Bob"), ("S2", "Math", "Alice")],
)
# The "update anomaly": one logical fact lives in two rows.
cur.execute("SELECT COUNT(*) FROM enrollment WHERE teacher = 'Alice'")
assert cur.fetchone()[0] == 2

# 3NF: split out the transitive dependency course -> teacher.
cur.execute("CREATE TABLE course (course TEXT PRIMARY KEY, teacher TEXT)")
cur.execute("CREATE TABLE takes (student TEXT, course TEXT, PRIMARY KEY (student, course))")
cur.execute("INSERT INTO course VALUES ('Math','Alice'), ('Bio','Bob')")
cur.execute("INSERT INTO takes VALUES ('S1','Math'),('S1','Bio'),('S2','Math')")
cur.execute(
    "SELECT t.student, t.course, c.teacher "
    "FROM takes t JOIN course c ON t.course = c.course ORDER BY 1,2"
)
assert cur.fetchall() == [
    ("S1", "Bio", "Bob"), ("S1", "Math", "Alice"), ("S2", "Math", "Alice"),
]
```

Now "Math is taught by Alice" is stored **once** in `course`; updating it
touches one row, and enrolling a student never forces you to restate the
teacher.

---

### 🟡 Q. What is BCNF, and how is it stronger than 3NF?

**Answer.** BCNF says: for every non-trivial dependency `X → Y`, `X` must
be a **superkey**. 3NF allows a non-key to determine another non-key as long
as the dependent side is a key; BCNF forbids it entirely. In practice the
two coincide unless you have overlapping candidate keys.

The classic 3NF-but-not-BCNF example: a table `student, course, teacher`
with candidate keys `(student, course)` and `(course, teacher)`, where
`course → teacher`. Here `teacher` is part of a candidate key, so 3NF is
satisfied (the dependent attribute is a key attribute), but `course →
teacher` has a non-superkey determinant, so BCNF is violated. Splitting on
`course → teacher` (a `course(teacher)` table) restores BCNF.

The interview takeaway: **3NF is the usual stopping point for OLTP
schemas** because BCNF decompositions can sometimes lose a dependency and
force joins; you reach for BCNF when you specifically want to kill every
remaining redundancy.

---

### 🟡 Q. If normalization is so good, why do people denormalize at all?

**Answer.** Normalization optimises for **write** consistency (no
anomalies, minimal storage). Denormalization trades that away to optimise
**read** cost — fewer joins, faster reports, simpler queries. It is a
deliberate, documented decision, not laziness.

| Reason to denormalize | Example |
|---|---|
| Join-heavy read path is the bottleneck | Store `order.total` instead of summing `line_item` each time |
| Historical / audit value | Keep `customer.name_at_purchase` frozen at the moment of sale |
| Redundant fact is cheap and almost never changes | Store `country` next to a normalised `region_id` |
| Analytics / reporting on a copy | A warehouse or materialised view is a denormalised projection |

The discipline: identify the specific read you are optimising, store the
redundant value, and own the **write path** that keeps it in sync (trigger,
application code, or a rebuild job). The moment you denormalise, you
re-introduce an update anomaly on purpose — so you must have a mechanism
and a test that proves the copy stays consistent.

---

### 🟢 Q. What is a surrogate key vs a natural key, and which do you use?

**Answer.** A **natural key** is a real-world identifier (email, VIN,
passport number); a **surrogate key** is an artificial, meaningless
identifier (auto-increment int, UUID) whose only job is to be unique and
stable. Surrogates are preferred for primary keys because natural keys
change (someone updates their email), are often long (bad for index size
and join speed), and can collide or be reused across contexts.

The rule of thumb: use a **surrogate** primary key, keep the natural
identifier as a **unique, indexed** column, and foreign keys reference the
surrogate. This keeps joins cheap and insulates your schema from the day
the business decides the "real" identifier was a bad choice.
