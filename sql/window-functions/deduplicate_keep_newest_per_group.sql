-- Topic: Deduplicate records with ROW_NUMBER (keep the newest row per group).
--
-- Concepts:
--   ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...) for stable ordering
--   The "latest record per group" pattern
--   Why this beats a naive MAX() join (which only dedupes one column)
--   Filtering with a subquery or CTE after numbering
--
-- Scenario: a customers table where every signup event is APPENDED
-- instead of updated, so each email has several rows with different
-- snapshot dates. We want exactly one row per email: the most recent.
--
-- Works on: PostgreSQL, SQLite 3.25+, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: duplicated customers (one row per snapshot)
-- ---------------------------------------------------------------
CREATE TABLE customer_events (
    event_id  INTEGER PRIMARY KEY,
    email     TEXT NOT NULL,
    full_name TEXT NOT NULL,
    city      TEXT NOT NULL,
    snapshot  DATE NOT NULL
);

INSERT INTO customer_events (event_id, email, full_name, city, snapshot) VALUES
    (1, 'ada@example.com',    'Ada Lovelace',   'London', '2024-01-15'),
    (2, 'grace@example.com',  'Grace Hopper',   'New York','2024-02-01'),
    (3, 'ada@example.com',    'Ada Lovelace',   'Paris',  '2024-03-10'),  -- moved city
    (4, 'margaret@example.com','Margaret Hamilton','Boston','2024-01-20'),
    (5, 'grace@example.com',  'Grace Hopper',   'Arlington','2024-04-05'), -- moved city
    (6, 'ada@example.com',    'A. Lovelace',    'Berlin', '2024-05-01');  -- name fixed

-- ---------------------------------------------------------------
-- 2. Number rows per email, newest snapshot first
-- ---------------------------------------------------------------
WITH numbered AS (
    SELECT
        email,
        full_name,
        city,
        snapshot,
        ROW_NUMBER() OVER (
            PARTITION BY email
            ORDER BY snapshot DESC
        ) AS recency_rank
    FROM customer_events
)
-- ---------------------------------------------------------------
-- 3. Keep only the most recent snapshot per email
-- ---------------------------------------------------------------
SELECT email, full_name, city, snapshot
FROM numbered
WHERE recency_rank = 1
ORDER BY email;

-- Expected result (3 rows, not 6):
--   ada@example.com      | A. Lovelace    | Berlin    | 2024-05-01
--   grace@example.com    | Grace Hopper   | Arlington | 2024-04-05
--   margaret@example.com | Margaret Hamilton | Boston | 2024-01-20

-- ---------------------------------------------------------------
-- Why not GROUP BY + MAX(snapshot)?
-- ---------------------------------------------------------------
-- SELECT email, MAX(snapshot) FROM customer_events GROUP BY email
-- only returns the newest DATE. To bring back full_name/city you'd
-- join back to the table, and if two snapshots share the same date
-- the join would still return duplicates. ROW_NUMBER() numbers each
-- row unambiguously, so exactly one row survives per email even with
-- tied dates (the ordering tiebreak is deterministic if you add a
-- second key, e.g. ORDER BY snapshot DESC, event_id DESC).

-- ---------------------------------------------------------------
-- Variant: summarize how many snapshots each email accumulated
-- ---------------------------------------------------------------
SELECT
    email,
    COUNT(*) AS snapshot_count,
    MIN(snapshot) AS first_seen,
    MAX(snapshot) AS last_seen
FROM customer_events
GROUP BY email
ORDER BY snapshot_count DESC;
