-- Topic: WHERE filtering basics — IN, BETWEEN, LIKE, NULL handling.
--
-- Concepts:
--   AND / OR / NOT boolean logic
--   IN: membership in a list
--   BETWEEN: inclusive range
--   LIKE: pattern matching with % and _ wildcards
--   IS NULL / IS NOT NULL (never use = NULL!)
--
-- Filtering is how you turn "the whole table" into "the rows I
-- care about". These five tools cover most everyday queries.
--
-- Works on: PostgreSQL, SQLite, MySQL 8+, SQL Server, Oracle.

-- ---------------------------------------------------------------
-- 1. Sample data: a small product catalog
-- ---------------------------------------------------------------
CREATE TABLE products (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       REAL NOT NULL,
    in_stock    INTEGER NOT NULL,   -- 0 or 1 (SQLite boolean style)
    release_year INTEGER            -- NULL = unreleased
);

INSERT INTO products (id, name, category, price, in_stock, release_year) VALUES
    (1,  'Mechanical Keyboard', 'peripherals', 89.99,  1, 2024),
    (2,  'Wireless Mouse',      'peripherals', 24.50,  1, 2023),
    (3,  'USB-C Hub',           'peripherals', 39.00,  0, 2024),
    (4,  '27" Monitor',         'displays',   219.00, 1, 2025),
    (5,  'Webcam',              'peripherals', 59.99,  0, 2023),
    (6,  'Laptop Stand',        'accessories', 34.00,  1, 2022),
    (7,  'Noise-Cancelling Headphones', 'audio', 149.00, 1, 2025),
    (8,  'Desk Mat',            'accessories', 19.99,  1, NULL);

-- ---------------------------------------------------------------
-- 2. Basic comparisons + boolean logic
-- ---------------------------------------------------------------
SELECT name, price
  FROM products
 WHERE price < 50 AND in_stock = 1
  ORDER BY price;

-- Expected result:
-- name          | price
-- --------------+-------
-- Desk Mat      |  19.99
-- Wireless Mouse|  24.50
-- Laptop Stand  |  34.00

-- ---------------------------------------------------------------
-- 3. IN: membership in an explicit list
-- ---------------------------------------------------------------
SELECT name, category
  FROM products
 WHERE category IN ('peripherals', 'audio')
  ORDER BY name;

-- Expected result (7 rows minus displays/accessories):
-- Desk-free list: Webcam, USB-C Hub, Wireless Mouse,
--                Mechanical Keyboard, Noise-Cancelling Headphones
-- i.e. 5 rows from peripherals + audio

-- ---------------------------------------------------------------
-- 4. BETWEEN: inclusive range (both endpoints included)
-- ---------------------------------------------------------------
SELECT name, price
  FROM products
 WHERE price BETWEEN 30 AND 90
  ORDER BY price;

-- Expected result:
-- name                  | price
-- ----------------------+-------
-- Laptop Stand          |  34.00
-- USB-C Hub             |  39.00
-- Webcam                |  59.99
-- Mechanical Keyboard   |  89.99

-- ---------------------------------------------------------------
-- 5. LIKE: pattern matching
-- ---------------------------------------------------------------
-- % matches any sequence (including none), _ matches one character.
SELECT name
  FROM products
 WHERE name LIKE '%Hub%'          -- %Hub%: "Hub" anywhere
  ORDER BY name;

-- Expected: USB-C Hub

SELECT name
  FROM products
 WHERE name LIKE 'W%'             -- starts with W
  ORDER BY name;

-- Expected: Webcam, Wireless Mouse

SELECT name
  FROM products
 WHERE UPPER(name) LIKE '%WEB%'   -- case-insensitive-ish trick
  ORDER BY name;

-- Expected: Webcam
-- (Real case-insensitivity: ILIKE in PostgreSQL,
--  LOWER() on both sides elsewhere.)

-- ---------------------------------------------------------------
-- 6. NULLs: the classic trap
-- ---------------------------------------------------------------
-- release_year IS NULL means "unreleased". The row with id=8.
-- WARNING: `release_year = NULL` matches NOTHING — comparison with
-- NULL is never true; you must use IS NULL.
SELECT name, release_year
  FROM products
 WHERE release_year IS NULL;

-- Expected result:
-- name     | release_year
-- ---------+-------------
-- Desk Mat | NULL

-- The other side: everything that HAS a release year.
SELECT COUNT(*) AS released_count
  FROM products
 WHERE release_year IS NOT NULL;

-- Expected: 7

-- ---------------------------------------------------------------
-- 7. Combining everything: a realistic filter
-- ---------------------------------------------------------------
-- "affordable, stocked peripherals or audio, released 2024 or later"
SELECT name, category, price
  FROM products
 WHERE price <= 100
   AND in_stock = 1
   AND category IN ('peripherals', 'audio')
   AND (release_year IS NULL OR release_year >= 2024)
  ORDER BY price;

-- Expected result:
-- name          | category    | price
-- --------------+-------------+-------
-- Mech Keyboard | peripherals |  89.99
-- (Wireless Mouse is excluded: released 2023, before the 2024 cutoff.)

-- Cheat sheet:
--   IN (a, b, c)        ==  x = a OR x = b OR x = c
--   BETWEEN a AND b     ==  x >= a AND x <= b   (inclusive!)
--   LIKE 'p%'           ==  starts with p
--   IS NULL             the ONLY correct null test
--   AND/OR: AND binds tighter than OR — use parentheses to be sure
