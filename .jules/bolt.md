## 2024-05-22 - Static Geometry Updates in Render Loop
**Learning:** Continuous updates to Three.js geometry buffers (e.g., `setXYZ`, `needsUpdate=true`) in a `requestAnimationFrame` loop are extremely costly, even if values haven't changed.
**Action:** Always wrap geometry/position updates in a check for simulation stability (e.g., `alpha > 0.001`) or dirty flags to avoid redundant CPU-GPU bus traffic.
