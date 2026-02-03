## 2025-02-18 - LanceDB Search Defaults
**Learning:** `table.search(query)` in LanceDB defaults to vector search. If the table only has FTS index and no vector column, this raises `ValueError`.
**Action:** Always specify `query_type="fts"` when performing full-text search, or check schema before searching.
