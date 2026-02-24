# Palette's Journal

## 2025-02-18 - Raw HTML Templates require manual A11y
**Learning:** The `hgk` frontend uses raw HTML strings for views, which bypasses standard linter checks for accessibility (like missing `for` attributes on labels).
**Action:** Always manually verify HTML structure in `src/views/*.ts` for accessible attributes (`for`, `aria-label`, `role`) as automated tools won't catch them during coding.
