## 2025-02-27 - [Raw HTML Templates in HGK]
**Learning:** The `hgk` frontend uses raw HTML template strings within TypeScript files (e.g., `settings.ts`). This pattern lacks automatic accessibility checks found in JSX/frameworks, making manual verification of `id`-`for` associations critical.
**Action:** When working on `hgk` views, always grep for `<label>` and ensure it has a `for` attribute matching a nearby input's `id`.
