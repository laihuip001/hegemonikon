## 2024-05-23 - Command Palette Accessibility
**Learning:** Custom command palette implementation relied entirely on CSS classes (`cp-item-active`) and DOM manipulation, lacking semantic HTML and ARIA roles, making it completely invisible to screen readers.
**Action:** When implementing custom interactive components, always start with the appropriate ARIA pattern (e.g., Combobox) and manage focus using `aria-activedescendant` alongside visual highlighting.
