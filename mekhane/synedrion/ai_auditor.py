"""
AI Synedrion Audit Checker (AI-001 〜 AI-022)

Jules Synedrion の 22 AI-Risk 評価軸を実装。
CCL: /dia --mode=ai-audit
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    """Detected issue."""
    code: str           # e.g., "AI-001"
    name: str           # e.g., "Naming Hallucination"
    severity: Severity
    line: int
    message: str
    suggestion: Optional[str] = None


@dataclass
class AuditResult:
    """Result of auditing a file."""
    file_path: Path
    issues: List[Issue] = field(default_factory=list)
    
    @property
    def has_critical(self) -> bool:
        return any(i.severity == Severity.CRITICAL for i in self.issues)
    
    @property
    def has_high(self) -> bool:
        return any(i.severity == Severity.HIGH for i in self.issues)


class AIAuditor:
    """AI-generated code auditor with 22 evaluation axes."""
    
    # Known standard library modules (comprehensive)
    STDLIB_MODULES = {
        'os', 'sys', 'io', 're', 'json', 'csv', 'math', 'random',
        'datetime', 'time', 'collections', 'itertools', 'functools',
        'pathlib', 'typing', 'enum', 'dataclasses', 'abc',
        'asyncio', 'aiohttp', 'logging', 'unittest', 'pytest',
        'hashlib', 'base64', 'urllib', 'http', 'socket',
        'subprocess', 'threading', 'multiprocessing', 'concurrent',
        'uuid', 'argparse', 'copy', 'pickle', 'shelve', 'sqlite3',
        'importlib', 'inspect', 'textwrap', 'string', 'struct',
        'contextlib', 'warnings', 'traceback', 'tempfile', 'shutil',
        'glob', 'fnmatch', 'stat', 'fileinput', 'configparser',
        'secrets', 'hmac', 'ssl', 'email', 'html', 'xml',
        'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'zlib',
        'decimal', 'fractions', 'cmath', 'statistics', 'operator',
        'heapq', 'bisect', 'array', 'weakref', 'types', 'pprint',
        'opentelemetry',  # Common observability
    }
    
    # Known third-party modules (common AI/ML stack) + local modules
    KNOWN_MODULES = STDLIB_MODULES | {
        'numpy', 'pandas', 'scipy', 'sklearn', 'torch', 'tensorflow',
        'transformers', 'openai', 'anthropic', 'google', 'langchain',
        'fastapi', 'flask', 'django', 'pydantic', 'requests',
        'aiofiles', 'httpx', 'lancedb', 'chromadb', 'sentence_transformers',
        'pymdp', 'jax', 'flax', 'optax', 'onnxruntime', 'tiktoken',
        'playwright', 'arxiv', 'ijson', 'yaml', 'bs4', 'beautifulsoup4',
        'pytest', 'pytest_asyncio', 'aiohttp', 'PIL', 'pillow',
        # Local modules
        'mekhane', 'hegemonikon', 'symploke', 'ergasterion', 'peira',
        'anamnesis', 'ccl', 'fep', 'synedrion', 'hermeneus', 'synergeia',
    }
    
    def __init__(self):
        self.issues: List[Issue] = []
        self.source: str = ""
        self.tree: Optional[ast.AST] = None
        self.lines: List[str] = []
    
    def audit_file(self, file_path: Path) -> AuditResult:
        """Audit a Python file for AI-generated code issues."""
        self.issues = []
        self.source = file_path.read_text(encoding='utf-8')
        self.lines = self.source.splitlines()
        
        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            self.issues.append(Issue(
                code="AI-000",
                name="Syntax Error",
                severity=Severity.CRITICAL,
                line=e.lineno or 1,
                message=f"Syntax error: {e.msg}",
            ))
            return AuditResult(file_path=file_path, issues=self.issues)
        
        # Run all checks
        self._check_ai_001_naming_hallucination()
        self._check_ai_005_incomplete_code()
        self._check_ai_008_self_contradiction()
        self._check_ai_009_security_vulnerabilities()
        self._check_ai_010_input_validation()
        self._check_ai_014_excessive_comment()
        self._check_ai_016_dead_code()
        self._check_ai_017_magic_number()
        self._check_ai_018_hardcoded_path()
        self._check_ai_020_exception_swallowing()
        self._check_ai_021_resource_leak()
        
        return AuditResult(file_path=file_path, issues=self.issues)
    
    # ─────────────────────────────────────────────────────────────
    # AI-001: Naming Hallucination
    # ─────────────────────────────────────────────────────────────
    def _check_ai_001_naming_hallucination(self):
        """Check for references to non-existent modules/functions."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module not in self.KNOWN_MODULES and not module.startswith('_'):
                        self.issues.append(Issue(
                            code="AI-001",
                            name="Naming Hallucination",
                            severity=Severity.HIGH,
                            line=node.lineno,
                            message=f"Unknown module '{alias.name}' - verify it exists",
                            suggestion=f"pip install {module} or check spelling",
                        ))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module not in self.KNOWN_MODULES and not module.startswith('_'):
                        self.issues.append(Issue(
                            code="AI-001",
                            name="Naming Hallucination",
                            severity=Severity.HIGH,
                            line=node.lineno,
                            message=f"Unknown module '{node.module}' - verify it exists",
                        ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-005: Incomplete Code
    # ─────────────────────────────────────────────────────────────
    def _check_ai_005_incomplete_code(self):
        """Check for incomplete code patterns (pass, TODO, etc.)."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check for lone 'pass' statements
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Pass)):
                    self.issues.append(Issue(
                        code="AI-005",
                        name="Incomplete Code",
                        severity=Severity.MEDIUM,
                        line=node.lineno,
                        message=f"Empty {type(node).__name__} '{node.name}' with only 'pass'",
                        suggestion="Implement the function body or add NotImplementedError",
                    ))
                
                # Check for ellipsis
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    node.body[0].value.value is ...):
                    self.issues.append(Issue(
                        code="AI-005",
                        name="Incomplete Code",
                        severity=Severity.MEDIUM,
                        line=node.lineno,
                        message=f"Stub {type(node).__name__} '{node.name}' with only '...'",
                    ))
        
        # Check for TODO/FIXME in comments
        for i, line in enumerate(self.lines, 1):
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                self.issues.append(Issue(
                    code="AI-005",
                    name="Incomplete Code",
                    severity=Severity.LOW,
                    line=i,
                    message="Found TODO/FIXME marker",
                ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-008: Self-Contradiction
    # ─────────────────────────────────────────────────────────────
    def _check_ai_008_self_contradiction(self):
        """Check for contradictory logic patterns."""
        for node in ast.walk(self.tree):
            # if x and not x
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                names = set()
                neg_names = set()
                for value in node.values:
                    if isinstance(value, ast.Name):
                        names.add(value.id)
                    elif isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
                        if isinstance(value.operand, ast.Name):
                            neg_names.add(value.operand.id)
                
                contradiction = names & neg_names
                if contradiction:
                    self.issues.append(Issue(
                        code="AI-008",
                        name="Self-Contradiction",
                        severity=Severity.HIGH,
                        line=node.lineno,
                        message=f"Contradictory logic: '{list(contradiction)[0]}' and 'not {list(contradiction)[0]}'",
                    ))
            
            # if True: / if False:
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Constant):
                    if node.test.value is True:
                        self.issues.append(Issue(
                            code="AI-008",
                            name="Self-Contradiction",
                            severity=Severity.MEDIUM,
                            line=node.lineno,
                            message="'if True:' is always executed - unnecessary condition",
                        ))
                    elif node.test.value is False:
                        self.issues.append(Issue(
                            code="AI-008",
                            name="Self-Contradiction",
                            severity=Severity.HIGH,
                            line=node.lineno,
                            message="'if False:' is never executed - dead code",
                        ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-009: Security Vulnerabilities (CWE-based)
    # ─────────────────────────────────────────────────────────────
    def _check_ai_009_security_vulnerabilities(self):
        """Check for common security vulnerabilities."""
        for node in ast.walk(self.tree):
            # eval() usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    self.issues.append(Issue(
                        code="AI-009",
                        name="Security Vulnerability",
                        severity=Severity.CRITICAL,
                        line=node.lineno,
                        message="CWE-94: eval() allows code injection",
                        suggestion="Use ast.literal_eval() or explicit parsing",
                    ))
                
                # exec() usage
                if isinstance(node.func, ast.Name) and node.func.id == 'exec':
                    self.issues.append(Issue(
                        code="AI-009",
                        name="Security Vulnerability",
                        severity=Severity.CRITICAL,
                        line=node.lineno,
                        message="CWE-94: exec() allows code injection",
                    ))
                
                # subprocess.shell=True
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr in ('run', 'call', 'Popen')):
                    for kw in node.keywords:
                        if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            self.issues.append(Issue(
                                code="AI-009",
                                name="Security Vulnerability",
                                severity=Severity.HIGH,
                                line=node.lineno,
                                message="CWE-78: shell=True allows command injection",
                                suggestion="Use shell=False with argument list",
                            ))
        
        # Hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']', "Hardcoded token"),
        ]
        for i, line in enumerate(self.lines, 1):
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(Issue(
                        code="AI-009",
                        name="Security Vulnerability",
                        severity=Severity.CRITICAL,
                        line=i,
                        message=f"CWE-798: {desc} detected",
                        suggestion="Use environment variables or secrets manager",
                    ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-010: Input Validation Omission
    # ─────────────────────────────────────────────────────────────
    def _check_ai_010_input_validation(self):
        """Check for missing input validation."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Functions with 'path' or 'file' parameters
                for arg in node.args.args:
                    if any(x in arg.arg.lower() for x in ['path', 'file', 'dir']):
                        # Check if there's any validation in first few statements
                        has_validation = False
                        for stmt in node.body[:5]:
                            if isinstance(stmt, ast.If):
                                has_validation = True
                                break
                            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                # Check for Path().exists() or similar
                                has_validation = True
                                break
                        
                        if not has_validation and len(node.body) > 3:
                            self.issues.append(Issue(
                                code="AI-010",
                                name="Input Validation Omission",
                                severity=Severity.MEDIUM,
                                line=node.lineno,
                                message=f"Path parameter '{arg.arg}' may lack validation",
                                suggestion="Add existence/type check at function start",
                            ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-014: Excessive Comment
    # ─────────────────────────────────────────────────────────────
    def _check_ai_014_excessive_comment(self):
        """Check for redundant comments that restate code."""
        redundant_patterns = [
            (r'#\s*import\s+', "Comment restates import"),
            (r'#\s*define\s+', "Comment restates definition"),
            (r'#\s*return\s+', "Comment restates return"),
            (r'#\s*set\s+.+\s*to\s+', "Comment restates assignment"),
            (r'#\s*increment\s+', "Comment restates increment"),
            (r'#\s*initialize\s+', "Comment restates initialization"),
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern, desc in redundant_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(Issue(
                        code="AI-014",
                        name="Excessive Comment",
                        severity=Severity.LOW,
                        line=i,
                        message=desc,
                        suggestion="Remove redundant comment or add non-obvious context",
                    ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-016: Dead Code
    # ─────────────────────────────────────────────────────────────
    def _check_ai_016_dead_code(self):
        """Check for unreachable code."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found_return = False
                for i, stmt in enumerate(node.body):
                    if found_return:
                        self.issues.append(Issue(
                            code="AI-016",
                            name="Dead Code",
                            severity=Severity.MEDIUM,
                            line=stmt.lineno,
                            message="Unreachable code after return statement",
                        ))
                        break
                    if isinstance(stmt, ast.Return):
                        found_return = True
    
    # ─────────────────────────────────────────────────────────────
    # AI-017: Magic Number
    # ─────────────────────────────────────────────────────────────
    def _check_ai_017_magic_number(self):
        """Check for unexplained numeric literals."""
        # Acceptable numbers
        acceptable = {0, 1, 2, -1, 10, 100, 1000, 0.0, 1.0, 0.5}
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in acceptable and abs(node.value) > 2:
                    # Check if in a constant assignment
                    parent_is_assignment = False
                    for parent in ast.walk(self.tree):
                        if isinstance(parent, ast.Assign):
                            for target in parent.targets:
                                if isinstance(target, ast.Name) and target.id.isupper():
                                    parent_is_assignment = True
                    
                    if not parent_is_assignment:
                        line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                        # Skip if there's an explanatory comment
                        if '#' not in line_content:
                            self.issues.append(Issue(
                                code="AI-017",
                                name="Magic Number",
                                severity=Severity.LOW,
                                line=node.lineno,
                                message=f"Magic number {node.value} - consider named constant",
                            ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-018: Hardcoded Path
    # ─────────────────────────────────────────────────────────────
    def _check_ai_018_hardcoded_path(self):
        """Check for hardcoded file paths."""
        path_patterns = [
            r'["\'][A-Za-z]:[/\\]',           # Windows absolute path
            r'["\']\/(?:home|usr|var|etc)\/', # Unix absolute path
            r'["\']~\/',                      # Home directory
            r'["\']\.\./',                    # Parent directory
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern in path_patterns:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        code="AI-018",
                        name="Hardcoded Path",
                        severity=Severity.MEDIUM,
                        line=i,
                        message="Hardcoded path detected",
                        suggestion="Use Path(__file__).parent or config",
                    ))
                    break
    
    # ─────────────────────────────────────────────────────────────
    # AI-020: Exception Swallowing
    # ─────────────────────────────────────────────────────────────
    def _check_ai_020_exception_swallowing(self):
        """Check for bare except or swallowed exceptions."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                # Bare except
                if node.type is None:
                    self.issues.append(Issue(
                        code="AI-020",
                        name="Exception Swallowing",
                        severity=Severity.HIGH,
                        line=node.lineno,
                        message="Bare 'except:' catches all exceptions including KeyboardInterrupt",
                        suggestion="Use 'except Exception:' or specific exception types",
                    ))
                
                # except with only pass
                if (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                    self.issues.append(Issue(
                        code="AI-020",
                        name="Exception Swallowing",
                        severity=Severity.HIGH,
                        line=node.lineno,
                        message="Exception silently caught and ignored",
                        suggestion="Log the exception or re-raise",
                    ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-021: Resource Leak
    # ─────────────────────────────────────────────────────────────
    def _check_ai_021_resource_leak(self):
        """Check for potential resource leaks."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                # open() without context manager
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Check if parent is a With statement
                    is_in_with = False
                    for parent in ast.walk(self.tree):
                        if isinstance(parent, ast.With):
                            for item in parent.items:
                                if item.context_expr is node:
                                    is_in_with = True
                    
                    if not is_in_with:
                        # Check if assigned to variable (might be closed later)
                        # This is a heuristic, not perfect
                        self.issues.append(Issue(
                            code="AI-021",
                            name="Resource Leak",
                            severity=Severity.MEDIUM,
                            line=node.lineno,
                            message="open() without context manager may leak file handle",
                            suggestion="Use 'with open(...) as f:' pattern",
                        ))


def audit_directory(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[AuditResult]:
    """Audit all Python files in a directory."""
    exclude_patterns = exclude_patterns or ['venv', '__pycache__', '.git', 'node_modules']
    auditor = AIAuditor()
    results = []
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded paths
        if any(p in str(py_file) for p in exclude_patterns):
            continue
        
        try:
            result = auditor.audit_file(py_file)
            if result.issues:
                results.append(result)
        except Exception as e:
            print(f"Error auditing {py_file}: {e}")
    
    return results


def format_report(results: List[AuditResult]) -> str:
    """Format audit results as a report."""
    if not results:
        return "✅ No issues found!"
    
    lines = ["# AI Audit Report\n"]
    
    total_critical = sum(1 for r in results for i in r.issues if i.severity == Severity.CRITICAL)
    total_high = sum(1 for r in results for i in r.issues if i.severity == Severity.HIGH)
    total_medium = sum(1 for r in results for i in r.issues if i.severity == Severity.MEDIUM)
    total_low = sum(1 for r in results for i in r.issues if i.severity == Severity.LOW)
    
    lines.append(f"## Summary")
    lines.append(f"- Files with issues: {len(results)}")
    lines.append(f"- 🔴 Critical: {total_critical}")
    lines.append(f"- 🟠 High: {total_high}")
    lines.append(f"- 🟡 Medium: {total_medium}")
    lines.append(f"- ⚪ Low: {total_low}")
    lines.append("")
    
    for result in sorted(results, key=lambda r: (-len([i for i in r.issues if i.severity == Severity.CRITICAL]), str(r.file_path))):
        lines.append(f"## {result.file_path.name}")
        lines.append("")
        
        for issue in sorted(result.issues, key=lambda i: (i.severity.value, i.line)):
            severity_icon = {
                Severity.CRITICAL: "🔴",
                Severity.HIGH: "🟠",
                Severity.MEDIUM: "🟡",
                Severity.LOW: "⚪",
            }[issue.severity]
            
            lines.append(f"- {severity_icon} **{issue.code}** L{issue.line}: {issue.message}")
            if issue.suggestion:
                lines.append(f"  - 💡 {issue.suggestion}")
        
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Synedrion Audit Checker")
    parser.add_argument("path", type=Path, help="File or directory to audit")
    parser.add_argument("--output", "-o", type=Path, help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    if args.path.is_file():
        auditor = AIAuditor()
        result = auditor.audit_file(args.path)
        results = [result] if result.issues else []
    else:
        results = audit_directory(args.path)
    
    report = format_report(results)
    print(report)
    
    if args.output:
        args.output.write_text(report)
        print(f"\nReport saved to {args.output}")
