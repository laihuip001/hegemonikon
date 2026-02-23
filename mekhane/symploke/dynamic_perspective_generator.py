#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/symploke/dynamic_perspective_generator.py Automatically added to satisfy CI
# PROOF: [L3/実験] <- mekhane/symploke/ K3→文脈適応→perspective 動的生成
# PURPOSE: Basanos Perspective の動的生成 — ファイル特性に応じて Perspective を合成
"""
Dynamic Perspective Generator

固定 480 (20 domains × 24 axes) ではなく、
ファイルの特性 (言語/ドメイン/複雑性/issue 履歴) に応じて
Perspective を動的に合成する。

Integration:
    - basanos_bridge.py: BasanosBridge.get_dynamic_perspectives() 経由で発動
    - audit_specialist_matcher.py: audit_issues パラメータで AIAuditor 連携

Usage:
    from dynamic_perspective_generator import DynamicPerspectiveGenerator

    gen = DynamicPerspectiveGenerator()
    perspectives = gen.generate_for_file("mekhane/symploke/jules_daily_scheduler.py")
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))


# PURPOSE: ファイル特性の分析結果
@dataclass
class FileProfile:
    """ファイルの特性プロファイル。"""
    path: str
    language: str = "python"
    lines: int = 0
    has_async: bool = False
    has_classes: bool = False
    has_tests: bool = False
    imports_count: int = 0
    function_count: int = 0
    class_count: int = 0
    complexity_tier: str = "low"  # low / medium / high
    detected_domains: list[str] = field(default_factory=list)
    audit_issues: list[str] = field(default_factory=list)  # AI-xxx codes


# PURPOSE: 動的 Perspective の定義
@dataclass
class DynamicPerspective:
    """動的に生成された Perspective。"""
    id: str
    domain: str
    focus: str       # 具体的な注目点
    severity: str    # critical / high / medium / low
    rationale: str   # なぜこの perspective を選んだか


# PURPOSE: ファイルの特性からドメインを検出する静的マッピング
PATTERN_TO_DOMAINS: dict[str, list[tuple[str, str]]] = {
    # pattern → [(domain, focus), ...]
    r"async\s+def": [("Concurrency", "async/await patterns")],
    r"await\s+": [("Concurrency", "await usage correctness")],
    r"Lock|Semaphore|Event": [("Concurrency", "synchronization primitives")],
    r"subprocess|os\.system": [("Security", "command injection risk")],
    r"eval\(|exec\(": [("Security", "code injection risk")],
    r"open\(.*['\"]w['\"]": [("Security", "file write safety")],
    r"\.env|API_KEY|SECRET": [("Security", "credential exposure")],
    r"SELECT|INSERT|DELETE|UPDATE": [("Database", "SQL operations")],
    r"\.cursor\(|\.execute\(": [("Database", "direct DB access")],
    r"requests\.|httpx\.|aiohttp": [("Networking", "HTTP client usage")],
    r"@app\.route|@router": [("API-Design", "endpoint design")],
    r"json\.loads|json\.dumps": [("Data-Integrity", "serialization safety")],
    r"Path\(|pathlib": [("Filesystem", "path handling")],
    r"pytest|unittest|mock": [("Testing", "test quality")],
    r"class\s+\w+.*Exception": [("Error-Handling", "custom exception design")],
    r"try:|except\s": [("Error-Handling", "exception handling patterns")],
    r"logging\.|logger\.": [("Observability", "logging practices")],
    r"@dataclass|TypedDict|NamedTuple": [("Type-Safety", "data structure design")],
    r"Optional\[|Union\[|\|": [("Type-Safety", "optional/union handling")],
}

# Complexity thresholds
COMPLEXITY_THRESHOLDS = {
    "low": 100,     # < 100 lines
    "medium": 300,  # 100-300 lines
    "high": 300,    # > 300 lines
}


class DynamicPerspectiveGenerator:
    """ファイル特性に応じた Perspective 動的生成器。"""

    def __init__(self, max_perspectives: int = 24):
        self._max = max_perspectives

    def profile_file(self, file_path: str) -> FileProfile:
        """ファイルを静的解析し、プロファイルを生成。"""
        path = Path(file_path)
        profile = FileProfile(path=file_path)

        if not path.exists():
            return profile

        content = path.read_text(errors="replace")
        lines = content.splitlines()
        profile.lines = len(lines)
        profile.language = self._detect_language(path)

        # Complexity tier
        if profile.lines < COMPLEXITY_THRESHOLDS["low"]:
            profile.complexity_tier = "low"
        elif profile.lines < COMPLEXITY_THRESHOLDS["high"]:
            profile.complexity_tier = "medium"
        else:
            profile.complexity_tier = "high"

        # Pattern-based domain detection
        for pattern, domains in PATTERN_TO_DOMAINS.items():
            if re.search(pattern, content):
                for domain, _ in domains:
                    if domain not in profile.detected_domains:
                        profile.detected_domains.append(domain)

        # AST analysis for Python
        if profile.language == "python":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.AsyncFunctionDef):
                        profile.has_async = True
                    elif isinstance(node, ast.ClassDef):
                        profile.has_classes = True
                        profile.class_count += 1
                    elif isinstance(node, ast.FunctionDef):
                        profile.function_count += 1
                    elif isinstance(node, ast.Import | ast.ImportFrom):
                        profile.imports_count += 1
            except SyntaxError:
                pass

        # Test file detection
        basename = path.name
        if basename.startswith("test_") or basename.endswith("_test.py"):
            profile.has_tests = True

        return profile

    def generate_for_file(
        self,
        file_path: str,
        audit_issues: Optional[list[str]] = None,
    ) -> list[DynamicPerspective]:
        """ファイルに最適化された Perspective セットを生成。"""
        profile = self.profile_file(file_path)
        if audit_issues:
            profile.audit_issues = audit_issues

        perspectives: list[DynamicPerspective] = []

        # 1. 検出されたドメインに基づく perspective
        for domain in profile.detected_domains:
            focuses = self._get_focuses_for_domain(domain, profile)
            for focus in focuses:
                perspectives.append(DynamicPerspective(
                    id=f"DP-{domain}-{len(perspectives)+1:02d}",
                    domain=domain,
                    focus=focus,
                    severity="high" if domain in ("Security", "Concurrency") else "medium",
                    rationale=f"Pattern detected: {domain} patterns in file",
                ))

        # 2. Complexity-based perspectives
        if profile.complexity_tier == "high":
            perspectives.append(DynamicPerspective(
                id=f"DP-Complexity-{len(perspectives)+1:02d}",
                domain="Complexity",
                focus="Function decomposition and SRP",
                severity="medium",
                rationale=f"High complexity: {profile.lines} lines, {profile.function_count} functions",
            ))

        # 3. Audit issue-based perspectives
        if profile.audit_issues:
            from audit_specialist_matcher import AuditSpecialistMatcher
            matcher = AuditSpecialistMatcher()
            for code in set(profile.audit_issues):
                categories = matcher.get_categories_for_code(code)
                for cat in categories[:1]:  # primary category only
                    perspectives.append(DynamicPerspective(
                        id=f"DP-Audit-{code}-{len(perspectives)+1:02d}",
                        domain=cat.replace("_", "-").title(),
                        focus=f"Issues related to {code}",
                        severity="critical" if code in ("AI-009", "AI-012") else "high",
                        rationale=f"AIAuditor flagged: {code}",
                    ))

        # 4. Universal perspectives (always included)
        universal = [
            ("Code-Quality", "Overall code readability and maintainability"),
            ("Error-Handling", "Exception safety and graceful degradation"),
        ]
        for domain, focus in universal:
            if not any(p.domain == domain for p in perspectives):
                perspectives.append(DynamicPerspective(
                    id=f"DP-Universal-{len(perspectives)+1:02d}",
                    domain=domain,
                    focus=focus,
                    severity="low",
                    rationale="Universal review perspective",
                ))

        # Trim to max
        # Priority: critical > high > medium > low
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        perspectives.sort(key=lambda p: severity_order.get(p.severity, 4))

        return perspectives[:self._max]

    def _detect_language(self, path: Path) -> str:
        """ファイル拡張子から言語を推定。"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".rs": "rust",
            ".go": "go",
            ".rb": "ruby",
            ".java": "java",
            ".sh": "shell",
        }
        return ext_map.get(path.suffix, "unknown")

    def _get_focuses_for_domain(self, domain: str, profile: FileProfile) -> list[str]:
        """ドメインとプロファイルに基づく具体的な注目点。"""
        focus_map: dict[str, list[str]] = {
            "Security": [
                "Input validation and sanitization",
                "Credential handling safety",
            ],
            "Concurrency": [
                "Race condition prevention",
                "Deadlock and resource contention",
            ],
            "Database": [
                "Query safety and parameterization",
                "Connection lifecycle management",
            ],
            "Networking": [
                "HTTP error handling and retries",
                "Timeout and connection pool management",
            ],
            "API-Design": [
                "Endpoint consistency and RESTful conventions",
            ],
            "Error-Handling": [
                "Exception hierarchy and specificity",
            ],
            "Type-Safety": [
                "Type narrowing and null safety",
            ],
            "Data-Integrity": [
                "Serialization roundtrip safety",
            ],
            "Testing": [
                "Test coverage and edge case testing",
            ],
            "Filesystem": [
                "Path traversal and symlink safety",
            ],
            "Observability": [
                "Structured logging and log levels",
            ],
        }
        return focus_map.get(domain, [f"{domain} best practices"])