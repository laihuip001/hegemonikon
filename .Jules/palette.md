# Palette's Journal

## 2026-02-23 - [Vanilla TS Template Literals Accessibility]
**Learning:** Using template literals for HTML generation bypasses accessibility linting and type checking, leading to missing `for` attributes and focus management.
**Action:** Manually audit all template strings for accessibility attributes (`aria-*`, `for`, `role`) and consider using a helper function or linting rule for raw HTML strings.
