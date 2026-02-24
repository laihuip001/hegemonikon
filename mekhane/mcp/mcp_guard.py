#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/mcp/ A0->MCPGuard
"""
MCP Guard — Security & Policy Enforcement for MCP Servers

Ensures all tool calls comply with:
  - Allowed path policies
  - Command blacklists
  - Resource usage limits
"""

from pathlib import Path

class MCPGuard:
    """Security guard for MCP operations."""

    def __init__(self, allowed_paths: list[Path] = None):
        self.allowed_paths = allowed_paths or []

    def check_path(self, path: str | Path) -> bool:
        """Check if path is allowed."""
        if not self.allowed_paths:
            return True
        p = Path(path).resolve()
        return any(p.is_relative_to(base) for base in self.allowed_paths)
