-- Topic: putting a filter on the joined table in WHERE silently turns your
--       LEFT JOIN into an INNER JOIN.
--
-- Concepts:
--   LEFT JOIN + WHERE <right_table>.col = x  -> the NULL rows the LEFT JOIN
--     produced no longer match the WHERE, so they vanish. You get exactly
--     the same rows as an INNER JOIN, without knowing it.
--   The fix: put the filter in the ON clause. ON decides which right rows
--     can match; WHERE decides which rows of the RESULT survive - and the
--     unmatched rows from a LEFT JOIN have NULLs in the right columns.
--   IS NOT NULL / IS NULL filters are the exception - they test the NULLs
--     directly, which is precisely what anti-joins use.
--   COALESCE when you want a default instead of NULL.
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data
-- ---------------------------------------------------------------
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS employees;

CREATE TABLE departments (
    dept_id   INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL
);

CREATE TABLE employees (
    emp_id    INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    dept_id   INTEGER REFERENCES departments(dept_id),
    salary    INTEGER NOT NULL
);

INSERT INTO departments (dept_id, dept_name) VALUES
    (1, 'Engineering'),
    (2, 'Sales'),
    (3, 'Support');

INSERT INTO employees (emp_id, name, dept_id, salary) VALUES
    (101, 'Alice',   1,   95000),
    (102, 'Bob',     1,   40000),
    (103, 'Carol',   2,  105000),
    (104, 'Dan',     2,   45000),
    (105, 'Erin',    3,   60000),
    (106, 'Frank',   NULL,70000);   -- no department: the row a LEFT JOIN exists to keep

-- ---------------------------------------------------------------
-- 2. The intention: every employee, with a high-salary colleague's
--    department when they have one
-- ---------------------------------------------------------------
-- All six employees, Frank's department NULL:
SELECT e.name, e.salary, d.dept_name
  FROM employees e
  LEFT JOIN departments d ON d.dept_id = e.dept_id
 ORDER BY e.emp_id;
-- expected: Alice, Bob, Carol, Dan, Erin, Frank (dept_name NULL)

-- ---------------------------------------------------------------
-- 3. The trap: "but only employees earning over 50k"
-- ---------------------------------------------------------------
-- Any predicate on the right side that NULLs fail will kill the
-- unmatched rows. The most obvious one:
SELECT e.name, e.salary, d.dept_name
  FROM employees e
  LEFT JOIN departments d ON d.dept_id = e.dept_id
 WHERE d.dept_name IS NOT NULL      -- keep only matched rows
 ORDER BY e.emp_id;
-- 5 rows: Frank's LEFT JOIN row is gone. That WHERE clause did exactly
-- what an INNER JOIN would have done - the LEFT is now meaningless.

-- The same mistake in a more common shape, comparing a value:
SELECT e.name, e.salary, d.dept_name
  FROM employees e
  LEFT JOIN departments d ON d.dept_id = e.dept_id
 WHERE d.dept_name = 'Engineering'   -- NULL = 'Engineering' is NULL, not TRUE
 ORDER BY e.emp_id;
-- 2 rows (Alice, Bob). Everyone else - including Frank - silently dropped.

-- ---------------------------------------------------------------
-- 4. The fix: filter in ON, keep the LEFT JOIN's job intact
-- ---------------------------------------------------------------
-- "All employees; show the department name only when it is Engineering."
SELECT e.name,
       e.salary,
       COALESCE(d.dept_name, '(no department)') AS dept
  FROM employees e
  LEFT JOIN departments d
    ON d.dept_id = e.dept_id
   AND d.dept_name = 'Engineering'    -- filter moved into ON
 ORDER BY e.emp_id;
-- All 6 rows survive; non-Engineering employees get '(no department)'.
-- Note the semantics: ON now means "match departments that are
-- Engineering", so Sales/Support employees also come back unmatched.

-- ---------------------------------------------------------------
-- 5. The exception: IS NULL / IS NOT NULL test the NULLs directly
-- ---------------------------------------------------------------
-- Anti-join: employees with no department.
SELECT e.name, e.salary
  FROM employees e
  LEFT JOIN departments d ON d.dept_id = e.dept_id
 WHERE d.dept_id IS NULL
 ORDER BY e.emp_id;
-- just Frank - and here the WHERE is load-bearing, not a bug.

-- Cheat sheet:
--   "I want ALL left rows"  -> every filter on the right table goes in ON
--   "I only want matched"   -> you do not need a LEFT JOIN; use INNER
--   "I want the unmatched"  -> LEFT JOIN ... WHERE right.col IS NULL
