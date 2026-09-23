-- Topic: Atomic UPSERT with INSERT ... ON CONFLICT.
-- Concepts: unique conflict target, excluded row, avoiding read-then-write.
-- Run: execute with SQLite 3.24+ (also validated by Python sqlite3).
-- Expected final rows: api=4, web=2.

CREATE TABLE page_views (
    page TEXT PRIMARY KEY,
    views INTEGER NOT NULL CHECK (views >= 0)
);

INSERT INTO page_views (page, views) VALUES ('api', 1);

-- excluded.views is the value that the attempted INSERT supplied.
-- The update happens in the same statement, so there is no race-prone
-- "SELECT, then maybe INSERT" gap.
INSERT INTO page_views (page, views)
VALUES ('api', 3)
ON CONFLICT (page) DO UPDATE
SET views = page_views.views + excluded.views;

INSERT INTO page_views (page, views)
VALUES ('web', 2)
ON CONFLICT (page) DO UPDATE
SET views = page_views.views + excluded.views;

SELECT page, views
FROM page_views
ORDER BY page;

-- PostgreSQL supports the same excluded-row idea. MySQL's syntax differs;
-- do not assume an UPSERT is portable merely because INSERT is portable.
