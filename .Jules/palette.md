# Palette Journal

## 2026-01-29 - CLI Visual Hierarchy
**Learning:** CLI tools often lack visual hierarchy, making it hard to scan important information vs metadata. Using simple colors (dim for metadata, bold/cyan for headers) and icons (✔, ⚠) dramatically improves scannability without adding heavy dependencies.
**Action:** Standardize CLI output using a `ux_utils` module with semantic print helpers (`print_success`, `print_dim`, etc.) that gracefully degrade in non-TTY environments.
