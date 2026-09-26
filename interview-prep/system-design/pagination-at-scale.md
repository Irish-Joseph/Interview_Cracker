# Pagination at Scale

### 🟡 Q. Offset pagination or cursor pagination: which do you choose for a large changing feed?

**Answer.** Use cursor pagination for a large, frequently changing feed. Offset pagination is simple and supports jumping to a page, but deep offsets scan skipped rows and concurrent inserts can create duplicates or gaps.

A cursor encodes the last row's stable sort key, such as `(created_at, id)`, and the next query asks for rows after that tuple. The ID is the tie-breaker that makes ordering total.

Treat cursors as opaque, versioned, and tamper-resistant. Cursor pagination is not a snapshot: updates to sort keys can still move records. If snapshot consistency matters, bind the cursor to a snapshot/version or materialize results, accepting added storage.
