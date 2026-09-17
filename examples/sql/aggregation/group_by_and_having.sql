-- Topic: GROUP BY and HAVING — aggregating, then filtering groups.
--
-- Concepts:
--   GROUP BY: collapse rows into one row per distinct value
--   Aggregate functions: COUNT, SUM, AVG, MIN, MAX
--   WHERE vs HAVING: WHERE filters ROWS before grouping,
--                    HAVING filters GROUPS after aggregation
--   The GROUP BY rule: SELECT columns must be grouped or aggregated
--   Multi-column GROUP BY
--
-- The classic confusion: "why can't I filter on SUM() in WHERE?"
-- Answer: WHERE runs BEFORE grouping, so aggregates don't exist
-- yet. HAVING runs AFTER — that's its job.
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: orders with customers and amounts
-- ---------------------------------------------------------------
CREATE TABLE orders (
    order_id   INTEGER PRIMARY KEY,
    customer   TEXT NOT NULL,
    region     TEXT NOT NULL,
    amount     REAL NOT NULL,
    cancelled  INTEGER NOT NULL DEFAULT 0   -- 0 = active, 1 = cancelled
);

INSERT INTO orders (order_id, customer, region, amount, cancelled) VALUES
    (1,  'Acme',    'EU',  120.00, 0),
    (2,  'Acme',    'EU',   80.00, 0),
    (3,  'Acme',    'EU',   30.00, 1),   -- cancelled
    (4,  'Globex',  'EU',  200.00, 0),
    (5,  'Globex',  'US',   40.00, 0),
    (6,  'Initech', 'US',   90.00, 0),
    (7,  'Initech', 'US',   95.00, 0),
    (8,  'Umbrella','US',   10.00, 0),
    (9,  'Umbrella','EU',    5.00, 1),   -- cancelled
    (10, 'Hooli',   'EU',   60.00, 0);

-- ---------------------------------------------------------------
-- 2. Basic GROUP BY: one row per customer ----------------------------
-- Rule: every SELECT column is either grouped or aggregated.
SELECT
    customer,
    COUNT(*)        AS order_count,
    SUM(amount)     AS total_spent,
    AVG(amount)     AS avg_order
  FROM orders
  GROUP BY customer
  ORDER BY total_spent DESC;

-- Expected result:
-- customer | order_count | total_spent | avg_order
-- ---------+-------------+-------------+----------
-- Globex   |           2 |       240.0 |      120.0
-- Acme     |           3 |       230.0 |       76.67
-- Initech  |           2 |       185.0 |       92.5
-- Hooli    |           1 |        60.0 |       60.0
-- Umbrella |           2 |        15.0 |        7.5

-- ---------------------------------------------------------------
-- 3. HAVING: filter on the AGGREGATED result --------------------------
-- "customers who ordered at least twice"
SELECT
    customer,
    COUNT(*) AS order_count
  FROM orders
  GROUP BY customer
 HAVING COUNT(*) >= 2
  ORDER BY order_count DESC, customer;

-- Expected result:
-- customer | order_count
-- ---------+-------------
-- Acme     |           3
-- Globex   |           2
-- Initech  |           2
-- Umbrella |           2

-- "customers whose TOTAL spending exceeds 150"
SELECT customer, SUM(amount) AS total
  FROM orders
  GROUP BY customer
 HAVING SUM(amount) > 150
  ORDER BY total DESC;

-- Expected result:
-- customer | total
-- ---------+-------
-- Globex   | 240.0
-- Acme     | 230.0
-- Initech  | 185.0

-- ---------------------------------------------------------------
-- 4. WHERE vs HAVING, together ----------------------------------------
-- WHERE filters individual rows FIRST (before grouping),
-- HAVING filters the resulting groups.
--
-- "per-customer totals counting only ACTIVE orders,
--  and only customers with 2+ active orders"
SELECT
    customer,
    COUNT(*)      AS active_orders,
    SUM(amount)   AS active_total
  FROM orders
 WHERE cancelled = 0          -- rows: drop cancelled BEFORE grouping
  GROUP BY customer
 HAVING COUNT(*) >= 2         -- groups: keep only 2+ active orders
  ORDER BY active_total DESC;

-- Expected result:
-- customer | active_orders | active_total
-- ---------+---------------+-------------
-- Globex   |             2 |        240.0
-- Acme     |             2 |        200.0
-- Initech  |             2 |        185.0

-- Same query WITHOUT the WHERE: Acme would have 3 orders (230.0)
-- and Umbrella 2 (15.0) — showing WHERE changes what gets grouped.

-- ---------------------------------------------------------------
-- 5. Multi-column GROUP BY ----------------------------------------------
-- One row per (customer, region) pair.
SELECT
    customer,
    region,
    COUNT(*)      AS orders,
    SUM(amount)   AS total
  FROM orders
 WHERE cancelled = 0
  GROUP BY customer, region
  ORDER BY customer, region;

-- Expected result:
-- customer | region | orders | total
-- ---------+--------+--------+-------
-- Acme     | EU     |      2 |  200.0
-- Globex   | EU     |      1 |  200.0
-- Globex   | US     |      1 |   40.0
-- Hooli    | EU     |      1 |   60.0
-- Initech  | US     |      2 |  185.0
-- Umbrella | US     |      1 |   10.0

-- ---------------------------------------------------------------
-- 6. Common pitfall: bare columns in SELECT -------------------------------
-- This is INVALID on strict engines (and wrong on lenient ones):
--
--   SELECT customer, amount, COUNT(*) FROM orders GROUP BY customer;
--
-- `amount` is neither grouped nor aggregated — which row's amount
-- would it show? The answer "it depends" is exactly why it's banned.
-- Fix: aggregate it (SUM(amount)) or add it to GROUP BY.

-- Cheat sheet:
--   WHERE    -> before GROUP BY (row-level filter)
--   HAVING   -> after  GROUP BY (group-level filter, aggregates ok)
--   GROUP BY -> the columns that define "a group"
--   SELECT   -> grouped columns + aggregates only
