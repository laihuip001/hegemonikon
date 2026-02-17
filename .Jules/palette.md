## 2024-05-22 - Icon-only Buttons A11y Gap
**Learning:** The 'hgk' frontend frequently uses icon-only buttons (⚙️, 🗑️, ✕) relying solely on `title` attributes, which are insufficient for screen readers.
**Action:** Always add `aria-label` to icon-only buttons during component creation or review.
