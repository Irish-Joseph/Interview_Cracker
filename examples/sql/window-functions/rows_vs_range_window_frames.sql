-- Topic: Window frames - ROWS vs RANGE, and why "the running total" can
--        silently jump when the ORDER BY value repeats.
--
-- Every window aggregate has a FRAME. If you do not write one, the default
-- is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW - and RANGE treats
-- rows that tie on ORDER BY as ONE logical row (a peer group). So a
-- "running total" can jump over the whole tie in one step, with no WHERE,
-- no JOIN and no warning.
--
-- Concepts:
-- - ROWS frames count PHYSICAL rows; RANGE frames count ORDER-BY VALUES
-- - tied rows are one peer group in RANGE, separate rows in ROWS
-- - the default frame, and how to pin the window to ROWS
-- - 1 PRECEDING / 1 FOLLOWING: same keywords, different windows per frame
-- - the frame is applied to the first ORDER BY term (use a numeric key)
--
-- Dialect: standard SQL; verified on SQLite 3.45 (supports ROWS and RANGE
-- framing identically to PostgreSQL, SQL Server, Oracle and MySQL 8).
-- NOTE: SQLite's RANGE offsets apply to the first ORDER BY term as a
-- numeric offset, so the frame column below is an integer day number.

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    day      INTEGER NOT NULL,   -- day number within the period
    amount   REAL    NOT NULL
);

INSERT INTO orders (order_id, day, amount) VALUES
    (1, 1, 100),
    (2, 1, 200),   -- three orders on day 1:
    (3, 1, 400),   -- the tie that makes ROWS and RANGE diverge
    (4, 2, 600),
    (5, 3, 100);

-- 1. Running total with the DEFAULT frame (RANGE .. CURRENT ROW).
--    The three day-1 orders are peers, so each of them already sees the
--    whole day: the total jumps 100 -> 700 in one step and repeats 700
--    twice before moving on. Nobody wrote "sum the day"; the frame did.
SELECT
    order_id,
    day,
    amount,
    SUM(amount) OVER (ORDER BY day) AS default_frame_total
FROM orders
ORDER BY order_id;
-- -> (1, 1, 100, 700) (2, 1, 200, 700) (3, 1, 400, 700)
--    (4, 2, 600, 1300) (5, 3, 100, 1400)

-- 2. The same query pinned to ROWS: each row sees itself plus earlier
--    PHYSICAL rows, so the total climbs one order at a time and reaches
--    700 only on the third day-1 row. This is what "running total"
--    usually means in practice.
--    Subtlety worth knowing: with a tied key the order WITHIN the tie is
--    database-dependent. If this engine ordered the day-1 tie as rows
--    1, 3, 2, the totals would read 100, 700 (row 2), 500 (row 3), 1300,
--    1400 instead. SQLite returns insertion order here, hence:
SELECT
    order_id,
    amount,
    SUM(amount) OVER (
        ORDER BY day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS rows_frame_total
FROM orders
ORDER BY order_id;
-- -> 100, 300, 700, 1300, 1400   (SQLite's insertion-order tie handling)

-- 3. 1 PRECEDING AND 1 FOLLOWING: in ROWS that is "me plus my physical
--    neighbours"; in RANGE it is "everything on my day and the adjacent
--    days". Same keywords, different windows when ties exist.
SELECT
    order_id,
    day,
    SUM(amount) OVER (
        ORDER BY day
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS rows_around,
    SUM(amount) OVER (
        ORDER BY day
        RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS range_around
FROM orders
ORDER BY order_id;
-- rows_around:  300, 700, 1200, 1100, 700   (physical neighbours)
-- range_around: 1300, 1300, 1300, 1400, 700 (day-1 peers all see days 1-2)

-- 4. The rule of thumb in one query: whenever the ORDER BY value can
--    repeat and you want physical rows, WRITE the frame. Here we aggregate
--    to days first, so the running total over days is unambiguous.
SELECT
    day,
    SUM(amount) AS day_total,
    SUM(SUM(amount)) OVER (
        ORDER BY day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_of_days
FROM orders
GROUP BY day
ORDER BY day;
-- -> (1, 700, 700) (2, 600, 1300) (3, 100, 1400)
