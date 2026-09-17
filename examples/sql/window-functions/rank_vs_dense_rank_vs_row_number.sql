-- Topic: Ranking functions — ROW_NUMBER vs RANK vs DENSE_RANK.
--
-- Concepts:
--   Ranking window functions
--   How ties affect each function
--   PARTITION BY for per-group rankings
--   "Top N per group" pattern (a very common interview question)
--
-- The three functions all order rows and assign a number, but they
-- differ in how they handle TIES:
--
--   ROW_NUMBER : 1, 2, 3, 4   (always unique — ties broken arbitrarily)
--   RANK       : 1, 2, 2, 4   (ties share a rank; the NEXT number jumps)
--   DENSE_RANK : 1, 2, 2, 3   (ties share a rank; no gaps in numbering)
--
-- Works on: PostgreSQL, SQLite 3.25+, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: exam scores with a tie
-- ---------------------------------------------------------------
CREATE TABLE scores (
    student_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    score      INTEGER NOT NULL
);

INSERT INTO scores (student_id, name, score) VALUES
    (1, 'Alice', 95),
    (2, 'Bob',   80),
    (3, 'Carol', 80),   -- ties with Bob
    (4, 'Dan',   70),
    (5, 'Eve',   95);   -- ties with Alice

-- ---------------------------------------------------------------
-- 2. All three ranking functions side by side
-- ---------------------------------------------------------------
SELECT
    name,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_number,
    RANK()       OVER (ORDER BY score DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
  FROM scores
  ORDER BY score DESC, name;

-- Expected result:
-- name  | score | row_number | rank | dense_rank
-- ------+-------+------------+------+-----------
-- Alice |    95 |          1 |    1 |          1
-- Eve   |    95 |          2 |    1 |          1
-- Bob   |    80 |          3 |    3 |          2
-- Carol |    80 |          4 |    3 |          2
-- Dan   |    70 |          5 |    5 |          3
--
-- Note the gap after the tie: RANK jumps 1 -> 3 (row 3 is "skipped"),
-- while DENSE_RANK goes 1 -> 2 with no gaps. ROW_NUMBER never ties:
-- its tie-break here is arbitrary, so use ORDER BY score DESC, name
-- (or another unique column) when a deterministic order matters.

-- ---------------------------------------------------------------
-- 3. Per-group ranking with PARTITION BY
-- ---------------------------------------------------------------
-- Imagine scores are per subject; rank within each subject.
CREATE TABLE subject_scores (
    student_id INTEGER,
    subject    TEXT NOT NULL,
    score      INTEGER NOT NULL,
    PRIMARY KEY (student_id, subject)
);

INSERT INTO subject_scores (student_id, subject, score) VALUES
    (1, 'Math',    90),
    (2, 'Math',    90),
    (3, 'Math',    75),
    (1, 'History', 60),
    (2, 'History', 85),
    (3, 'History', 85);

SELECT
    subject,
    student_id,
    score,
    RANK() OVER (
        PARTITION BY subject
        ORDER BY score DESC
    ) AS subject_rank
  FROM subject_scores
  ORDER BY subject, subject_rank, student_id;

-- Expected result:
-- subject | student_id | score | subject_rank
-- --------+------------+-------+-------------
-- History |          2 |    85 |            1
-- History |          3 |    85 |            1
-- History |          1 |    60 |            3
-- Math    |          1 |    90 |            1
-- Math    |          2 |    90 |            1
-- Math    |          3 |    75 |            3

-- ---------------------------------------------------------------
-- 4. Classic pattern: top 2 students per subject, ties included
-- ---------------------------------------------------------------
-- Wrap the ranking in a CTE, then filter. DENSE_RANK is usually the
-- right tool here: "top 2" means the first two DISTINCT score levels.
WITH ranked AS (
    SELECT
        subject,
        student_id,
        score,
        DENSE_RANK() OVER (
            PARTITION BY subject
            ORDER BY score DESC
        ) AS rnk
    FROM subject_scores
)
SELECT subject, student_id, score
  FROM ranked
 WHERE rnk <= 2
  ORDER BY subject, score DESC, student_id;

-- Expected result:
-- subject | student_id | score
-- --------+------------+-------
-- History |          2 |    85
-- History |          3 |    85
-- History |          1 |    60
-- Math    |          1 |    90
-- Math    |          2 |    90
-- Math    |          3 |    75

-- Rule of thumb:
--   ROW_NUMBER  -> exactly N rows, ties broken by a secondary key
--   RANK        -> "official competition" ranking (1, 2, 2, 4)
--   DENSE_RANK  -> "top N distinct values" without gaps
