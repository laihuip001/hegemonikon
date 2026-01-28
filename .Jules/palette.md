## 2026-01-27 - [CLI UX Standardization]
**Learning:** Python CLI tools in this repo lack a unified feedback mechanism (colors/symbols), leading to flat text output. `ux_utils.py` pattern with TTY detection is the accepted lightweight solution.
**Action:** Use `mekhane.anamnesis.ux_utils` for all future CLI output formatting instead of raw `print` or external libraries.
