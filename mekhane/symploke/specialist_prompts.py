#!/usr/bin/env python3
"""
Jules 専門家プロンプト生成モジュール

tekhne-maker v5.0 のアーキタイプ駆動設計に基づく
専門家レビュープロンプトの自動生成。
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Archetype(Enum):
    """tekhne-maker 5 Archetypes"""
    PRECISION = "precision"     # 🎯 誤答率 < 1%
    SPEED = "speed"             # ⚡ レイテンシ < 2秒
    AUTONOMY = "autonomy"       # 🤖 人間介入 < 10%
    CREATIVE = "creative"       # 🎨 多様性 > 0.8
    SAFETY = "safety"           # 🛡 リスク = 0


class Severity(Enum):
    """発見事項の重大度"""
    CRITICAL = "critical"   # 即時修正必須
    HIGH = "high"           # 早期修正推奨
    MEDIUM = "medium"       # 改善推奨
    LOW = "low"             # 任意
    NONE = "none"           # 問題なし


@dataclass
class SpecialistDefinition:
    """専門家定義"""
    id: str
    name: str
    category: str
    archetype: Archetype
    focus: str
    quality_standards: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    fallback: str = ""
    

# === カテゴリ別専門家定義 ===

COGNITIVE_LOAD_SPECIALISTS = [
    SpecialistDefinition(
        id="CL-001",
        name="変数スコープ認知負荷評価者",
        category="cognitive_load",
        archetype=Archetype.PRECISION,
        focus="変数スコープを分析し、認知負荷の問題を指摘",
        quality_standards=[
            "変数は使用するブロックの直前で定義すること",
            "グローバル/クラス変数は定数として明確に定義",
            "クロージャによる変数キャプチャは標準パターンに限定",
        ],
        edge_cases=["難読化コード", "動的生成変数"],
        fallback="構文解析失敗 → 最初の5件のエラーを提示",
    ),
    SpecialistDefinition(
        id="CL-002",
        name="抽象度層状評価者",
        category="cognitive_load",
        archetype=Archetype.PRECISION,
        focus="抽象度の階層構造を分析し、一貫性を評価",
        quality_standards=[
            "同一関数内で異なる抽象度の操作を混在させない",
            "高レベルAPI呼び出しと低レベル操作を分離",
        ],
    ),
    SpecialistDefinition(
        id="CL-003",
        name="メンタルモデル穴検出者",
        category="cognitive_load",
        archetype=Archetype.PRECISION,
        focus="暗黙的な前提条件を洗い出し、ドキュメント化の必要性を評価",
        quality_standards=[
            "暗黙的前提は明示的にdocstringに記載",
            "マジックナンバーは定数化",
        ],
    ),
]

AI_RISK_SPECIALISTS = [
    SpecialistDefinition(
        id="AI-001",
        name="命名ハルシネーション検出者",
        category="ai_risk",
        archetype=Archetype.PRECISION,
        focus="実在しないライブラリ/関数参照を確認",
        quality_standards=["全importが実在すること", "標準ライブラリ参照が正確"],
    ),
    SpecialistDefinition(
        id="AI-002",
        name="Mapping ハルシネーション検出者",
        category="ai_risk",
        archetype=Archetype.PRECISION,
        focus="存在しないAPIメソッド呼び出しを確認",
        quality_standards=["呼び出すメソッドが実際に存在すること"],
    ),
    SpecialistDefinition(
        id="AI-003",
        name="Resource ハルシネーション検出者",
        category="ai_risk",
        archetype=Archetype.PRECISION,
        focus="非実在リソース参照を確認",
        quality_standards=["参照するファイル/URLが存在すること"],
    ),
]

ASYNC_SPECIALISTS = [
    SpecialistDefinition(
        id="AS-001",
        name="イベントループブロッキング検出者",
        category="async",
        archetype=Archetype.PRECISION,
        focus="asyncioコード内のブロッキング呼び出しを検出",
        quality_standards=[
            "asyncio.sleep使用（time.sleep禁止）",
            "aiohttp/aiodnsなど非同期ライブラリ使用",
            "CPUバウンド処理はexecutorに委譲",
        ],
    ),
    SpecialistDefinition(
        id="AS-002",
        name="Orphaned Task 検出者",
        category="async",
        archetype=Archetype.PRECISION,
        focus="awaitされていないcreate_task呼び出しを確認",
        quality_standards=["create_taskの戻り値は必ず追跡"],
    ),
]

THEORY_SPECIALISTS = [
    SpecialistDefinition(
        id="TH-001",
        name="予測誤差バグ検出者",
        category="theory",
        archetype=Archetype.CREATIVE,
        focus="FEP観点での予測誤差（サプライズ）を確認",
        quality_standards=["ドキュメントとコードの整合性"],
    ),
    SpecialistDefinition(
        id="TH-002",
        name="信念状態一貫性評価者",
        category="theory",
        archetype=Archetype.CREATIVE,
        focus="暗黙的前提の統一性を評価",
        quality_standards=["モジュール間で前提条件が矛盾しない"],
    ),
]

# === 全専門家リスト ===
ALL_SPECIALISTS = (
    COGNITIVE_LOAD_SPECIALISTS +
    AI_RISK_SPECIALISTS +
    ASYNC_SPECIALISTS +
    THEORY_SPECIALISTS
)


def generate_prompt(spec: SpecialistDefinition, target_file: str, output_dir: str = "docs/reviews") -> str:
    """
    tekhne-maker 形式の専門家レビュープロンプトを生成
    
    Args:
        spec: 専門家定義
        target_file: レビュー対象ファイル
        output_dir: レビュー結果の出力ディレクトリ
    
    Returns:
        生成されたプロンプト文字列
    """
    archetype_emoji = {
        Archetype.PRECISION: "🎯",
        Archetype.SPEED: "⚡",
        Archetype.AUTONOMY: "🤖",
        Archetype.CREATIVE: "🎨",
        Archetype.SAFETY: "🛡",
    }
    
    emoji = archetype_emoji.get(spec.archetype, "📋")
    
    # 品質基準をフォーマット
    standards_text = ""
    if spec.quality_standards:
        standards_text = "\n## Quality Standards\n" + "\n".join(
            f"- {s}" for s in spec.quality_standards
        )
    
    # エッジケースをフォーマット
    edge_cases_text = ""
    if spec.edge_cases:
        edge_cases_text = "\n## Edge Cases\n" + "\n".join(
            f"- {e}" for e in spec.edge_cases
        )
    
    # フォールバック
    fallback_text = ""
    if spec.fallback:
        fallback_text = f"\n## Fallback\n{spec.fallback}"
    
    output_file = f"{output_dir}/{spec.id.lower()}_review.md"
    
    prompt = f"""# {emoji} 専門家レビュー: {spec.name}

> **Archetype:** {spec.archetype.value.capitalize()}
> **Category:** {spec.category}

## Task

`{target_file}` を以下の観点で分析し、結果を `{output_file}` に書き込んでください。

## Focus

{spec.focus}
{standards_text}
{edge_cases_text}

## Output Format

以下の形式でファイルに出力:

```markdown
# {spec.name} レビュー

## 対象ファイル
`{target_file}`

## 発見事項
- (問題があれば列挙、なければ「問題なし」)

## 重大度
- Critical/High/Medium/Low/None

## 推奨事項
- (改善提案があれば)

## 沈黙判定
- 沈黙（問題なし）/ 発言（要改善）
```
{fallback_text}

**重要**: 必ず上記ファイルを作成してコミットしてください。
"""
    return prompt.strip()


def get_specialists_by_category(category: str) -> list[SpecialistDefinition]:
    """カテゴリ別に専門家を取得"""
    return [s for s in ALL_SPECIALISTS if s.category == category]


def get_specialists_by_archetype(archetype: Archetype) -> list[SpecialistDefinition]:
    """アーキタイプ別に専門家を取得"""
    return [s for s in ALL_SPECIALISTS if s.archetype == archetype]


if __name__ == "__main__":
    # サンプル出力
    spec = COGNITIVE_LOAD_SPECIALISTS[0]
    prompt = generate_prompt(spec, "mekhane/symploke/jules_client.py")
    print(prompt)
