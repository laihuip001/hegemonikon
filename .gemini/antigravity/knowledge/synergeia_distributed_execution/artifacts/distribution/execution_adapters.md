# Synergeia Execution Adapters

## Overview

To enable distributed CCL execution on restricted environments (like GCP virtual machines), Synergeia utilizes specialized adapter scripts that wrap CLI tools and APIs.

## 1. Claude Code Adapter (`claude-code`)

- **Purpose**: Leverages Claude's high-fidelity coding capabilities.
- **Pattern**: Non-interactive command execution using the `-p` (or `--prompt`) flag.
- **Implementation (coordinator.py)**:

```python
def execute_claude(ccl: str, context: str) -> Dict[str, Any]:
    import subprocess
    prompt = f"{context}\n\nExecute CCL: {ccl}\n\nProvide a detailed response."
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=600,
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        answer = result.stdout.strip()
        # handle error...
    except Exception as e:
        return {"status": "error", "error": str(e), "ccl": ccl}
    return {"status": "success", "ccl": ccl, "thread": "claude", "answer": answer}
```

- **Verification**:
  - Local installation via `npm install @anthropic-ai/claude-code`.
  - Command: `claude -p "Prompt"`

## 2. Gemini CLI Adapter (JS Bundle)

- **Purpose**: High-context processing and environment-native tool access.
- **Pattern**: Non-interactive command execution using the `-p` (or `--prompt`) flag.
- **Implementation (coordinator.py)**:

```python
def execute_gemini(ccl: str, context: str) -> Dict[str, Any]:
    """Gemini CLI でCCLを実行。"""
    import subprocess
    
    # ツール操作を避けるプロンプト
    prompt = f"""You are a Hegemonikon CCL interpreter.
Do NOT use any file system tools. Just analyze and respond in text.

{context}

Analyze and explain the CCL command: {ccl}

Provide a detailed conceptual response without executing any tools."""
    
    try:
        result = subprocess.run(
            [
                "node", 
                "/path/to/gemini.js", 
                "-p", prompt
                # Note: --approval-mode plan is experimental and avoided for stability.
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 最大10分
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        # 応答のパース処理...
```

- **Avoid Tool Use (Prompt Guidance)**: When running non-interactively in a coordinator, explicit negative prompting ("Do NOT use any file system tools") is used to prevent Gemini from attempting tool calls (like `list_directory`) that require user confirmation or fail in restricted shells.

- **Benefit**: More robust than the Python script in environments where CLI features (like MCP) might be needed.

## 3. Codex CLI Adapter (`codex-cli`)

- **Purpose**: Code generation and logic expansion.
- **Pattern**: Non-interactive command execution via `exec` subcommand.
- **Implementation (coordinator.py)**:

```python
def execute_codex(ccl: str, context: str) -> Dict[str, Any]:
    """OpenAI Codex CLI でCCLを実行。"""
    import subprocess
    
    prompt = f"{context}\n\nExecute CCL: {ccl}\n\nProvide a detailed response."
    
    try:
        result = subprocess.run(
            [CODEX_CLI, "exec", prompt],
            capture_output=True,
            text=True,
            timeout=600,  # 最大10分
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        # Codex は最初と最後にメタデータがあるので整理
        lines = result.stdout.strip().split("\n")
        # メタデータ行を除去して純粋な回答を抽出
        answer = "\n".join([l for l in lines if 
            not l.startswith("OpenAI Codex") and 
            not l.startswith("---") and 
            not l.startswith("workdir:") and 
            not l.startswith("model:") and 
            not l.startswith("provider:") and 
            not l.startswith("approval:") and 
            not l.startswith("sandbox:") and 
            not l.startswith("reasoning") and 
            not l.startswith("session id:") and 
            not l.startswith("user") and 
            not l.startswith("mcp startup:") and 
            not l.startswith("codex") and 
            not l.startswith("tokens used")
        ])
        if result.returncode != 0:
            return {"status": "error", "error": result.stderr, "ccl": ccl}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout (600s)", "ccl": ccl}
    except Exception as e:
        return {"status": "error", "error": str(e), "ccl": ccl}
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "codex",
        "answer": answer.strip(),
    }
```

- **Verification**:
  - Local installation via `npm install @openai/codex` (recommended to avoid `EACCES` on global install).
  - Version check: `npx codex --version` (v0.93.0).

- **Troubleshooting & Authentication**:
  - **EACCES Error**: Global installation (`npm i -g`) may fail in restricted environments. Use local installation in the project directory.
  - **Login (Device Auth)**:
    1. Run `npx codex login --device-auth`.
    2. Open `https://auth.openai.com/codex/device` in a browser.
    3. Enter the provided code (e.g., `RDPJ-5KBFH`).
  - **Status**: ✅ Logged in using ChatGPT.
  - **Note on Output**: The CLI outputs a header (workdir, model, tokens used) before and after the actual content. Parsers should account for this.
  - **API Key**: Alternatively, use `export OPENAI_API_KEY="your-key"`.

## 4. Gemini API Adapter (`gemini_api.py`)

- **Purpose**: High-context processing and Google Ecosystem integration.
- **Optimization**: Uses `Futures` in the main Coordinator for parallel delegation.
- **Structured Output Support (v0.8.7)**: Supports the `response_schema` parameter for Grammar-Constrained Decoding. This allows the system to enforce JSON schemas on LLM outputs using Gemini's native structured output capabilities, ensuring high compliance with CCL execution traces and SEL requirements.
- **Timeout Monitoring**: Configured with a default 600s timeout for complex reasoning tasks.

## 5. Perplexity API Adapter (`perplexity_api.py`)

- **Purpose**: Deep web research and citation management.
- **Status**: Stable. Primary research thread for `/sop` and `/zet` operations.
- **Timeout Optimization**:
  - **Python (httpx)**: Use `timeout = httpx.Timeout(300.0, read=180.0, connect=30.0)` for long research tasks.
  - **Node.js (OpenAI compatible)**: Set `timeout: 300000` (5 minutes) in the client constructor.
  - **curl**: Use `--max-time 600` flags.
  - **MCP (Claude Code)**: Set environment variable `export MCP_TIMEOUT=300000`.
- **System Constraints**:
  - **BASH_MAX_TIMEOUT_MS**: Typically limited to 600,000ms (10 minutes). Longer tasks should be split.
  - **MCP_TIMEOUT**: Defaults to 60s. For heavy tool use, increasing this to 120-180s is recommended but may hit hardcoded limits in some environments.

## 6. Claude API Adapter (`claude_api.py`)

- **Purpose**: High-fidelity reasoning and structured output enforcement.
- **Features**:
  - **Structured Output (output_config.format)**: Utilizes native JSON Schema enforcement (GA 2026-01-12) to ensure responses match Pydantic models.
  - **Strict Tool Use**: Supports `strict: true` for deterministic tool calls.
- **Implementation (claude_api.py)**:

```python
def query(
    prompt: str,
    response_schema: Optional[Type[BaseModel]] = None,
    system: str = None,
) -> dict:
    # ...
    if response_schema:
        schema = response_schema.model_json_schema()
        request_params["output_config"] = {
            "format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.__name__,
                    "schema": schema,
                    "strict": True,
                }
            }
        }
    # ...
```

- **Usage**: Primary adapter for the /vet v3.0 SEL compliance layer (L5), providing a separate model family for cross-validation.

## 7. Ollama Adapter (`ollama_api.py`) ⚡NEW

- **Purpose**: Infinite, low-cost local LLM execution on consumer hardware (e.g., RTX 2070 Super).
- **Primary Model**: Qwen 2.5 7B (optimal quality/speed ratio for 8GB VRAM).
- **Implementation Pattern**:

```python
class OllamaAdapter:
    """ローカル LLM (Ollama) アダプター"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen2.5:7b"
    
    async def query(self, prompt: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {"num_ctx": 4096, "temperature": 0.0}
                },
                timeout=120,
            )
            answer = response.json()["response"]
            return {"status": "success", "thread": "local_llm", "answer": answer}
```

- **Usage**: Enables the "Continuous Worker" thread in Synergeia, allowing long-running background tasks (via OpenManus) without API costs.
- **Hardware Profile**: Optimized for Windows + WSL2 + NVIDIA GPU environments.

---
*Updated: 2026-02-01 | Synergeia Operational Tech v0.8 | Local LLM Integration Added*
