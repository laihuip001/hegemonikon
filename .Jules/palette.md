## 2025-02-18 - CLI UX Standardization
**Learning:** CLI tools in this repo (`mekhane`) lacked consistent visual feedback. Created `ux_utils.py` as a centralized, lightweight wrapper around `termcolor` with semantic functions (`print_success`, `print_error`, etc.).
**Action:** Use `mekhane.anamnesis.ux_utils` for all future CLI output to ensure consistent styling and graceful degradation in non-TTY environments.
