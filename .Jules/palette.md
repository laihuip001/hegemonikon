# Palette's Journal

## 2026-01-25 - Standardized CLI Output
**Learning:** CLI tools lacked consistent visual feedback (colors/emojis), making it hard to distinguish errors from info.
**Action:** Created `mekhane.anamnesis.ux_utils` with semantic print functions (`print_success`, `print_error`, etc.) and graceful `termcolor` fallback. Use this for all future CLI tools.
