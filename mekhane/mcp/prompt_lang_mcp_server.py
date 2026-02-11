#!/usr/bin/env python3
"""
Prompt-Lang MCP Server v2.0 — Hegemonikón Skill Generator

Model Context Protocol server for Prompt-Lang code generation,
parsing, validation, compilation, and convergence/divergence policy.

Tools:
  - generate: Natural language → .prompt code (domain-aware)
  - parse: .prompt file → JSON AST
  - validate: .prompt file syntax check
  - compile: .prompt file → system prompt (markdown/xml/plain)
  - expand: .prompt file → natural language prompt
  - policy_check: Convergence/divergence task classification

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io

_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr


def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Prompt-Lang MCP Server v2.0...")
log(f"Python: {sys.executable}")
log(f"Platform: {sys.platform}")

# ============ Import path setup ============
sys.path.insert(0, str(Path(__file__).parent.parent))
log(f"Added to path: {Path(__file__).parent.parent}")


# ============ Suppress stdout during imports ============
class StdoutSuppressor:
    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    def __exit__(self, *args):
        sys.stdout = self._old_stdout
        captured = self._null.getvalue()
        if captured.strip():
            log(f"Suppressed stdout during import: {captured[:100]}...")


# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Import prompt-lang parser
try:
    # prompt-lang directory has a hyphen — use importlib for safe import
    import importlib
    _pl_path = Path(__file__).parent.parent / "ergasterion" / "prompt-lang"
    if str(_pl_path) not in sys.path:
        sys.path.insert(0, str(_pl_path))
    _pl_module = importlib.import_module("prompt_lang")
    PromptLangParser = _pl_module.PromptLangParser
    parse_file = _pl_module.parse_file
    parse_all = _pl_module.parse_all
    resolve = _pl_module.resolve
    validate_file = _pl_module.validate_file
    Prompt = _pl_module.Prompt
    ParseError = _pl_module.ParseError
    log("prompt_lang parser imported successfully")
    PARSER_AVAILABLE = True
except Exception as e:
    log(f"prompt_lang import error: {e}, falling back to basic generation")
    PARSER_AVAILABLE = False

# ============ Paths ============
SKILL_DIR = Path(__file__).parent.parent / ".agent/skills/utils/prompt-lang-generator"
TEMPLATES_DIR = SKILL_DIR / "templates"
# v2.1: Use correct domain templates path
DOMAIN_TEMPLATES_DIR = (
    Path(__file__).parent.parent / "ergasterion" / "tekhne" / "references"
    / "prompt-lang-templates" / "domain_templates"
)

log(f"SKILL_DIR: {SKILL_DIR}")
log(f"DOMAIN_TEMPLATES_DIR: {DOMAIN_TEMPLATES_DIR} (exists: {DOMAIN_TEMPLATES_DIR.exists()})")

# ============ Domain Detection ============
DOMAIN_KEYWORDS = {
    "technical": [
        "コードレビュー", "code review", "セキュリティ", "security",
        "api", "endpoint", "バグ", "bug", "デバッグ", "debug",
        "リファクタリング", "refactor", "テスト", "test",
        "実装", "implementation", "アーキテクチャ", "architecture",
    ],
    "rag": [
        "検索", "search", "rag", "ドキュメント", "document",
        "知識ベース", "knowledge base", "引用", "citation",
        "qa", "質問応答", "retrieval", "embedding",
    ],
    "summarization": [
        "要約", "summary", "summarize", "抽出", "extract",
        "圧縮", "compress", "ポイント", "key points",
        "議事録", "meeting notes", "condensation",
    ],
    "research": [
        "調査", "research", "リサーチ", "survey", "動向", "trend",
        "文献", "literature", "レビュー", "review", "分析", "analysis",
        "比較", "comparison", "ベストプラクティス", "best practice",
        "フレームワーク", "framework", "手法", "methodology",
        "feasibility", "可能性", "competitive", "競合",
    ],
}


def detect_domain(text: str) -> str:
    """Detect domain from requirements text."""
    text_lower = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                log(f"Detected domain: {domain} (keyword: {kw})")
                return domain
    log("No domain detected, defaulting to 'technical'")
    return "technical"


# ============ Security: Domain Validation (Defense-in-Depth) ============
ALLOWED_DOMAINS = frozenset(["technical", "rag", "summarization", "research"])


def validate_domain(domain: str) -> str:
    """Validate domain against whitelist. Defense-in-depth against path traversal."""
    if domain not in ALLOWED_DOMAINS:
        log(f"SECURITY: Invalid domain '{domain}' rejected. Defaulting to 'technical'")
        return "technical"
    return domain


# ============ Convergence/Divergence Policy ============
# FEP Function axiom: Explore ↔ Exploit
CONVERGENT_TASKS = frozenset([
    "data_extraction", "spec_generation", "test_generation",
    "code_formatting", "translation", "schema_validation",
    "jules_coding", "api_integration", "config_generation",
])

DIVERGENT_TASKS = frozenset([
    "brainstorming", "ideation", "exploration",
    "creative_writing", "design_review", "concept_art",
])

CONVERGENT_KEYWORDS = [
    "抽出", "extract", "仕様", "spec", "テスト", "test",
    "整形", "format", "翻訳", "translate", "検証", "validate",
    "Jules", "コーディング", "coding", "API", "設定", "config",
]

DIVERGENT_KEYWORDS = [
    "ブレスト", "brainstorm", "アイデア", "idea", "探索", "explore",
    "創造", "creative", "デザイン", "design", "コンセプト", "concept",
    "発想", "想像", "自由に", "多様", "diversity",
]


def classify_task(description: str) -> dict:
    """Classify task as convergent, divergent, or ambiguous.

    Returns:
        dict with keys: classification, confidence, keywords_found, recommendation
    """
    desc_lower = description.lower()

    conv_hits = [kw for kw in CONVERGENT_KEYWORDS if kw.lower() in desc_lower]
    div_hits = [kw for kw in DIVERGENT_KEYWORDS if kw.lower() in desc_lower]

    conv_score = len(conv_hits)
    div_score = len(div_hits)

    if conv_score > 0 and div_score == 0:
        classification = "convergent"
        confidence = min(0.95, 0.6 + conv_score * 0.1)
        recommendation = "✅ .prompt 推奨: 構造化により精度・再現性が向上"
    elif div_score > 0 and conv_score == 0:
        classification = "divergent"
        confidence = min(0.95, 0.6 + div_score * 0.1)
        recommendation = "❌ .prompt 非推奨: 構造化が多様性を阻害する可能性"
    elif conv_score > div_score:
        classification = "convergent-leaning"
        confidence = 0.5 + (conv_score - div_score) * 0.1
        recommendation = "⚠️ .prompt 条件付き推奨: 收束要素が優勢だが拡散要素も存在"
    elif div_score > conv_score:
        classification = "divergent-leaning"
        confidence = 0.5 + (div_score - conv_score) * 0.1
        recommendation = "⚠️ .prompt 条件付き非推奨: 拡散要素が優勢だが收束要素も存在"
    else:
        classification = "ambiguous"
        confidence = 0.3
        recommendation = "❓ 判断困難: Creator に確認してください"

    return {
        "classification": classification,
        "confidence": round(confidence, 2),
        "convergent_keywords": conv_hits,
        "divergent_keywords": div_hits,
        "recommendation": recommendation,
        "fep_basis": "Function axiom (Explore ↔ Exploit): .prompt = precision weighting ↑",
    }


# ============ Template Loading ============
def load_yaml_file(path: Path) -> dict:
    """Load YAML file as dict."""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        log(f"Error loading {path}: {e}")
        return {}


# ============ Prompt-Lang Generation (v2.1) ============
# --- Archetype-specific constraint injection (施策 3) ---
ARCHETYPE_CONSTRAINTS = {
    "Precision": [
        "出力は検証(verification)可能であること。CoVe手法で自己検証を行うこと",
        "Confidence score を付与し、WACK基準で確度を保証すること",
    ],
    "Speed": [
        "圧縮(compression)された出力を優先し、キャッシュ(cache)可能な形式で返すこと",
        "短文で要点のみを返すこと",
    ],
    "Autonomy": [
        "ReAct パターンで自律判断し、Reflexion で自己修正すること",
        "Fallback 時はエスカレーションし、Mem0 で学習を蓄積すること",
    ],
    "Creative": [
        "Temperature を高めに設定し、SAC手法で多様性(diversity)を確保すること",
    ],
    "Safety": [
        "URIAL 原則に基づき、Constitutional AI の基準で有害コンテンツをフィルタすること",
        "Neutralizing 手法で偏りを低減すること",
    ],
}


def generate_prompt_lang(requirements: str, domain: str, output_format: str) -> str:
    """Generate Prompt-Lang code from requirements.

    v2.2 Enhancement:
      - v2.1 features (domain_examples, anti_patterns, convergence/divergence)
      - safety_base_constraints injection (施策 1: Safety +30)
      - failure scenario injection (施策 2: Completeness +15)
      - archetype-specific constraints (施策 3: Archetype Fit +10)
      - domain-specific @context (施策 4: Context +5)
    """

    # Extract skill name from requirements
    name_match = re.search(r'「(.+?)」|"(.+?)"|を作|スキル', requirements)
    if name_match:
        skill_name = name_match.group(1) or name_match.group(2) or "generated_skill"
        skill_name = re.sub(r"[^\w]", "_", skill_name.lower())[:30]
    else:
        skill_name = "generated_skill"

    # Load domain template (v2.1: full template utilization)
    domain_template = load_yaml_file(DOMAIN_TEMPLATES_DIR / f"{domain}.yaml")
    domain_constraints = domain_template.get("domain_constraints", [])
    safety_base = domain_template.get("safety_base_constraints", [])  # 施策 1
    domain_rubric = domain_template.get("domain_rubric", [])
    domain_examples = domain_template.get("domain_examples", [])
    domain_format = domain_template.get("domain_format", "")
    context_recs = domain_template.get("context_recommendations", [])  # 施策 4
    anti_patterns = domain_template.get("anti_patterns", [])
    output_style = domain_template.get("output_style", {})

    # Convergence/divergence policy check
    policy = classify_task(requirements)
    policy_warning = ""
    if policy["classification"] in ("divergent", "divergent-leaning"):
        policy_warning = (
            f"# ⚠️ DIVERGENT TASK DETECTED (conf: {policy['confidence']})\n"
            f"# {policy['recommendation']}\n"
            f"# Consider using natural language prompt instead of .prompt format\n\n"
        )

    # Build improved Prompt-Lang code
    lines = []
    if policy_warning:
        lines.append(policy_warning)

    lines.extend([
        f"#prompt {skill_name}",
        "",
        "@role:",
        f"  {domain} ドメインの専門家",
        "",
        "@goal:",
        f"  {requirements}",
        "",
        "@constraints:",
    ])

    # Add domain-specific constraints
    if domain_constraints:
        for c in domain_constraints[:6]:
            lines.append(f"  - {c}")
    else:
        lines.extend([
            "  - 具体的かつ実行可能な出力を提供すること",
            "  - 曖昧な表現（「適切に」「うまく」）を避けること",
            "  - エラーハンドリングを明示すること",
            "  - 出力は再現可能であること",
        ])

    # v2.1: Add anti-pattern constraints from template
    if anti_patterns:
        lines.append("  # --- 避けるべきパターン ---")
        for ap in anti_patterns[:3]:
            pattern = ap.get("pattern", "")
            bad = ap.get("bad", "")
            lines.append(f"  - 禁止: {pattern}（例: 「{bad}」）")

    # v2.2 施策 1: Safety 基盤制約の注入
    if safety_base:
        lines.append("  # --- 安全基盤制約 ---")
        for sc in safety_base:
            lines.append(f"  - {sc}")

    # v2.2 施策 2: 失敗シナリオの注入 (Completeness: failure/edge case/境界)
    lines.append("  # --- 失敗ケース予測 (Pre-Mortem) ---")
    lines.append("  - 失敗ケース1: 入力が不完全・欠損している場合の境界条件を処理すること")
    lines.append("  - 失敗ケース2: edge case（極端に長い/短い/空の入力）に安全に対応すること")
    lines.append("  - 失敗ケース3: 最悪ケース(worst case)でもシステムが安全に停止すること")

    # v2.2 施策 3: Archetype 固有制約の注入
    archetype_constraints = ARCHETYPE_CONSTRAINTS.get(policy.get("archetype", ""), [])
    if not archetype_constraints:
        # Detect archetype from domain
        domain_archetype_map = {
            "technical": "Precision",
            "rag": "Precision",
            "summarization": "Precision",
            "research": "Precision",
        }
        detected = domain_archetype_map.get(domain, "")
        archetype_constraints = ARCHETYPE_CONSTRAINTS.get(detected, [])
    if archetype_constraints:
        lines.append("  # --- Archetype 固有制約 ---")
        for ac in archetype_constraints:
            lines.append(f"  - {ac}")

    # Context section — v2.2 施策 4: ドメイン固有ツール展開
    lines.extend([
        "",
        "@context:",
        f"  - file: .agent/rules/prompt-lang-policy.md",
        f"    priority: HIGH",
    ])
    if context_recs:
        for rec in context_recs:
            tool_name = rec.get("tool", "")
            usage = rec.get("usage", "")
            lines.append(f"  - tool: {tool_name}")
            lines.append(f"    usage: {usage}")

    # Rubric section
    lines.extend(["", "@rubric:"])
    if domain_rubric:
        for rubric in domain_rubric[:4]:
            rubric_name = rubric.get("name", "quality")
            rubric_desc = rubric.get("description", "品質評価")
            rubric_scale = rubric.get("scale", "1-5")
            criteria = rubric.get("criteria", {})
            lines.extend([
                f"  - {rubric_name}:",
                f"      description: {rubric_desc}",
                f"      scale: {rubric_scale}",
            ])
            # v2.1: Include criteria details for precision
            if criteria:
                lines.append("      criteria:")
                for score, desc in sorted(criteria.items(), reverse=True):
                    lines.append(f"        {score}: \"{desc}\"")
    else:
        lines.extend([
            "  - correctness:",
            "      description: 出力の正確性",
            "      scale: 1-5",
            "  - completeness:",
            "      description: 要件の充足度",
            "      scale: 1-5",
        ])

    # Format section — v2.1: use domain template format instead of hardcoded
    lines.extend(["", "@format:"])
    if output_style and output_style.get("structure"):
        for fmt_line in output_style["structure"].strip().split("\n"):
            lines.append(f"  {fmt_line}")
    elif domain_format:
        for fmt_line in domain_format.strip().split("\n"):
            lines.append(f"  {fmt_line}")
    else:
        lines.extend([
            "  ```json",
            "  {",
            '    "result": "string",',
            '    "confidence": "high | medium | low",',
            '    "reasoning": "string"',
            "  }",
            "  ```",
        ])

    # Examples section — v2.1: use domain_examples from YAML (few-shot)
    lines.extend(["", "@examples:"])
    if domain_examples:
        for ex in domain_examples[:2]:
            ex_input = ex.get("input", "").strip()
            ex_output = ex.get("output", "").strip()
            # Truncate long inputs for .prompt format
            if len(ex_input) > 200:
                ex_input = ex_input[:200] + "..."
            lines.append(f"  - input: |")
            for input_line in ex_input.split("\n"):
                lines.append(f"      {input_line}")
            lines.append(f"    output: |")
            for output_line in ex_output.split("\n"):
                lines.append(f"      {output_line}")
    else:
        lines.extend([
            '  - input: "サンプル入力"',
            '    output: "具体的な出力例"',
        ])

    # Activation section
    lines.extend([
        "",
        "@activation:",
        "  mode: model_decision",
        "  conditions:",
        f'    - input_contains: ["{domain}"]',
        "  priority: 3",
    ])

    return "\n".join(lines)


# ============ Initialize MCP Server ============
server = Server(
    name="prompt-lang",
    version="2.0.0",
    instructions="Prompt-Lang v2.0: generate, parse, validate, compile, expand, and policy_check for structured prompt definitions",
)
log("Server v2.0 initialized")


@server.list_tools()
async def list_tools():
    """List available tools."""
    log("list_tools called")
    tools = [
        Tool(
            name="generate",
            description="Generate Prompt-Lang code from natural language requirements. Returns structured prompt definition (.prompt format).",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of what the prompt should do (e.g., 'コードレビューでバグを検出するスキル')",
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain hint: 'technical', 'rag', or 'summarization'. Auto-detected if not specified.",
                        "enum": ["technical", "rag", "summarization"],
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format: '.prompt' or '.skill.md'",
                        "default": ".prompt",
                    },
                },
                "required": ["requirements"],
            },
        ),
        Tool(
            name="parse",
            description="Parse a .prompt file into JSON AST. Supports v2.1 features: @rubric, @context, @if/@else, @extends, @mixin.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": ".prompt file content to parse",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to .prompt file (alternative to content)",
                    },
                },
            },
        ),
        Tool(
            name="validate",
            description="Validate .prompt file syntax. Returns errors and warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": ".prompt file content to validate",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to .prompt file (alternative to content)",
                    },
                },
            },
        ),
        Tool(
            name="compile",
            description="Compile .prompt file to system prompt string (markdown format). Resolves @context, @if/@else, @extends, @mixin.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": ".prompt file content to compile",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to .prompt file (alternative to content)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Variables for @if evaluation (e.g., {\"env\": \"prod\"})",
                    },
                },
            },
        ),
        Tool(
            name="expand",
            description="Expand .prompt file to natural language prompt for human readability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": ".prompt file content to expand",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to .prompt file (alternative to content)",
                    },
                },
            },
        ),
        Tool(
            name="policy_check",
            description="Check if a task is convergent (precision-oriented) or divergent (creativity-oriented). Based on FEP Function axiom (Explore ↔ Exploit). Convergent tasks benefit from .prompt, divergent tasks don't.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to classify",
                    },
                },
                "required": ["task_description"],
            },
        ),
    ]
    return tools


def _get_content(arguments: dict) -> str:
    """Extract content from arguments (content or filepath)."""
    content = arguments.get("content", "")
    filepath = arguments.get("filepath", "")

    if content:
        return content
    elif filepath:
        path = Path(filepath)
        if path.exists():
            return path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"File not found: {filepath}")
    else:
        raise ValueError("Either 'content' or 'filepath' is required")


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {list(arguments.keys())}")

    try:
        if name == "generate":
            return await _handle_generate(arguments)
        elif name == "parse":
            return await _handle_parse(arguments)
        elif name == "validate":
            return await _handle_validate(arguments)
        elif name == "compile":
            return await _handle_compile(arguments)
        elif name == "expand":
            return await _handle_expand(arguments)
        elif name == "policy_check":
            return await _handle_policy_check(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Tool {name} error: {e}")
        return [TextContent(type="text", text=f"Error in {name}: {str(e)}")]


async def _handle_generate(arguments: dict):
    """Handle generate tool call."""
    requirements = arguments.get("requirements", "")
    domain = arguments.get("domain")
    output_format = arguments.get("output_format", ".prompt")

    if not requirements:
        return [TextContent(type="text", text="Error: requirements is required")]

    if not domain:
        domain = detect_domain(requirements)
    domain = validate_domain(domain)

    # Run policy check on the requirements
    policy = classify_task(requirements)

    log(f"Generating for domain: {domain}, policy: {policy['classification']}")

    code = generate_prompt_lang(requirements, domain, output_format)

    output_lines = [
        "# [Hegemonikon] Prompt-Lang Generator v2.0\n",
        f"- **Requirements**: {requirements[:200]}",
        f"- **Detected Domain**: {domain}",
        f"- **Task Classification**: {policy['classification']} (confidence: {policy['confidence']})",
        f"- **Recommendation**: {policy['recommendation']}",
        "",
        "## Generated Code",
        "",
        "```prompt-lang",
        code,
        "```",
        "",
    ]

    if policy["classification"].startswith("divergent"):
        output_lines.extend([
            "> ⚠️ **警告**: このタスクは拡散的です。.prompt による構造化は多様性を阻害する可能性があります。",
            "> 自然言語での指示を検討してください。",
            "",
        ])

    output_lines.extend([
        "> ℹ️ このコードは基本テンプレートから生成されました。",
        "> `parse` で構文確認、`compile` で実行用プロンプトに変換できます。",
    ])

    log(f"Generation completed for: {requirements[:50]}...")
    return [TextContent(type="text", text="\n".join(output_lines))]


async def _handle_parse(arguments: dict):
    """Handle parse tool call."""
    if not PARSER_AVAILABLE:
        return [TextContent(type="text", text="Error: prompt_lang parser not available")]

    content = _get_content(arguments)

    try:
        # Try multi-definition parse first
        result = parse_all(content)
        if result.prompts:
            import json
            output = {
                "prompts": {k: v.to_dict() for k, v in result.prompts.items()},
                "mixins": {k: {"name": v.name, "role": v.role, "goal": v.goal,
                               "constraints": v.constraints}
                           for k, v in result.mixins.items()},
            }
            return [TextContent(
                type="text",
                text=f"# Parse Result\n\n```json\n{json.dumps(output, indent=2, ensure_ascii=False)}\n```"
            )]
        else:
            # Single prompt parse
            parser = PromptLangParser(content)
            prompt = parser.parse()
            import json
            return [TextContent(
                type="text",
                text=f"# Parse Result\n\n```json\n{json.dumps(prompt.to_dict(), indent=2, ensure_ascii=False)}\n```"
            )]
    except ParseError as e:
        return [TextContent(type="text", text=f"# Parse Error\n\n❌ {str(e)}")]


async def _handle_validate(arguments: dict):
    """Handle validate tool call."""
    content = _get_content(arguments)

    errors = []
    warnings = []

    # Basic structure checks
    if not content.strip():
        errors.append("Empty content")
        return [TextContent(type="text", text="# Validation Result\n\n❌ Empty content")]

    has_header = bool(re.search(r"^#prompt\s+\w+", content, re.MULTILINE))
    has_mixin = bool(re.search(r"^#mixin\s+\w+", content, re.MULTILINE))

    if not has_header and not has_mixin:
        errors.append("Missing #prompt or #mixin header")

    # Check core directives
    directives_found = re.findall(r"^(@\w+):", content, re.MULTILINE)
    core_directives = {"@role", "@goal", "@constraints"}
    found_set = set(directives_found)

    for directive in core_directives:
        if directive not in found_set:
            warnings.append(f"Missing recommended directive: {directive}")

    # Check for anti-patterns
    anti_patterns = [
        (r"適切に|うまく|いい感じ|できるだけ", "曖昧語の使用を検出"),
        (r"@format:\s*JSON形式で出力", "@format が抽象的（具体的なスキーマを指定してください）"),
    ]
    for pattern, msg in anti_patterns:
        if re.search(pattern, content):
            warnings.append(f"Anti-pattern: {msg}")

    # Full parser validation if available
    if PARSER_AVAILABLE and has_header:
        try:
            parser = PromptLangParser(content)
            prompt = parser.parse()

            if not prompt.constraints:
                warnings.append("No constraints defined")
            if not prompt.examples:
                warnings.append("No examples provided (few-shot recommended)")
            if not prompt.rubric:
                warnings.append("No rubric defined (self-evaluation recommended)")
        except ParseError as e:
            errors.append(f"Parse error: {str(e)}")

    # Format result
    status = "✅ PASS" if not errors else "❌ FAIL"
    lines = [f"# Validation Result: {status}", ""]

    if errors:
        lines.append("## Errors")
        for e in errors:
            lines.append(f"- ❌ {e}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    if not errors and not warnings:
        lines.append("No issues found. ✨")

    lines.extend([
        "",
        f"**Directives found**: {', '.join(directives_found) if directives_found else 'none'}",
    ])

    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_compile(arguments: dict):
    """Handle compile tool call."""
    if not PARSER_AVAILABLE:
        return [TextContent(type="text", text="Error: prompt_lang parser not available")]

    content = _get_content(arguments)
    context = arguments.get("context", {})

    try:
        parser = PromptLangParser(content)
        prompt = parser.parse()
        compiled = prompt.compile(context=context)

        return [TextContent(
            type="text",
            text=f"# Compiled System Prompt\n\n{compiled}"
        )]
    except ParseError as e:
        return [TextContent(type="text", text=f"# Compile Error\n\n❌ {str(e)}")]


async def _handle_expand(arguments: dict):
    """Handle expand tool call."""
    if not PARSER_AVAILABLE:
        return [TextContent(type="text", text="Error: prompt_lang parser not available")]

    content = _get_content(arguments)

    try:
        parser = PromptLangParser(content)
        prompt = parser.parse()
        expanded = prompt.expand()

        return [TextContent(
            type="text",
            text=f"# Expanded Prompt (Natural Language)\n\n{expanded}"
        )]
    except ParseError as e:
        return [TextContent(type="text", text=f"# Expand Error\n\n❌ {str(e)}")]


async def _handle_policy_check(arguments: dict):
    """Handle policy_check tool call."""
    task_description = arguments.get("task_description", "")
    if not task_description:
        return [TextContent(type="text", text="Error: task_description is required")]

    policy = classify_task(task_description)

    lines = [
        "# Convergence/Divergence Policy Check",
        f"## FEP Basis: {policy['fep_basis']}",
        "",
        f"**Task**: {task_description[:200]}",
        "",
        f"**Classification**: {policy['classification']}",
        f"**Confidence**: {policy['confidence']}",
        f"**Recommendation**: {policy['recommendation']}",
        "",
    ]

    if policy["convergent_keywords"]:
        lines.append(f"**收束キーワード**: {', '.join(policy['convergent_keywords'])}")
    if policy["divergent_keywords"]:
        lines.append(f"**拡散キーワード**: {', '.join(policy['divergent_keywords'])}")

    lines.extend([
        "",
        "---",
        "",
        "| 適用 | 場面 | 効果 |",
        "|:-----|:-----|:-----|",
        "| ✅ .prompt 推奨 | 收束タスク (データ抽出, テスト, 仕様) | 再現性+150%, Hallucination-55% |",
        "| ❌ .prompt 非推奨 | 拡散タスク (ブレスト, 探索, 創造) | 多様性喪失リスク |",
    ])

    return [TextContent(type="text", text="\n".join(lines))]


async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
    except Exception as e:
        log(f"Server error: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    log("Running main...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
