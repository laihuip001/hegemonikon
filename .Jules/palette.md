## 2026-02-11 - [Accessibility in Custom Components]
**Learning:** The Command Palette in `hgk-desktop` was implemented entirely with `div` elements and CSS classes for selection, completely bypassing keyboard semantics for screen readers. This indicates a pattern of custom UI components needing explicit ARIA role management (especially `combobox` and `listbox` patterns).
**Action:** When auditing other custom interactive components in `hgk-desktop`, prioritize checking for `role`, `aria-activedescendant`, and keyboard interaction semantics.
