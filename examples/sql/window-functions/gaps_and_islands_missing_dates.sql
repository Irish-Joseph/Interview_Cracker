-- Topic: Gaps and islands — finding missing dates in a time series.
--
-- Concepts:
--   Window functions to build consecutive "runs" (islands)
--   The classic daterow_number trick: date minus row_number
--   Generating a calendar spine (recursive CTE) for full coverage
--   LEFT JOIN of spine vs data to expose the gaps
--
-- "Gaps and islands" is a famous SQL problem family: data falls
-- into consecutive runs (islands) separated by missing values
-- (gaps). The trick that solves most of them:
--
--   FOR CONSECUTIVE DATES,  (date - row_number) IS CONSTANT.
--
-- So grouping by that constant groups each island.
--
-- Works on: PostgreSQL*, SQLite (with strftime/date), SQL Server*.
-- (*date arithmetic syntax varies; this file uses SQLite-style
--  date math, noted where engines differ)

-- ---------------------------------------------------------------
-- 1. Sample data: daily visits with a 3-day gap and a 2-day gap
-- ---------------------------------------------------------------
CREATE TABLE visits (
    visit_date DATE NOT NULL PRIMARY KEY,
    visitors   INTEGER NOT NULL
);

INSERT INTO visits (visit_date, visitors) VALUES
    ('2026-09-01', 120),
    ('2026-09-02', 135),
    ('2026-09-03',  98),
    -- gap: 09-04, 09-05 missing
    ('2026-09-06', 210),
    ('2026-09-07', 180),
    -- gap: 09-08 missing
    ('2026-09-09', 150),
    ('2026-09-10', 165);

-- ---------------------------------------------------------------
-- 2. Method A: the row-number trick (find the ISLANDS)
-- ---------------------------------------------------------------
-- Order the dates, number them 1..n, and subtract the number from
-- the date. Consecutive dates keep the SAME resulting value, so a
-- GROUP BY on it groups each island.
SELECT
    MIN(visit_date)                             AS island_start,
    MAX(visit_date)                             AS island_end,
    COUNT(*)                                    AS days_in_island,
    SUM(visitors)                               AS total_visitors
  FROM (
    SELECT
        visit_date,
        visitors,
        -- SQLite: date - integer days. (PostgreSQL: visit_date -
        -- ROW_NUMBER() OVER (...)::int; SQL Server: DATEADD)
        date(visit_date,
            '-' || ROW_NUMBER() OVER (ORDER BY visit_date) || ' days')
            AS island_key
    FROM visits
  )
  GROUP BY island_key
  ORDER BY island_start;

-- Expected result:
-- island_start | island_end | days_in_island | total_visitors
-- -------------+------------+----------------+---------------
-- 2026-09-01   | 2026-09-03 |              3 |            353
-- 2026-09-06   | 2026-09-07 |              2 |            390
-- 2026-09-09   | 2026-09-10 |              2 |            315
--
-- Three islands. The missing days are exactly what falls BETWEEN
-- one island_end and the next island_start.

-- ---------------------------------------------------------------
-- 3. Method B: calendar spine + LEFT JOIN (list the MISSING days)
-- ---------------------------------------------------------------
-- Generate EVERY date in the range, left-join the data, and keep
-- the rows with no match. The recursive CTE builds the spine.
WITH RECURSIVE
  bounds AS (
    SELECT MIN(visit_date) AS lo, MAX(visit_date) AS hi FROM visits
  ),
  calendar(d) AS (
    SELECT lo FROM bounds
    UNION ALL
    SELECT date(d, '+1 day') FROM calendar, bounds
     WHERE d < bounds.hi
  )
SELECT
    c.d            AS missing_date,
    -- context: previous and next known days, for readable output
    (SELECT MAX(visit_date) FROM visits v WHERE v.visit_date < c.d) AS prev_known,
    (SELECT MIN(visit_date) FROM visits v WHERE v.visit_date > c.d) AS next_known
  FROM calendar c
  LEFT JOIN visits v ON v.visit_date = c.d
 WHERE v.visit_date IS NULL
  ORDER BY c.d;

-- Expected result:
-- missing_date | prev_known | next_known
-- -------------+------------+-----------
-- 2026-09-04   | 2026-09-03 | 2026-09-06
-- 2026-09-05   | 2026-09-03 | 2026-09-06
-- 2026-09-08   | 2026-09-07 | 2026-09-09

-- ---------------------------------------------------------------
-- 4. Bonus: zero-fill instead of listing (for charts)
-- ---------------------------------------------------------------
-- The same spine LEFT JOIN, but keep ALL dates and coalesce to 0:
WITH RECURSIVE
  bounds AS (
    SELECT MIN(visit_date) AS lo, MAX(visit_date) AS hi FROM visits
  ),
  calendar(d) AS (
    SELECT lo FROM bounds
    UNION ALL
    SELECT date(d, '+1 day') FROM calendar, bounds
     WHERE d < bounds.hi
  )
SELECT
    c.d                                   AS day,
    COALESCE(v.visitors, 0)               AS visitors
  FROM calendar c
  LEFT JOIN visits v ON v.visit_date = c.d
  ORDER BY c.d;

-- Expected result:
-- 2026-09-01 | 120
-- 2026-09-02 | 135
-- 2026-09-03 |  98
-- 2026-09-04 |   0   <- gap filled
-- 2026-09-05 |   0   <- gap filled
-- 2026-09-06 | 210
-- 2026-09-07 | 180
-- 2026-09-08 |   0   <- gap filled
-- 2026-09-09 | 150
-- 2026-09-10 | 165

-- Rule of thumb:
--   "group consecutive values"  -> date - row_number island key
--   "enumerate the missing"     -> calendar spine + LEFT JOIN ... IS NULL
--   "fill for charts"           -> calendar spine + COALESCE(..., 0)
