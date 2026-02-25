## 2025-05-15 - Improving Accessibility of "Hint" Elements
**Learning:** Static elements like `<span>` used as interactive "hints" or "chips" are inaccessible to keyboard users and screen readers. They should be `<button>` elements with `type="button"`.
**Action:** Always use `<button type="button">` for interactive elements that trigger actions, even if they look like simple text or tags. Use CSS to reset styles (`appearance: none`, `font: inherit`, `color: inherit`) and add `:focus-visible` styles for keyboard navigation.
