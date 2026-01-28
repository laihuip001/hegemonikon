#!/usr/bin/env python3
"""
Jules 専門家プロンプト生成モジュール v3.0

tekhne-maker v5.0 のアーキタイプ駆動設計に基づく
専門家レビュープロンプトの自動生成。

Phase 1: 見落とし層 91人
Phase 2: 運用・実務層 290人 (Layer 7-15)
Phase 3: 高度分析層 230人 (Layer 16-20)
合計: 611人 (Phase 0の既存255人を含め866人)
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


# ============ Phase 1: 見落とし層 (91人) ============

# --- 認知負荷層 (15人) ---
COGNITIVE_LOAD_SPECIALISTS = [
    SpecialistDefinition(id="CL-001", name="変数スコープ認知負荷評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="変数スコープを分析し、認知負荷の問題を指摘"),
    SpecialistDefinition(id="CL-002", name="抽象度層状評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="抽象度の階層構造を分析し、一貫性を評価"),
    SpecialistDefinition(id="CL-003", name="メンタルモデル穴検出者", category="cognitive_load", archetype=Archetype.PRECISION, focus="暗黙的な前提条件を洗い出し、ドキュメント化の必要性を評価"),
    SpecialistDefinition(id="CL-004", name="チャンク化効率評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="関連処理のグループ化の効率性を評価"),
    SpecialistDefinition(id="CL-005", name="事前知識査定者", category="cognitive_load", archetype=Archetype.PRECISION, focus="コード理解に必要な事前知識を列挙"),
    SpecialistDefinition(id="CL-006", name="一時変数負荷評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="一時変数の認知負荷を評価"),
    SpecialistDefinition(id="CL-007", name="ネスト深度評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="ネスト深度と論理的複雑性のバランスを評価"),
    SpecialistDefinition(id="CL-008", name="コード密度測定者", category="cognitive_load", archetype=Archetype.PRECISION, focus="行あたりの意思決定点を測定"),
    SpecialistDefinition(id="CL-009", name="パターン認識評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="認識可能なパターンと視認性を評価"),
    SpecialistDefinition(id="CL-010", name="ドメイン概念評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="ドメイン固有概念の統一性を評価"),
    SpecialistDefinition(id="CL-011", name="認知的ウォークスルー評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="新規開発者の理解プロセスをシミュレート"),
    SpecialistDefinition(id="CL-012", name="コンテキストスイッチ検出者", category="cognitive_load", archetype=Archetype.PRECISION, focus="ファイル間の頻繁な移動が必要な箇所を検出"),
    SpecialistDefinition(id="CL-013", name="エラーハンドリング一貫性評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="例外処理パターンの一貫性を評価"),
    SpecialistDefinition(id="CL-014", name="命名規則一貫性評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="変数・関数・クラス名の命名規則の一貫性を評価"),
    SpecialistDefinition(id="CL-015", name="コメント品質評価者", category="cognitive_load", archetype=Archetype.PRECISION, focus="コメントの有用性と最新性を評価"),
]

# --- 感情・社会層 (18人) ---
EMOTIONAL_SOCIAL_SPECIALISTS = [
    SpecialistDefinition(id="ES-001", name="査読バイアス検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="査読者の主観的バイアスを検出"),
    SpecialistDefinition(id="ES-002", name="コードレビュートーン評価者", category="emotional_social", archetype=Archetype.SAFETY, focus="レビューコメントのトーンと建設性を評価"),
    SpecialistDefinition(id="ES-003", name="チーム協調性評価者", category="emotional_social", archetype=Archetype.SAFETY, focus="コードがチーム規約に沿っているか評価"),
    SpecialistDefinition(id="ES-004", name="新人フレンドリー評価者", category="emotional_social", archetype=Archetype.SAFETY, focus="新規参加者への配慮度を評価"),
    SpecialistDefinition(id="ES-005", name="エラーメッセージ共感性評価者", category="emotional_social", archetype=Archetype.CREATIVE, focus="エラーメッセージのユーザーフレンドリー度を評価"),
    SpecialistDefinition(id="ES-006", name="ドキュメント親和性評価者", category="emotional_social", archetype=Archetype.CREATIVE, focus="ドキュメントの読みやすさと親しみやすさを評価"),
    SpecialistDefinition(id="ES-007", name="変更履歴透明性評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="コミットメッセージと変更理由の明確さを評価"),
    SpecialistDefinition(id="ES-008", name="責任分界点評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="所有権と責任範囲の明確さを評価"),
    SpecialistDefinition(id="ES-009", name="コラボレーション障壁検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="チーム協力を妨げる構造を検出"),
    SpecialistDefinition(id="ES-010", name="知識移転可能性評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="知識の引き継ぎやすさを評価"),
    SpecialistDefinition(id="ES-011", name="燃え尽き症候群リスク検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="過度に複雑な保守要求を検出"),
    SpecialistDefinition(id="ES-012", name="ペアプログラミング適性評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="ペアプログラミングの容易さを評価"),
    SpecialistDefinition(id="ES-013", name="非同期コラボ評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="リモートチームでの協力のしやすさを評価"),
    SpecialistDefinition(id="ES-014", name="多様性包摂性評価者", category="emotional_social", archetype=Archetype.SAFETY, focus="排他的表現や仮定を検出"),
    SpecialistDefinition(id="ES-015", name="オンボーディング障壁検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="新規参加者の障壁を検出"),
    SpecialistDefinition(id="ES-016", name="レビュー疲労検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="レビュー負荷の偏りを検出"),
    SpecialistDefinition(id="ES-017", name="技術的議論品質評価者", category="emotional_social", archetype=Archetype.PRECISION, focus="PRコメントの議論品質を評価"),
    SpecialistDefinition(id="ES-018", name="承認バイアス検出者", category="emotional_social", archetype=Archetype.SAFETY, focus="安易な承認パターンを検出"),
]

# --- AI固有リスク層 (22人) ---
AI_RISK_SPECIALISTS = [
    SpecialistDefinition(id="AI-001", name="命名ハルシネーション検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="実在しないライブラリ/関数参照を確認"),
    SpecialistDefinition(id="AI-002", name="Mapping ハルシネーション検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="存在しないAPIメソッド呼び出しを確認"),
    SpecialistDefinition(id="AI-003", name="Resource ハルシネーション検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="非実在リソース参照を確認"),
    SpecialistDefinition(id="AI-004", name="Logic ハルシネーション検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="構文的に正しいが意味的欠陥のあるロジックを確認"),
    SpecialistDefinition(id="AI-005", name="不完全コード検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="未完成ブロック(try/except未完成等)を確認"),
    SpecialistDefinition(id="AI-006", name="DRY違反検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="重複コード(同機能3箇所以上)を確認"),
    SpecialistDefinition(id="AI-007", name="パターン一貫性検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="同じライブラリを異なる命名規則で使用していないか確認"),
    SpecialistDefinition(id="AI-008", name="自己矛盾検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="前後の前提条件が矛盾していないか確認"),
    SpecialistDefinition(id="AI-009", name="既知脆弱性パターン検出者", category="ai_risk", archetype=Archetype.SAFETY, focus="セキュリティ脆弱性パターン(CWE)を確認"),
    SpecialistDefinition(id="AI-010", name="入力検証欠落検出者", category="ai_risk", archetype=Archetype.SAFETY, focus="入力バリデーションが省略されていないか確認"),
    SpecialistDefinition(id="AI-011", name="過剰最適化検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="AIによる過度な最適化を検出"),
    SpecialistDefinition(id="AI-012", name="コンテキスト喪失検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="AIが生成時のコンテキストを失っている兆候を検出"),
    SpecialistDefinition(id="AI-013", name="スタイル不整合検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="AI生成部分と既存コードのスタイル不整合を検出"),
    SpecialistDefinition(id="AI-014", name="過剰コメント検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="明らかなコードへの冗長なコメントを検出"),
    SpecialistDefinition(id="AI-015", name="コピペ痕跡検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="コピペされたがカスタマイズされていないコードを検出"),
    SpecialistDefinition(id="AI-016", name="デッドコード検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="到達不能コードや未使用コードを検出"),
    SpecialistDefinition(id="AI-017", name="マジックナンバー検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="説明のない数値リテラルを検出"),
    SpecialistDefinition(id="AI-018", name="ハードコードパス検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="環境固有のハードコードされたパスを検出"),
    SpecialistDefinition(id="AI-019", name="暗黙的型変換検出者", category="ai_risk", archetype=Archetype.PRECISION, focus="意図しない型変換を検出"),
    SpecialistDefinition(id="AI-020", name="例外握りつぶし検出者", category="ai_risk", archetype=Archetype.SAFETY, focus="空のexceptブロックを検出"),
    SpecialistDefinition(id="AI-021", name="リソースリーク検出者", category="ai_risk", archetype=Archetype.SAFETY, focus="未解放リソースを検出"),
    SpecialistDefinition(id="AI-022", name="競合状態検出者", category="ai_risk", archetype=Archetype.SAFETY, focus="並行処理での競合状態リスクを検出"),
]

# --- 非同期層 (12人) ---
ASYNC_SPECIALISTS = [
    SpecialistDefinition(id="AS-001", name="イベントループブロッキング検出者", category="async", archetype=Archetype.PRECISION, focus="asyncioコード内のブロッキング呼び出しを検出"),
    SpecialistDefinition(id="AS-002", name="Orphaned Task 検出者", category="async", archetype=Archetype.PRECISION, focus="awaitされていないcreate_task呼び出しを確認"),
    SpecialistDefinition(id="AS-003", name="キャンセレーション処理評価者", category="async", archetype=Archetype.PRECISION, focus="CancelledErrorハンドリングを評価"),
    SpecialistDefinition(id="AS-004", name="非同期リソース管理評価者", category="async", archetype=Archetype.PRECISION, focus="async withコンテキストマネージャの使用を評価"),
    SpecialistDefinition(id="AS-005", name="gather制限評価者", category="async", archetype=Archetype.PRECISION, focus="gather()のタスク数制限(Semaphore)を評価"),
    SpecialistDefinition(id="AS-006", name="タイムアウト設定評価者", category="async", archetype=Archetype.PRECISION, focus="適切なタイムアウト設定を確認"),
    SpecialistDefinition(id="AS-007", name="再試行ロジック評価者", category="async", archetype=Archetype.PRECISION, focus="エクスポネンシャルバックオフ等の再試行パターンを評価"),
    SpecialistDefinition(id="AS-008", name="コネクションプール評価者", category="async", archetype=Archetype.PRECISION, focus="接続プールの適切な管理を確認"),
    SpecialistDefinition(id="AS-009", name="TaskGroup使用評価者", category="async", archetype=Archetype.PRECISION, focus="Python 3.11+ TaskGroupの活用を評価"),
    SpecialistDefinition(id="AS-010", name="シグナルハンドリング評価者", category="async", archetype=Archetype.PRECISION, focus="graceful shutdownの実装を評価"),
    SpecialistDefinition(id="AS-011", name="非同期イテレータ評価者", category="async", archetype=Archetype.PRECISION, focus="async for/async generatorの使用を評価"),
    SpecialistDefinition(id="AS-012", name="ロック競合検出者", category="async", archetype=Archetype.SAFETY, focus="asyncio.Lockのデッドロックリスクを検出"),
]

# --- 理論的整合性層 (16人) ---
THEORY_SPECIALISTS = [
    SpecialistDefinition(id="TH-001", name="予測誤差バグ検出者", category="theory", archetype=Archetype.CREATIVE, focus="FEP観点での予測誤差（サプライズ）を確認"),
    SpecialistDefinition(id="TH-002", name="信念状態一貫性評価者", category="theory", archetype=Archetype.CREATIVE, focus="暗黙的前提の統一性を評価"),
    SpecialistDefinition(id="TH-003", name="Markov blanket 検出者", category="theory", archetype=Archetype.CREATIVE, focus="依存関係の条件付き独立性を分析"),
    SpecialistDefinition(id="TH-004", name="支配二分法評価者", category="theory", archetype=Archetype.CREATIVE, focus="変更可能な側面とシステム制約の区別を評価"),
    SpecialistDefinition(id="TH-005", name="因果構造透明性評価者", category="theory", archetype=Archetype.CREATIVE, focus="実装における因果関係の明確さを評価"),
    SpecialistDefinition(id="TH-006", name="自己証拠性評価者", category="theory", archetype=Archetype.CREATIVE, focus="コードが自己説明的かを評価"),
    SpecialistDefinition(id="TH-007", name="能動推論パターン評価者", category="theory", archetype=Archetype.CREATIVE, focus="期待状態に向かう行動パターンを評価"),
    SpecialistDefinition(id="TH-008", name="変分自由エネルギー評価者", category="theory", archetype=Archetype.CREATIVE, focus="複雑性と精度のトレードオフを評価"),
    SpecialistDefinition(id="TH-009", name="階層的予測評価者", category="theory", archetype=Archetype.CREATIVE, focus="多層的な抽象化の整合性を評価"),
    SpecialistDefinition(id="TH-010", name="ストア派規範評価者", category="theory", archetype=Archetype.CREATIVE, focus="行動が規範的原則に沿っているか評価"),
    SpecialistDefinition(id="TH-011", name="JTB知識評価者", category="theory", archetype=Archetype.PRECISION, focus="正当化された真なる信念かを評価"),
    SpecialistDefinition(id="TH-012", name="認識論的謙虚さ評価者", category="theory", archetype=Archetype.CREATIVE, focus="不確実性の適切な表現を評価"),
    SpecialistDefinition(id="TH-013", name="CMoC適合性評価者", category="theory", archetype=Archetype.CREATIVE, focus="Computational Model of Cognitionへの適合を評価"),
    SpecialistDefinition(id="TH-014", name="目的論的一貫性評価者", category="theory", archetype=Archetype.CREATIVE, focus="コードの目的と実装の一致を評価"),
    SpecialistDefinition(id="TH-015", name="システム境界評価者", category="theory", archetype=Archetype.CREATIVE, focus="モジュール境界の適切さを評価"),
    SpecialistDefinition(id="TH-016", name="ホメオスタシス評価者", category="theory", archetype=Archetype.CREATIVE, focus="システムの自己安定性を評価"),
]

# --- 美学・デザイン層 (8人) ---
AESTHETICS_SPECIALISTS = [
    SpecialistDefinition(id="AE-001", name="import順序評価者", category="aesthetics", archetype=Archetype.PRECISION, focus="import文の順序と整理を評価"),
    SpecialistDefinition(id="AE-002", name="コメント品質評価者", category="aesthetics", archetype=Archetype.PRECISION, focus="コメントの明確さと有用性を評価"),
    SpecialistDefinition(id="AE-003", name="エラーメッセージ評価者", category="aesthetics", archetype=Archetype.CREATIVE, focus="エラーメッセージの明確さと共感性を評価"),
    SpecialistDefinition(id="AE-004", name="フォーマット一貫性評価者", category="aesthetics", archetype=Archetype.PRECISION, focus="コードフォーマットの一貫性を評価"),
    SpecialistDefinition(id="AE-005", name="ドキュメント構造評価者", category="aesthetics", archetype=Archetype.PRECISION, focus="docstringの構造と完全性を評価"),
    SpecialistDefinition(id="AE-006", name="比喩一貫性評価者", category="aesthetics", archetype=Archetype.CREATIVE, focus="命名における比喩の一貫性を評価"),
    SpecialistDefinition(id="AE-007", name="視覚的リズム評価者", category="aesthetics", archetype=Archetype.CREATIVE, focus="空白行やインデントによるリズムを評価"),
    SpecialistDefinition(id="AE-008", name="シンプリシティ評価者", category="aesthetics", archetype=Archetype.CREATIVE, focus="不必要な複雑さの排除を評価"),
]

# === 全専門家リスト (Phase 1: 91人) ===
PHASE1_SPECIALISTS = (
    COGNITIVE_LOAD_SPECIALISTS +      # 15人
    EMOTIONAL_SOCIAL_SPECIALISTS +    # 18人
    AI_RISK_SPECIALISTS +             # 22人
    ASYNC_SPECIALISTS +               # 12人
    THEORY_SPECIALISTS +              # 16人
    AESTHETICS_SPECIALISTS            # 8人
)  # 合計 91人

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
            PHASE0_SPECIALISTS +             # 255人 (Layer 1-6 + Buffer)
            PHASE1_SPECIALISTS +             # 91人  (見落とし層)
            PHASE2_LAYER_7_10_SPECIALISTS +  # 170人 (Layer 7-10)
            PHASE2_LAYER_11_15_SPECIALISTS + # 120人 (Layer 11-15)
            PHASE3_SPECIALISTS               # 230人 (Layer 16-20)
        )  # 合計 866人
    return _ALL_SPECIALISTS_CACHE

# 後方互換性のため
ALL_SPECIALISTS = PHASE1_SPECIALISTS


def generate_prompt(spec: SpecialistDefinition, target_file: str, output_dir: str = "docs/reviews") -> str:
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


def get_specialists_by_category(category: str, include_all_phases: bool = False) -> list[SpecialistDefinition]:
    """カテゴリ別に専門家を取得"""
    specialists = get_all_specialists() if include_all_phases else ALL_SPECIALISTS
    return [s for s in specialists if s.category == category]


def get_specialists_by_archetype(archetype: Archetype, include_all_phases: bool = False) -> list[SpecialistDefinition]:
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
    for cat in ["cognitive_load", "emotional_social", "ai_risk", "async", "theory", "aesthetics"]:
        count = len(get_specialists_by_category(cat))
        print(f"  {cat}: {count}")
    
    # All phases
    print(f"\n[全Phase統合 (Phase 1-3)]")
    all_specs = get_all_specialists()
    print(f"Total specialists: {len(all_specs)}")
    for cat in get_all_categories(include_all_phases=True):
        count = len(get_specialists_by_category(cat, include_all_phases=True))
        print(f"  {cat}: {count}")
