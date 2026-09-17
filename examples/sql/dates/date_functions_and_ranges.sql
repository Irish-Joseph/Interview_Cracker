-- Topic: Working with dates - truncating, bucketing, and filtering ranges.
--
-- Date handling is where portable SQL breaks down fastest: every engine spells
-- these differently. The IDEAS below transfer everywhere; the function names
-- do not, so each section notes the equivalents.
--
-- Concepts:
-- - Why "WHERE DATE(created_at) = '...'" is a performance bug, and the fix
-- - Half-open ranges [start, end) and why they beat BETWEEN for timestamps
-- - Bucketing rows by month for a report
-- - Age / duration between two dates
-- - Generating a complete date series so empty periods still appear
--
-- Dialect: written for SQLite. Equivalents are noted per section for
-- PostgreSQL, MySQL and SQL Server.

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    id         INTEGER PRIMARY KEY,
    customer   TEXT    NOT NULL,
    placed_at  TEXT    NOT NULL,   -- ISO-8601 'YYYY-MM-DD HH:MM:SS'
    amount     INTEGER NOT NULL    -- pence, to avoid floating point money
);

INSERT INTO orders (id, customer, placed_at, amount) VALUES
    (1, 'ada',   '2026-01-15 09:30:00', 1200),
    (2, 'grace', '2026-01-31 23:59:59', 4500),
    (3, 'ada',   '2026-02-01 00:00:01',  800),
    (4, 'alan',  '2026-02-14 12:00:00', 2200),
    (5, 'grace', '2026-02-28 18:45:00',  600),
    (6, 'ada',   '2026-04-02 08:15:00', 3100),
    (7, 'alan',  '2026-04-30 21:10:00',  950);

-- ---------------------------------------------------------------------------
-- 1. Extracting parts of a date
--
-- SQLite:     strftime('%Y', placed_at)
-- PostgreSQL: EXTRACT(YEAR FROM placed_at)  or  DATE_TRUNC('month', ...)
-- MySQL:      YEAR(placed_at), DATE_FORMAT(placed_at, '%Y-%m')
-- SQL Server: DATEPART(YEAR, placed_at), FORMAT(placed_at, 'yyyy-MM')
-- ---------------------------------------------------------------------------
SELECT
    id,
    placed_at,
    strftime('%Y', placed_at)     AS year,
    strftime('%m', placed_at)     AS month,
    strftime('%Y-%m', placed_at)  AS year_month,
    strftime('%w', placed_at)     AS weekday,   -- 0 = Sunday
    date(placed_at)               AS date_only,
    time(placed_at)               AS time_only
FROM orders
ORDER BY id
LIMIT 3;

-- ---------------------------------------------------------------------------
-- 2. The range filter that kills your index
--
-- This works, but wrapping the column in a function means the engine must
-- compute it for EVERY row -- no index on placed_at can be used:
--
--     WHERE strftime('%Y-%m', placed_at) = '2026-02'
--
-- Instead, leave the column bare and bound it with a HALF-OPEN range.
-- Half-open ([start, end)) is important: BETWEEN is inclusive at both ends,
-- so BETWEEN '2026-02-01' AND '2026-02-28' silently drops everything after
-- midnight on the 28th, and '2026-02-28 18:45:00' is exactly such a row.
-- ---------------------------------------------------------------------------
SELECT 'BETWEEN (wrong for timestamps)' AS method, COUNT(*) AS matched
FROM orders
WHERE placed_at BETWEEN '2026-02-01' AND '2026-02-28'
UNION ALL
SELECT 'half-open range (correct)', COUNT(*)
FROM orders
WHERE placed_at >= '2026-02-01'
  AND placed_at <  '2026-03-01';

-- The half-open form also keeps working across month lengths, leap years and
-- daylight-saving boundaries, because you never compute the last instant.

-- ---------------------------------------------------------------------------
-- 3. Bucketing by month
--
-- SQLite:     strftime('%Y-%m', placed_at)
-- PostgreSQL: DATE_TRUNC('month', placed_at)::date
-- MySQL:      DATE_FORMAT(placed_at, '%Y-%m-01')
-- SQL Server: DATEFROMPARTS(YEAR(placed_at), MONTH(placed_at), 1)
--
-- Grouping by a derived expression is fine here: the aggregate reads every
-- row anyway, so there is no index to lose.
-- ---------------------------------------------------------------------------
SELECT
    strftime('%Y-%m', placed_at) AS month,
    COUNT(*)                     AS orders,
    SUM(amount)                  AS total_pence,
    ROUND(AVG(amount), 1)        AS avg_pence,
    MIN(date(placed_at))         AS first_day,
    MAX(date(placed_at))         AS last_day
FROM orders
GROUP BY month
ORDER BY month;

-- ---------------------------------------------------------------------------
-- 4. Durations between dates
--
-- SQLite:     julianday(a) - julianday(b)          -> days, as a float
-- PostgreSQL: a - b                                -> an interval
-- MySQL:      DATEDIFF(a, b), TIMESTAMPDIFF(unit, b, a)
-- SQL Server: DATEDIFF(day, b, a)
-- ---------------------------------------------------------------------------
SELECT
    customer,
    MIN(date(placed_at)) AS first_order,
    MAX(date(placed_at)) AS latest_order,
    CAST(julianday(MAX(placed_at)) - julianday(MIN(placed_at)) AS INTEGER)
        AS days_between_first_and_last,
    COUNT(*) AS orders
FROM orders
GROUP BY customer
ORDER BY customer;

-- Date arithmetic: SQLite uses modifiers on date()/datetime().
SELECT
    date('2026-02-14')                          AS given,
    date('2026-02-14', '+1 month')              AS plus_one_month,
    date('2026-02-14', '-7 days')               AS minus_seven_days,
    date('2026-02-14', 'start of month')        AS month_start,
    date('2026-02-14', 'start of month', '+1 month', '-1 day') AS month_end,
    date('2026-02-14', 'weekday 0')             AS next_sunday;

-- 'start of month' then '+1 month' then '-1 day' is the portable way to get
-- the last day of a month without hard-coding 28/29/30/31.

-- ---------------------------------------------------------------------------
-- 5. Reporting on a COMPLETE series, including empty months
--
-- A plain GROUP BY only returns months that have rows. March 2026 has no
-- orders, so it silently vanishes from the report -- which is usually not
-- what a business wants to see. Generate the periods, then LEFT JOIN.
--
-- SQLite:     a recursive CTE, as below
-- PostgreSQL: generate_series('2026-01-01', '2026-04-01', '1 month')
-- SQL Server: a numbers/calendar table, or a recursive CTE
-- ---------------------------------------------------------------------------
WITH RECURSIVE months(month_start) AS (
    SELECT date('2026-01-01')
    UNION ALL
    SELECT date(month_start, '+1 month')
    FROM months
    WHERE month_start < date('2026-04-01')      -- always bound the recursion
)
SELECT
    strftime('%Y-%m', m.month_start) AS month,
    COUNT(o.id)                      AS orders,
    COALESCE(SUM(o.amount), 0)       AS total_pence
FROM months m
LEFT JOIN orders o
       ON o.placed_at >= m.month_start
      AND o.placed_at <  date(m.month_start, '+1 month')
GROUP BY month
ORDER BY month;

-- Note COUNT(o.id) rather than COUNT(*): COUNT(*) counts the LEFT JOIN's
-- placeholder row and would report 1 for an empty month instead of 0.

-- ---------------------------------------------------------------------------
-- Results (verified on SQLite 3.45)
-- ---------------------------------------------------------------------------
--
-- 2. The two range filters do NOT agree:
--      BETWEEN (wrong for timestamps)  -> 2
--      half-open range (correct)       -> 3
--    BETWEEN misses order 5 at '2026-02-28 18:45:00', because the upper bound
--    '2026-02-28' is read as '2026-02-28 00:00:00'.
--
-- 3. month   | orders | total_pence | avg_pence
--    2026-01 |      2 |        5700 |    2850.0
--    2026-02 |      3 |        3600 |    1200.0
--    2026-04 |      2 |        4050 |    2025.0     <- March is MISSING
--
-- 4. customer | first_order | latest_order | days_between | orders
--    ada      | 2026-01-15  | 2026-04-02   |           76 |      3
--    alan     | 2026-02-14  | 2026-04-30   |           75 |      2
--    grace    | 2026-01-31  | 2026-02-28   |           27 |      2
--
--    date modifiers: '2026-02-14' +1 month -> 2026-03-14
--                    start of month        -> 2026-02-01
--                    month end recipe      -> 2026-02-28  (2026 is not a leap year)
--
-- 5. With the generated series, March appears as it should:
--    month   | orders | total_pence
--    2026-01 |      2 |        5700
--    2026-02 |      3 |        3600
--    2026-03 |      0 |           0     <- the point of the exercise
--    2026-04 |      2 |        4050
