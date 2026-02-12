## 2024-05-22 - [GitHub Actions Dependency Management]
**Learning:** The GitHub Actions workflow `tests.yml` installs dependencies manually via `pip install` rather than using `requirements.txt`. This means any new dependency required for tests (like `aiohttp`) must be explicitly added to the workflow file, or tests will fail with `ModuleNotFoundError`.
**Action:** When adding new Python dependencies that are used in tests, always update `.github/workflows/tests.yml` to include them in the installation step.
