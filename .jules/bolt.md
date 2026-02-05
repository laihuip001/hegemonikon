## 2024-05-23 - [LanceDB Generator Ingestion]
**Learning:** LanceDB `create_table` accepts a generator, but it must yield *batches* (lists of dicts), not individual records. Passing a generator of single dicts causes a confusing error "Cannot add a single dictionary to a table. Use a list.".
**Action:** Always batch data when using generators with LanceDB to minimize memory usage while maintaining compatibility.

## 2024-05-23 - [Regex Compilation]
**Learning:** Moving repeated `re.sub` calls to module-level compiled patterns yielded ~11-13% performance improvement even on small files.
**Action:** Systematically check for re-compilation in loops during performance reviews.
