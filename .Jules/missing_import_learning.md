## 2024-05-22 - [NameError in CI]
**Learning:** Local development environments (or linting configurations) might implicitly allow or miss missing imports that stricter CI environments catch. In this case, `time` was used in `hermeneus/src/prover.py` but not imported, causing a `NameError` in the CI test run.
**Action:** Always verify imports, especially for standard library modules like `time`, `json`, etc., when using them in code.
