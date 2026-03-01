## 2024-03-01 - Icon-only buttons accessibility
**Learning:** Icon-only buttons that rely purely on `title` attributes for tooltips are insufficient for robust screen reader accessibility. They must also include explicit `aria-label` attributes to ensure screen readers correctly interpret and announce the button's function.
**Action:** Always verify that every icon-only button rendered in the DOM includes an appropriate `aria-label`, even if it already has a `title` tooltip.
