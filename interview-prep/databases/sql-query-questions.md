# SQL Query Questions

SQL rounds are mostly the same eight ideas. Know joins, grouping, window
functions and how NULL behaves, and you will handle almost anything asked.

---

### 🟢 Q. Explain the join types.

**Answer.** A join matches rows from two tables on a condition; the type decides
what happens to rows that find no match.

| Join | Keeps |
|---|---|
| `INNER` | Only rows matching in both |
| `LEFT` | All left rows; NULLs where the right has no match |
| `RIGHT` | All right rows; NULLs where the left has no match |
| `FULL OUTER` | All rows from both sides |
| `CROSS` | Every combination (Cartesian product) |

The **anti-join** is the pattern worth having ready — "rows on the left with no
match on the right":

```sql
SELECT c.*
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;      -- the join produced no match
```

Worked examples: [`examples/sql/joins/inner_left_right_and_anti_joins.sql`](../../examples/sql/joins/inner_left_right_and_anti_joins.sql).

---

### 🟡 Q. What is the difference between WHERE and HAVING?

**Answer.** `WHERE` filters **rows before** grouping. `HAVING` filters **groups
after** aggregation.

```sql
SELECT department, COUNT(*) AS headcount
FROM employees
WHERE active = TRUE          -- drop inactive people first
GROUP BY department
HAVING COUNT(*) > 5;         -- then drop small departments
```

You cannot put `COUNT(*) > 5` in `WHERE`, because at that point the groups do not
exist yet. The logical order of evaluation explains every question of this shape:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

`SELECT` running so late is also why you generally cannot reference a column
alias in `WHERE`, but usually can in `ORDER BY`.

---

### 🟡 Q. What is the trap with NULL?

**Answer.** NULL means *unknown*, not *empty*, and comparisons with unknown are
themselves unknown — not false.

- `NULL = NULL` is **NULL**, not true. Use `IS NULL`.
- `WHERE status != 'shipped'` **excludes rows where status is NULL**, which
  surprises almost everyone. Write `WHERE status IS DISTINCT FROM 'shipped'` or
  add `OR status IS NULL`.
- Aggregates skip NULLs: `COUNT(col)` ignores them, `COUNT(*)` does not. `AVG`
  divides by the non-NULL count.

The worst one, and a genuine favourite in interviews:

```sql
SELECT * FROM employees
WHERE id NOT IN (SELECT manager_id FROM departments);
```

If any `manager_id` is NULL, this returns **zero rows**, always. `x NOT IN (1,
NULL)` evaluates to `NOT (x=1 OR x=NULL)` = `NOT (false OR unknown)` = unknown.
Use `NOT EXISTS`, which handles NULL correctly. See
[`examples/sql/subqueries/exists_in_and_correlated.sql`](../../examples/sql/subqueries/exists_in_and_correlated.sql).

---

### 🟡 Q. Find the second-highest salary.

**Answer.** Several ways; the interviewer usually wants to see you handle ties
and the "no such row" case.

```sql
-- Ranking approach: DENSE_RANK treats tied salaries as one rank.
SELECT DISTINCT salary
FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
      FROM employees) ranked
WHERE rnk = 2;
```

```sql
-- Without window functions:
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

The second form returns `NULL` rather than no rows when everyone earns the same —
worth saying out loud, because "what if there is no second-highest?" is the
follow-up.

---

### 🟡 Q. Explain RANK, DENSE_RANK and ROW_NUMBER.

**Answer.** All three number rows within a window; they differ on ties.

For salaries 100, 90, 90, 80:

| Salary | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 80 | 4 | **4** | **3** |

- `ROW_NUMBER` — always distinct, ties broken arbitrarily.
- `RANK` — ties share a rank, then it **skips**.
- `DENSE_RANK` — ties share a rank, no gaps.

Use `ROW_NUMBER` for deduplication (keep the first row per group), `DENSE_RANK`
for "top 3 salary levels". Worked example:
[`examples/sql/window-functions/rank_vs_dense_rank_vs_row_number.sql`](../../examples/sql/window-functions/rank_vs_dense_rank_vs_row_number.sql).

---

### 🟡 Q. How do you remove duplicate rows, keeping the newest per group?

**Answer.** Number rows within each group, then keep number 1.

```sql
WITH ranked AS (
    SELECT id, email, updated_at,
           ROW_NUMBER() OVER (PARTITION BY email ORDER BY updated_at DESC) AS rn
    FROM users
)
DELETE FROM users
WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
```

The CTE is required because a window function cannot appear in `WHERE` — `WHERE`
is evaluated before window functions are. Full example:
[`examples/sql/window-functions/deduplicate_keep_newest_per_group.sql`](../../examples/sql/window-functions/deduplicate_keep_newest_per_group.sql).

---

### 🟡 Q. What is a CTE, and when would you use a recursive one?

**Answer.** A Common Table Expression is a named subquery defined with `WITH`,
used to give a step a name and to reference it more than once. It makes long
queries readable and is often the only way to use a window function in a filter.

A **recursive** CTE references itself, which is how you traverse hierarchies —
org charts, category trees, bill-of-materials, graph reachability:

```sql
WITH RECURSIVE chain AS (
    SELECT id, name, manager_id, 1 AS depth
    FROM employees WHERE manager_id IS NULL     -- anchor
    UNION ALL
    SELECT e.id, e.name, e.manager_id, c.depth + 1
    FROM employees e JOIN chain c ON e.manager_id = c.id   -- recursive step
)
SELECT * FROM chain ORDER BY depth;
```

Always confirm the recursion terminates — a cycle in the data loops forever
unless you track visited nodes or cap the depth. Worked example:
[`examples/sql/recursive-ctes/org_chart_tree_traversal.sql`](../../examples/sql/recursive-ctes/org_chart_tree_traversal.sql).

---

### 🟡 Q. What is the difference between UNION and UNION ALL?

**Answer.** `UNION` removes duplicate rows; `UNION ALL` keeps everything.

Deduplication requires a sort or hash over the combined result, so `UNION` is
materially more expensive. **Use `UNION ALL` unless you actually need distinct
rows** — this is one of the most common easy wins in slow queries.
