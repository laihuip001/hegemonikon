## 2024-05-22 - Optimizing d3-force with Three.js
**Learning:** Directly binding Three.js mesh updates to every frame (requestAnimationFrame) is wasteful if the underlying physics simulation (d3-force) has stabilized.
**Action:** Always wrap position updates in `if (simulation.alpha() > threshold)` to skip redundant matrix calculations and GPU bus transfers when the graph is static.
