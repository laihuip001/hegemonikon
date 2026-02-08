# PROOF: [L2/ユーティリティ] <- mekhane/fep/
"""
PROOF: [L2/ユーティリティ] このファイルは存在しなければならない

A0 → L1 (Modality PW) と L2 (Theorem PW) を接続する自然変換が必要
   → fep_agent の precision_weights → cone_builder の pw へのブリッジ
   → pw_adapter.py が担う

Q.E.D.

---

PW Adapter — L1 (Modality Precision) ↔ L2 (Theorem Precision) Bridge

FEP の Precision Weighting は2層構造:
  L1: Modality PW (fep_agent.py) — 観測チャネルの信頼度 [0, 1]
      {"context": 0.8, "urgency": 0.3, "confidence": 1.0}
  L2: Theorem PW (cone_builder.py) — 定理の実行時重み [-1, +1]
      {"S1": 0.5, "S2": 0.0, "S3": -0.3, "S4": 0.0}

このモジュールは3つの戦略で L2 PW を決定する:
  1. parse_pw_spec()   — 明示指定 "/s{pw: S1+, S3-}" をパース
  2. infer_pw()        — 暗黙推定 (WF 文書の条件テーブルを実装)
  3. derive_pw()       — FEP agent 由来 (modality → theorem マッピング)

Usage:
    from mekhane.fep.pw_adapter import resolve_pw

    # Strategy 1: Explicit
    pw = resolve_pw("S", pw_spec="S1+, S3-")

    # Strategy 2: Context-inferred
    pw = resolve_pw("S", context="新規設計 フロントエンド アーキテクチャ")

    # Strategy 3: Agent-derived
    pw = resolve_pw("S", agent=fep_agent)

    # Priority: explicit > context > agent > default (all zeros)
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from mekhane.fep.fep_agent import HegemonikónFEPAgent


# =============================================================================
# Series theorem IDs
# =============================================================================

SERIES_THEOREMS: Dict[str, List[str]] = {
    "O": ["O1", "O2", "O3", "O4"],
    "S": ["S1", "S2", "S3", "S4"],
    "H": ["H1", "H2", "H3", "H4"],
    "P": ["P1", "P2", "P3", "P4"],
    "K": ["K1", "K2", "K3", "K4"],
    "A": ["A1", "A2", "A3", "A4"],
}


# =============================================================================
# Strategy 1: Explicit PW spec parsing
# =============================================================================


def parse_pw_spec(spec: str, series: str) -> Dict[str, float]:
    """Parse explicit PW specification string.

    Formats:
        "S1+, S3-"       → {"S1": 0.5, "S3": -0.5}
        "S1++, S3--"     → {"S1": 1.0, "S3": -1.0}
        "S1=0.3, S3=-0.7" → {"S1": 0.3, "S3": -0.7}
        "S2"             → {"S2": 0.5}  (bare = positive default)

    Returns:
        Dict[str, float]: PW weights for specified theorems.
        Unspecified theorems default to 0.0.
    """
    theorems = SERIES_THEOREMS.get(series.upper(), [])
    if not theorems:
        return {}

    pw: Dict[str, float] = {t: 0.0 for t in theorems}

    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue

        # Try "T1=0.5" format
        eq_match = re.match(r"([A-Z]\d)=(-?[\d.]+)", part)
        if eq_match:
            tid, val = eq_match.group(1), float(eq_match.group(2))
            if tid in pw:
                pw[tid] = max(-1.0, min(1.0, val))
            continue

        # Try "T1++" / "T1--" / "T1+" / "T1-" / "T1" format
        sign_match = re.match(r"([A-Z]\d)(\+{1,2}|-{1,2})?$", part)
        if sign_match:
            tid = sign_match.group(1)
            signs = sign_match.group(2) or "+"
            if tid in pw:
                if signs == "++":
                    pw[tid] = 1.0
                elif signs == "+":
                    pw[tid] = 0.5
                elif signs == "--":
                    pw[tid] = -1.0
                elif signs == "-":
                    pw[tid] = -0.5

    return pw


# =============================================================================
# Strategy 2: Context-based inference
# =============================================================================

# Inference rules extracted from each Peras WF's C0 暗黙推定 table.
# Format: (keywords, result_pw_dict)
# First match wins.

_INFERENCE_RULES: Dict[str, List[Tuple[List[str], Dict[str, float]]]] = {
    # o.md L116-124
    "O": [
        # "直前が /noe" → O1+
        (["noesis", "noe", "直前", "認識", "直観"], {"O1": 0.5}),
        # V[] > 0.5 → O3+ (不確実性高 → 探求強化)
        (["不確実", "曖昧", "探求", "zētēsis"], {"O3": 0.5}),
        # バイアス警告 → バイアス元を抑制 (default: O1-)
        (["バイアス", "bias", "偏り"], {"O1": -0.5}),
    ],
    # s.md L342-349
    "S": [
        (["新規", "設計", "新機能", "アーキテクチャ", "design"], {"S2": 0.5}),
        (["リファクタ", "refactor", "整理", "改善"], {"S1": 0.5, "S3": 0.5}),
        (["実装", "コーディング", "implement", "開発"], {"S4": 0.5}),
    ],
    # h.md L144-151
    "H": [
        (["バイアス", "bias", "偏り"], {"H1": -0.5}),
        (["感情", "emotion", "気持ち", "怒り", "喜び"], {"H1": 0.5}),
        (["知識", "確定", "knowledge", "記録"], {"H4": 0.5}),
    ],
    # p.md L143-150
    "P": [
        (["スコープ", "scope", "範囲", "領域"], {"P1": 0.5}),
        (["技術", "技法", "tool", "ツール"], {"P4": 0.5}),
        (["経路", "道", "path", "route"], {"P2": 0.5}),
    ],
    # k.md L124-131
    "K": [
        (["緊急", "urgent", "今すぐ", "急"], {"K1": 0.5, "K2": 0.5}),
        (["戦略", "strategy", "長期", "計画"], {"K3": 0.5, "K4": 0.5}),
        (["優先", "priority", "pri"], {"K1": 0.5, "K3": 0.5}),
    ],
    # a.md L121-128
    "A": [
        (["感情", "emotion", "主観"], {"A1": -0.5, "A2": 0.5}),
        (["知識", "確定", "KI", "エビデンス"], {"A4": 0.5}),
        (["洞察", "原則", "格言", "教訓"], {"A3": 0.5}),
    ],
}


def infer_pw(series: str, context: str) -> Dict[str, float]:
    """Infer PW from context using series-specific keyword rules.

    Scans context text for keywords defined in the WF 暗黙推定 tables.
    First matching rule wins.

    Args:
        series: Series identifier (O/S/H/P/K/A)
        context: Natural language context string

    Returns:
        Dict[str, float]: Inferred PW weights.
        All zeros if no rules match (uniform weighting).
    """
    theorems = SERIES_THEOREMS.get(series.upper(), [])
    if not theorems:
        return {}

    default_pw = {t: 0.0 for t in theorems}
    rules = _INFERENCE_RULES.get(series.upper(), [])

    context_lower = context.lower()

    for keywords, pw_delta in rules:
        if any(kw.lower() in context_lower for kw in keywords):
            result = default_pw.copy()
            result.update(pw_delta)
            return result

    return default_pw


# =============================================================================
# Strategy 3: Agent-derived PW
# =============================================================================

# Mapping from modality precision → theorem functional role.
# Each theorem in each series has a "functional character":
#   - cognitive (context-sensitive): clarity of information
#   - action (urgency-sensitive): need for immediate response
#   - judgment (confidence-sensitive): certainty of assessment
#
# This is a fixed mapping (Phase 1: bootstrapping).
# Phase 2 will learn from BasinLogger data.

_MODALITY_MAPPING: Dict[str, Dict[str, str]] = {
    # O-series: Ousia (pure cognition)
    "O": {
        "O1": "context",     # Noēsis: recognition depends on context clarity
        "O2": "confidence",  # Boulēsis: will depends on confidence
        "O3": "context",     # Zētēsis: inquiry depends on context
        "O4": "urgency",     # Energeia: action depends on urgency
    },
    # S-series: Schema (strategic design)
    "S": {
        "S1": "context",     # Metron: scale depends on context clarity
        "S2": "context",     # Mekhanē: method depends on understanding
        "S3": "confidence",  # Stathmos: criteria need confident assessment
        "S4": "urgency",     # Praxis: implementation responds to urgency
    },
    # H-series: Hormē (motivation)
    "H": {
        "H1": "urgency",     # Propatheia: initial reaction is urgency-driven
        "H2": "confidence",  # Pistis: trust depends on confidence
        "H3": "urgency",     # Orexis: desire has urgency component
        "H4": "context",     # Doxa: belief formation needs clear context
    },
    # P-series: Perigraphē (environment)
    "P": {
        "P1": "context",     # Khōra: space/scope depends on context
        "P2": "urgency",     # Hodos: path urgency (time pressure)
        "P3": "confidence",  # Trokhia: trajectory needs confident assessment
        "P4": "context",     # Tekhnē: technique selection needs information
    },
    # K-series: Kairos (context/timing)
    "K": {
        "K1": "urgency",     # Eukairia: opportunity is urgency-sensitive
        "K2": "urgency",     # Chronos: time allocation
        "K3": "confidence",  # Telos: purpose needs confident assessment
        "K4": "context",     # Sophia: wisdom depends on information quality
    },
    # A-series: Akribeia (accuracy)
    "A": {
        "A1": "urgency",     # Pathos: emotional precision under pressure
        "A2": "confidence",  # Krisis: judgment depends on confidence
        "A3": "context",     # Gnōmē: insight needs clear context
        "A4": "confidence",  # Epistēmē: knowledge requires high confidence
    },
}


def derive_pw(
    series: str,
    agent: "HegemonikónFEPAgent",
) -> Dict[str, float]:
    """Derive L2 theorem PW from L1 modality precision weights.

    Natural transformation η: F(modality) ⇒ G(theorem)

    The mapping converts modality precision [0, 1] to theorem weight [-1, +1]:
        pw_theorem = (precision_modality - 0.5) * 2

    This means:
        precision = 1.0 → pw = +1.0 (fully emphasize)
        precision = 0.5 → pw =  0.0 (neutral)
        precision = 0.0 → pw = -1.0 (fully suppress)

    Args:
        series: Series identifier (O/S/H/P/K/A)
        agent: HegemonikónFEPAgent with current precision_weights

    Returns:
        Dict[str, float]: Derived PW weights from agent state.
    """
    theorems = SERIES_THEOREMS.get(series.upper(), [])
    if not theorems:
        return {}

    mapping = _MODALITY_MAPPING.get(series.upper(), {})
    if not mapping:
        return {t: 0.0 for t in theorems}

    precision = agent.precision_weights  # {"context": x, "urgency": y, "confidence": z}

    pw: Dict[str, float] = {}
    for tid in theorems:
        modality = mapping.get(tid, "context")
        p = precision.get(modality, 0.5)
        # Transform [0, 1] → [-1, +1]
        pw[tid] = max(-1.0, min(1.0, (p - 0.5) * 2.0))

    return pw


# =============================================================================
# Main: resolve_pw() — priority cascade
# =============================================================================


def resolve_pw(
    series: str,
    pw_spec: Optional[str] = None,
    context: Optional[str] = None,
    agent: Optional["HegemonikónFEPAgent"] = None,
) -> Dict[str, float]:
    """Resolve Precision Weighting with priority cascade.

    Priority: explicit pw_spec > context inference > agent derivation > default

    Args:
        series: Series identifier (O/S/H/P/K/A)
        pw_spec: Explicit PW spec string (e.g., "S1+, S3-")
        context: Natural language context for inference
        agent: HegemonikónFEPAgent for derivation

    Returns:
        Dict[str, float]: Resolved PW weights for all theorems.
        All zeros if no strategy produces non-zero weights.
    """
    theorems = SERIES_THEOREMS.get(series.upper(), [])
    if not theorems:
        return {}

    # Strategy 1: Explicit
    if pw_spec:
        pw = parse_pw_spec(pw_spec, series)
        if any(v != 0.0 for v in pw.values()):
            return pw

    # Strategy 2: Context-inferred
    if context:
        pw = infer_pw(series, context)
        if any(v != 0.0 for v in pw.values()):
            return pw

    # Strategy 3: Agent-derived
    if agent is not None:
        pw = derive_pw(series, agent)
        if any(v != 0.0 for v in pw.values()):
            return pw

    # Default: uniform (all zeros)
    return {t: 0.0 for t in theorems}


# =============================================================================
# Display utility
# =============================================================================


def describe_pw(pw: Dict[str, float]) -> str:
    """Format PW weights for human display.

    Returns:
        str: e.g. "S1=+0.5 S2=0.0 S3=-0.3 S4=0.0"
    """
    parts = []
    for tid, val in sorted(pw.items()):
        sign = "+" if val > 0 else ""
        parts.append(f"{tid}={sign}{val:.1f}")
    return " ".join(parts)


def is_uniform(pw: Dict[str, float]) -> bool:
    """Check if PW is uniform (all zeros)."""
    return all(abs(v) < 1e-6 for v in pw.values())
