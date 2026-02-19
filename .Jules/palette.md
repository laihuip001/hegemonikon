# Palette's Journal

## 2025-10-27 - Custom Toggle Buttons
**Learning:** Custom buttons used as toggle chips (e.g., in search filters) often lack state indication for screen readers. Using `active` class is visual-only.
**Action:** Always add `aria-pressed="true/false"` to custom toggle buttons and update this attribute in the click handler alongside the visual class.
