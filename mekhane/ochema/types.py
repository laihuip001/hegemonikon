# PROOF: [L2/インフラ] <- mekhane/ochema/ 共有型定義
# PURPOSE: Ochēma モジュール間で共有される型定義。循環依存を防ぐための独立モジュール。
"""Ochēma shared types — LLMResponse and constants.

This module exists to break the circular dependency between
antigravity_client.py and cortex_client.py. Both modules
import LLMResponse from here instead of from each other.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# PURPOSE: LLM からの応答を保持する。
@dataclass
class LLMResponse:
    """LLM からの応答を保持する。"""
    text: str = ""
    thinking: str = ""
    model: str = ""
    token_usage: dict = field(default_factory=dict)
    cascade_id: str = ""
    trajectory_id: str = ""
    raw_steps: list = field(default_factory=list)
    step_count: int = 0  # total steps seen (for multi-turn offset)
