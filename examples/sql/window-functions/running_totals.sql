-- Topic: Running totals with the SUM() window function.
--
-- Concepts:
--   Window functions (SUM OVER)
--   PARTITION BY for per-group running totals
--   ORDER BY inside the window frame
--   Frameworks: RANGE 'UNBOUNDED PRECEDING' vs ROWS
--
-- A "running total" accumulates a value over ordered rows WITHOUT
-- collapsing rows the way a normal GROUP BY aggregate does.
--
-- Works on standard SQL (PostgreSQL, MySQL 8+, SQL Server, Oracle).

-- ---------------------------------------------------------------
-- 1. Sample data: daily sales per product
-- ---------------------------------------------------------------
CREATE TABLE sales (
    sale_id    INTEGER PRIMARY KEY,
    product    TEXT    NOT NULL,
    sale_date  DATE    NOT NULL,
    amount     INTEGER NOT NULL
);

INSERT INTO sales (sale_id, product, sale_date, amount) VALUES
    (1, 'Widget', '2026-09-01', 100),
    (2, 'Widget', '2026-09-02',  50),
    (3, 'Widget', '2026-09-04', 250),
    (4, 'Gadget', '2026-09-01',  20),
    (5, 'Gadget', '2026-09-03',  80),
    (6, 'Gadget', '2026-09-05',  40);

-- ---------------------------------------------------------------
-- 2. Running total of amount per product, ordered by date
-- ---------------------------------------------------------------
-- SUM() OVER (...) computes a total that "sees" all preceding rows
-- in the partition, but returns one row per input row.
SELECT
    product,
    sale_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY product
        ORDER BY sale_date
        -- default frame: all rows from partition start up to current row
    ) AS running_total
FROM sales
ORDER BY product, sale_date;

-- Expected result:
-- product | sale_date  | amount | running_total
-- --------+------------+--------+--------------
-- Gadget  | 2026-09-01 |    20  |           20
-- Gadget  | 2026-09-03 |    80  |          100
-- Gadget  | 2026-09-05 |    40  |          140
-- Widget  | 2026-09-01 |   100  |          100
-- Widget  | 2026-09-02 |    50  |          150
-- Widget  | 2026-09-04 |   250  |          400

-- ---------------------------------------------------------------
-- 3. Difference: ROWS vs RANGE with ties in the order column
-- ---------------------------------------------------------------
-- Add a tie: two Widget sales on the same date.
INSERT INTO sales (sale_id, product, sale_date, amount) VALUES
    (7, 'Widget', '2026-09-04',  10);

-- ROWS frame: each physical row only. Tied rows get DIFFERENT totals
-- (the second tied row does not see the first).
-- RANGE frame: all *peer* rows (same sale_date) count together.
SELECT
    sale_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY product
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_rows,
    SUM(amount) OVER (
        PARTITION BY product
        ORDER BY sale_date
        RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_range
FROM sales
WHERE product = 'Widget'
ORDER BY sale_date, sale_id;

-- Expected on 2026-09-04 (amounts 250 and 10):
--   ROWS   totals: ... 150, 400, 410
--   RANGE  totals: ... 150, 410, 410   <- tied rows share the total

-- ---------------------------------------------------------------
-- 4. Bonus: gap-free running total is a classic interview question.
--    Replace `ORDER BY sale_date` with any ordering, and drop the
--    PARTITION BY clause to get a single global running total.
-- ---------------------------------------------------------------
SELECT
    sale_date,
    amount,
    SUM(amount) OVER (ORDER BY sale_date) AS global_running_total
FROM sales
ORDER BY sale_date;
