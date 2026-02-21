## 2024-05-22 - Combined Render Functions State Collision
**Learning:** When multiple render functions (e.g., `renderRouteItems`, `renderWFItems`) each manage their own "active" state (index 0), combining their output results in multiple active items visually.
**Action:** Use a post-render cleanup pass to enforce a single global active state across the combined list, rather than relying on individual render functions to know their global context.
