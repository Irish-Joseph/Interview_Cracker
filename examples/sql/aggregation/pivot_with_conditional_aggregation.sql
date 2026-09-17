-- Topic: Pivot rows into columns with conditional aggregation.
--
-- Concepts:
--   CASE expressions inside aggregate functions
--   GROUP BY as the "one output row per group" engine
--   Building a transpose/pivot without a PIVOT clause
--   COALESCE for missing combinations
--
-- "Pivoting" means turning values that live in ROWS into separate
-- COLUMNS. Many engines (SQL Server, Oracle) have a PIVOT keyword;
-- plain SQL does it with aggregates + CASE, which works everywhere.
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: long format (one row per measurement)
-- ---------------------------------------------------------------
CREATE TABLE measurements (
    sensor   TEXT NOT NULL,
    metric   TEXT NOT NULL,   -- 'temp' or 'humidity'
    reading  REAL NOT NULL,
    period   TEXT NOT NULL    -- 'morning' | 'evening'
);

INSERT INTO measurements (sensor, metric, period, reading) VALUES
    ('room-a', 'temp',     'morning', 21.5),
    ('room-a', 'temp',     'evening', 23.0),
    ('room-a', 'humidity', 'morning', 40.0),
    ('room-b', 'temp',     'morning', 19.5),
    ('room-b', 'temp',     'evening', 22.5),
    ('room-c', 'temp',     'morning', 20.0);
    -- note: room-c has NO evening row and no humidity data

-- ---------------------------------------------------------------
-- 2. Pivot: one row per sensor, one column per metric
-- ---------------------------------------------------------------
-- The trick: for each (metric, period) combination we want, write
-- an aggregate that picks up only that combination's rows and
-- returns NULL for everything else.
SELECT
    sensor,
    MAX(CASE WHEN metric = 'temp'     AND period = 'morning' THEN reading END) AS temp_morning,
    MAX(CASE WHEN metric = 'temp'     AND period = 'evening' THEN reading END) AS temp_evening,
    MAX(CASE WHEN metric = 'humidity' AND period = 'morning' THEN reading END) AS humidity_morning
  FROM measurements
  GROUP BY sensor
  ORDER BY sensor;

-- Expected result:
-- sensor | temp_morning | temp_evening | humidity_morning
-- -------+--------------+--------------+-----------------
-- room-a |         21.5 |         23.0 |            40.0
-- room-b |         19.5 |         22.5 |             NULL
-- room-c |         20.0 |          NULL |             NULL
--
-- Why MAX and not SUM? We know there is at most ONE matching row
-- per group, so MAX simply "lifts" that single value into the
-- group. (SUM would give the same result here but would silently
-- add values if duplicates ever appeared — MAX is safer for pivots.)
-- Missing combinations become NULL; wrap in COALESCE(..., 0) if
-- zeros are preferred.

-- ---------------------------------------------------------------
-- 3. Aggregating across many rows per cell: monthly sales pivot
-- ---------------------------------------------------------------
-- Here each cell legitimately holds a SUM (many orders per month).
CREATE TABLE orders (
    order_id  INTEGER PRIMARY KEY,
    customer  TEXT NOT NULL,
    month     TEXT NOT NULL,  -- '2026-07' | '2026-08' | '2026-09'
    amount    REAL NOT NULL
);

INSERT INTO orders (customer, month, amount) VALUES
    ('Acme',  '2026-07', 100.0),
    ('Acme',  '2026-07',  50.0),
    ('Acme',  '2026-08',  75.0),
    ('Globex','2026-07',  30.0),
    ('Globex','2026-09',  90.0),
    ('Globex','2026-09',  10.0);

SELECT
    customer,
    COALESCE(SUM(CASE WHEN month = '2026-07' THEN amount END), 0) AS jul,
    COALESCE(SUM(CASE WHEN month = '2026-08' THEN amount END), 0) AS aug,
    COALESCE(SUM(CASE WHEN month = '2026-09' THEN amount END), 0) AS sep,
    SUM(amount)                                                    AS total
  FROM orders
  GROUP BY customer
  ORDER BY customer;

-- Expected result:
-- customer | jul  | aug | sep | total
-- ---------+------+-----+-----+------
-- Acme     | 150  |  75 |   0 | 225
-- Globex   |  30  |   0 | 100 | 130

-- ---------------------------------------------------------------
-- 4. The reverse operation: unpivot (columns -> rows)
-- ---------------------------------------------------------------
-- The inverse of a pivot is often needed when loading data that
-- arrived wide. A SELECT/UNION ALL subquery broadcasts rows.
SELECT
    customer, month, amount
  FROM (
        SELECT 'Acme'   AS customer, '2026-07' AS month, 150.0 AS amount
    UNION ALL SELECT 'Acme',   '2026-08',  75.0
    UNION ALL SELECT 'Globex', '2026-07',  30.0
    UNION ALL SELECT 'Globex', '2026-09', 100.0
       )
  ORDER BY customer, month;

-- Round-trip check: this output has the same shape as the raw
-- `orders` table after aggregation — pivots and unpivots are
-- inverses when no information is lost.

-- Rule of thumb:
--   fixed, few columns  -> conditional aggregation (this file)
--   many/unknown cols   -> engine PIVOT/UNPIVOT or app-side reshape
