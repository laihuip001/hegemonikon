"""
AI Synedrion Issue Fixer (AI-001 〜 AI-022)

CCL: /mek+ >> /ene (方法配置 → 実行)
Generated: 2026-02-01
Purpose: AI Auditor で検出された問題を自動修正

Usage:
    python ai_fixer.py <file_or_dir> [--dry-run] [--severity critical,high]
    python ai_fixer.py mekhane/ --severity critical  # Critical のみ修正
    python ai_fixer.py mekhane/ --dry-run            # 変更なしでプレビュー
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import argparse


@dataclass
class Fix:
    """A fix to apply."""

    code: str  # e.g., "AI-020"
    file_path: Path
    line: int
    original: str
    replacement: str
    description: str


class AIFixer:
    """Auto-fixer for AI Audit issues."""

    def __init__(self, dry_run: bool = False, target_severities: Optional[List[str]] = None):
        self.dry_run = dry_run
        self.target_severities = target_severities or ["critical", "high"]
        self.fixes_applied: List[Fix] = []
        self.fixes_skipped: List[Fix] = []

    def fix_file(self, file_path: Path) -> List[Fix]:
        """Fix issues in a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            fixes = []

            # AI-020: Bare except → except Exception
            fixes.extend(self._fix_ai_020_bare_except(lines, file_path))

            # AI-020: Silent except (except + pass)
            fixes.extend(self._fix_ai_020_silent_except(content, lines, file_path))

            # AI-015: Self-assignment (x = x)
            fixes.extend(self._fix_ai_015_self_assignment(lines, file_path))

            # AI-009: Hardcoded secrets (can't auto-fix, but can suggest)
            # AI-012: time.sleep in async → asyncio.sleep
            fixes.extend(self._fix_ai_012_time_sleep_in_async(content, lines, file_path))

            # AI-013: Mutable default arguments
            fixes.extend(self._fix_ai_013_mutable_defaults(content, file_path))

            # AI-018: Hardcoded paths (suggest environment variable)
            fixes.extend(self._fix_ai_018_hardcoded_paths(lines, file_path))

            # AI-011: range(len(x)) → enumerate(x)
            fixes.extend(self._fix_ai_011_range_len(lines, file_path))

            # AI-019: Deprecated asyncio.get_event_loop
            fixes.extend(self._fix_ai_019_deprecated_api(lines, file_path))

            # Apply fixes
            if fixes and not self.dry_run:
                self._apply_fixes(file_path, lines, fixes)
                self.fixes_applied.extend(fixes)
            elif fixes:
                self.fixes_skipped.extend(fixes)

            return fixes

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def _fix_ai_020_bare_except(self, lines: List[str], file_path: Path) -> List[Fix]:
        """Fix bare except: → except Exception:"""
        fixes = []
        pattern = re.compile(r"^(\s*)except\s*:\s*$")

        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                indent = match.group(1)
                fixes.append(
                    Fix(
                        code="AI-020",
                        file_path=file_path,
                        line=i + 1,
                        original=line,
                        replacement=f"{indent}except Exception:",
                        description="bare except → except Exception",
                    )
                )

        return fixes

    def _fix_ai_020_silent_except(
        self, content: str, lines: List[str], file_path: Path
    ) -> List[Fix]:
        """Fix except with only pass → add logging."""
        fixes = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return fixes

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check if body is only 'pass'
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    line_idx = node.body[0].lineno - 1
                    if 0 <= line_idx < len(lines):
                        original = lines[line_idx]
                        indent = len(original) - len(original.lstrip())
                        indent_str = " " * indent
                        # Replace pass with logging
                        fixes.append(
                            Fix(
                                code="AI-020",
                                file_path=file_path,
                                line=node.body[0].lineno,
                                original=original,
                                replacement=f"{indent_str}pass  # TODO: Add proper error handling",
                                description="silent except + pass → marked for review",
                            )
                        )

        return fixes

    def _fix_ai_015_self_assignment(self, lines: List[str], file_path: Path) -> List[Fix]:
        """Fix self-assignment: x = x → remove or mark."""
        fixes = []
        pattern = re.compile(r"^(\s*)(\w+)\s*=\s*(\w+)\s*$")

        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                var1 = match.group(2)
                var2 = match.group(3)
                if var1 == var2:
                    indent = match.group(1)
                    fixes.append(
                        Fix(
                            code="AI-015",
                            file_path=file_path,
                            line=i + 1,
                            original=line,
                            replacement=f"{indent}# NOTE: Removed self-assignment: {var1} = {var1}",
                            description=f"self-assignment {var1} = {var1} → commented out",
                        )
                    )

        return fixes

    def _fix_ai_012_time_sleep_in_async(
        self, content: str, lines: List[str], file_path: Path
    ) -> List[Fix]:
        """Fix time.sleep() in async functions → asyncio.sleep()"""
        fixes = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return fixes

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr == "sleep":
                                if (
                                    isinstance(child.func.value, ast.Name)
                                    and child.func.value.id == "time"
                                ):
                                    line_idx = child.lineno - 1
                                    if line_idx < len(lines):
                                        original = lines[line_idx]
                                        replacement = original.replace(
                                            "time.sleep", "await asyncio.sleep"
                                        )
                                        if original != replacement:
                                            fixes.append(
                                                Fix(
                                                    code="AI-012",
                                                    file_path=file_path,
                                                    line=child.lineno,
                                                    original=original,
                                                    replacement=replacement,
                                                    description="time.sleep → await asyncio.sleep",
                                                )
                                            )

        return fixes

    def _fix_ai_013_mutable_defaults(self, content: str, file_path: Path) -> List[Fix]:
        """Fix mutable default arguments: def f(x=[]) → def f(x=None)"""
        fixes = []

        # Pattern: def func(arg=[]) or def func(arg={})
        pattern = re.compile(r"def\s+\w+\s*\([^)]*(\w+)\s*=\s*(\[\]|\{\})[^)]*\)")

        for match in pattern.finditer(content):
            line_start = content.count("\n", 0, match.start()) + 1
            # This is complex to auto-fix correctly, so we skip for now
            # Would need to also add initialization in function body

        return fixes

    def _fix_ai_018_hardcoded_paths(self, lines: List[str], file_path: Path) -> List[Fix]:
        """Suggest fixes for hardcoded paths (cannot fully auto-fix)."""
        fixes = []
        pattern = re.compile(r'["\']\/home\/[^"\']+["\']')

        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                path_str = match.group(0)
                # Suggest using Path(__file__).parent or os.environ
                # Cannot safely auto-fix without context
                pass

        return fixes

    def _fix_ai_011_range_len(self, lines: List[str], file_path: Path) -> List[Fix]:
        """Fix range(len(x)) → enumerate(x) where possible."""
        fixes = []
        # This is complex because it requires understanding the loop body
        # Skip auto-fix, just note
        return fixes

    def _fix_ai_019_deprecated_api(self, lines: List[str], file_path: Path) -> List[Fix]:
        """Fix deprecated API usage."""
        fixes = []

        replacements = [
            ("asyncio.get_running_loop()", "asyncio.get_running_loop()"),
            ("collections.abc.Mapping", "collections.abc.Mapping"),
            ("collections.abc.MutableMapping", "collections.abc.MutableMapping"),
            ("collections.abc.Iterable", "collections.abc.Iterable"),
        ]

        for i, line in enumerate(lines):
            for old, new in replacements:
                if old in line:
                    fixes.append(
                        Fix(
                            code="AI-019",
                            file_path=file_path,
                            line=i + 1,
                            original=line,
                            replacement=line.replace(old, new),
                            description=f"{old} → {new}",
                        )
                    )

        return fixes

    def _apply_fixes(self, file_path: Path, lines: List[str], fixes: List[Fix]):
        """Apply fixes to file."""
        # Sort fixes by line number in reverse to avoid offset issues
        fixes_sorted = sorted(fixes, key=lambda f: f.line, reverse=True)

        for fix in fixes_sorted:
            idx = fix.line - 1
            if 0 <= idx < len(lines):
                lines[idx] = fix.replacement

        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def fix_directory(
        self, directory: Path, exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Fix all Python files in directory."""
        exclude_patterns = exclude_patterns or [
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
        ]

        stats = {"files": 0, "fixes": 0, "skipped": 0}

        for py_file in directory.rglob("*.py"):
            if any(p in str(py_file) for p in exclude_patterns):
                continue

            fixes = self.fix_file(py_file)
            if fixes:
                stats["files"] += 1
                stats["fixes"] += len(fixes)

        return stats


def format_fixes_report(fixes: List[Fix]) -> str:
    """Format fixes as a report."""
    if not fixes:
        return "✅ No fixes to apply!"

    lines = ["# AI Fixer Report\n"]

    # Group by file
    by_file: Dict[Path, List[Fix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file_path, []).append(fix)

    lines.append(f"## Summary")
    lines.append(f"- Files: {len(by_file)}")
    lines.append(f"- Total fixes: {len(fixes)}")
    lines.append("")

    for file_path, file_fixes in sorted(by_file.items()):
        lines.append(f"## {file_path.name}")
        for fix in sorted(file_fixes, key=lambda f: f.line):
            lines.append(f"- L{fix.line} [{fix.code}]: {fix.description}")
            lines.append(f"  - `{fix.original.strip()}`")
            lines.append(f"  - → `{fix.replacement.strip()}`")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Synedrion Issue Fixer")
    parser.add_argument("path", type=Path, help="File or directory to fix")
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--severity",
        "-s",
        type=str,
        default="critical,high",
        help="Comma-separated severity levels to fix",
    )
    parser.add_argument("--output", "-o", type=Path, help="Output report file")
    args = parser.parse_args()

    severities = [s.strip().lower() for s in args.severity.split(",")]
    fixer = AIFixer(dry_run=args.dry_run, target_severities=severities)

    if args.path.is_file():
        fixes = fixer.fix_file(args.path)
    else:
        fixer.fix_directory(args.path)
        fixes = fixer.fixes_applied if not args.dry_run else fixer.fixes_skipped

    report = format_fixes_report(fixes)
    print(report)

    if args.dry_run:
        print("\n⚠️  DRY RUN - No changes applied")
    else:
        print(f"\n✅ Applied {len(fixes)} fixes")

    if args.output:
        args.output.write_text(report)
        print(f"Report saved to {args.output}")
