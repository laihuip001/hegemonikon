## 2026-03-01 - Adding ARIA labels to template literal components
**Learning:** In the `hgk` frontend directory, components are rendered using vanilla TypeScript template literals instead of frameworks like React, and tests generate large unignored artifacts in `playwright-report` and `test-results`.
**Action:** When adding accessibility attributes like `aria-label` to icon-only buttons, directly modify the raw HTML template strings. Always take care to clean up and avoid committing Playwright test artifacts after verifying changes.
