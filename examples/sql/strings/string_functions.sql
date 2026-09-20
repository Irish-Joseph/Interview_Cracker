-- Topic: String functions — length, substr, trim, case, and building strings.
--
-- Concepts:
--   LENGTH / CHAR_LENGTH   how many characters
--   SUBSTR / SUBSTRING     take a slice (1-based in SQL)
--   UPPER / LOWER / INITCAP  case transforms
--   TRIM / LTRIM / RTRIM    strip padding
--   REPLACE / LIKE          simple substitution and pattern matching
--   CONCAT / ||             build strings (portability differs)
--
-- Portability notes:
--   * SUBSTR is 1-based in PostgreSQL, SQLite, Oracle; MySQL uses SUBSTRING.
--   * `||` is the SQL-standard concatenation; use CONCAT() on older MySQL.
--   * Negative SUBSTR start ("from the end") works in PostgreSQL, SQLite
--     and Oracle; older MySQL does not.
--
-- Validated by executing the statements below in SQLite (via Python sqlite3).

CREATE TABLE authors (
    id      INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    nickname TEXT,
    site    TEXT
);

INSERT INTO authors (full_name, nickname, site) VALUES
    ('  Ada Lovelace  ', 'countess', 'ada.example.com'),
    ('Grace Hopper',     'adm',      'grace.example.com'),
    ('Alan Turing',      NULL,       'alan.example.com');

-- 1. LENGTH: how many characters (TRIM first to ignore the padding).
SELECT full_name,
       LENGTH(full_name)            AS raw_len,
       LENGTH(TRIM(full_name))      AS trimmed_len
FROM authors;
-- '  Ada Lovelace  ' -> raw 16, trimmed 12

-- 2. SUBSTR is 1-BASED: SUBSTR(x, start, len).
SELECT TRIM(full_name) AS name,
       SUBSTR(TRIM(full_name), 1, 3)  AS first3,
       SUBSTR(TRIM(full_name), -3)    AS last3      -- negative start = from end
FROM authors
WHERE full_name = 'Grace Hopper';
-- first3 'Gra', last3 'per'

-- 3. Case transforms.
SELECT TRIM(full_name) AS original,
       UPPER(TRIM(full_name))  AS upper,
       LOWER(TRIM(full_name))  AS lower
FROM authors
WHERE id = 1;
-- 'Ada Lovelace' -> 'ADA LOVELACE' / 'ada lovelace'

-- 4. LIKE: pattern matching with % (any run) and _ (one char).
SELECT TRIM(full_name) AS name
FROM authors
WHERE TRIM(full_name) LIKE 'A%';        -- starts with A
-- Ada Lovelace, Alan Turing

-- 5. REPLACE: swap a substring.
SELECT site,
       REPLACE(site, '.example.com', '.io') AS short_site
FROM authors;
-- ada.example.com -> ada.io

-- 6. CONCAT and the || operator (both work in SQLite/PostgreSQL).
SELECT TRIM(full_name) AS name,
       'dr-' || LOWER(SUBSTR(TRIM(full_name), 1, 3)) AS handle,
       CONCAT(TRIM(full_name), ' <', site, '>')       AS contact
FROM authors
WHERE nickname IS NOT NULL;
-- 'Ada Lovelace' -> handle 'dr-ada', contact 'Ada Lovelace <ada.example.com>'

-- 7. NULL handling: most string fns return NULL on NULL input.
SELECT nickname,
       UPPER(nickname) AS upper_nick
FROM authors;
-- Alan Turing has NULL nickname -> UPPER(NULL) is NULL (no error)
