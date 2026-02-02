# PROOF: [L2/インフラ] <- mekhane/synteleia/poiesis/ Poiēsis 生成層パッケージ
"""
Poiēsis (ποίησις) — 生成層

「何を・どう・なぜ」を問う3エージェント:
- OusiaAgent: 本質洞察 (O)
- SchemaAgent: 構造設計 (S)
- HormeAgent: 動機評価 (H)
"""

from .ousia_agent import OusiaAgent
from .schema_agent import SchemaAgent
from .horme_agent import HormeAgent

__all__ = ["OusiaAgent", "SchemaAgent", "HormeAgent"]
