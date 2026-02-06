## 2025-05-20 - CLI UX Enhancements
**Learning:** CLI tools often lack visual hierarchy, making it hard to distinguish between headers, success messages, and errors. Using color and bold text significantly improves scanability without adding complexity.
**Action:** When building CLIs, always include a simple `UX` helper class that abstracts `termcolor` or similar libraries to ensure consistent messaging (Success=Green, Error=Red, Info=Blue).
