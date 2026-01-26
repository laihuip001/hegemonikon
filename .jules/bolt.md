## 2026-01-26 - [Parallel Processing with LanceDB]
**Learning:** `lancedb` is not fork-safe. When parallelizing scripts that import `lancedb` (even if the worker doesn't use it directly but imports it), `multiprocessing` must use the `spawn` context to avoid warnings and potential instability.
**Action:** Always use `multiprocessing.get_context("spawn")` when using `ProcessPoolExecutor` in scripts involving `lancedb`.
