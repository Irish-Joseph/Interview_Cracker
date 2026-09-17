-- Topic: Compare a row with the previous and next row using LAG() and LEAD().
--
-- Aggregates collapse rows; window functions keep every row and let it look
-- sideways at its neighbours. LAG() reaches backwards, LEAD() reaches forwards
-- within the same PARTITION BY group, in the ORDER BY order you specify.
--
-- Concepts:
-- - LAG(col, offset, default) OVER (PARTITION BY ... ORDER BY ...)
-- - Month-over-month deltas and growth percentages
-- - Detecting the exact rows where a value changed (state transitions)
-- - Measuring the gap between consecutive events per user
--
-- Dialect: standard SQL; runs as-is on SQLite 3.25+, PostgreSQL, MySQL 8+,
-- SQL Server 2012+ and Oracle.

DROP TABLE IF EXISTS monthly_revenue;

CREATE TABLE monthly_revenue (
    region  TEXT    NOT NULL,
    month   TEXT    NOT NULL,   -- YYYY-MM
    revenue INTEGER NOT NULL
);

INSERT INTO monthly_revenue (region, month, revenue) VALUES
    ('north', '2026-01', 12000),
    ('north', '2026-02', 13500),
    ('north', '2026-03', 12800),
    ('north', '2026-04', 16000),
    ('south', '2026-01',  8000),
    ('south', '2026-02',  8000),
    ('south', '2026-03',  9600),
    ('south', '2026-04', 11040);

-- ---------------------------------------------------------------------------
-- 1. Month-over-month change
--
-- LAG(revenue) is the previous row's revenue *inside the same region*.
-- The third argument supplies a default for the first row of each partition,
-- which avoids a NULL rippling through the arithmetic below.
-- ---------------------------------------------------------------------------
SELECT
    region,
    month,
    revenue,
    LAG(revenue) OVER w                     AS prev_revenue,
    revenue - LAG(revenue, 1, revenue) OVER w AS change_vs_prev,
    ROUND(
        100.0 * (revenue - LAG(revenue, 1, revenue) OVER w)
        / LAG(revenue, 1, revenue) OVER w,
        1
    )                                       AS pct_change,
    LEAD(revenue) OVER w                    AS next_revenue
FROM monthly_revenue
WINDOW w AS (PARTITION BY region ORDER BY month)
ORDER BY region, month;

-- region | month   | revenue | prev_revenue | change_vs_prev | pct_change | next_revenue
-- north  | 2026-01 |   12000 |         NULL |              0 |        0.0 |        13500
-- north  | 2026-02 |   13500 |        12000 |           1500 |       12.5 |        12800
-- north  | 2026-03 |   12800 |        13500 |           -700 |       -5.2 |        16000
-- north  | 2026-04 |   16000 |        12800 |           3200 |       25.0 |         NULL

-- ---------------------------------------------------------------------------
-- 2. Only the rows that moved
--
-- Wrap the window function in a CTE: window functions cannot appear in WHERE,
-- because WHERE runs before they are evaluated.
-- ---------------------------------------------------------------------------
WITH changes AS (
    SELECT
        region,
        month,
        revenue,
        LAG(revenue) OVER (PARTITION BY region ORDER BY month) AS prev_revenue
    FROM monthly_revenue
)
SELECT region, month, prev_revenue, revenue
FROM changes
WHERE prev_revenue IS NOT NULL
  AND revenue <> prev_revenue
ORDER BY region, month;

-- Every month except south 2026-02, which repeated 8000.

-- ---------------------------------------------------------------------------
-- 3. Detecting state transitions
--
-- A subscription log where only the rows that actually change plan matter.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS subscription_log;

CREATE TABLE subscription_log (
    user_id  INTEGER NOT NULL,
    logged_at TEXT   NOT NULL,
    plan     TEXT    NOT NULL
);

INSERT INTO subscription_log (user_id, logged_at, plan) VALUES
    (1, '2026-01-05', 'free'),
    (1, '2026-02-05', 'free'),
    (1, '2026-03-05', 'pro'),
    (1, '2026-04-05', 'pro'),
    (1, '2026-05-05', 'free'),
    (2, '2026-01-09', 'pro'),
    (2, '2026-02-09', 'team');

WITH transitions AS (
    SELECT
        user_id,
        logged_at,
        LAG(plan) OVER (PARTITION BY user_id ORDER BY logged_at) AS previous_plan,
        plan AS current_plan
    FROM subscription_log
)
SELECT user_id, logged_at, previous_plan, current_plan
FROM transitions
WHERE previous_plan IS NOT NULL
  AND previous_plan <> current_plan
ORDER BY user_id, logged_at;

-- user_id | logged_at  | previous_plan | current_plan
--       1 | 2026-03-05 | free          | pro
--       1 | 2026-05-05 | pro           | free
--       2 | 2026-02-09 | pro           | team

-- ---------------------------------------------------------------------------
-- 4. Time between consecutive events
--
-- LEAD() gives each event its successor, so the gap needs no self-join.
-- (julianday() is SQLite; use `next_at - logged_at` on PostgreSQL dates or
--  DATEDIFF on SQL Server / MySQL.)
-- ---------------------------------------------------------------------------
SELECT
    user_id,
    logged_at,
    LEAD(logged_at) OVER (PARTITION BY user_id ORDER BY logged_at) AS next_at,
    CAST(
        julianday(LEAD(logged_at) OVER (PARTITION BY user_id ORDER BY logged_at))
        - julianday(logged_at) AS INTEGER
    ) AS days_until_next
FROM subscription_log
ORDER BY user_id, logged_at;

-- The final row of each user has NULL for next_at and days_until_next,
-- which is the honest answer: that event has no successor yet.
