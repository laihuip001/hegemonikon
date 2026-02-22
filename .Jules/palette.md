## 2025-02-23 - Command Palette Accessibility
**Learning:** Custom combobox implementations require manual management of `aria-activedescendant` and `aria-selected` to ensure screen reader focus follows visual focus. Playwright's `toHaveAttribute` makes verification easy.
**Action:** Always verify custom keyboard navigation components with ARIA attribute tests.
