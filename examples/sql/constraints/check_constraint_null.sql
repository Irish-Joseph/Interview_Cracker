-- Topic: CHECK constraints accept UNKNOWN unless NULL is forbidden separately.
-- Concepts: SQL three-valued logic, CHECK, NOT NULL, defensive schema design.
-- Run: execute with SQLite; final query returns loose_rows=1, strict_rows=0.

CREATE TABLE loose_scores (
    score INTEGER CHECK (score >= 0)
);

-- `NULL >= 0` is UNKNOWN, not FALSE. CHECK rejects only FALSE.
INSERT INTO loose_scores (score) VALUES (NULL);

CREATE TABLE strict_scores (
    score INTEGER NOT NULL CHECK (score >= 0)
);

-- This would fail because NOT NULL handles the absence separately:
-- INSERT INTO strict_scores (score) VALUES (NULL);

SELECT
    (SELECT COUNT(*) FROM loose_scores) AS loose_rows,
    (SELECT COUNT(*) FROM strict_scores) AS strict_rows;

-- A CHECK such as `end_at > start_at` has the same trap if either column is
-- nullable. Decide whether absence is valid; do not assume CHECK implies it.
