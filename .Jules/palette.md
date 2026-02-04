## 2025-01-26 - [CLI] Centralized Output Styling
**Learning:** CLI tools were using inconsistent, plain `print` statements. Standardizing on a `ux_utils` module with semantic functions (`print_success`, `print_error`) and safe `termcolor` handling ensures consistency and accessibility (fallback support).
**Action:** Use `mekhane.anamnesis.ux_utils` for all future CLI output. Avoid direct `print` for status messages.
