# Palette's Journal

## 2026-02-08 - [Hardcoded Paths Breaker]
**Learning:** Found critical UX/portability issue: CLI tool hardcoded to `/home/makaron8426/...`. This immediately crashes for anyone else.
**Action:** Always use `Path.home()` or `.` relative paths for user-specific data.
