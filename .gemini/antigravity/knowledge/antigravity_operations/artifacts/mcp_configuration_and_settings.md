# Antigravity MCP Configuration & Settings

## 1. Overview

Hegemonikón leverages the Model Context Protocol (MCP) to extend the capabilities of the Antigravity IDE. These settings are managed at the IDE level, allowing agents to access specialized tools (e.g., Sequential Thinking, Redis) through a standardized interface.

### 2.1 Extension Level (Roo-Cline)

Location: `/home/makaron8426/.config/Antigravity/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`
*Used by:* The Roo-Cline / Cline extension agents.

### 2.2 IDE Level (Antigravity Internal Agent)

Location: `/home/makaron8426/oikos/.gemini/antigravity/mcp_config.json`
*Used by:* The core Antigravity Gemini agent (the primary system assistant).

## 3. Active Server Configuration (2026-01-29)

### 3.1 Sequential Thinking

The Sequential Thinking MCP server provides a structured, multi-step reasoning process.

**Configuration Example:**

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "disabled": false,
      "alwaysAllow": ["sequentialthinking"]
    }
  }
}
```

> **CRITICAL RULE**: For most environments (especially Cline-based), the `alwaysAllow` array MUST contain the tool name for the LLM to "see" and use the tool. If left as an empty array `[]`, the server may connect but the agent will not recognize the available tools.

### 3.2 Redis MCP (Blocked)

The Redis MCP server is intended for high-speed state management in the `anamnesis/` layer.

**Status:** Blocked (Requires local Redis server installation).

### 3.3 Hermēneus (CCL Compiler)

The Hermēneus MCP server allows the AI to autonomously execute and verify CCL workflows.

**Configuration Example:**

```json
{
  "mcpServers": {
    "hermeneus": {
      "command": "python",
      "args": ["-m", "hermeneus.src.mcp_server"],
      "cwd": "/home/makaron8426/oikos/hegemonikon",
      "env": {
        "PYTHONPATH": "/home/makaron8426/oikos/hegemonikon"
      }
    }
  }
}
```

> **Note**: This server utilizes the global `PYTHONPATH` to resolve the `hermeneus` package.

## 4. Visibility Constraints & Limits

### 4.1 The 50-Tool Limit

Antigravity IDE has a recommended limit of **50 tools** (approx.) for the LLM context. If the total number of tools across all active MCP servers exceeds this limit, some tools (often the most recently added) may be excluded from the agent's context window, making them "invisible" to the LLM despite the server being connected.

**Strategy for High Tool Count:**

- Disable unused MCP servers.
- Use an MCP Router (like Rube) to dynamically load tools.
- Prioritize core tools (`gnosis`, `prompt-lang`, etc.).

### 4.2 alwaysAllow vs. Automatic Discovery

- **Cline/Roo-Cline**: Requires tool names to be explicitly listed in the `alwaysAllow` array to be visible.
- **Antigravity Internal Agent**: Automatically discovers and exposes tools listed in `mcp_config.json`, provided the 50-tool limit is not exceed. `alwaysAllow` is not strictly required for the IDE-level agent.

## 4. Verification Protocol

To verify that an MCP server is correctly integrated:

1. Run `npx -y [package-name] --help` to check package availability.
2. Observe the logs or command output for `MCP Server running on stdio`.
3. Check the IDE's MCP settings panel to ensure the server status is "Connected" or has 1/1 tools available.

---
*Last Updated: 2026-01-29*
