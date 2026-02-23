# PROOF: [L2/インフラ] <- mekhane/mcp/ Ochēma MCP Server
# PURPOSE: Ochēma MCP Server — Antigravity Language Server Bridge
#!/usr/bin/env python3
"""
Ochēma MCP Server — Antigravity Language Server Bridge

Send prompts to LLM (Claude/Gemini) via local Language Server.
Also provides status, model listing, Jules code tasks, and chat.

WARNING: ToS グレーゾーン。実験用途限定。公開禁止。
"""

import sys
import os
import uuid

from mekhane.mcp.mcp_base import MCPBase, StdoutSuppressor
from mcp.types import TextContent, Tool
from pathlib import Path

_base = MCPBase(
    "ochema",
    "0.2.0",
    "Ochēma — Antigravity Language Server bridge. "
    "Send prompts to LLM (Claude/Gemini) via local Language Server. "
    "Also provides status, model listing, Jules tasks, and chat.",
)
server = _base.server
log = _base.log

# OchemaService — unified LLM service (singleton)
# PURPOSE: get_service — OchemaService シングルトン取得
def get_service():
    """OchemaService をシングルトンで取得。"""
    with StdoutSuppressor():
        from mekhane.ochema.service import OchemaService
    svc = OchemaService.get()
    log(f"OchemaService: {svc}")
    return svc

# ============ Stateful Chat Conversations ============
_MAX_CONVERSATIONS = 10
_conversations: dict[str, object] = {}  # {conv_id: ChatConversation}

# ============ Jules API Key Pool (from jules_mcp_server.py) ============
_jules_api_key_pool = []
_jules_api_key_index = 0
_jules_dashboard = None


def _jules_init_pool():
    """Load Jules API keys from environment (JULES_API_KEY_01 to JULES_API_KEY_18)."""
    global _jules_api_key_pool, _jules_dashboard
    for i in range(1, 19):
        key_name = f"JULES_API_KEY_{i:02d}"
        key = os.environ.get(key_name)
        if key:
            _jules_api_key_pool.append((i, key))
    log(f"Jules API Key Pool: {len(_jules_api_key_pool)} keys loaded")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "synergeia"))
        from jules_dashboard import JulesDashboard
        _jules_dashboard = JulesDashboard()
    except ImportError:
        pass


def _jules_get_key():
    """Get next Jules API key (load-balanced or round-robin)."""
    global _jules_api_key_index, _jules_dashboard
    if not _jules_api_key_pool:
        _jules_init_pool()
    if not _jules_api_key_pool:
        return None, 0
    if _jules_dashboard:
        try:
            _, best_idx = _jules_dashboard.get_best_account()
            for idx, key in _jules_api_key_pool:
                if idx == best_idx:
                    return key, idx
        except Exception:
            pass
    idx, key = _jules_api_key_pool[_jules_api_key_index % len(_jules_api_key_pool)]
    _jules_api_key_index += 1
    return key, idx


def _jules_record(key_index: int, session_id: str):
    """Record Jules usage."""
    if _jules_dashboard:
        try:
            _jules_dashboard.record_usage(key_index, session_id)
        except Exception:
            pass


# PURPOSE: [L2-auto] List available tools.

@server.list_tools()
async def list_tools():
    """List available tools."""
    log("list_tools called")
    return [
        Tool(
            name="ask",
            description=(
                "Send a prompt to an LLM via Antigravity Language Server. "
                "Returns the LLM response text, thinking process, and model info. "
                "Available models: Claude Sonnet 4.5 Thinking (default), "
                "Claude Opus 4.6 Thinking, Gemini 2.5 Pro, Gemini 2.5 Flash."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The prompt to send to the LLM",
                    },
                    "model": {
                        "type": "string",
                        "description": (
                            "Model enum string. Defaults to MODEL_CLAUDE_4_5_SONNET_THINKING. "
                            "Options: MODEL_CLAUDE_4_5_SONNET_THINKING, "
                            "MODEL_PLACEHOLDER_M26 (Opus 4.6), "
                            "MODEL_GEMINI_2_5_PRO, MODEL_GEMINI_2_5_FLASH"
                        ),
                        "default": "MODEL_CLAUDE_4_5_SONNET_THINKING",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Max wait seconds for LLM response (default: 120)",
                        "default": 120,
                    },
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="ask_cortex",
            description=(
                "Send a prompt to Gemini via Cortex API (direct, no Language Server). "
                "Faster and more reliable than LS-proxied calls. "
                "Available models: gemini-2.0-flash (default), gemini-2.5-pro, "
                "gemini-2.5-flash, gemini-3-pro-preview, gemini-3-flash-preview."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The prompt to send to Gemini",
                    },
                    "model": {
                        "type": "string",
                        "description": (
                            "Gemini model name. Options: gemini-2.0-flash (default), "
                            "gemini-2.5-pro, gemini-2.5-flash, "
                            "gemini-3-pro-preview, gemini-3-flash-preview"
                        ),
                        "default": "gemini-2.0-flash",
                    },
                    "system_instruction": {
                        "type": "string",
                        "description": "Optional system instruction for the model",
                    },
                    "max_tokens": {
                        "type": "number",
                        "description": "Maximum output tokens (default: 8192)",
                        "default": 8192,
                    },
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="ask_chat",
            description=(
                "Chat with Gemini via generateChat API (direct, no Language Server). "
                "Supports multi-turn conversation with history. "
                "2MB context window, 100+ turns. Uses Gemini 3 Pro Preview."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send",
                    },
                    "history": {
                        "type": "array",
                        "description": (
                            "Conversation history. Array of objects with "
                            "'author' (1=user, 2=model) and 'content' (string)"
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "author": {"type": "number"},
                                "content": {"type": "string"},
                            },
                        },
                    },
                    "tier_id": {
                        "type": "string",
                        "description": "Model routing tier (empty=default, g1-ultra-tier=premium)",
                        "default": "",
                    },
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="start_chat",
            description=(
                "Start a stateful multi-turn chat conversation. "
                "Returns a conversation_id to use with send_chat. "
                "Supports Claude and Gemini models. Max 10 concurrent conversations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": (
                            "Model config ID (e.g. 'claude-sonnet-4-5'). "
                            "Empty = server default"
                        ),
                        "default": "",
                    },
                    "tier_id": {
                        "type": "string",
                        "description": "Model routing tier (empty=default)",
                        "default": "",
                    },
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
            },
        ),
        Tool(
            name="send_chat",
            description=(
                "Send a message to an existing chat conversation. "
                "Requires conversation_id from start_chat. "
                "History is managed server-side automatically."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "Conversation ID from start_chat",
                    },
                    "message": {
                        "type": "string",
                        "description": "The message to send",
                    },
                },
                "required": ["conversation_id", "message"],
            },
        ),
        Tool(
            name="close_chat",
            description="Close a chat conversation and free resources.",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "Conversation ID to close",
                    },
                },
                "required": ["conversation_id"],
            },
        ),
        Tool(
            name="cortex_quota",
            description="Get Gemini API quota (remaining requests per model).",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
            },
        ),
        Tool(
            name="status",
            description="Get Language Server connection status and quota info.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="models",
            description="List available LLM models with remaining quota percentages.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="session_info",
            description=(
                "Get current session info: step count, Context Rot risk score, "
                "and session metadata. Use to monitor context health."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "Optional: specific conversation ID to inspect. If omitted, shows all active sessions.",
                    },
                },
            },
        ),
        Tool(
            name="ask_with_tools",
            description=(
                "Send a prompt to Gemini with Tool Use (Function Calling). "
                "AI can autonomously read/write local files, search text, "
                "list directories, and run shell commands. "
                "Agent loop: prompt → LLM → functionCall → execute locally → "
                "send result back → repeat until final text response."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The prompt to send (AI will use tools to fulfill it)",
                    },
                    "model": {
                        "type": "string",
                        "description": (
                            "Gemini model. Options: gemini-3-pro-preview (default), "
                            "gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, "
                            "gemini-3-flash-preview. "
                            "Claude models (via LS): MODEL_CLAUDE_4_5_SONNET_THINKING, "
                            "MODEL_PLACEHOLDER_M26 (Opus 4.6)"
                        ),
                        "default": "gemini-3-pro-preview",
                    },
                    "system_instruction": {
                        "type": "string",
                        "description": (
                            "Optional system prompt for the AI. "
                            "Or use a template name: 'default', 'hgk_citizen', "
                            "'code_review', 'researcher'"
                        ),
                    },
                    "thinking_budget": {
                        "type": "integer",
                        "description": (
                            "Thinking token budget. Controls depth of reasoning. "
                            "0=minimal, 1024=light, 8192=standard, 32768=deep (default). "
                            "None=model default."
                        ),
                        "default": 32768,
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Max tool call rounds (default: 10)",
                        "default": 10,
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Max output tokens per call (default: 8192)",
                        "default": 8192,
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Per-API-call timeout seconds (default: 120)",
                        "default": 120,
                    },
                    "account": {
                        "type": "string",
                        "description": "TokenVault account name (default: 'default')",
                        "default": "default",
                    },
                },
                "required": ["message"],
            },
        ),
        # ============ Jules tools (from jules_mcp_server.py) ============
        Tool(
            name="jules_create_task",
            description="Create a single Jules code generation task. Returns session ID for tracking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Task description (e.g., 'Fix bug in utils.py')"},
                    "repo": {"type": "string", "description": "Repository in format 'owner/repo'"},
                    "branch": {"type": "string", "description": "Starting branch (default: main)", "default": "main"},
                },
                "required": ["prompt", "repo"],
            },
        ),
        Tool(
            name="jules_get_status",
            description="Get status of a Jules session by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID from jules_create_task"},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="jules_list_repos",
            description="List available GitHub repositories connected to Jules.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="jules_batch_execute",
            description="Execute multiple Jules tasks in parallel (max 30 concurrent). Waits for all to complete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "List of task objects with 'prompt', 'repo', optional 'branch'",
                        "items": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string"},
                                "repo": {"type": "string"},
                                "branch": {"type": "string"},
                            },
                            "required": ["prompt", "repo"],
                        },
                    },
                    "max_concurrent": {
                        "type": "integer",
                        "description": "Maximum concurrent sessions (default: 30, max: 60)",
                        "default": 30,
                    },
                },
                "required": ["tasks"],
            },
        ),
    ]

# PURPOSE: [L2-auto] Handle tool calls.

@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {arguments}")

    if name == "ask":
        message = arguments.get("message", "")
        model = arguments.get("model", "MODEL_CLAUDE_4_5_SONNET_THINKING")
        timeout = arguments.get("timeout", 120)

        if not message:
            return [TextContent(type="text", text="Error: message is required")]

        try:
            svc = get_service()
            log(f"Sending to {model}: {message[:50]}...")

            response = svc.ask(message, model=model, timeout=timeout)

            output_lines = [
                "# Ochēma LLM Response\n",
                f"**Model**: {response.model}",
                f"**Cascade ID**: {response.cascade_id[:16]}...",
                "",
                "## Response\n",
                response.text,
            ]

            if response.thinking:
                output_lines.extend([
                    "",
                    "## Thinking\n",
                    response.thinking[:1000],
                ])

            if response.token_usage:
                output_lines.extend([
                    "",
                    "## Token Usage\n",
                    f"```json\n{response.token_usage}\n```",
                ])

            log(f"Response received: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except TimeoutError as e:
            log(f"Timeout: {e}")
            return [TextContent(type="text", text=f"Error: LLM response timed out ({timeout}s)")]
        except Exception as e:
            log(f"Ask error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "ask_cortex":
        message = arguments.get("message", "")
        model = arguments.get("model", "gemini-2.0-flash")
        system_instruction = arguments.get("system_instruction")
        max_tokens = int(arguments.get("max_tokens", 8192))
        timeout = float(arguments.get("timeout", 120))
        account = arguments.get("account", "default")

        if not message:
            return [TextContent(type="text", text="Error: message is required")]

        try:
            svc = get_service()
            log(f"Asking {model} (account={account}): {message[:50]}...")

            response = svc.ask(
                message,
                model=model,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                timeout=timeout,
                account=account,
            )

            output_lines = [
                "# Cortex Response (Gemini Direct)\n",
                f"**Model**: {response.model}",
            ]

            if response.token_usage:
                usage = response.token_usage
                output_lines.append(
                    f"**Tokens**: {usage.get('prompt_tokens', 0)} → "
                    f"{usage.get('completion_tokens', 0)} "
                    f"(total: {usage.get('total_tokens', 0)})"
                )

            output_lines.extend(["", "## Response\n", response.text])

            log(f"Cortex response: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Cortex ask error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "ask_chat":
        message = arguments.get("message", "")
        model = arguments.get("model", "")
        history = arguments.get("history", [])
        tier_id = arguments.get("tier_id", "")
        account = arguments.get("account", "default")

        if not message:
            return [TextContent(type="text", text="Error: message is required")]

        try:
            svc = get_service()
            log(f"Chat: {message[:50]}... (model={model or 'default'}, account={account})")

            response = svc.chat(
                message=message,
                model=model,
                history=history,
                tier_id=tier_id,
                account=account,
            )

            output_lines = [
                "# Chat Response (generateChat)\n",
                f"**Model**: {response.model}",
                "",
                "## Response\n",
                response.text,
            ]

            log(f"Chat response: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Chat error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "start_chat":
        model = arguments.get("model", "")
        tier_id = arguments.get("tier_id", "")
        account = arguments.get("account", "default")
        try:
            if len(_conversations) >= _MAX_CONVERSATIONS:
                oldest_id = next(iter(_conversations))
                _conversations[oldest_id].close()
                del _conversations[oldest_id]
                log(f"Evicted conversation {oldest_id}")

            svc = get_service()
            conv = svc.start_chat(model=model, tier_id=tier_id, account=account)
            conv_id = str(uuid.uuid4())[:8]
            _conversations[conv_id] = conv
            log(f"Started conversation {conv_id} (model={model or 'default'}, total: {len(_conversations)})")
            return [TextContent(
                type="text",
                text=(
                    f"# Chat Started\n\n"
                    f"**Conversation ID**: `{conv_id}`\n"
                    f"Use `send_chat` with this ID to send messages.\n"
                    f"Use `close_chat` to end the conversation."
                ),
            )]
        except Exception as e:
            log(f"Start chat error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "send_chat":
        conv_id = arguments.get("conversation_id", "")
        message = arguments.get("message", "")

        if not conv_id or not message:
            return [TextContent(type="text", text="Error: conversation_id and message are required")]

        conv = _conversations.get(conv_id)
        if conv is None:
            return [TextContent(
                type="text",
                text=f"Error: conversation '{conv_id}' not found. Use start_chat first.",
            )]

        try:
            log(f"Send to {conv_id}: {message[:50]}... (turn {conv.turn_count + 1})")
            response = conv.send(message)

            output_lines = [
                "# Chat Response\n",
                f"**Conversation**: `{conv_id}` (turn {conv.turn_count})",
                f"**Model**: {response.model}",
                "",
                "## Response\n",
                response.text,
            ]

            log(f"Chat {conv_id} turn {conv.turn_count}: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Send chat error ({conv_id}): {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "close_chat":
        conv_id = arguments.get("conversation_id", "")

        if not conv_id:
            return [TextContent(type="text", text="Error: conversation_id is required")]

        conv = _conversations.pop(conv_id, None)
        if conv is None:
            return [TextContent(
                type="text",
                text=f"Error: conversation '{conv_id}' not found.",
            )]

        turns = conv.turn_count
        conv.close()
        log(f"Closed conversation {conv_id} ({turns} turns)")
        return [TextContent(
            type="text",
            text=f"Chat `{conv_id}` closed ({turns} turns completed).",
        )]

    elif name == "cortex_quota":
        try:
            account = arguments.get("account", "default")
            svc = get_service()
            quota_data = svc.quota(account=account)
            quota = quota_data.get("cortex", {})

            output_lines = ["# Gemini Quota\n"]
            output_lines.append("| Model | Remaining | Reset |")
            output_lines.append("|:------|----------:|:------|")
            for bucket in quota.get("buckets", []):
                model = bucket.get("modelId", "?")
                remaining = bucket.get("remainingFraction", 0)
                reset = bucket.get("resetTime", "?")[:16]
                output_lines.append(
                    f"| `{model}` | {remaining*100:.1f}% | {reset} |"
                )

            # Chat session info (F8)
            if _conversations:
                output_lines.append("")
                output_lines.append("## Active Chat Sessions")
                output_lines.append(f"**{len(_conversations)}/{_MAX_CONVERSATIONS}** sessions active")
                total_turns = 0
                for cid, conv in _conversations.items():
                    try:
                        turns = conv.turn_count  # type: ignore[union-attr]
                        total_turns += turns
                        output_lines.append(f"- `{cid[:8]}…`: {turns} turns")
                    except AttributeError:
                        output_lines.append(f"- `{cid[:8]}…`: (unknown)")
                output_lines.append(f"\n**Total turns**: {total_turns}")

            # Token health (F5)
            token_health = quota_data.get("token_health")
            if token_health and token_health.get("accounts"):
                output_lines.append("")
                output_lines.append("## Token Health")
                for acct_name, info in token_health["accounts"].items():
                    if info.get("cached"):
                        ttl = info.get("ttl_seconds", 0)
                        healthy = "✅" if info.get("healthy") else "⚠️"
                        output_lines.append(
                            f"- `{acct_name}`: {healthy} TTL={ttl}s"
                        )
                    else:
                        output_lines.append(
                            f"- `{acct_name}`: 🔘 not cached"
                        )

            log(f"Quota returned: {len(quota.get('buckets', []))} buckets")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Cortex quota error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "status":
        try:
            svc = get_service()
            svc_status = svc.status()

            output_lines = ["# Ochēma Status\n"]
            ls_info = svc_status.get("ls", {})
            if ls_info:
                output_lines.extend([
                    f"- **PID**: {ls_info.get('pid', 'N/A')}",
                    f"- **Port**: {ls_info.get('port', 'N/A')}",
                    f"- **Workspace**: {ls_info.get('workspace', 'N/A')}",
                    f"- **Name**: {ls_info.get('name', 'N/A')}",
                ])
            else:
                output_lines.append("- **LS**: unavailable")
            output_lines.append(f"- **Cortex**: {'✓' if svc_status.get('cortex_available') else '✗'}")

            log("Status returned")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Status error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "models":
        try:
            svc = get_service()
            ls_models = svc.ls_models()

            output_lines = ["# Available Models\n"]
            if ls_models:
                output_lines.append("| Model | Label | Remaining |")
                output_lines.append("|:------|:------|----------:|")
                for m in ls_models:
                    output_lines.append(
                        f"| `{m['name']}` | {m['label']} | {m['remaining']}% |"
                    )
            else:
                output_lines.append("*LS unavailable — LS models not shown*")

            log(f"Models listed: {len(ls_models)}")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Models error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "session_info":
        try:
            svc = get_service()
            ls_client = svc._get_ls_client()
            if not ls_client:
                return [TextContent(type="text", text="Error: Language Server is not available")]
            conv_id = arguments.get("conversation_id")

            # Fetch all trajectories
            all_data = ls_client._rpc(
                "exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories", {}
            )
            summaries = all_data.get("trajectorySummaries", {})

            if conv_id and conv_id in summaries:
                # Show specific session
                info = summaries[conv_id]
                step_count = info.get("stepCount", 0)
                status = info.get("status", "unknown")
                rot_level = (
                    "🔴 CRITICAL" if step_count > 50
                    else "🟡 WARNING" if step_count > 30
                    else "🟢 HEALTHY"
                )
                output_lines = [
                    "# Session Info\n",
                    f"- **ID**: `{conv_id[:16]}...`",
                    f"- **Summary**: {info.get('summary', 'N/A')}",
                    f"- **Steps**: {step_count}",
                    f"- **Status**: {status}",
                    f"- **Context Rot**: {rot_level}",
                ]
            else:
                # Show overview of all sessions sorted by step count
                sessions = []
                for cid, info in summaries.items():
                    sessions.append({
                        "id": cid[:12],
                        "summary": info.get("summary", "")[:40],
                        "steps": info.get("stepCount", 0),
                        "status": info.get("status", "unknown"),
                    })
                sessions.sort(key=lambda x: x["steps"], reverse=True)

                output_lines = [
                    f"# Session Overview ({len(sessions)} total)\n",
                    "| ID | Summary | Steps | Rot Risk |",
                    "|:---|:--------|------:|:--------|",
                ]
                for s in sessions[:15]:
                    rot = (
                        "🔴" if s["steps"] > 50
                        else "🟡" if s["steps"] > 30
                        else "🟢"
                    )
                    output_lines.append(
                        f"| `{s['id']}` | {s['summary']} | {s['steps']} | {rot} |"
                    )

            log(f"Session info returned: {len(summaries)} sessions")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Session info error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "ask_with_tools":
        message = arguments.get("message", "")
        model = arguments.get("model", "gemini-3-pro-preview")
        system_instruction = arguments.get("system_instruction")
        thinking_budget = arguments.get("thinking_budget", 32768)
        max_iterations = int(arguments.get("max_iterations", 10))
        max_tokens = int(arguments.get("max_tokens", 8192))
        timeout = float(arguments.get("timeout", 120))
        account = arguments.get("account", "default")

        if not message:
            return [TextContent(type="text", text="Error: message is required")]

        try:
            svc = get_service()
            log(f"Tool use: model={model} account={account}: {message[:50]}...")

            # Convert thinking_budget to int if provided
            tb = int(thinking_budget) if thinking_budget is not None else None

            response = svc.ask_with_tools(
                message=message,
                model=model,
                system_instruction=system_instruction,
                max_iterations=max_iterations,
                max_tokens=max_tokens,
                thinking_budget=tb,
                timeout=timeout,
                account=account,
            )

            output_lines = [
                "# Tool Use Response (AI + Local Tools)\n",
                f"**Model**: {response.model}",
            ]

            if response.token_usage:
                usage = response.token_usage
                output_lines.append(
                    f"**Tokens**: {usage.get('prompt_tokens', 0)} → "
                    f"{usage.get('completion_tokens', 0)} "
                    f"(total: {usage.get('total_tokens', 0)})"
                )

            output_lines.extend(["", "## Response\n", response.text])

            if response.thinking:
                output_lines.extend(["", "## Thinking\n", response.thinking[:1000]])

            log(f"Tool use response: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            detail = str(e)
            if hasattr(e, "response_body") and e.response_body:
                detail += f"\n\nAPI Response:\n{e.response_body[:1000]}"
            log(f"Tool use error: {detail}")
            return [TextContent(type="text", text=f"Error: {detail}")]

    # ============ Jules tools ============
    elif name in ("jules_create_task", "jules_get_status", "jules_batch_execute", "jules_list_repos"):
        return await _handle_jules(name, arguments)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ============ Jules Handler (from jules_mcp_server.py) ============

async def _handle_jules(name: str, arguments: dict) -> list[TextContent]:
    """Handle Jules tool calls."""
    try:
        from mekhane.symploke.jules_client import JulesClient, SessionState
    except ImportError as e:
        return [TextContent(type="text", text=f"Error: Jules client not available: {e}")]

    api_key, key_index = _jules_get_key()
    if not api_key:
        return [TextContent(type="text", text="Error: No JULES_API_KEY_XX environment variables set")]

    try:
        client = JulesClient(api_key)
    except Exception as e:
        return [TextContent(type="text", text=f"Error initializing Jules client: {e}")]

    if name == "jules_create_task":
        prompt = arguments.get("prompt", "")
        repo = arguments.get("repo", "")
        branch = arguments.get("branch", "main")
        if not prompt or not repo:
            return [TextContent(type="text", text="Error: prompt and repo are required")]
        try:
            source = f"sources/github/{repo}"
            session = await client.create_session(prompt, source, branch)
            _jules_record(key_index, session.id)
            output = (
                f"# Jules Task Created\n\n"
                f"- **Session ID**: `{session.id}`\n"
                f"- **State**: {session.state.value}\n"
                f"- **Repository**: {repo}\n"
                f"- **Branch**: {branch}\n"
                f"- **Account**: Key #{key_index} (auto-balanced)\n\n"
                f"Use `jules_get_status` with session_id to check progress."
            )
            log(f"Jules: created session {session.id}")
            return [TextContent(type="text", text=output)]
        except Exception as e:
            log(f"Jules create error: {e}")
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "jules_get_status":
        session_id = arguments.get("session_id", "")
        if not session_id:
            return [TextContent(type="text", text="Error: session_id is required")]
        try:
            session = await client.get_session(session_id)
            emoji = {"planning": "📝", "implementing": "🔨", "testing": "🧪", "completed": "✅", "failed": "❌"}
            output = (
                f"# Jules Session Status\n\n"
                f"- **Session ID**: `{session.id}`\n"
                f"- **State**: {emoji.get(session.state.value, '❓')} {session.state.value}\n"
            )
            if session.pull_request_url:
                output += f"- **Pull Request**: {session.pull_request_url}\n"
            if session.error:
                output += f"- **Error**: {session.error}\n"
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "jules_batch_execute":
        tasks = arguments.get("tasks", [])
        max_concurrent = min(arguments.get("max_concurrent", 30), 60)
        if not tasks:
            return [TextContent(type="text", text="Error: tasks list is required")]
        try:
            formatted = [
                {"prompt": t["prompt"], "source": f"sources/github/{t['repo']}", "branch": t.get("branch", "main")}
                for t in tasks
            ]
            log(f"Jules batch: {len(tasks)} tasks, max_concurrent={max_concurrent}")
            results = await client.batch_execute(formatted, max_concurrent)
            lines = [f"# Jules Batch Results\n", f"**Total**: {len(results)} tasks\n"]
            completed = sum(1 for r in results if r.state == SessionState.COMPLETED)
            failed = sum(1 for r in results if r.state == SessionState.FAILED)
            lines.extend([f"- ✅ Completed: {completed}", f"- ❌ Failed: {failed}\n"])
            for i, r in enumerate(results, 1):
                emoji = "✅" if r.state == SessionState.COMPLETED else "❌"
                lines.append(f"## [{i}] {emoji} {r.prompt[:50]}...")
                if r.pull_request_url:
                    lines.append(f"- PR: {r.pull_request_url}")
                if r.error:
                    lines.append(f"- Error: {r.error}")
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "jules_list_repos":
        return [TextContent(type="text", text=(
            "# Jules Repositories\n\n"
            "Repository listing not yet implemented.\n"
            "Use repository format: `owner/repo` (e.g., `laihuip001/hegemonikon`)"
        ))]

    return [TextContent(type="text", text=f"Unknown Jules tool: {name}")]



if __name__ == "__main__":
    from mekhane.mcp.mcp_guard import guard
    guard("ochema")
    _base.run()
