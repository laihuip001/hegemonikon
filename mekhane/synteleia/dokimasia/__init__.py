# PROOF: [L2/インフラ] Dokimasia 審査層パッケージ
"""
Dokimasia (δοκιμασία) — 審査層

「範囲・時期・精度」を問う5エージェント:
- PerigrapheAgent: 境界画定 (P)
- KairosAgent: 時宜判断 (K)
- OperatorAgent: 記号/演算子 (A)
- LogicAgent: 論理矛盾 (A)
- CompletenessAgent: 欠落要素 (A)
"""

from .perigraphe_agent import PerigrapheAgent
from .kairos_agent import KairosAgent
from .operator_agent import OperatorAgent
from .logic_agent import LogicAgent
from .completeness_agent import CompletenessAgent

__all__ = [
    "PerigrapheAgent",
    "KairosAgent",
    "OperatorAgent",
    "LogicAgent",
    "CompletenessAgent",
]
