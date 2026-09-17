-- Topic: JOIN fundamentals — INNER, LEFT, RIGHT and the anti-join.
--
-- Concepts:
--   INNER JOIN      -> only rows with a match on BOTH sides
--   LEFT JOIN       -> all left rows; unmatched right side = NULL
--   RIGHT JOIN      -> all right rows (mirror of LEFT)
--   Anti-join       -> rows with NO match (LEFT JOIN ... IS NULL)
--   Self-join       -> a table joined to itself
--
-- The mental model: a JOIN is a filtered cross product on the
-- ON condition. Every join type decides which side's unmatched
-- rows survive.
--
-- Works on: PostgreSQL, SQLite*, MySQL 8+, SQL Server, Oracle.
-- *SQLite has no RIGHT JOIN; emulate it by swapping the tables.

-- ---------------------------------------------------------------
-- 1. Sample data: customers and their orders
-- ---------------------------------------------------------------
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL
);

CREATE TABLE orders (
    order_id  INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    amount    REAL NOT NULL
);

INSERT INTO customers (customer_id, name) VALUES
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Carol'),
    (4, 'Dan');      -- Dan has NO orders

INSERT INTO orders (order_id, customer_id, amount) VALUES
    (101, 1, 50.0),
    (102, 1, 25.0),   -- Alice ordered twice
    (103, 3, 90.0),
    (104, 2, 15.0),
    (105, 9, 999.0);  -- orphan order: customer_id 9 does not exist!

-- ---------------------------------------------------------------
-- 2. INNER JOIN: customers who placed at least one order
-- ---------------------------------------------------------------
-- One output row per MATCHING PAIR, so Alice appears twice.
SELECT
    c.name,
    o.order_id,
    o.amount
  FROM customers c
  INNER JOIN orders o ON o.customer_id = c.customer_id
  ORDER BY c.name, o.order_id;

-- Expected result:
-- name  | order_id | amount
-- ------+----------+-------
-- Alice |      101 |  50.0
-- Alice |      102 |  25.0
-- Bob   |      104 |  15.0
-- Carol |      103 |  90.0
-- (Dan is absent: no matching order. The orphan order 105 is
--  absent too: no matching customer.)

-- ---------------------------------------------------------------
-- 3. LEFT JOIN: everyone, with NULLs for the missing side
-- ---------------------------------------------------------------
SELECT
    c.name,
    o.order_id,
    o.amount
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  ORDER BY c.name, o.order_id;

-- Expected result:
-- name  | order_id | amount
-- ------+----------+-------
-- Alice |      101 |  50.0
-- Alice |      102 |  25.0
-- Bob   |      104 |  15.0
-- Carol |      103 |  90.0
-- Dan   |     NULL |  NULL   <- kept, with NULLs for the order

-- ---------------------------------------------------------------
-- 4. Anti-join: customers with NO orders
-- ---------------------------------------------------------------
-- The classic idiom: LEFT JOIN, then keep rows where the joined
-- side is NULL. (Many engines now also support NOT EXISTS /
-- EXCEPT for the same job.)
SELECT c.name
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
 WHERE o.order_id IS NULL
  ORDER BY c.name;

-- Expected result:
-- name
-- ----
-- Dan

-- ---------------------------------------------------------------
-- 5. Finding orphans the other way: orders with no customer
-- ---------------------------------------------------------------
SELECT o.order_id, o.amount
  FROM orders o
  LEFT JOIN customers c ON c.customer_id = o.customer_id
 WHERE c.customer_id IS NULL;

-- Expected result:
-- order_id | amount
-- ---------+-------
--      105 |  999.0

-- ---------------------------------------------------------------
-- 6. RIGHT JOIN (emulated: swap the tables in a LEFT JOIN)
-- ---------------------------------------------------------------
-- "All orders, with customer info when it exists" ==
-- RIGHT JOIN customers<->orders == LEFT JOIN orders<->customers.
SELECT
    o.order_id,
    c.name
  FROM orders o
  LEFT JOIN customers c ON c.customer_id = o.customer_id
  ORDER BY o.order_id;

-- Expected result:
-- order_id | name
-- ---------+------
--      101 | Alice
--      102 | Alice
--      103 | Carol
--      104 | Bob
--      105 | NULL   <- orphan order kept

-- ---------------------------------------------------------------
-- 7. Self-join: employees and their managers
-- ---------------------------------------------------------------
CREATE TABLE employees (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(id)
);

INSERT INTO employees (id, name, manager_id) VALUES
    (1, 'Alice', NULL),
    (2, 'Bob',   1),
    (3, 'Carol', 1),
    (4, 'Dan',   2);

-- Each employee next to their manager.
SELECT
    e.name  AS employee,
    m.name  AS manager
  FROM employees e
  LEFT JOIN employees m ON m.id = e.manager_id
  ORDER BY e.id;

-- Expected result:
-- employee | manager
-- -------- + --------
-- Alice    | NULL
-- Bob      | Alice
-- Carol    | Alice
-- Dan      | Bob

-- Cheat sheet:
--   "only matching pairs"          -> INNER JOIN
--   "everything from the left"     -> LEFT JOIN
--   "things that have no match"    -> LEFT JOIN ... IS NULL
--   "two sides of the same table"  -> self-join with aliases
