# PROOF: [L2/インフラ] <- synergeia/ Synergeia v2 — n8n Distributed CCL Executor
"""
Synergeia v2 — マルチエージェント協調実行

n8n WF + MCP bridge による分散 CCL 実行。
v0.1 のコードは _archive_v01/ に保存。
"""

from synergeia.bridge import dispatch, dispatch_compile_only, health_check, SynergeiaResult

__all__ = ["dispatch", "dispatch_compile_only", "health_check", "SynergeiaResult"]
__version__ = "2.0.0"
