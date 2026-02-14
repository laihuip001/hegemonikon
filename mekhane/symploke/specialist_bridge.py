#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→統合が必要→specialist_bridge が担う
"""
Specialist Bridge — Phase 0-3 (866人) と v2 (140人) の統合アダプタ

SpecialistDefinition (specialist_prompts.py) → Specialist (specialist_v2.py) 変換。
これにより run_specialists.py から全 ~1000 人の専門家を利用可能にする。
"""

import sys
from pathlib import Path

# ローカルモジュールインポート
try:
    from specialist_v2 import Specialist, Archetype, VerdictFormat, Severity
    from specialist_prompts import (
        SpecialistDefinition,
        Archetype as PromptArchetype,
        get_all_specialists as get_phase_specialists,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from specialist_v2 import Specialist, Archetype, VerdictFormat, Severity
    from specialist_prompts import (
        SpecialistDefinition,
        Archetype as PromptArchetype,
        get_all_specialists as get_phase_specialists,
    )


# PURPOSE: Archetype enum のマッピング (同値だが異なるクラス)
_ARCHETYPE_MAP = {
    "precision": Archetype.PRECISION,
    "speed": Archetype.SPEED,
    "autonomy": Archetype.AUTONOMY,
    "creative": Archetype.CREATIVE,
    "safety": Archetype.SAFETY,
}


# PURPOSE: SpecialistDefinition → Specialist 変換
def adapt(defn: SpecialistDefinition) -> Specialist:
    """SpecialistDefinition (Phase 0-3) を Specialist (v2) に変換する

    SpecialistDefinition (簡易版):
      id, name, category, archetype, focus, quality_standards, edge_cases, fallback

    Specialist (詳細版):
      id, name, category, archetype, domain, principle,
      perceives, blind_to, measure, verdict, severity_map
    """
    archetype = _ARCHETYPE_MAP.get(
        defn.archetype.value, Archetype.PRECISION
    )

    return Specialist(
        id=defn.id,
        name=defn.name,
        category=defn.category,
        archetype=archetype,
        domain=defn.focus,
        principle=defn.focus,  # focus を principle として流用
        perceives=defn.quality_standards if defn.quality_standards else [defn.focus],
        blind_to=[],
        measure=f"{defn.focus}が適切であること",
        verdict=VerdictFormat.REVIEW,
        severity_map={},
    )


# PURPOSE: Phase 0-3 の全専門家を v2 形式で取得
def get_all_phase_specialists_v2() -> list[Specialist]:
    """Phase 0-3 の全専門家を Specialist (v2) 形式に変換して返す"""
    try:
        phase_specs = get_phase_specialists()
    except ImportError:
        # 相対インポートの問題を回避するためフォールバック
        try:
            from specialist_prompts import PHASE1_SPECIALISTS
            from phase0_specialists import PHASE0_SPECIALISTS
            from phase2_specialists import PHASE2_LAYER_7_10_SPECIALISTS
            from phase3_specialists import PHASE3_SPECIALISTS
            phase_specs = (
                PHASE0_SPECIALISTS
                + PHASE1_SPECIALISTS
                + PHASE2_LAYER_7_10_SPECIALISTS
                + PHASE3_SPECIALISTS
            )
        except ImportError as e2:
            print(f"WARNING: Could not load phase specialists: {e2}")
            phase_specs = []
            try:
                from specialist_prompts import PHASE1_SPECIALISTS
                phase_specs = PHASE1_SPECIALISTS
            except ImportError:
                pass
    return [adapt(s) for s in phase_specs]


# PURPOSE: 重複を除外して統合
def get_unified_specialists() -> list[Specialist]:
    """v2 (140人) + Phase 0-3 (866人) を統合して返す（ID重複を除外）

    Returns:
        統合された専門家リスト (~1000人)
    """
    from specialist_v2 import ALL_SPECIALISTS as V2_SPECIALISTS

    # v2 の ID を優先 (詳細定義が存在するため)
    v2_ids = {s.id for s in V2_SPECIALISTS}

    # Phase 0-3 から v2 に変換 (v2 と重複する ID は除外)
    phase_specs = get_all_phase_specialists_v2()
    unique_phase = [s for s in phase_specs if s.id not in v2_ids]

    unified = list(V2_SPECIALISTS) + unique_phase
    return unified


# PURPOSE: カテゴリ別の統計
def print_stats():
    """統合後の専門家統計を表示"""
    from specialist_v2 import ALL_SPECIALISTS as V2_SPECIALISTS

    unified = get_unified_specialists()
    v2_count = len(V2_SPECIALISTS)
    phase_count = len(unified) - v2_count

    print(f"=== Specialist Bridge Stats ===")
    print(f"  v2 Specialists: {v2_count}")
    print(f"  Phase 0-3 (adapted): {phase_count}")
    print(f"  Total (unified): {len(unified)}")
    print()

    # カテゴリ別
    from collections import Counter
    cats = Counter(s.category for s in unified)
    print("By Category:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    print_stats()
