1. **Import `logging` module in `mekhane/ccl/semantic_matcher.py`**:
   - Add `import logging` at the top of the file alongside existing imports.
2. **Initialize a logger in `mekhane/ccl/semantic_matcher.py`**:
   - Create a module-level logger: `logger = logging.getLogger(__name__)`.
3. **Add proper error handling for `SentenceTransformer` initialization**:
   - In the `__init__` method of `SemanticMacroMatcher`, replace the `pass` statement in the `except Exception:` block with `logger.warning(f"Failed to initialize SentenceTransformer: {e}")` (capturing the exception as `e`).
4. **Complete pre commit steps**:
   - Complete pre commit steps to make sure proper testing, verifications, reviews and reflections are done.
5. **Submit the change**:
   - Submit the change with a descriptive branch and commit message.
