## 2025-02-19 - Semantic Coloring in CLI Tools

**Learning:** CLI tools benefit significantly from semantic coloring (Success=Green, Error=Red, Info=Cyan) to reduce cognitive load when parsing text logs. Even simple prefixes like `✅` or `❌` improve scannability instantly.

**Action:** For all future CLI tools in this project, use `mekhane.anamnesis.ux_utils` to ensure consistent, scannable output. Avoid raw `print()` for status updates.
