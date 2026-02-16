# Palette's Journal

## 2026-02-16 - Command Palette State Management
**Learning:** The custom Command Palette had decentralized active state logic (in each render function), causing multiple items to be active simultaneously and making ARIA state management difficult.
**Action:** Centralize active state management in a single function (`updateActive`) that handles both visual classes and ARIA attributes (`aria-selected`, `aria-activedescendant`), ensuring a single source of truth.
