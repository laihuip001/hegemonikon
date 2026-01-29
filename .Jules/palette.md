# Palette's Journal

## 2026-01-27 - CLI UX Standardization
**Learning:** This project lacked standardized CLI feedback mechanisms (colors, spinners), leading to inconsistent and dry user experiences.
**Action:** Created `mekhane.anamnesis.ux_utils` as a central utility for ANSI colors and threaded spinners. Use this for all future CLI tools to ensure consistent, accessible (TTY-aware) feedback.
