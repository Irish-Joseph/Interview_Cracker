# Covering Indexes

### 🟡 Q. What is a covering index, and when can it make a query much faster?

**Answer.** A covering index contains every column a query needs for filtering,
joining, and output, so the database can answer from the index without looking
up the base table rows.

For `SELECT created_at FROM orders WHERE customer_id = ?`, an index on
`(customer_id, created_at)` may cover the query. It avoids a random table-page
lookup for every match and can be a large win for selective, read-heavy paths.

It is not free: extra columns enlarge the index, reduce cache density, and make
inserts and updates more expensive. Verify an index-only scan in the query
plan, and remember that MVCC visibility rules may still force table access.
