## 2024-05-22 - [Raw HTML Injection Accessibility]
**Learning:** This app frequently uses raw HTML string injection (e.g., `command_palette.ts`) for dynamic UI components, bypassing framework-level accessibility features. This pattern requires manual implementation of ARIA roles and focus management for every interactive component.
**Action:** When modifying any dynamic UI component in this repo, explicitly check for and add missing ARIA attributes and focus handling logic.
