# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP経由のアクセスが必要→prompt_lang_mcp_server が担う
#!/usr/bin/env python3
"""
Prompt-Lang MCP Server - Hegemonikón Skill Generator

Model Context Protocol server for Prompt-Lang code generation.
Exposes generate tool via stdio transport.

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


# PURPOSE: log — MCPサービスの処理
def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Prompt-Lang MCP Server...")
log(f"Python: {sys.executable}")
log(f"Platform: {sys.platform}")

# ============ Import path setup ============
sys.path.insert(0, str(Path(__file__).parent.parent))
log(f"Added to path: {Path(__file__).parent.parent}")


# ============ Suppress stdout during imports ============
# PURPOSE: クラス: StdoutSuppressor
class StdoutSuppressor:
    # PURPOSE: StdoutSuppressor の構成と依存関係の初期化
    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    # PURPOSE: enter__ — MCPサービスの内部処理
    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    # PURPOSE: exit__ — MCPサービスの内部処理
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

# ============ Paths ============
SKILL_DIR = Path(__file__).parent.parent / ".agent/skills/utils/prompt-lang-generator"
TEMPLATES_DIR = SKILL_DIR / "templates"
DOMAIN_TEMPLATES_DIR = TEMPLATES_DIR / "domain_templates"

log(f"SKILL_DIR: {SKILL_DIR}")

# ============ Domain Detection ============
DOMAIN_KEYWORDS = {
    "technical": [
        "コードレビュー",
        "code review",
        "セキュリティ",
        "security",
        "api",
        "endpoint",
        "バグ",
        "bug",
        "デバッグ",
        "debug",
        "リファクタリング",
        "refactor",
        "テスト",
        "test",
    ],
    "rag": [
        "検索",
        "search",
        "rag",
        "ドキュメント",
        "document",
        "知識ベース",
        "knowledge base",
        "引用",
        "citation",
        "qa",
        "質問応答",
    ],
    "summarization": [
        "要約",
        "summary",
        "summarize",
        "抽出",
        "extract",
        "圧縮",
        "compress",
        "ポイント",
        "key points",
        "議事録",
        "meeting notes",
    ],
# PURPOSE: Detect domain from requirements text.
}


# PURPOSE: Detect domain from requirements text.
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
# PURPOSE: Validate domain against whitelist.
ALLOWED_DOMAINS = frozenset(["technical", "rag", "summarization"])


# PURPOSE: Validate domain against whitelist.
def validate_domain(domain: str) -> str:
    """
    Validate domain against whitelist.

    Defense-in-depth: Even though MCP SDK enforces enum constraint,
    we explicitly validate to prevent path traversal if validation is disabled.

    Security Note (from Synedrion v2 review):
    - Line 130 uses domain directly in file path construction
    - This validation prevents ../../ traversal attacks
    """
    if domain not in ALLOWED_DOMAINS:
        log(f"SECURITY: Invalid domain '{domain}' rejected. Defaulting to 'technical'")
        return "technical"
    return domain
# PURPOSE: Load YAML file as dict.


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
# PURPOSE: Generate Prompt-Lang code from requirements.


# ============ Prompt-Lang Generation ============
def generate_prompt_lang(requirements: str, domain: str, output_format: str) -> str:
    """Generate Prompt-Lang code from requirements."""

    # Extract skill name from requirements
    name_match = re.search(r'「(.+?)」|"(.+?)"|を作|スキル', requirements)
    if name_match:
        skill_name = name_match.group(1) or name_match.group(2) or "generated_skill"
        skill_name = re.sub(r"[^\w]", "_", skill_name.lower())[:30]
    else:
        skill_name = "generated_skill"

    # Load domain template for constraints/rubric hints
    domain_template = load_yaml_file(DOMAIN_TEMPLATES_DIR / f"{domain}.yaml")
    domain_constraints = domain_template.get("domain_constraints", [])
    domain_rubric = domain_template.get("domain_rubric", [])

    # Build Prompt-Lang code
    lines = [
        f"#prompt {skill_name}",
        "",
        "@role:",
        f"  {domain} ドメインの専門家",
        "",
        "@goal:",
        f"  {requirements}",
        "",
        "@constraints:",
    ]

    # Add domain-specific constraints
    if domain_constraints:
        for c in domain_constraints[:3]:
            lines.append(f"  - {c}")
    else:
        lines.extend(
            [
                "  - 具体的かつ実行可能な出力を提供すること",
                "  - 曖昧な表現（「適切に」「うまく」）を避けること",
                "  - エラーハンドリングを明示すること",
            ]
        )

    lines.extend(
        [
            "",
            "@rubric:",
        ]
    )

    # Add rubric from domain template or default
    if domain_rubric:
        rubric = domain_rubric[0]
        lines.extend(
            [
                f"  - {rubric.get('name', 'quality')}:",
                f"      description: {rubric.get('description', '品質評価')}",
                f"      scale: {rubric.get('scale', '1-5')}",
            ]
        )
    else:
        lines.extend(
            ["  - quality:", "      description: 出力の品質", "      scale: 1-5"]
        )

    lines.extend(
        [
            "",
            "@format:",
            "  ```json",
            "  {",
            '    "result": "string",',
            '    "confidence": "high | medium | low"',
            "  }",
            "  ```",
            "",
            "@examples:",
            '  - input: "サンプル入力"',
            "    output: |",
            "      {",
            '        "result": "サンプル出力",',
            '        "confidence": "high"',
            "      }",
        ]
    )

    return "\n".join(lines)


# ============ Initialize MCP Server ============
server = Server(
    name="prompt-lang",
    version="1.0.0",
    instructions="Prompt-Lang code generator for structured prompt definitions",
)
log("Server initialized")
# PURPOSE: List available tools.


@server.list_tools()
async def list_tools():
    """List available tools."""
    log("list_tools called")
    return [
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
        )
    ]
# PURPOSE: Handle tool calls.


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {arguments}")

    if name == "generate":
        requirements = arguments.get("requirements", "")
        domain = arguments.get("domain")
        output_format = arguments.get("output_format", ".prompt")

        if not requirements:
            return [TextContent(type="text", text="Error: requirements is required")]

        try:
            # Auto-detect domain if not specified
            if not domain:
                domain = detect_domain(requirements)

            # Security: Validate domain (defense-in-depth)
            domain = validate_domain(domain)

            log(f"Generating for domain: {domain}")

            # Generate Prompt-Lang code
            code = generate_prompt_lang(requirements, domain, output_format)

            output_lines = [
                "# [Hegemonikon] Prompt-Lang Generator\n",
                f"- **Requirements**: {requirements[:100]}...",
                f"- **Detected Domain**: {domain}",
                f"- **Output Format**: {output_format}",
                "",
                "## Generated Code",
                "",
                "```prompt-lang",
                code,
                "```",
                "",
                "> ℹ️ このコードは基本テンプレートから生成されました。",
                "> 必要に応じて @constraints, @examples を調整してください。",
            ]

            log(f"Generation completed for: {requirements[:50]}...")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Generate error: {e}")
            return [TextContent(type="text", text=f"Error generating: {str(e)}")]

    else:
# PURPOSE: Run the MCP server.
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# PURPOSE: Run the MCP server.
async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],  # read_stream
                streams[1],  # write_stream
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
