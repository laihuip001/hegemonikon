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
        'ast', 'os', 'sys', 'io', 're', 'json', 'csv', 'math', 'random',
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
        # Common third-party
        'numpy', 'pandas', 'scipy', 'sklearn', 'torch', 'tensorflow',
        'transformers', 'openai', 'anthropic', 'google', 'langchain',
        'fastapi', 'flask', 'django', 'pydantic', 'requests',
        'aiofiles', 'httpx', 'lancedb', 'chromadb', 'sentence_transformers',
        'pymdp', 'jax', 'flax', 'optax', 'onnxruntime', 'tiktoken',
        'playwright', 'arxiv', 'ijson', 'yaml', 'bs4', 'beautifulsoup4',
        'pytest', 'pytest_asyncio', 'aiohttp', 'PIL', 'pillow',
        'html2text', 'tokenizers', 'huggingface_hub', 'networkx',
        'pyarrow', 'schedule', 'dotenv', 'dateutil', 'hnswlib',
        # MCP
        'mcp',
        # Local Hegemonikón modules
        'mekhane', 'hegemonikon', 'symploke', 'ergasterion', 'peira',
        'anamnesis', 'ccl', 'fep', 'synedrion', 'hermeneus', 'synergeia',
        'prompt_lang', 'gnosis', 'sophia', 'kairos', 'chronos',
        # Internal sub-modules (relative imports)
        'base', 'config', 'engine', 'executor', 'generator', 'validator',
        'validator', 'validators', 'checker', 'reporter', 'ranker', 'selector',
        'adapters', 'indices', 'persistence', 'encoding', 'learning', 'guardrails',
        'state_spaces', 'pattern_cache', 'macro_registry', 'macro_expander',
        'llm_parser', 'llm_evaluator', 'doxa_learner', 'doxa_persistence', 'doxa_cache',
        'fep_agent', 'fep_bridge', 'epoche_shield', 'metron_resolver',
        'telos_checker', 'tekhne_registry', 'spec_injector', 'syntax_validator',
        'semantic_validator', 'semantic_matcher', 'schema_analyzer', 'tracer', 'pipeline',
        'specialist_prompts', 'prompt_generator', 'prompt_lang_integrate', 'workflow_signature',
        'noesis_client', 'sophia_researcher', 'zetesis_inquirer', 'eukairia_detector',
        'chronos_evaluator', 'akribeia_evaluator', 'horme_evaluator', 'perigraphe_engine',
        'energeia_executor', 'energeia_core', 'krisis_judge', 'failure_db', 'vocab_store', 'signal',
        'phase0_specialists', 'phase2_specialists', 'phase2_remaining', 'phase3_specialists',
        'adaptive_allocator', 'jules_mcp_server',
    }
    
    def __init__(self, strict: bool = False):
        """
        Initialize AI Auditor.
        
        Args:
            strict: If True, report all issues (Critical/High/Medium/Low).
                   If False (default), report only Critical and High issues.
        """
        self.strict = strict
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
        
        # Run all checks (22 axes)
        self._check_ai_001_naming_hallucination()
        self._check_ai_002_api_misuse()
        self._check_ai_003_type_confusion()
        self._check_ai_004_logic_hallucination()
        self._check_ai_005_incomplete_code()
        self._check_ai_006_context_drift()
        self._check_ai_007_pattern_inconsistency()
        self._check_ai_008_self_contradiction()
        self._check_ai_009_security_vulnerabilities()
        self._check_ai_010_input_validation()
        self._check_ai_011_boundary_condition()
        self._check_ai_012_async_misuse()
        self._check_ai_013_concurrency_issues()
        self._check_ai_014_excessive_comment()
        self._check_ai_015_copy_paste_error()
        self._check_ai_016_dead_code()
        self._check_ai_017_magic_number()
        self._check_ai_018_hardcoded_path()
        self._check_ai_019_deprecated_api()
        self._check_ai_020_exception_swallowing()
        self._check_ai_021_resource_leak()
        self._check_ai_022_test_coverage_gap()
        
        # Filter issues based on strict mode
        if not self.strict:
            # In lenient mode, only report Critical and High
            self.issues = [i for i in self.issues if i.severity in (Severity.CRITICAL, Severity.HIGH)]
        
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
    # AI-002: API Misuse
    # ─────────────────────────────────────────────────────────────
    def _check_ai_002_api_misuse(self):
        """Check for common API misuse patterns."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                # json.loads() on already-parsed object
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'loads':
                    if node.args and isinstance(node.args[0], ast.Dict):
                        self.issues.append(Issue(
                            code="AI-002",
                            name="API Misuse",
                            severity=Severity.MEDIUM,
                            line=node.lineno,
                            message="json.loads() called on dict literal",
                            suggestion="Remove json.loads(), already a dict",
                        ))
                
                # list() on already-list
                if isinstance(node.func, ast.Name) and node.func.id == 'list':
                    if node.args and isinstance(node.args[0], ast.List):
                        self.issues.append(Issue(
                            code="AI-002",
                            name="API Misuse",
                            severity=Severity.LOW,
                            line=node.lineno,
                            message="list() called on list literal",
                        ))
                
                # str.split() followed by str.join()
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
                    if node.args and isinstance(node.args[0], ast.Call):
                        inner = node.args[0]
                        if isinstance(inner.func, ast.Attribute) and inner.func.attr == 'split':
                            self.issues.append(Issue(
                                code="AI-002",
                                name="API Misuse",
                                severity=Severity.LOW,
                                line=node.lineno,
                                message="Unnecessary split/join pattern",
                                suggestion="Consider str.replace() instead",
                            ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-003: Type Confusion
    # ─────────────────────────────────────────────────────────────
    def _check_ai_003_type_confusion(self):
        """Check for type confusion patterns."""
        for node in ast.walk(self.tree):
            # Comparing different types
            if isinstance(node, ast.Compare):
                if node.comparators:
                    left_type = type(node.left).__name__
                    right_type = type(node.comparators[0]).__name__
                    
                    # String vs Number comparison
                    if isinstance(node.left, ast.Constant) and isinstance(node.comparators[0], ast.Constant):
                        left_val = node.left.value
                        right_val = node.comparators[0].value
                        if isinstance(left_val, str) and isinstance(right_val, (int, float)):
                            self.issues.append(Issue(
                                code="AI-003",
                                name="Type Confusion",
                                severity=Severity.HIGH,
                                line=node.lineno,
                                message="String compared with number",
                            ))
                        elif isinstance(left_val, (int, float)) and isinstance(right_val, str):
                            self.issues.append(Issue(
                                code="AI-003",
                                name="Type Confusion",
                                severity=Severity.HIGH,
                                line=node.lineno,
                                message="Number compared with string",
                            ))
            
            # len() == True/False (should be > 0 or == 0)
            if isinstance(node, ast.Compare):
                if isinstance(node.left, ast.Call):
                    if isinstance(node.left.func, ast.Name) and node.left.func.id == 'len':
                        for comp in node.comparators:
                            if isinstance(comp, ast.Constant) and comp.value in (True, False):
                                self.issues.append(Issue(
                                    code="AI-003",
                                    name="Type Confusion",
                                    severity=Severity.LOW,  # Common pattern, not critical
                                    line=node.lineno,
                                    message="len() compared with boolean",
                                    suggestion="Use len() > 0 or len() == 0",
                                ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-004: Logic Hallucination
    # ─────────────────────────────────────────────────────────────
    def _check_ai_004_logic_hallucination(self):
        """Check for implausible logic patterns."""
        for node in ast.walk(self.tree):
            # Division by literal zero
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    self.issues.append(Issue(
                        code="AI-004",
                        name="Logic Hallucination",
                        severity=Severity.CRITICAL,
                        line=node.lineno,
                        message="Division by zero",
                    ))
            
            # Infinite loop: while True without break/return/sys.exit
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_exit = False
                    for n in ast.walk(node):
                        # break statement
                        if isinstance(n, ast.Break):
                            has_exit = True
                        # return statement
                        if isinstance(n, ast.Return):
                            has_exit = True
                        # sys.exit() call
                        if isinstance(n, ast.Call):
                            if isinstance(n.func, ast.Attribute) and n.func.attr == 'exit':
                                has_exit = True
                            if isinstance(n.func, ast.Name) and n.func.id == 'exit':
                                has_exit = True
                    if not has_exit:
                        # Check if in main() function with signal handler in file
                        # (pattern for schedulers/daemons)
                        is_scheduler_pattern = False
                        file_has_signal = 'signal.' in self.source
                        if file_has_signal and 'def main' in self.source:
                            is_scheduler_pattern = True
                        
                        if not is_scheduler_pattern:
                            self.issues.append(Issue(
                                code="AI-004",
                                name="Logic Hallucination",
                                severity=Severity.HIGH,
                                line=node.lineno,
                                message="Infinite loop without break/return/exit",
                            ))
            
            # Empty range
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'range':
                    if len(node.args) >= 2:
                        start = node.args[0]
                        end = node.args[1]
                        if (isinstance(start, ast.Constant) and isinstance(end, ast.Constant) and
                            isinstance(start.value, int) and isinstance(end.value, int)):
                            if start.value >= end.value:
                                self.issues.append(Issue(
                                    code="AI-004",
                                    name="Logic Hallucination",
                                    severity=Severity.MEDIUM,
                                    line=node.lineno,
                                    message=f"Empty range({start.value}, {end.value})",
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
    # AI-006: Context Drift
    # ─────────────────────────────────────────────────────────────
    def _check_ai_006_context_drift(self):
        """Check for context drift patterns (variable redefinition, scope confusion)."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check for parameter shadowing
                param_names = {arg.arg for arg in node.args.args}
                
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name) and target.id in param_names:
                                self.issues.append(Issue(
                                    code="AI-006",
                                    name="Context Drift",
                                    severity=Severity.LOW,  # Common Python pattern
                                    line=stmt.lineno,
                                    message=f"Parameter '{target.id}' is reassigned",
                                    suggestion="Use different variable name to avoid confusion",
                                ))
                
                # Check for global/nonlocal misuse
                has_global = any(isinstance(s, ast.Global) for s in node.body)
                has_return = any(isinstance(s, ast.Return) for s in ast.walk(node))
                if has_global and has_return:
                    self.issues.append(Issue(
                        code="AI-006",
                        name="Context Drift",
                        severity=Severity.LOW,
                        line=node.lineno,
                        message="Function uses both global and return",
                        suggestion="Consider avoiding global state",
                    ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-007: Pattern Inconsistency
    # ─────────────────────────────────────────────────────────────
    def _check_ai_007_pattern_inconsistency(self):
        """Check for inconsistent coding patterns."""
        # Check for mixed string quotes in the same file
        single_quote_count = self.source.count("'")
        double_quote_count = self.source.count('"')
        
        # Significant imbalance suggests inconsistency (ignoring if one is dominant)
        if single_quote_count > 10 and double_quote_count > 10:
            ratio = min(single_quote_count, double_quote_count) / max(single_quote_count, double_quote_count)
            if 0.3 < ratio < 0.7:  # Neither is clearly dominant
                self.issues.append(Issue(
                    code="AI-007",
                    name="Pattern Inconsistency",
                    severity=Severity.LOW,
                    line=1,
                    message="Mixed single and double quotes throughout file",
                    suggestion="Standardize on one quote style",
                ))
        
        # Check for inconsistent naming (mixedCase and snake_case in same scope)
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        names.append(child.id)
                
                snake_case = [n for n in names if '_' in n and n.islower()]
                camel_case = [n for n in names if not '_' in n and any(c.isupper() for c in n[1:])]
                
                if len(snake_case) > 3 and len(camel_case) > 3:
                    self.issues.append(Issue(
                        code="AI-007",
                        name="Pattern Inconsistency",
                        severity=Severity.LOW,
                        line=node.lineno,
                        message="Mixed naming conventions in same scope",
                        suggestion="Use consistent snake_case or camelCase",
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
        
        # Hardcoded secrets (skip documentation examples)
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']', "Hardcoded token"),
        ]
        # Placeholder values to skip (documentation examples and test dummies)
        placeholder_patterns = [
            r'YOUR_', r'your_', r'xxx', r'XXX', r'\*\*\*',
            r'<.*>', r'\${', r'%\(', r'PLACEHOLDER', r'EXAMPLE',
            r'sk-\.\.\.', r'sk_test_', r'pk_test_',
            r'test[-_]key', r'test[-_]token', r'test[-_]secret', r'test[-_]pass',
            r'dummy', r'DUMMY', r'fake', r'FAKE', r'mock', r'MOCK',
        ]
        for i, line in enumerate(self.lines, 1):
            # Skip if in docstring or comment
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            for pattern, desc in secret_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    matched_value = match.group(0)
                    # Skip if contains placeholder pattern
                    is_placeholder = any(re.search(p, matched_value, re.IGNORECASE) for p in placeholder_patterns)
                    if not is_placeholder:
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
                                severity=Severity.LOW,  # Recommendation, not critical
                                line=node.lineno,
                                message=f"Path parameter '{arg.arg}' may lack validation",
                                suggestion="Add existence/type check at function start",
                            ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-011: Boundary Condition Error
    # ─────────────────────────────────────────────────────────────
    def _check_ai_011_boundary_condition(self):
        """Check for off-by-one and boundary errors."""
        for node in ast.walk(self.tree):
            # len(x) - 1 in index access (potential off-by-one)
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.BinOp):
                    if isinstance(node.slice.op, ast.Sub):
                        if isinstance(node.slice.right, ast.Constant) and node.slice.right.value == 1:
                            if isinstance(node.slice.left, ast.Call):
                                if isinstance(node.slice.left.func, ast.Name) and node.slice.left.func.id == 'len':
                                    # x[len(x) - 1] is actually valid for last element
                                    # But check if it's in a range context
                                    pass  # Skip for now, this is valid
            
            # range(len(x)) pattern
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'range':
                    if node.args and isinstance(node.args[0], ast.Call):
                        inner = node.args[0]
                        if isinstance(inner.func, ast.Name) and inner.func.id == 'len':
                            self.issues.append(Issue(
                                code="AI-011",
                                name="Boundary Condition",
                                severity=Severity.LOW,
                                line=node.lineno,
                                message="range(len(x)) pattern - consider enumerate()",
                                suggestion="Use 'for i, item in enumerate(x):'",
                            ))
            
            # >= len() or > len() - 1
            if isinstance(node, ast.Compare):
                for i, (op, comp) in enumerate(zip(node.ops, node.comparators)):
                    if isinstance(comp, ast.Call):
                        if isinstance(comp.func, ast.Name) and comp.func.id == 'len':
                            if isinstance(op, (ast.GtE, ast.Gt)):
                                self.issues.append(Issue(
                                    code="AI-011",
                                    name="Boundary Condition",
                                    severity=Severity.MEDIUM,
                                    line=node.lineno,
                                    message="Comparison with len() may cause index error",
                                ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-012: Async Misuse
    # ─────────────────────────────────────────────────────────────
    def _check_ai_012_async_misuse(self):
        """Check for async/await misuse patterns."""
        for node in ast.walk(self.tree):
            # Async function without await
            if isinstance(node, ast.AsyncFunctionDef):
                has_await = any(isinstance(n, ast.Await) for n in ast.walk(node))
                if not has_await:
                    self.issues.append(Issue(
                        code="AI-012",
                        name="Async Misuse",
                        severity=Severity.MEDIUM,
                        line=node.lineno,
                        message=f"Async function '{node.name}' has no await",
                        suggestion="Remove async or add await for I/O operations",
                    ))
            
            # await in non-async function (but skip if inside nested async function)
            if isinstance(node, ast.FunctionDef):  # Not AsyncFunctionDef
                for child in ast.walk(node):
                    if isinstance(child, ast.Await):
                        # Check if this await is inside a nested async function
                        is_in_nested_async = False
                        for n in ast.walk(node):
                            if isinstance(n, ast.AsyncFunctionDef):
                                for deep_child in ast.walk(n):
                                    if deep_child is child:
                                        is_in_nested_async = True
                                        break
                        
                        if not is_in_nested_async:
                            self.issues.append(Issue(
                                code="AI-012",
                                name="Async Misuse",
                                severity=Severity.CRITICAL,
                                line=child.lineno,
                                message="await in non-async function",
                            ))
            
            # time.sleep in async function
            if isinstance(node, ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr == 'sleep':
                                if isinstance(child.func.value, ast.Name) and child.func.value.id == 'time':
                                    self.issues.append(Issue(
                                        code="AI-012",
                                        name="Async Misuse",
                                        severity=Severity.HIGH,
                                        line=child.lineno,
                                        message="time.sleep() in async function blocks event loop",
                                        suggestion="Use asyncio.sleep() instead",
                                    ))
    
    # ─────────────────────────────────────────────────────────────
    # AI-013: Concurrency Issues
    # ─────────────────────────────────────────────────────────────
    def _check_ai_013_concurrency_issues(self):
        """Check for race conditions and thread safety issues."""
        # Check for global variable modification without lock
        global_vars = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Global):
                global_vars.update(node.names)
        
        if global_vars:
            # Check if there's any threading import
            has_threading = any('threading' in line or 'multiprocessing' in line for line in self.lines)
            if has_threading:
                self.issues.append(Issue(
                    code="AI-013",
                    name="Concurrency Issue",
                    severity=Severity.MEDIUM,
                    line=1,
                    message=f"Global variables {global_vars} with threading - potential race condition",
                    suggestion="Use threading.Lock() to protect shared state",
                ))
        
        # Check for mutable default arguments (common thread safety issue)
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.issues.append(Issue(
                            code="AI-013",
                            name="Concurrency Issue",
                            severity=Severity.HIGH,
                            line=node.lineno,
                            message="Mutable default argument - shared between calls",
                            suggestion="Use None as default and create new object in function",
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
    # AI-015: Copy-Paste Error
    # ─────────────────────────────────────────────────────────────
    def _check_ai_015_copy_paste_error(self):
        """Check for copy-paste errors (duplicated code with minor changes)."""
        # Check for consecutive similar lines
        for i in range(len(self.lines) - 1):
            line1 = self.lines[i].strip()
            line2 = self.lines[i + 1].strip()
            
            # Skip empty lines, comments, and short lines
            if not line1 or not line2 or line1.startswith('#') or len(line1) < 20:
                continue
            
            # Check for very similar consecutive lines (potential copy-paste)
            if line1 == line2:
                self.issues.append(Issue(
                    code="AI-015",
                    name="Copy-Paste Error",
                    severity=Severity.MEDIUM,
                    line=i + 1,
                    message="Consecutive duplicate lines detected",
                    suggestion="Remove duplicate or extract to variable/function",
                ))
        
        # Check for common copy-paste patterns
        for i, line in enumerate(self.lines, 1):
            # Same variable assigned to itself
            match = re.match(r'\s*(\w+)\s*=\s*(\w+)\s*$', line)
            if match and match.group(1) == match.group(2):
                self.issues.append(Issue(
                    code="AI-015",
                    name="Copy-Paste Error",
                    severity=Severity.HIGH,
                    line=i,
                    message=f"Variable '{match.group(1)}' assigned to itself",
                ))
            
            # if x: x (condition same as body)
            if re.match(r'\s*if\s+(\w+):\s*\1\s*$', line):
                self.issues.append(Issue(
                    code="AI-015",
                    name="Copy-Paste Error",
                    severity=Severity.MEDIUM,
                    line=i,
                    message="Condition same as body - likely copy-paste error",
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
                        severity=Severity.LOW,  # Recommendation, not critical
                        line=i,
                        message="Hardcoded path detected",
                        suggestion="Use Path(__file__).parent or config",
                    ))
                    break
    
    # ─────────────────────────────────────────────────────────────
    # AI-019: Deprecated API Usage
    # ─────────────────────────────────────────────────────────────
    def _check_ai_019_deprecated_api(self):
        """Check for deprecated API usage."""
        deprecated_patterns = [
            # Python deprecations
            (r'\basyncio\.get_event_loop\(\)', "asyncio.get_running_loop() - use asyncio.get_running_loop()"),
            (r'\bcollections\.Mapping\b', "collections.abc.Mapping - use collections.abc.Mapping"),
            (r'\bcollections\.MutableMapping\b', "collections.abc.MutableMapping - use collections.abc.MutableMapping"),
            (r'\bcollections\.Iterable\b', "collections.abc.Iterable - use collections.abc.Iterable"),
            (r'\boptparse\b', "optparse - use argparse"),
            (r'\bimp\b', "imp module - use importlib"),
            (r'\bdistutils\b', "distutils - use setuptools"),
            (r'\.format\s*\([^)]*%', "Mixed .format() and % formatting"),
            # Common library deprecations
            (r'requests\.packages\.urllib3', "requests.packages.urllib3 - import urllib3 directly"),
            (r'from typing import Optional, Union', "Optional[X] is deprecated in 3.10+ - use X | None"),
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern, desc in deprecated_patterns:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        code="AI-019",
                        name="Deprecated API",
                        severity=Severity.LOW,
                        line=i,
                        message=desc,
                    ))
        
        # Check for deprecated function decorators
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id in ('abstractproperty', 'abstractstaticmethod', 'abstractclassmethod'):
                            self.issues.append(Issue(
                                code="AI-019",
                                name="Deprecated API",
                                severity=Severity.LOW,
                                line=node.lineno,
                                message=f"@{decorator.id} is deprecated",
                                suggestion="Use @property/@staticmethod/@classmethod with @abstractmethod",
                            ))
    
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
                
                # except with only pass (but allow if it has a TODO comment)
                if (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                    line_content = self.lines[node.body[0].lineno - 1] if node.body[0].lineno <= len(self.lines) else ""
                    # Allow if there's a TODO/NOTE/FIXME comment
                    if not re.search(r'#\s*(TODO|NOTE|FIXME|HACK)', line_content, re.IGNORECASE):
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
    
    # ─────────────────────────────────────────────────────────────
    # AI-022: Test Coverage Gap
    # ─────────────────────────────────────────────────────────────
    def _check_ai_022_test_coverage_gap(self):
        """Check for potential test coverage gaps."""
        # Count public functions
        public_functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    public_functions.append(node.name)
        
        # Check if this is a test file
        is_test_file = 'test_' in str(self.lines[0] if self.lines else '') or 'test' in str(self.source[:100])
        
        if not is_test_file and len(public_functions) > 5:
            # Check for any test-related patterns
            has_doctest = any('>>>' in line for line in self.lines)
            has_assert = any('assert ' in line for line in self.lines)
            
            if not has_doctest and not has_assert:
                self.issues.append(Issue(
                    code="AI-022",
                    name="Test Coverage Gap",
                    severity=Severity.LOW,
                    line=1,
                    message=f"File has {len(public_functions)} public functions but no visible tests",
                    suggestion="Add unit tests or doctests for public API",
                ))
        
        # Check for complex functions without docstrings
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check complexity (number of branches)
                branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try)))
                
                if branches >= 5:
                    # Check for docstring
                    has_docstring = (node.body and isinstance(node.body[0], ast.Expr) and 
                                    isinstance(node.body[0].value, ast.Constant) and 
                                    isinstance(node.body[0].value.value, str))
                    
                    if not has_docstring:
                        self.issues.append(Issue(
                            code="AI-022",
                            name="Test Coverage Gap",
                            severity=Severity.LOW,
                            line=node.lineno,
                            message=f"Complex function '{node.name}' ({branches} branches) lacks docstring",
                            suggestion="Add docstring explaining edge cases",
                        ))


def audit_directory(directory: Path, exclude_patterns: Optional[List[str]] = None, strict: bool = False) -> List[AuditResult]:
    """Audit all Python files in a directory."""
    exclude_patterns = exclude_patterns or ['venv', '__pycache__', '.git', 'node_modules']
    auditor = AIAuditor(strict=strict)
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
    parser.add_argument("--strict", "-s", action="store_true", 
                       help="Strict mode: report all issues including Low severity")
    args = parser.parse_args()
    
    if args.path.is_file():
        auditor = AIAuditor(strict=args.strict)
        result = auditor.audit_file(args.path)
        results = [result] if result.issues else []
    else:
        results = audit_directory(args.path, strict=args.strict)
    
    report = format_report(results)
    print(report)
    
    if args.output:
        args.output.write_text(report)
        print(f"\nReport saved to {args.output}")
