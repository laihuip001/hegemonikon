## 2025-05-15 - Glassmorphism Accessibility Pattern
**Learning:** Glassmorphism cards with complex content are often implemented as divs. To make them accessible without breaking layout, add role='button', tabindex='0', aria-label, and keydown handlers (Enter/Space).
**Action:** Use this pattern for all interactive glass-cards instead of replacing them with <button> tags which reset flex/grid styles.
