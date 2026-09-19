-- Topic: Set operations - UNION, UNION ALL, INTERSECT and EXCEPT.
--
-- Joins combine tables SIDEWAYS, adding columns. Set operations stack them
-- VERTICALLY, combining rows from queries that share a column shape. Reaching
-- for the right one often replaces a tangle of OUTER JOINs and NULL checks.
--
-- Concepts:
-- - UNION removes duplicates; UNION ALL keeps them (and is much cheaper)
-- - INTERSECT: rows in both results
-- - EXCEPT (MINUS on Oracle): rows in the first result but not the second
-- - The rules: same column COUNT, compatible types, names come from the first
-- - ORDER BY applies to the whole result and goes last
-- - How NULLs behave: set operations treat NULL as equal to NULL
-- - Set operations vs the equivalent JOIN / EXISTS forms
--
-- Dialect: SQLite. UNION/UNION ALL/INTERSECT/EXCEPT are standard and work on
-- PostgreSQL, SQL Server and modern MySQL (8.0.31+ for INTERSECT/EXCEPT).
-- Oracle spells EXCEPT as MINUS.

DROP TABLE IF EXISTS newsletter_subscribers;
DROP TABLE IF EXISTS app_users;

CREATE TABLE newsletter_subscribers (email TEXT, signed_up TEXT);
CREATE TABLE app_users            (email TEXT, plan TEXT);

INSERT INTO newsletter_subscribers (email, signed_up) VALUES
    ('ada@example.com',    '2026-01-04'),
    ('grace@example.com',  '2026-01-11'),
    ('alan@example.com',   '2026-02-02'),
    ('katherine@example.com', '2026-02-20'),
    ('ada@example.com',    '2026-03-01');   -- signed up twice

INSERT INTO app_users (email, plan) VALUES
    ('ada@example.com',   'pro'),
    ('alan@example.com',  'free'),
    ('marie@example.com', 'pro');

-- ---------------------------------------------------------------------------
-- 1. UNION vs UNION ALL
--
-- UNION must DEDUPLICATE, which means sorting or hashing the whole result.
-- UNION ALL just concatenates. If you know the inputs are disjoint, or you
-- want the duplicates, UNION ALL is the cheaper and more honest choice.
-- ---------------------------------------------------------------------------
SELECT 'UNION (distinct)' AS variant, COUNT(*) AS rows FROM (
    SELECT email FROM newsletter_subscribers
    UNION
    SELECT email FROM app_users
)
UNION ALL
SELECT 'UNION ALL (keeps duplicates)', COUNT(*) FROM (
    SELECT email FROM newsletter_subscribers
    UNION ALL
    SELECT email FROM app_users
);

-- The distinct list of everyone we can contact, in one query.
SELECT email FROM newsletter_subscribers
UNION
SELECT email FROM app_users
ORDER BY email;          -- ORDER BY belongs to the WHOLE result, so it goes last

-- ---------------------------------------------------------------------------
-- 2. INTERSECT - in both
--
-- "Subscribers who are also app users." Note INTERSECT also deduplicates:
-- ada appears twice in the subscriber table but once here.
-- ---------------------------------------------------------------------------
SELECT email FROM newsletter_subscribers
INTERSECT
SELECT email FROM app_users
ORDER BY email;

-- ---------------------------------------------------------------------------
-- 3. EXCEPT - in the first, not the second
--
-- Order matters, unlike UNION and INTERSECT. These two ask opposite questions.
-- ---------------------------------------------------------------------------
SELECT 'subscribed but never signed up' AS segment, email FROM (
    SELECT email FROM newsletter_subscribers
    EXCEPT
    SELECT email FROM app_users
)
UNION ALL
SELECT 'app user but not subscribed', email FROM (
    SELECT email FROM app_users
    EXCEPT
    SELECT email FROM newsletter_subscribers
)
ORDER BY segment, email;

-- ---------------------------------------------------------------------------
-- 4. The same questions as JOINs
--
-- INTERSECT and EXCEPT are usually clearer, but the JOIN forms scale better
-- when you need COLUMNS from both sides rather than just the shared key.
-- ---------------------------------------------------------------------------

-- INTERSECT, as an inner join. Note the DISTINCT: the join would otherwise
-- emit ada twice, once per subscriber row. INTERSECT deduplicates for you.
SELECT DISTINCT s.email, u.plan
FROM newsletter_subscribers s
JOIN app_users u ON u.email = s.email
ORDER BY s.email;

-- EXCEPT, as an anti-join. This is the form to reach for when you also want
-- columns from the left table.
SELECT DISTINCT s.email, s.signed_up
FROM newsletter_subscribers s
LEFT JOIN app_users u ON u.email = s.email
WHERE u.email IS NULL
ORDER BY s.email;

-- ---------------------------------------------------------------------------
-- 5. The rules, and NULL
--
-- Both sides must have the same NUMBER of columns and compatible types.
-- Column NAMES come from the FIRST query; the second's are ignored.
-- ---------------------------------------------------------------------------
SELECT email AS contact, 'newsletter' AS source FROM newsletter_subscribers
UNION
SELECT email, 'app' FROM app_users          -- these names are discarded
ORDER BY contact, source
LIMIT 6;

-- NULL handling is the surprise. In a WHERE clause NULL = NULL is unknown,
-- but set operations compare rows for DISTINCT-ness, where two NULLs ARE
-- considered the same. So UNION collapses duplicate NULL rows.
SELECT 'union collapses NULLs' AS note, COUNT(*) AS rows FROM (
    SELECT NULL AS v
    UNION
    SELECT NULL
)
UNION ALL
SELECT 'union all keeps them', COUNT(*) FROM (
    SELECT NULL AS v
    UNION ALL
    SELECT NULL
)
UNION ALL
SELECT 'intersect matches NULL to NULL', COUNT(*) FROM (
    SELECT NULL AS v
    INTERSECT
    SELECT NULL
);

-- ---------------------------------------------------------------------------
-- Results (verified on SQLite 3.45)
-- ---------------------------------------------------------------------------
--
-- 1. UNION (distinct)              -> 5    (ada, grace, alan, katherine, marie)
--    UNION ALL (keeps duplicates)  -> 8    (5 subscriber rows + 3 app rows)
--
--    all contacts: ada, alan, grace, katherine, marie
--
-- 2. INTERSECT: ada@example.com, alan@example.com
--    (ada appears ONCE, though she subscribed twice)
--
-- 3. subscribed but never signed up : grace@example.com, katherine@example.com
--    app user but not subscribed    : marie@example.com
--
-- 4. inner join   -> ada/pro, alan/free
--    anti-join    -> grace 2026-01-11, katherine 2026-02-20
--
-- 5. union collapses NULLs           -> 1
--    union all keeps them            -> 2
--    intersect matches NULL to NULL  -> 1
--
--    That last one is the point worth remembering: in a WHERE clause
--    NULL = NULL is unknown, but set operations use DISTINCT-style
--    comparison, where NULL is equal to NULL.
