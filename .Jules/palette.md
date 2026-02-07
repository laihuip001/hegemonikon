## 2026-02-07 - [Keyboard Accessibility for Interactive Cards]
**Learning:** Interactive elements implemented as `div`s (like hub cards) are invisible to keyboard users unless they have `role="button"`, `tabindex="0"`, and proper event listeners (`keydown` for Enter/Space).
**Action:** Always audit `div` elements with `onclick` handlers and upgrade them to semantic `<button>` elements or fully accessible ARIA widgets.
