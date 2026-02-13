# Palette's Journal

## 2024-05-22 - Accessibility in Vanilla TS
**Learning:** This project uses Vanilla TypeScript with manual DOM manipulation (creating HTML strings). This means ARIA attributes must be manually added to the HTML strings and state updates (like `aria-selected` and `aria-activedescendant`) must be handled imperatively in the logic, rather than declaratively in a framework.
**Action:** When working on `hgk-desktop`, always remember to update both the HTML generation strings and the state update functions (`updateActive`, `handleInput`) to keep ARIA states in sync.
