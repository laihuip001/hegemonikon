## 2024-05-20 - Add ARIA Labels to Icon-Only Buttons
**Learning:** Many icon-only utility buttons across the interface (like chat clear, settings, rail navigation) lack accessible names, making navigation for screen readers difficult.
**Action:** Systematically add `aria-label`s to icon-only buttons, even when a `title` attribute is present, to ensure proper accessibility for all users.
