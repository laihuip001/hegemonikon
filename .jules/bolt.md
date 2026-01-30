## 2026-01-27 - LanceDB Pydantic Schema Incompatibility
**Learning:** `lancedb` (v0.27.1) `create_table` raised `AttributeError: metadata` when passing a Pydantic v2 model class as `schema` alongside a data generator.
**Action:** Rely on data inference from the generator's first batch instead of explicitly passing the Pydantic model class as schema when using generators.
