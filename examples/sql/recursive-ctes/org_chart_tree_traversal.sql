-- Topic: Traversing a hierarchy (org chart) with a recursive CTE.
--
-- Concepts:
--   Recursive Common Table Expressions (WITH RECURSIVE)
--   Anchor member vs recursive member
--   Building paths while walking a tree
--   Detecting (and defending against) cycles
--
-- A self-referencing table (each row points at its parent) is one of
-- the classic cases where recursion shines. SQL's recursive CTE lets
-- you "walk down" the tree without application-level loops.
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: a small org chart
-- ---------------------------------------------------------------
CREATE TABLE employees (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(id)  -- NULL = root
);

INSERT INTO employees (id, name, manager_id) VALUES
    (1, 'Alice',   NULL),   -- CEO (root)
    (2, 'Bob',     1),
    (3, 'Carol',   1),
    (4, 'Dan',     2),
    (5, 'Eve',     2),
    (6, 'Frank',   4),
    (7, 'Grace',   3);

-- ---------------------------------------------------------------
-- 2. Report the full subtree under a manager, with depth
-- ---------------------------------------------------------------
-- Structure of a recursive CTE:
--   anchor member     -> the starting row(s)
--   recursive member  -> joined to the CTE itself, one level deeper
WITH RECURSIVE subtree(id, name, manager_id, depth) AS (
    -- Anchor: the chosen manager (id = 2, Bob)
    SELECT id, name, manager_id, 0
      FROM employees
     WHERE id = 2

    UNION ALL

    -- Recursive step: each direct report of the rows found so far
    SELECT e.id, e.name, e.manager_id, s.depth + 1
      FROM employees e
      JOIN subtree s ON e.manager_id = s.id
)
SELECT
    depth,
    name,
    -- Build an indented "tree view" using the depth
    -- (2 spaces per level — SQLite lacks REPEAT(), so use nested logic.)
    id AS employee_id
  FROM subtree
  ORDER BY depth, name;

-- Expected result (Bob's subtree):
-- depth | name  | employee_id
-- ------+-------+------------
--     0 | Bob   | 2
--     1 | Dan   | 4
--     1 | Eve   | 5
--     2 | Frank | 6

-- ---------------------------------------------------------------
-- 3. Build the full path from root to each employee
-- ---------------------------------------------------------------
WITH RECURSIVE report_path(id, name, manager_id, path) AS (
    -- Anchor: all top-level employees (no manager).
    SELECT id, name, manager_id, name
      FROM employees
     WHERE manager_id IS NULL

    UNION ALL

    -- Append each direct report to the parent's path.
    SELECT e.id, e.name, e.manager_id, s.path || ' > ' || e.name
      FROM employees e
      JOIN report_path s ON e.manager_id = s.id
)
SELECT path
  FROM report_path
  ORDER BY path;

-- Expected result:
-- Alice
-- Alice > Bob
-- Alice > Bob > Dan
-- Alice > Bob > Dan > Frank
-- Alice > Bob > Eve
-- Alice > Carol
-- Alice > Carol > Grace

-- ---------------------------------------------------------------
-- 4. Cycle defense
-- ---------------------------------------------------------------
-- If bad data ever makes the hierarchy a cycle (A -> B -> A), the
-- recursive CTE loops forever until the engine's recursion limit.
-- Guard against it by tracking the visited path and refusing to
-- revisit an id:

WITH RECURSIVE safe_walk(id, name, visited) AS (
    SELECT id, name, ',' || id
      FROM employees
     WHERE manager_id IS NULL

    UNION ALL

    SELECT e.id, e.name, s.visited || ',' || e.id
      FROM employees e
      JOIN safe_walk s ON e.manager_id = s.id
     WHERE ',' || e.id || ',' NOT LIKE '%' || s.visited || '%'
)
SELECT id, name FROM safe_walk ORDER BY id;

-- If a cycle exists, the walk simply stops at the repeated node
-- instead of running away. (Some engines also support
-- SEARCH DEPTH FIRST / CYCLE DETECT clauses for this.)
