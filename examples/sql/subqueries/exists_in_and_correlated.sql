-- Topic: Subqueries — scalar, IN, EXISTS and correlated.
--
-- Concepts:
--   Scalar subquery      -> returns exactly one row/one column; usable
--                           anywhere a single value is allowed
--   IN (subquery)        -> membership test against a list of values
--   EXISTS (subquery)    -> "does at least one matching row exist?"
--   NOT EXISTS vs NOT IN -> the NULL trap that silently returns nothing
--   Correlated subquery  -> references the outer row; re-evaluated per row
--   Derived table        -> a subquery in FROM, used like a table
--
-- Rule of thumb:
--   Need a value?          -> scalar subquery
--   Need "is it there?"    -> EXISTS
--   Need "is it missing?"  -> NOT EXISTS (never NOT IN on a nullable column)
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: employees and the projects they are booked on
-- ---------------------------------------------------------------
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    department  TEXT    NOT NULL,
    salary      REAL    NOT NULL
);

CREATE TABLE assignments (
    assignment_id INTEGER PRIMARY KEY,
    employee_id   INTEGER,          -- nullable on purpose (see section 5)
    project       TEXT NOT NULL,
    hours         INTEGER NOT NULL
);

INSERT INTO employees (employee_id, name, department, salary) VALUES
    (1, 'Alice',  'Engineering', 95000),
    (2, 'Bob',    'Engineering', 72000),
    (3, 'Carol',  'Design',      81000),
    (4, 'Dan',    'Design',      64000),
    (5, 'Erin',   'Support',     58000);   -- Erin has no assignments

INSERT INTO assignments (assignment_id, employee_id, project, hours) VALUES
    (10, 1,    'atlas',    120),
    (11, 1,    'beacon',    40),
    (12, 2,    'atlas',     80),
    (13, 3,    'beacon',   150),
    (14, 4,    'atlas',     20),
    (15, NULL, 'unstaffed',  0);   -- unassigned booking: employee_id IS NULL

-- ---------------------------------------------------------------
-- 2. Scalar subquery — one value, used inline
-- ---------------------------------------------------------------
-- Compare every salary against the company average. The subquery runs
-- once and its single value is reused for every row.
SELECT
    name,
    salary,
    ROUND(salary - (SELECT AVG(salary) FROM employees), 2) AS diff_from_avg
FROM employees
ORDER BY salary DESC;

-- A scalar subquery in the SELECT list may also be correlated: this one
-- is recomputed for each employee (see section 6 for the cost of that).
SELECT
    e.name,
    (SELECT COUNT(*) FROM assignments a
      WHERE a.employee_id = e.employee_id) AS project_count
FROM employees e
ORDER BY project_count DESC, e.name;

-- ---------------------------------------------------------------
-- 3. IN (subquery) — membership against a value list
-- ---------------------------------------------------------------
-- "Who works on project atlas?"
SELECT name, department
FROM employees
WHERE employee_id IN (SELECT employee_id
                        FROM assignments
                       WHERE project = 'atlas')
ORDER BY name;
-- Expected: Alice, Bob, Dan

-- ---------------------------------------------------------------
-- 4. EXISTS — "is there at least one matching row?"
-- ---------------------------------------------------------------
-- EXISTS stops at the first match, so the inner SELECT list is
-- irrelevant; SELECT 1 is the conventional placeholder.
SELECT e.name
FROM employees e
WHERE EXISTS (SELECT 1
                FROM assignments a
               WHERE a.employee_id = e.employee_id
                 AND a.hours > 100)
ORDER BY e.name;
-- Expected: Alice (120h on atlas), Carol (150h on beacon)

-- The anti-join: employees with no assignment at all.
SELECT e.name
FROM employees e
WHERE NOT EXISTS (SELECT 1
                    FROM assignments a
                   WHERE a.employee_id = e.employee_id);
-- Expected: Erin

-- ---------------------------------------------------------------
-- 5. The NOT IN / NULL trap
-- ---------------------------------------------------------------
-- assignments.employee_id contains a NULL (the unstaffed row).
-- "x NOT IN (1, 2, NULL)" evaluates to UNKNOWN, never TRUE, so the
-- WHERE clause keeps nothing. This query returns ZERO rows:
SELECT e.name AS never_returned
FROM employees e
WHERE e.employee_id NOT IN (SELECT employee_id FROM assignments);

-- Two safe rewrites of the same intent:
SELECT e.name AS safe_with_not_exists
FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM assignments a
                   WHERE a.employee_id = e.employee_id);

SELECT e.name AS safe_with_null_filter
FROM employees e
WHERE e.employee_id NOT IN (SELECT employee_id
                              FROM assignments
                             WHERE employee_id IS NOT NULL);
-- Both return Erin. NOT EXISTS is NULL-safe by construction, which is
-- why it is the preferred form.

-- ---------------------------------------------------------------
-- 6. Correlated subquery — per-row comparisons
-- ---------------------------------------------------------------
-- "Who earns more than their own department average?"
-- The inner query depends on e.department, so it cannot be hoisted out.
SELECT e.name, e.department, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(x.salary)
                    FROM employees x
                   WHERE x.department = e.department)
ORDER BY e.department, e.salary DESC;
-- Expected: Carol (Design), Alice (Engineering)

-- ---------------------------------------------------------------
-- 7. Derived table — a subquery used in FROM
-- ---------------------------------------------------------------
-- Aggregate first, then join to the aggregate. This totals each
-- employee's hours ONCE instead of once per output row.
SELECT
    e.name,
    COALESCE(t.total_hours, 0) AS total_hours
FROM employees e
LEFT JOIN (SELECT employee_id, SUM(hours) AS total_hours
             FROM assignments
            WHERE employee_id IS NOT NULL
            GROUP BY employee_id) AS t
       ON t.employee_id = e.employee_id
ORDER BY total_hours DESC, e.name;
-- Erin shows 0 instead of disappearing, because of the LEFT JOIN.

-- ---------------------------------------------------------------
-- 8. Choosing between them
-- ---------------------------------------------------------------
--   IN vs EXISTS      Modern optimizers usually plan them the same way;
--                     prefer EXISTS when the inner query is correlated
--                     or the inner set is large.
--   NOT IN            Only when the inner column is guaranteed NOT NULL.
--   Correlated        Clear to read, but conceptually runs per outer row.
--                     If it is hot, rewrite as a derived table + JOIN (7).
--   Derived table     Best when the aggregate is needed for many rows.
