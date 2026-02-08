#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→Tier1進化専門家→specialists_tier1 が担う
"""
Tier 1 進化専門家: Hegemonikón の進化に直接寄与する純化された知性

設計思想:
    - Tier 1 = 進化専門家（常時実行）
    - Tier 2 = 衛生専門家（月次/CI）

選定基準:
    1. Hegemonikón 固有（一般プロジェクトに適用不可）
    2. 高発言率（沈黙より発言が多い）
    3. 構造的洞察（表層ではなく本質を見る）
    4. 情報利得 = P(発言) × 発見の構造的価値

構成:
    - HG-* (8人): Hegemonikón 核心（PROOF/FEP/CCL/定理/WF/座標/Dendron）
    - AI-* (2人): ハルシネーション検出（CRITICAL/HIGH）
    - CG-* (2人): 認知負荷（HIGH）
    - AE-* (3人): 構造的美学（視覚リズム/シンプル/比喩）
    - CF-* (2人): クロスファイル依存（循環/契約）
    - EV-* (2人): 進化方向（配置/カバレッジ）
    - LM-* (1人): LLM生成パターン（統合臭気判断）

派生システム (v2.0):
    3軸派生により視点を拡張し、Jules枠を効率活用
    - Scope: μ (Micro/関数), m (Meso/ファイル), M (Macro/モジュール)
    - Intent: D (Detect/検出), F (Fix/修正), P (Prevent/予防)
    - Archetype: 既存5種 (Precision/Speed/Autonomy/Creative/Safety)
    
    CCL記法: HG-001.μD, HG-001.MF+safety など

Usage:
    from specialists_tier1 import (
        TIER1_SPECIALISTS,
        get_tier1_by_category,
        derive_specialist,  # 派生生成
        Scope, Intent,
    )
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from copy import deepcopy

try:
    from .specialist_v2 import Specialist, Archetype, VerdictFormat, Severity
except ImportError:
    from specialist_v2 import Specialist, Archetype, VerdictFormat, Severity


# ============ 派生軸 (Derivative Axes) ============

class Scope(Enum):
    """検査範囲 (Scale公理からの導出)"""
    MICRO = "μ"   # 関数レベル
    MESO = "m"    # ファイルレベル (デフォルト)
    MACRO = "M"   # モジュール/パッケージレベル


class Intent(Enum):
    """検査意図 (Value公理からの導出)"""
    DETECT = "D"   # 検出のみ (デフォルト)
    FIX = "F"      # 修正提案付き
    PREVENT = "P"  # 予防ルール化


# ============ 派生生成 ============

def derive_specialist(
    base: Specialist,
    scope: Optional[Scope] = None,
    intent: Optional[Intent] = None,
    archetype_override: Optional[Archetype] = None,
) -> Specialist:
    """
    基本専門家から派生を生成する
    
    Args:
        base: 基本専門家
        scope: 検査範囲 (None=Meso)
        intent: 検査意図 (None=Detect)
        archetype_override: アーキタイプ上書き (None=維持)
    
    Returns:
        派生専門家 (新インスタンス)
    
    Example:
        >>> derived = derive_specialist(HG_001, scope=Scope.MACRO, intent=Intent.FIX)
        >>> derived.id
        'HG-001.MF'
    """
    derived = deepcopy(base)
    
    # ID生成
    suffix_parts = []
    if scope and scope != Scope.MESO:
        suffix_parts.append(scope.value)
    if intent and intent != Intent.DETECT:
        suffix_parts.append(intent.value)
    if archetype_override:
        suffix_parts.append(f"+{archetype_override.value[:3]}")
    
    if suffix_parts:
        derived.id = f"{base.id}.{''.join(suffix_parts)}"
    
    # Scope による perceives 調整
    if scope == Scope.MICRO:
        derived.domain = f"[Micro] {base.domain}"
        derived.perceives = [f"(関数単位) {p}" for p in base.perceives]
    elif scope == Scope.MACRO:
        derived.domain = f"[Macro] {base.domain}"
        derived.perceives = [f"(モジュール全体) {p}" for p in base.perceives]
    
    # Intent による verdict 調整
    if intent == Intent.FIX:
        derived.verdict = VerdictFormat.DIFF
        derived.measure = f"{base.measure} + 修正コード提案"
    elif intent == Intent.PREVENT:
        derived.verdict = VerdictFormat.REVIEW
        derived.measure = f"{base.measure} + 予防ルール (.pre-commit, lint設定)"
    
    # Archetype 上書き
    if archetype_override:
        derived.archetype = archetype_override
    
    return derived


def get_all_derivatives(base: Specialist) -> list[Specialist]:
    """
    基本専門家から全派生を生成する (3×3=9派生)
    
    注意: 基本形 (Meso×Detect) は含まない
    """
    derivatives = []
    for scope in Scope:
        for intent in Intent:
            if scope == Scope.MESO and intent == Intent.DETECT:
                continue  # 基本形はスキップ
            derivatives.append(derive_specialist(base, scope, intent))
    return derivatives



# ============ Tier 1: Hegemonikón Core (6人) ============

HEGEMONIKON_TIER1 = [
    Specialist(
        id="HG-001",
        name="PROOF行検査官",
        category="hegemonikon",
        archetype=Archetype.PRECISION,
        domain="存在証明の完全性",
        principle="存在証明のないコードは存在しないコードと同じ",
        perceives=[
            "# PROOF: で始まる行がファイル冒頭20行内に不在",
            "PROOF行の形式違反（パス/定理参照の欠落）",
            "PROOF行とファイルパスの不整合",
            "PROOF行の定理参照が24定理に存在しない",
        ],
        blind_to=[
            "コードロジックの正しさ",
            "パフォーマンス",
        ],
        measure="全Pythonファイルに有効なPROOF行が存在する",
        verdict=VerdictFormat.DIFF,
        severity_map={
            "PROOF行欠如": Severity.HIGH,
            "形式違反": Severity.MEDIUM,
            "パス不整合": Severity.MEDIUM,
            "定理参照エラー": Severity.LOW,
        },
    ),
    Specialist(
        id="HG-002",
        name="予測誤差審問官",
        category="hegemonikon",
        archetype=Archetype.CREATIVE,
        domain="FEP原則の体現",
        principle="予測誤差を最小化しているか — 驚きは設計の失敗",
        perceives=[
            "関数の副作用が名前から予測不能",
            "戻り値の型が呼び出し元で予測困難",
            "状態変更が暗黙的（self.xxx = 等が隠れている）",
            "例外の発生が関数シグネチャから不明",
        ],
        blind_to=[
            "ビジネスロジックの妥当性",
            "ドメイン知識",
        ],
        measure="コードの振る舞いが名前・型・シグネチャから予測可能",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "副作用非明示": Severity.HIGH,
            "型予測困難": Severity.MEDIUM,
            "暗黙状態変更": Severity.MEDIUM,
        },
    ),
    Specialist(
        id="HG-003",
        name="ストア派制御審判",
        category="hegemonikon",
        archetype=Archetype.SAFETY,
        domain="制御の二分法の適用",
        principle="制御できないことを制御しようとするな — 受け入れよ",
        perceives=[
            "外部API呼び出しにタイムアウト設定なし",
            "ネットワーク障害時のフォールバック欠如",
            "ファイルI/O失敗時のリカバリ戦略なし",
            "外部サービス依存で retry/circuit breaker なし",
        ],
        blind_to=[
            "楽観主義の利点",
            "開発速度",
        ],
        measure="制御不能な外部要素に対する防御策が存在する",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "タイムアウト欠如": Severity.HIGH,
            "フォールバック欠如": Severity.MEDIUM,
            "リカバリ戦略なし": Severity.MEDIUM,
        },
    ),
    Specialist(
        id="HG-004",
        name="CCL式美学者",
        category="hegemonikon",
        archetype=Archetype.CREATIVE,
        domain="CCL構文の美しさ",
        principle="/noe+*dia^ は思考の軌跡 — 美しく簡潔であれ",
        perceives=[
            "CCL式が60ポイント超過（分割推奨）",
            "演算子の意図が不明（コメントなし）",
            "冗長なCCL式（簡略化可能）",
            "ネストが3レベル超過",
        ],
        blind_to=[
            "CCLの実行結果",
            "ワークフローの有効性",
        ],
        measure="CCL式が簡潔で意図明確、45ポイント以内",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "60pt超過": Severity.MEDIUM,
            "意図不明": Severity.LOW,
            "冗長": Severity.LOW,
        },
    ),
    Specialist(
        id="HG-005",
        name="定理整合性監査官",
        category="hegemonikon",
        archetype=Archetype.PRECISION,
        domain="24定理との整合",
        principle="O/H/A/S/P/K の6カテゴリ×4定理 — 体系に逆らうな",
        perceives=[
            "ワークフローが定理体系から逸脱",
            "スキルが定理参照を持たない",
            ".md ファイルに hegemonikon: フロントマター欠如",
            "定理間の依存関係違反（X-series）",
        ],
        blind_to=[
            "実装詳細",
            "コード品質",
        ],
        measure="全ワークフロー/スキルが定理体系に整合",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "定理逸脱": Severity.MEDIUM,
            "フロントマター欠如": Severity.LOW,
            "X-series違反": Severity.LOW,
        },
    ),
    Specialist(
        id="HG-006",
        name="ワークフロー適合審査官",
        category="hegemonikon",
        archetype=Archetype.PRECISION,
        domain="ワークフローパターン遵守",
        principle="/boot, /bye, /zet, /dia... パターンは体系の骨格",
        perceives=[
            ".agent/workflows/ 外のワークフロー定義",
            "ワークフローに description フロントマター欠如",
            "ワークフロー間の循環参照",
            "派生モード（+/-/*）の未定義使用",
        ],
        blind_to=[
            "ワークフローの内容品質",
            "ステップの妥当性",
        ],
        measure="ワークフローが規定の形式・配置に従う",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "配置違反": Severity.MEDIUM,
            "フロントマター欠如": Severity.LOW,
            "循環参照": Severity.HIGH,
        },
    ),
]


# ============ Tier 1: AI生成コード検出 (2人) ============

AI_TIER1 = [
    Specialist(
        id="AI-002",
        name="ハルシネーション検出者",
        category="ai_generated",
        archetype=Archetype.SAFETY,
        domain="存在しないAPIの呼び出し",
        principle="LLMは自信満々に嘘をつく — 検証せよ",
        perceives=[
            "存在しないモジュールの import",
            "存在しないメソッド呼び出し（例: .to_list() vs list()）",
            "存在しないクラス属性へのアクセス",
            "廃止されたAPIの使用（例: asyncio.get_event_loop() in 3.10+）",
            "実在しない引数名の使用",
        ],
        blind_to=[
            "コードロジックの正しさ",
            "設計の妥当性",
        ],
        measure="全API呼び出しが実在し、現行バージョンで有効",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "存在しないモジュール": Severity.CRITICAL,
            "存在しないメソッド": Severity.CRITICAL,
            "廃止API": Severity.HIGH,
            "存在しない引数": Severity.MEDIUM,
        },
    ),
    Specialist(
        id="AI-005",
        name="コード/コメント矛盾検出者",
        category="ai_generated",
        archetype=Archetype.SAFETY,
        domain="コードとコメントの一致",
        principle="LLMはコメントとコードで違うことを言う — 嘘つきを暴け",
        perceives=[
            "docstring の Args と実際の引数の不一致",
            "docstring の Returns と実際の戻り値型の不一致",
            "コメントが説明する処理と実コードの乖離",
            "TODO コメントが指す処理が既に実装済み",
            "例外の説明が Raises に書かれていない",
        ],
        blind_to=[
            "コメントの意図",
            "ビジネス要件",
        ],
        measure="コードとコメントが完全に一致",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "Args不一致": Severity.HIGH,
            "Returns不一致": Severity.HIGH,
            "処理乖離": Severity.MEDIUM,
            "古いTODO": Severity.LOW,
        },
    ),
]


# ============ Tier 1: 認知科学 (2人) ============

COGNITIVE_TIER1 = [
    Specialist(
        id="CG-001",
        name="ネスト深度警報者",
        category="cognitive",
        archetype=Archetype.PRECISION,
        domain="認知負荷（ネスト）",
        principle="脳は7±2しか処理できない — 4段以上は地獄への入口",
        perceives=[
            "if/for/while/with のネストが4段以上",
            "try-except 内のネストが3段以上",
            "リスト内包表記のネストが2段以上",
            "コールバック関数のネストが3段以上",
        ],
        blind_to=[
            "ロジックの必然性",
            "ビジネス要件の複雑さ",
        ],
        measure="全ネストが3段以内",
        verdict=VerdictFormat.REFACTOR,
        severity_map={
            "4段以上": Severity.HIGH,
            "3段": Severity.MEDIUM,
            "内包2段以上": Severity.MEDIUM,
        },
    ),
    Specialist(
        id="CG-002",
        name="認知チャンク分析者",
        category="cognitive",
        archetype=Archetype.PRECISION,
        domain="情報チャンキング",
        principle="1行に5演算は認知の限界を超える — 分割せよ",
        perceives=[
            "1行に演算子が5つ以上",
            "1行に関数呼び出しが4つ以上（チェーン含む）",
            "1行が100文字を超えて論理的に分割可能",
            "複雑な条件式（and/or が3つ以上連続）",
        ],
        blind_to=[
            "簡潔さの利点",
            "Pythonic イディオム",
        ],
        measure="1行は1-2チャンク（演算3つ以内）",
        verdict=VerdictFormat.REFACTOR,
        severity_map={
            "5演算以上": Severity.MEDIUM,
            "4関数呼び出し": Severity.MEDIUM,
            "複雑条件": Severity.LOW,
        },
    ),
]


# ============ Tier 1: 構造的美学 (3人) ============

AESTHETICS_TIER1 = [
    Specialist(
        id="AE-012",
        name="視覚リズムの指揮者",
        category="aesthetics",
        archetype=Archetype.CREATIVE,
        domain="コード全体の視覚的リズム",
        principle="コードは音楽 — リズムは視覚に宿る",
        perceives=[
            "密度の偏り（100行連続でコメントなし）",
            "インデントの波形の乱れ（急激な深浅変化）",
            "視覚的な重心の偏り（右側に寄りすぎ）",
            "関数サイズの不均一（10行と200行が混在）",
        ],
        blind_to=[
            "コードの機能",
            "パフォーマンス",
        ],
        measure="スクロール時に視覚的なリズムが感じられる",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "密度偏り": Severity.LOW,
            "波形乱れ": Severity.LOW,
            "サイズ不均一": Severity.MEDIUM,
        },
    ),
    Specialist(
        id="AE-013",
        name="シンプリシティの門番",
        category="aesthetics",
        archetype=Archetype.CREATIVE,
        domain="不要な複雑さの排除",
        principle="削るものがなくなった時に完成する — YAGNI",
        perceives=[
            "使われていない import",
            "使われていない変数/関数/クラス",
            "不要なネスト（early return で解消可能）",
            "過剰な抽象化（1メソッドのためのクラス）",
            "将来のための過剰設計（コメントに「将来使う」）",
        ],
        blind_to=[
            "将来の拡張性",
            "他モジュールからの依存",
        ],
        measure="YAGNI原則に従い、不要なものがない",
        verdict=VerdictFormat.REFACTOR,
        severity_map={
            "未使用import": Severity.LOW,
            "未使用コード": Severity.MEDIUM,
            "過剰抽象化": Severity.MEDIUM,
            "過剰設計": Severity.LOW,
        },
    ),
    Specialist(
        id="AE-014",
        name="比喩一貫性の詩人",
        category="aesthetics",
        archetype=Archetype.CREATIVE,
        domain="命名における比喩の統一",
        principle="一つのドメインには一つの比喩世界 — 混ぜるな危険",
        perceives=[
            "同一モジュール内で異なる比喩体系（工場と庭園が混在）",
            "関連クラス間で命名規則の不統一",
            "動詞の活用不統一（get/fetch/retrieve が混在）",
            "抽象度の不統一（Manager と helper が同列）",
        ],
        blind_to=[
            "命名の正確性",
            "ドメイン知識",
        ],
        measure="モジュール内で比喩体系が統一されている",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "比喩混在": Severity.MEDIUM,
            "命名規則不統一": Severity.LOW,
            "動詞不統一": Severity.LOW,
        },
    ),
]


# ============ Tier 1: Hegemonikón 体系整合 (2人) ============

HEGEMONIKON_INTEGRITY_TIER1 = [
    Specialist(
        id="HG-007",
        name="公理座標整合検査官",
        category="hegemonikon",
        archetype=Archetype.PRECISION,
        domain="公理座標とコンテンツの整合",
        principle="coordinates: [A, E] と書いて中身が S なら体系が壊れる",
        perceives=[
            "WF/SKILL の coordinates: フィールドと実際の内容の矛盾",
            "trigonon の series/type 宣言と内容の不一致",
            "bridge: で宣言された Series への遷移が本文に存在しない",
            "cognitive_algebra: の演算子定義と実際の挙動の乖離",
        ],
        blind_to=[
            "コンテンツの品質",
            "ワークフローの有効性",
        ],
        measure="全 WF/SKILL のメタデータと内容が矛盾なく整合",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "coordinates矛盾": Severity.HIGH,
            "trigonon不一致": Severity.HIGH,
            "bridge欠落": Severity.MEDIUM,
            "algebra乖離": Severity.LOW,
        },
    ),
    Specialist(
        id="HG-009",
        name="Dendron×PROOF一致検査官",
        category="hegemonikon",
        archetype=Archetype.PRECISION,
        domain="二重存在証明の一致",
        principle="PROOF行と Dendron Purpose が矛盾したら、どちらが嘘をついている？",
        perceives=[
            "PROOF行の [L*/カテゴリ] と Dendron の surface.purpose の不一致",
            "PROOF行の定理参照と Dendron の theorem_refs の不一致",
            "PROOF行は存在するが Dendron 登録がない (逆も)",
            "PROOF行のパスと実際のファイルパスの不一致",
        ],
        blind_to=[
            "コードの機能",
            "Dendron の technical fields",
        ],
        measure="PROOF行と Dendron Purpose が完全一致",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "Purpose矛盾": Severity.HIGH,
            "定理参照不一致": Severity.MEDIUM,
            "登録漏れ": Severity.MEDIUM,
            "パス不一致": Severity.LOW,
        },
    ),
]


# ============ Tier 1: クロスファイル依存 (2人) ============

CROSSFILE_TIER1 = [
    Specialist(
        id="CF-001",
        name="インポートグラフ監査官",
        category="crossfile",
        archetype=Archetype.PRECISION,
        domain="インポート依存グラフの整合性",
        principle="循環は癌、孤立は壊疽 — グラフ全体の健康を見よ",
        perceives=[
            "循環インポートチェーン (A→B→C→A)",
            "__init__.py の re-export リストと実際のモジュールの不一致",
            "存在しないモジュールパスへの参照 (移動/リネーム後の残骸)",
            "import されているが一度も使われていないモジュール間の接続",
        ],
        blind_to=[
            "個々の関数の品質",
            "インポートの順序/スタイル",
        ],
        measure="インポートグラフが DAG (非循環有向グラフ) であること",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "循環インポート": Severity.CRITICAL,
            "re-export不一致": Severity.HIGH,
            "存在しない参照": Severity.HIGH,
            "未使用接続": Severity.LOW,
        },
    ),
    Specialist(
        id="CF-002",
        name="暗黙契約違反検出者",
        category="crossfile",
        archetype=Archetype.SAFETY,
        domain="ファイル間の暗黙の契約",
        principle="File A が File B の内部構造を仮定している — その仮定は今も正しいか？",
        perceives=[
            "関数シグネチャ変更だが呼び出し側が未更新 (引数追加/削除)",
            "dataclass フィールド追加/変更だが利用側が対応していない",
            "Enum 値の追加だが match/if 分岐が網羅していない",
            "定数/設定値の変更だが参照側が旧値を前提にしている",
        ],
        blind_to=[
            "変更の意図",
            "テストの有無",
        ],
        measure="API変更が全ての利用箇所に波及していること",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "シグネチャ不一致": Severity.CRITICAL,
            "フィールド未対応": Severity.HIGH,
            "Enum非網羅": Severity.HIGH,
            "定数旧値参照": Severity.MEDIUM,
        },
    ),
]


# ============ Tier 1: 進化方向 (2人) ============

EVOLUTION_TIER1 = [
    Specialist(
        id="EV-001",
        name="Series適所配置検査官",
        category="evolution",
        archetype=Archetype.CREATIVE,
        domain="コードの居場所と責務の一致",
        principle="mekhane/anamnesis に S-series のコードがあるなら、それは家出している",
        perceives=[
            "ディレクトリの Series 意味とファイルの実際の責務の不一致",
            "mekhane/fep に UI/表示ロジックがある (本来 ergasterion)",
            "mekhane/symploke に知識管理ロジックがある (本来 anamnesis)",
            "scripts/ に本来 mekhane/ に属するべきビジネスロジックがある",
        ],
        blind_to=[
            "コードの品質",
            "リファクタリングコスト",
        ],
        measure="全ファイルがディレクトリの Series 意味に整合した責務を持つ",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "Series不一致": Severity.MEDIUM,
            "責務の越境": Severity.MEDIUM,
            "ロジック配置違反": Severity.LOW,
        },
    ),
    Specialist(
        id="EV-002",
        name="定理カバレッジ分析者",
        category="evolution",
        archetype=Archetype.CREATIVE,
        domain="24定理の実装カバレッジ",
        principle="体系の白い部分を見つける — 実装されていない定理は進化の余地",
        perceives=[
            "PROOF行の定理分布の偏り (特定定理に集中、他が空白)",
            "24定理のうちコード/WF/SKILLがカバーしていない定理",
            "1つの定理に過密するファイル群 (分割の必要性)",
            "X-series (関係) が宣言されているが実装されていない",
        ],
        blind_to=[
            "個々のファイルの品質",
            "コードの正しさ",
        ],
        measure="24定理が均等にカバーされ、X-series 関係が実装されている",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "定理未カバー": Severity.LOW,
            "過密定理": Severity.LOW,
            "X-series未実装": Severity.LOW,
        },
    ),
]


# ============ Tier 1: LLM生成パターン (1人) ============

LLM_PATTERN_TIER1 = [
    Specialist(
        id="LM-001",
        name="LLM臭気検出者",
        category="llm_pattern",
        archetype=Archetype.SAFETY,
        domain="LLM生成コードの統合的判断",
        principle="個々は問題なくても、5つの兆候が共存すればそのファイルは人間の目を通っていない",
        perceives=[
            "明白なことを説明する docstring ('Returns the sum of a and b')",
            "Happy path のみのロジック (異常系/エッジケースがゼロ)",
            "コピペ変異体 (構造が同じで変数名だけ違う関数群)",
            "教科書的すぎるパターン適用 (不要な Factory/Strategy/Observer)",
            "関数内のスタイル不統一 (複数ソース融合の痕跡)",
        ],
        blind_to=[
            "LLM生成自体の善悪",
            "コードの動作の正しさ",
        ],
        measure="ファイル全体のLLM臭気スコアが閾値以下、人間レビュー済みの証跡あり",
        verdict=VerdictFormat.REVIEW,
        severity_map={
            "高臭気スコア": Severity.MEDIUM,
            "レビュー証跡なし": Severity.LOW,
            "コピペ変異体": Severity.MEDIUM,
        },
    ),
]


# ============ Export ============

TIER1_SPECIALISTS = (
    HEGEMONIKON_TIER1
    + HEGEMONIKON_INTEGRITY_TIER1
    + AI_TIER1
    + COGNITIVE_TIER1
    + AESTHETICS_TIER1
    + CROSSFILE_TIER1
    + EVOLUTION_TIER1
    + LLM_PATTERN_TIER1
)


def get_tier1_by_category(category: str) -> list[Specialist]:
    """カテゴリ別に Tier 1 専門家を取得"""
    return [s for s in TIER1_SPECIALISTS if s.category == category]


def get_tier1_categories() -> list[str]:
    """Tier 1 に含まれるカテゴリ一覧を取得"""
    return list(set(s.category for s in TIER1_SPECIALISTS))


# ============ Summary ============

if __name__ == "__main__":
    print("=" * 60)
    print("Tier 1 進化専門家 — Hegemonikón の進化に直接寄与")
    print("=" * 60)
    
    categories = {}
    for spec in TIER1_SPECIALISTS:
        if spec.category not in categories:
            categories[spec.category] = []
        categories[spec.category].append(spec)
    
    for cat, specs in categories.items():
        print(f"\n[{cat}] ({len(specs)}人)")
        for s in specs:
            print(f"  {s.id}: {s.name} ({s.archetype.value})")
    
    print(f"\n総計: {len(TIER1_SPECIALISTS)}人")
