## 2026-02-08 - Optimized FEP Agent Matrix Generation
**Learning:** Initializing large multi-dimensional arrays (48x48x7) using nested Python loops is significantly slower (~7ms) than using `numpy` vectorized operations (~0.16ms).
**Action:** Always prefer `numpy` broadcasting and slicing for matrix initialization, especially when the matrix dimensions are fixed and known.
