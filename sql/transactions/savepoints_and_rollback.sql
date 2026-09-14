-- Savepoints allow part of a transaction to be undone without losing all work.

CREATE TABLE inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);

BEGIN TRANSACTION;

INSERT INTO inventory (product_id, product_name, quantity) VALUES
    (1, 'Keyboard', 10),
    (2, 'Mouse', 25);

-- Everything before this point remains if we roll back only to the savepoint.
SAVEPOINT before_stock_adjustment;

UPDATE inventory
SET quantity = quantity - 3
WHERE product_id = 1;

SELECT 'after adjustment' AS stage, product_name, quantity
FROM inventory
ORDER BY product_id;

-- Undo the update, but keep both inserts made earlier in the transaction.
ROLLBACK TO SAVEPOINT before_stock_adjustment;

-- RELEASE removes the savepoint name; it does not commit the transaction.
RELEASE SAVEPOINT before_stock_adjustment;

COMMIT;

SELECT 'after commit' AS stage, product_name, quantity
FROM inventory
ORDER BY product_id;

-- A full ROLLBACK would instead undo every uncommitted statement after BEGIN.
