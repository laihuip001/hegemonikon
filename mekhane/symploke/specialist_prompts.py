#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→specialist_prompts が担う
"""
Jules 専門家プロンプト生成モジュール v3.0

tekhne-maker v5.0 のアーキタイプ駆動設計に基づく
専門家レビュープロンプトの自動生成。

Phase 1: 見落とし層 91人
Phase 2: 運用・実務層 290人 (Layer 7-15)
Phase 3: 高度分析層 230人 (Layer 16-20)
合計: 611人 (Phase 0の既存255人を含め866人)
"""

from .specialist_types import Archetype, Severity, SpecialistDefinition
from .specialists_tier1 import PHASE1_SPECIALISTS


# Phase 2/3/0 は別モジュールで定義
# インポート時の循環参照を避けるため、遅延インポートを使用
_ALL_SPECIALISTS_CACHE = None


def get_all_specialists():
    """全専門家リストを取得 (Phase 0-3: 866人)"""
    global _ALL_SPECIALISTS_CACHE
    if _ALL_SPECIALISTS_CACHE is None:
        from .phase0_specialists import PHASE0_SPECIALISTS
        from .phase2_specialists import PHASE2_LAYER_7_10_SPECIALISTS
        from .phase2_remaining import PHASE2_LAYER_11_15_SPECIALISTS
        from .phase3_specialists import PHASE3_SPECIALISTS

        _ALL_SPECIALISTS_CACHE = (
            PHASE0_SPECIALISTS  # 255人 (Layer 1-6 + Buffer)
            + PHASE1_SPECIALISTS  # 91人  (見落とし層)
            + PHASE2_LAYER_7_10_SPECIALISTS  # 170人 (Layer 7-10)
            + PHASE2_LAYER_11_15_SPECIALISTS  # 120人 (Layer 11-15)
            + PHASE3_SPECIALISTS  # 230人 (Layer 16-20)
        )  # 合計 866人
    return _ALL_SPECIALISTS_CACHE


# 後方互換性のため
ALL_SPECIALISTS = PHASE1_SPECIALISTS


def generate_prompt(
    spec: SpecialistDefinition, target_file: str, output_dir: str = "docs/reviews"
) -> str:
    """tekhne-maker 形式の専門家レビュープロンプトを生成"""
    archetype_emoji = {
        Archetype.PRECISION: "🎯",
        Archetype.SPEED: "⚡",
        Archetype.AUTONOMY: "🤖",
        Archetype.CREATIVE: "🎨",
        Archetype.SAFETY: "🛡",
    }
    emoji = archetype_emoji.get(spec.archetype, "📋")
    output_file = f"{output_dir}/{spec.id.lower()}_review.md"

    prompt = f"""# {emoji} 専門家レビュー: {spec.name}

> **Archetype:** {spec.archetype.value.capitalize()}
> **Category:** {spec.category}

## Task

`{target_file}` を以下の観点で分析し、結果を `{output_file}` に書き込んでください。

## Focus

{spec.focus}

## Output Format

```markdown
# {spec.name} レビュー

## 対象ファイル
`{target_file}`

## 発見事項
- (問題があれば列挙、なければ「問題なし」)

## 重大度
- Critical/High/Medium/Low/None

## 沈黙判定
- 沈黙（問題なし）/ 発言（要改善）
```

**重要**: 必ず上記ファイルを作成してコミットしてください。
"""
    return prompt.strip()


def get_specialists_by_category(
    category: str, include_all_phases: bool = False
) -> list[SpecialistDefinition]:
    """カテゴリ別に専門家を取得"""
    specialists = get_all_specialists() if include_all_phases else ALL_SPECIALISTS
    return [s for s in specialists if s.category == category]


def get_specialists_by_archetype(
    archetype: Archetype, include_all_phases: bool = False
) -> list[SpecialistDefinition]:
    """アーキタイプ別に専門家を取得"""
    specialists = get_all_specialists() if include_all_phases else ALL_SPECIALISTS
    return [s for s in specialists if s.archetype == archetype]


def get_all_categories(include_all_phases: bool = False) -> list[str]:
    """全カテゴリを取得"""
    specialists = get_all_specialists() if include_all_phases else ALL_SPECIALISTS
    return sorted(set(s.category for s in specialists))


if __name__ == "__main__":
    print(f"=== Jules Specialist Prompts v3.0 ===")

    # Phase 1 only
    print(f"\n[Phase 1: 見落とし層]")
    print(f"Total specialists: {len(PHASE1_SPECIALISTS)}")
    for cat in [
        "cognitive_load",
        "emotional_social",
        "ai_risk",
        "async",
        "theory",
        "aesthetics",
    ]:
        count = len(get_specialists_by_category(cat))
        print(f"  {cat}: {count}")

    # All phases
    print(f"\n[全Phase統合 (Phase 1-3)]")
    all_specs = get_all_specialists()
    print(f"Total specialists: {len(all_specs)}")
    for cat in get_all_categories(include_all_phases=True):
        count = len(get_specialists_by_category(cat, include_all_phases=True))
        print(f"  {cat}: {count}")
