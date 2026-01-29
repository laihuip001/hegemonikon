"""
O-Series & S-Series Derivative Selector for Hegemonikón Active Inference

Selects the optimal derivative workflow based on problem context analysis.

O-series (Pure Theorems - Ousia) - 12 derivatives:
- O1 Noēsis: nous (intuition), phro (practical), meta (reflection)
- O2 Boulēsis: desir (desire), voli (volition), akra (akrasia)
- O3 Zētēsis: anom (anomaly), hypo (hypothesis), eval (evaluation)
- O4 Energeia: flow (optimal), prax (praxis), pois (poiesis)

S-series (Strategic Theorems - Schema) - 12 derivatives:
- S1 Metron: cont (continuous), disc (discrete), abst (abstraction)
- S2 Mekhanē: comp (composition), inve (invention), adap (adaptation)
- S3 Stathmos: norm (normative), empi (empirical), rela (relative)
- S4 Praxis: prax (praxis), pois (poiesis), temp (temporal)

References:
- O-Series派生ワークフロー発見 報告書 v1.0/v2.0
- S-Series派生概念体系化レポート v1.0
- Stoic-FEP Correspondence
"""


from dataclasses import dataclass
from typing import Literal, List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path
import re
import os
import json
import logging
import yaml

# -----------------------------------------------------------------------------
# LLM Fallback Configuration (v3.1 新規)
# -----------------------------------------------------------------------------
GEMINI_AVAILABLE = False
GEMINI_CLIENT = None
LLM_FALLBACK_ENABLED = True  # Set to False to disable LLM fallback
LLM_FALLBACK_THRESHOLD = 0.55  # Keyword confidence below this triggers LLM
LLM_DERIVATIVE_MODEL = "gemini-2.0-flash-lite"  # Free tier model

# -----------------------------------------------------------------------------
# Selection Logging Configuration (v3.2 新規 - 学習基盤)
# -----------------------------------------------------------------------------
SELECTION_LOG_ENABLED = True
SELECTION_LOG_PATH = Path("/home/laihuip001/oikos/mneme/.hegemonikon/derivative_selections.yaml")

logger = logging.getLogger(__name__)

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
    if api_key:
        GEMINI_CLIENT = genai.Client(api_key=api_key)
        GEMINI_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Derivative State Spaces
# =============================================================================

class DerivativeStateSpace:
    """State spaces for derivative selection across O-series theorems."""
    
    # O1 Noēsis: Recognition/Understanding derivatives
    O1_STATES: List[str] = [
        "abstract_problem",     # 抽象的問題 → nous
        "practical_situation",  # 実践的状況 → phro  
        "need_reflection",      # 反省が必要 → meta
    ]
    
    O1_DERIVATIVES: List[str] = ["nous", "phro", "meta"]
    O1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "abstract_problem": "nous",
        "practical_situation": "phro",
        "need_reflection": "meta",
    }
    
    # O2 Boulēsis: Will/Desire derivatives
    O2_STATES: List[str] = [
        "raw_desire",           # 生の欲動 → desir
        "conflict_resolution",  # 葛藤解決 → voli
        "will_action_gap",      # 意志-行為乖離 → akra
    ]
    
    O2_DERIVATIVES: List[str] = ["desir", "voli", "akra"]
    O2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "raw_desire": "desir",
        "conflict_resolution": "voli",
        "will_action_gap": "akra",
    }
    
    # O3 Zētēsis: Inquiry/Search derivatives
    O3_STATES: List[str] = [
        "anomaly_detected",     # 異常検出 → anom
        "hypothesis_needed",    # 仮説が必要 → hypo
        "evaluation_phase",     # 評価段階 → eval
    ]
    
    O3_DERIVATIVES: List[str] = ["anom", "hypo", "eval"]
    O3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "anomaly_detected": "anom",
        "hypothesis_needed": "hypo",
        "evaluation_phase": "eval",
    }
    
    # O4 Energeia: Activity/Actualization derivatives
    O4_STATES: List[str] = [
        "optimal_engagement",   # 最適没入 → flow
        "self_sufficient_act",  # 自己目的的行為 → prax
        "production_goal",      # 産出目標 → pois
    ]
    
    O4_DERIVATIVES: List[str] = ["flow", "prax", "pois"]
    O4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "optimal_engagement": "flow",
        "self_sufficient_act": "prax",
        "production_goal": "pois",
    }
    
    # =========================================================================
    # S-Series State Spaces (Schema / Strategic Theorems)
    # =========================================================================
    
    # S1 Metron: Scale/Measure derivatives
    S1_STATES: List[str] = [
        "continuous_measure",    # 連続量 → cont
        "discrete_measure",      # 離散量 → disc
        "abstraction_level",     # 抽象度 → abst
    ]
    
    S1_DERIVATIVES: List[str] = ["cont", "disc", "abst"]
    S1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "continuous_measure": "cont",
        "discrete_measure": "disc",
        "abstraction_level": "abst",
    }
    
    # S2 Mekhanē: Method/Tool derivatives
    S2_STATES: List[str] = [
        "assemble_existing",     # 既存組立 → comp
        "create_new",            # 新規創出 → inve
        "adapt_existing",        # 既存適応 → adap
    ]
    
    S2_DERIVATIVES: List[str] = ["comp", "inve", "adap"]
    S2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "assemble_existing": "comp",
        "create_new": "inve",
        "adapt_existing": "adap",
    }
    
    # S3 Stathmos: Criteria/Standard derivatives
    S3_STATES: List[str] = [
        "ideal_based",           # 理想基準 → norm
        "data_based",            # 経験基準 → empi
        "comparison_based",      # 相対基準 → rela
    ]
    
    S3_DERIVATIVES: List[str] = ["norm", "empi", "rela"]
    S3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "ideal_based": "norm",
        "data_based": "empi",
        "comparison_based": "rela",
    }
    
    # S4 Praxis: Practice/Execution derivatives
    S4_STATES: List[str] = [
        "self_purpose_action",   # 内在目的 → prax
        "external_production",   # 外的産出 → pois
        "temporal_execution",    # 時間構造 → temp
    ]
    
    S4_DERIVATIVES: List[str] = ["prax", "pois", "temp"]
    S4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "self_purpose_action": "prax",
        "external_production": "pois",
        "temporal_execution": "temp",
    }
    
    # =========================================================================
    # H-Series State Spaces (Hormē / Impulse Theorems)
    # =========================================================================
    
    # H1 Propatheia: Pre-affective response derivatives
    H1_STATES: List[str] = [
        "approach_response",     # 接近反応 → appr
        "avoidance_response",    # 回避反応 → avoi
        "arrest_response",       # 保留反応 → arre
    ]
    
    H1_DERIVATIVES: List[str] = ["appr", "avoi", "arre"]
    H1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "approach_response": "appr",
        "avoidance_response": "avoi",
        "arrest_response": "arre",
    }
    
    # H2 Pistis: Confidence level derivatives
    H2_STATES: List[str] = [
        "subjective_confidence",    # 主観的確信 → subj
        "intersubjective_conf",     # 間主観的確信 → inte
        "objective_evidence",       # 客観的証拠 → obje
    ]
    
    H2_DERIVATIVES: List[str] = ["subj", "inte", "obje"]
    H2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "subjective_confidence": "subj",
        "intersubjective_conf": "inte",
        "objective_evidence": "obje",
    }
    
    # H3 Orexis: Desire orientation derivatives
    H3_STATES: List[str] = [
        "target_oriented",       # 対象志向 → targ
        "activity_oriented",     # 活動志向 → acti
        "state_oriented",        # 状態志向 → stat
    ]
    
    H3_DERIVATIVES: List[str] = ["targ", "acti", "stat"]
    H3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "target_oriented": "targ",
        "activity_oriented": "acti",
        "state_oriented": "stat",
    }
    
    # H4 Doxa: Belief representation derivatives
    H4_STATES: List[str] = [
        "sensory_belief",        # 感覚的信念 → sens
        "conceptual_belief",     # 概念的信念 → conc
        "formal_belief",         # 形式的信念 → form
    ]
    
    H4_DERIVATIVES: List[str] = ["sens", "conc", "form"]
    H4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "sensory_belief": "sens",
        "conceptual_belief": "conc",
        "formal_belief": "form",
    }
    
    # =========================================================================
    # P-Series State Spaces (Perigraphē / Environment Theorems)
    # =========================================================================
    
    # P1 Khōra: Spatial structure derivatives
    P1_STATES: List[str] = [
        "physical_space",        # 物理的空間 → phys
        "conceptual_space",      # 概念的空間 → conc
        "relational_space",      # 関係的空間 → rela
    ]
    
    P1_DERIVATIVES: List[str] = ["phys", "conc", "rela"]
    P1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "physical_space": "phys",
        "conceptual_space": "conc",
        "relational_space": "rela",
    }
    
    # P2 Hodos: Path topology derivatives
    P2_STATES: List[str] = [
        "linear_path",           # 線形経路 → line
        "branching_path",        # 分岐経路 → bran
        "cyclical_path",         # 循環経路 → cycl
    ]
    
    P2_DERIVATIVES: List[str] = ["line", "bran", "cycl"]
    P2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "linear_path": "line",
        "branching_path": "bran",
        "cyclical_path": "cycl",
    }
    
    # P3 Trokhia: Attractor stability derivatives
    P3_STATES: List[str] = [
        "fixed_attractor",       # 固定パターン → fixe
        "adaptive_attractor",    # 適応パターン → adap
        "emergent_attractor",    # 創発パターン → emer
    ]
    
    P3_DERIVATIVES: List[str] = ["fixe", "adap", "emer"]
    P3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "fixed_attractor": "fixe",
        "adaptive_attractor": "adap",
        "emergent_attractor": "emer",
    }
    
    # P4 Tekhnē: Technical operation derivatives
    P4_STATES: List[str] = [
        "manual_operation",      # 手動操作 → manu
        "mechanical_operation",  # 機械操作 → mech
        "automated_operation",   # 自動操作 → auto
    ]
    
    P4_DERIVATIVES: List[str] = ["manu", "mech", "auto"]
    P4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "manual_operation": "manu",
        "mechanical_operation": "mech",
        "automated_operation": "auto",
    }
    
    # =========================================================================
    # K-Series State Spaces (Kairos / Context Theorems)
    # =========================================================================
    
    # K1 Eukairia: Temporal opportunity derivatives
    K1_STATES: List[str] = [
        "urgent_opportunity",    # 緊急機会 → urge
        "optimal_opportunity",   # 最適機会 → opti
        "missed_opportunity",    # 逸失機会 → miss
    ]
    
    K1_DERIVATIVES: List[str] = ["urge", "opti", "miss"]
    K1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "urgent_opportunity": "urge",
        "optimal_opportunity": "opti",
        "missed_opportunity": "miss",
    }
    
    # K2 Chronos: Temporal horizon derivatives
    K2_STATES: List[str] = [
        "short_term",            # 短期 → shor
        "medium_term",           # 中期 → medi
        "long_term",             # 長期 → long
    ]
    
    K2_DERIVATIVES: List[str] = ["shor", "medi", "long"]
    K2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "short_term": "shor",
        "medium_term": "medi",
        "long_term": "long",
    }
    
    # K3 Telos: Goal hierarchy derivatives
    K3_STATES: List[str] = [
        "intrinsic_goal",        # 内在目的 → intr
        "instrumental_goal",     # 手段目的 → inst
        "ultimate_goal",         # 究極目的 → ulti
    ]
    
    K3_DERIVATIVES: List[str] = ["intr", "inst", "ulti"]
    K3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "intrinsic_goal": "intr",
        "instrumental_goal": "inst",
        "ultimate_goal": "ulti",
    }
    
    # K4 Sophia: Knowledge representation derivatives
    K4_STATES: List[str] = [
        "tacit_knowledge",       # 暗黙知 → taci
        "explicit_knowledge",    # 明示知 → expl
        "meta_knowledge",        # メタ知 → meta
    ]
    
    K4_DERIVATIVES: List[str] = ["taci", "expl", "meta"]
    K4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "tacit_knowledge": "taci",
        "explicit_knowledge": "expl",
        "meta_knowledge": "meta",
    }
    
    # =========================================================================
    # A-Series State Spaces (Akribeia / Precision Theorems)
    # =========================================================================
    
    # A1 Pathos: Emotion appraisal derivatives
    A1_STATES: List[str] = [
        "primary_emotion",       # 一次感情 → prim
        "secondary_emotion",     # 二次感情 → seco
        "regulated_emotion",     # 調整感情 → regu
    ]
    
    A1_DERIVATIVES: List[str] = ["prim", "seco", "regu"]
    A1_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "primary_emotion": "prim",
        "secondary_emotion": "seco",
        "regulated_emotion": "regu",
    }
    
    # A2 Krisis: Judgment criteria derivatives
    A2_STATES: List[str] = [
        "affirm_judgment",       # 肯定判定 → affi
        "negate_judgment",       # 否定判定 → nega
        "suspend_judgment",      # 保留判定 → susp
    ]
    
    A2_DERIVATIVES: List[str] = ["affi", "nega", "susp"]
    A2_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "affirm_judgment": "affi",
        "negate_judgment": "nega",
        "suspend_judgment": "susp",
    }
    
    # A3 Gnōmē: Wisdom level derivatives
    A3_STATES: List[str] = [
        "concrete_wisdom",       # 具体的知恵 → conc
        "abstract_wisdom",       # 抽象的知恵 → abst
        "universal_wisdom",      # 普遍的知恵 → univ
    ]
    
    A3_DERIVATIVES: List[str] = ["conc", "abst", "univ"]
    A3_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "concrete_wisdom": "conc",
        "abstract_wisdom": "abst",
        "universal_wisdom": "univ",
    }
    
    # A4 Epistēmē: Knowledge confidence derivatives
    A4_STATES: List[str] = [
        "tentative_knowledge",   # 暫定知識 → tent
        "justified_knowledge",   # 正当化知識 → just
        "certain_knowledge",     # 確実知識 → cert
    ]
    
    A4_DERIVATIVES: List[str] = ["tent", "just", "cert"]
    A4_STATE_TO_DERIVATIVE: Dict[str, str] = {
        "tentative_knowledge": "tent",
        "justified_knowledge": "just",
        "certain_knowledge": "cert",
    }

# =============================================================================
# Keyword Patterns for Derivative Selection
# =============================================================================

# O1 Noēsis derivative patterns
O1_PATTERNS: Dict[str, List[str]] = {
    "nous": [
        r"(本質|原理|根本|普遍|概念|定義|真理)",
        r"(essence|principle|fundamental|universal|definition)",
        r"(抽象|理論|形而上|哲学)",
        r"(abstract|theoretical|philosophical)",
        r"(なぜ|why|根源|origin)",
    ],
    "phro": [
        r"(具体|実際|現場|状況|ケース|事例)",
        r"(practical|concrete|specific|situation|case)",
        r"(この場合|今回|特定の|においては)",
        r"(in this case|for this|specifically)",
        r"(適用|判断|決定|どうすべき)",
        r"(apply|judge|decide|should)",
    ],
    "meta": [
        r"(確かか|信頼|再考|見直し|本当に|疑問)",
        r"(certain|trust|reconsider|review|really|doubt)",
        r"(自己|反省|振り返り|メタ)",
        r"(self|reflect|introspect|meta)",
        r"(どう思う|どうですか|意見)",
        r"(what do you think|opinion)",
    ],
}

# O2 Boulēsis derivative patterns
O2_PATTERNS: Dict[str, List[str]] = {
    "desir": [
        r"(したい|欲しい|望む|願う)",
        r"(want|desire|wish|hope)",
        r"(理想|夢|目標|ゴール)",
        r"(ideal|dream|goal)",
        r"(第一に|まず|本能的)",
    ],
    "voli": [
        r"(したいけど|迷い|葛藤|両立|どちらか)",
        r"(want.*but|conflicted|dilemma|either|or)",
        r"(優先|選ぶ|取捨|決断)",
        r"(prioritize|choose|select|decide)",
        r"(統合|調整|バランス)",
        r"(integrate|balance|harmonize)",
    ],
    "akra": [
        r"(できない|やれない|わかっているのに)",
        r"(can't|unable|know.*but)",
        r"(意志が弱い|継続できない|挫折)",
        r"(weak will|procrastin|give up)",
        r"(実行に移せない|先延ばし)",
        r"(can't execute|postpone|delay)",
    ],
}

# O3 Zētēsis derivative patterns
O3_PATTERNS: Dict[str, List[str]] = {
    "anom": [
        r"(不思議|なぜ|おかしい|予想外|違和感)",
        r"(strange|why|weird|unexpected|odd)",
        r"(異常|例外|想定外|驚き)",
        r"(anomaly|exception|surpris)",
        r"(気になる|引っかかる)",
    ],
    "hypo": [
        r"(仮説|もしかして|考えられる|推測|可能性)",
        r"(hypothesis|maybe|perhaps|possibly)",
        r"(〜かもしれない|〜ではないか)",
        r"(might be|could be|what if)",
        r"(アイデア|発想|推理)",
        r"(idea|notion|inference)",
    ],
    "eval": [
        r"(どれが|比較|優先|選ぶ|判断)",
        r"(which|compare|priorit|choose|judge)",
        r"(評価|検証|テスト|妥当性)",
        r"(evaluat|verify|test|valid)",
        r"(ベスト|最適|ランク)",
        r"(best|optimal|rank)",
    ],
}

# O4 Energeia derivative patterns
O4_PATTERNS: Dict[str, List[str]] = {
    "flow": [
        r"(没入|集中|zone|最適|楽しい)",
        r"(immerse|focus|flow|optimal|enjoy)",
        r"(時間を忘れ|夢中|熱中)",
        r"(lose track|engrossed|absorbed)",
        r"(パフォーマンス|生産性|効率)",
    ],
    "prax": [
        r"(それ自体|意味|価値|本質的|内発)",
        r"(intrinsic|meaning|value|essential|internal)",
        r"(目的ではなく手段|過程|journey)",
        r"(not the goal|process|means)",
        r"(実践|行い|生き方)",
        r"(practice|way of|living)",
    ],
    "pois": [
        r"(作る|成果|アウトプット|製品|完成)",
        r"(make|create|output|product|finish)",
        r"(納品|リリース|デリバリー)",
        r"(deliver|release|ship)",
        r"(形にする|具現化|実現)",
        r"(materialize|realize|implement)",
    ],
}


# =============================================================================
# S-series Keyword Patterns
# =============================================================================

# S1 Metron derivative patterns
S1_PATTERNS: Dict[str, List[str]] = {
    "cont": [
        r"(時間|空間|面積|距離|連続)",
        r"(time|space|area|distance|continuous)",
        r"(流れ|期間|長さ)",
        r"(flow|duration|length)",
        r"(グラデーション|スペクトラム)",
    ],
    "disc": [
        r"(数|個数|回数|カウント|件数)",
        r"(count|number|quantity|discrete)",
        r"(何個|何回|いくつ)",
        r"(how many|unit|instance)",
        r"(ステップ|段階|フェーズ)",
    ],
    "abst": [
        r"(抽象|概念|モデル|粒度|レベル)",
        r"(abstract|concept|model|granularity|level)",
        r"(詳細|全体|俯瞰|ズーム)",
        r"(detail|overview|zoom|macro|micro)",
        r"(どのレベルで|どの粒度)",
    ],
}

# S2 Mekhanē derivative patterns
S2_PATTERNS: Dict[str, List[str]] = {
    "comp": [
        r"(組み合わせ|組み立て|統合|合成)",
        r"(combine|assemble|integrate|compose)",
        r"(既存の.*使う|ライブラリ|パッケージ)",
        r"(existing|library|package|reuse)",
        r"(寄せ集め|つなげる)",
    ],
    "inve": [
        r"(新しい|創出|発明|ゼロから|一から)",
        r"(new|create|invent|from scratch)",
        r"(前例がない|初めて|独自)",
        r"(novel|original|unique|innovative)",
        r"(作り出す|生み出す)",
    ],
    "adap": [
        r"(変更|修正|カスタマイズ|調整)",
        r"(modify|customize|adapt|adjust)",
        r"(既存を.*変え|フォーク|派生)",
        r"(fork|derive|tailor|tweak)",
        r"(状況に合わせ|最適化)",
    ],
}

# S3 Stathmos derivative patterns
S3_PATTERNS: Dict[str, List[str]] = {
    "norm": [
        r"(理想|あるべき|原則|規範)",
        r"(ideal|should be|principle|norm)",
        r"(ベストプラクティス|標準|基準)",
        r"(best practice|standard|criterion)",
        r"(正しい|正解|理論上)",
    ],
    "empi": [
        r"(データ|実績|測定|ベンチマーク)",
        r"(data|performance|measure|benchmark)",
        r"(過去の|実際の|経験的)",
        r"(historical|actual|empirical)",
        r"(KPI|メトリクス|スコア)",
    ],
    "rela": [
        r"(比較|競合|他と|相対)",
        r"(compare|competitor|versus|relative)",
        r"(ランキング|順位|対抗)",
        r"(ranking|position|against)",
        r"(良い悪い|上下|差)",
    ],
}

# S4 Praxis derivative patterns
S4_PATTERNS: Dict[str, List[str]] = {
    "prax": [
        r"(それ自体|内発|自己目的|意味ある)",
        r"(intrinsic|self-purpose|meaningful)",
        r"(過程が大事|結果より)",
        r"(process|journey|experience)",
        r"(実践|行為|生き方)",
    ],
    "pois": [
        r"(成果物|アウトプット|製品|納品)",
        r"(output|product|deliverable)",
        r"(完成|リリース|提出)",
        r"(finish|release|submit)",
        r"(作る|形にする)",
    ],
    "temp": [
        r"(順番|並行|繰り返し|反復)",
        r"(sequential|parallel|iterative)",
        r"(アジャイル|ウォーターフォール|スプリント)",
        r"(agile|waterfall|sprint)",
        r"(いつ|スケジュール|タイミング)",
    ],
}


# =============================================================================
# H-series Keyword Patterns (Hormē / Impulse)
# =============================================================================

# H1 Propatheia derivative patterns
H1_PATTERNS: Dict[str, List[str]] = {
    "appr": [
        r"(惹かれる|興味|ポジティブ|好き|魅力)",
        r"(attract|interest|positive|like|appeal)",
        r"(やってみたい|近づきたい|触れたい)",
        r"(approach|explore|engage)",
        r"(わくわく|楽しみ|期待)",
    ],
    "avoi": [
        r"(嫌|避けたい|ネガティブ|危険|恐い)",
        r"(dislike|avoid|negative|danger|fear)",
        r"(離れたい|逃げたい|拒否)",
        r"(retreat|escape|reject)",
        r"(不安|心配|警戒)",
    ],
    "arre": [
        r"(待って|保留|判断停止|様子見)",
        r"(wait|hold|pause|suspend)",
        r"(まだ決めない|考え中|どちらとも)",
        r"(undecided|pending|neutral)",
        r"(epochē|停止|中断)",
    ],
}

# H2 Pistis derivative patterns
H2_PATTERNS: Dict[str, List[str]] = {
    "subj": [
        r"(感じる|思う|直感|個人的|私は)",
        r"(feel|think|intuition|personal|subjective)",
        r"(なんとなく|気がする|印象)",
        r"(sense|impression|gut)",
        r"(経験上|体感|主観)",
    ],
    "inte": [
        r"(みんな|合意|共有|チーム|議論)",
        r"(everyone|consensus|shared|team|discuss)",
        r"(一般的に|普通は|常識)",
        r"(generally|usually|common)",
        r"(レビュー|承認|同意)",
    ],
    "obje": [
        r"(データ|証拠|測定|実験|検証)",
        r"(data|evidence|measure|experiment|verify)",
        r"(事実|論文|研究|統計)",
        r"(fact|paper|research|statistics)",
        r"(客観的|科学的|実証)",
    ],
}

# H3 Orexis derivative patterns
H3_PATTERNS: Dict[str, List[str]] = {
    "targ": [
        r"(〜が欲しい|〜を得たい|対象|目標物)",
        r"(want.*object|get.*thing|target|goal)",
        r"(取得|獲得|入手)",
        r"(acquire|obtain|achieve)",
        r"(特定の|これが|あれを)",
    ],
    "acti": [
        r"(〜すること自体|プロセス|行為|活動)",
        r"(doing.*itself|process|activity|action)",
        r"(楽しむ|体験|経験)",
        r"(enjoy|experience|engage)",
        r"(やりがい|成長|学び)",
    ],
    "stat": [
        r"(〜な状態|維持|達成|安定)",
        r"(state|maintain|achieve|stable)",
        r"(平和|健康|幸福|バランス)",
        r"(peace|health|happy|balance)",
        r"(ホメオスタシス|均衡|調和)",
    ],
}

# H4 Doxa derivative patterns
H4_PATTERNS: Dict[str, List[str]] = {
    "sens": [
        r"(見た|聞いた|感じた|知覚|体験)",
        r"(saw|heard|felt|perceive|experience)",
        r"(パターン|直感的|すぐわかる)",
        r"(pattern|intuitive|obvious)",
        r"(System 1|implicit|暗黙)",
    ],
    "conc": [
        r"(概念|カテゴリ|分類|意味|定義)",
        r"(concept|category|classify|meaning|define)",
        r"(〜とは|という|種類|タイプ)",
        r"(semantic|type|kind)",
        r"(理解|解釈|枠組み)",
    ],
    "form": [
        r"(論理|規則|法則|形式|証明)",
        r"(logic|rule|law|formal|proof)",
        r"(〜ならば|必然|演繹)",
        r"(if.*then|necessary|deduce)",
        r"(System 2|explicit|明示)",
    ],
}


# =============================================================================
# P-series Keyword Patterns (Perigraphē / Environment)
# =============================================================================

# P1 Khōra derivative patterns
P1_PATTERNS: Dict[str, List[str]] = {
    "phys": [
        r"(物理|地理|場所|位置|空間)",
        r"(physical|geography|location|position|space)",
        r"(ここ|あそこ|どこで|建物|部屋)",
        r"(where|building|room|territory)",
        r"(実際の|現実の|リアル)",
    ],
    "conc": [
        r"(概念|抽象|モデル|図|設計)",
        r"(concept|abstract|model|diagram|design)",
        r"(計画|マップ|構造|スキーマ)",
        r"(plan|map|structure|schema)",
        r"(メンタルモデル|考え方)",
    ],
    "rela": [
        r"(関係|ネットワーク|つながり|コミュニティ)",
        r"(relation|network|connection|community)",
        r"(象徴|意味|文化|社会)",
        r"(symbol|meaning|culture|social)",
        r"(人々|グループ|チーム)",
    ],
}

# P2 Hodos derivative patterns
P2_PATTERNS: Dict[str, List[str]] = {
    "line": [
        r"(順番に|一つずつ|ステップバイステップ|直線)",
        r"(sequential|step-by-step|linear|straight)",
        r"(最初から最後|一方向|フロー)",
        r"(start to end|one-way|flow)",
        r"(ウォーターフォール|順次)",
    ],
    "bran": [
        r"(分岐|選択肢|条件分岐|if-then)",
        r"(branch|choice|conditional|decision)",
        r"(AかBか|どちらか|オプション)",
        r"(either|option|alternative)",
        r"(決定木|判断|複数経路)",
    ],
    "cycl": [
        r"(繰り返し|ループ|サイクル|反復)",
        r"(loop|cycle|iterate|repeat)",
        r"(フィードバック|アジャイル|スプリント)",
        r"(feedback|agile|sprint)",
        r"(何度も|継続的|回す)",
    ],
}

# P3 Trokhia derivative patterns
P3_PATTERNS: Dict[str, List[str]] = {
    "fixe": [
        r"(固定|安定|一定|変わらない)",
        r"(fixed|stable|constant|unchanged)",
        r"(いつも同じ|毎回|ルーティン)",
        r"(always|routine|regular)",
        r"(均衡|定常|ホメオスタシス)",
    ],
    "adap": [
        r"(適応|調整|変化|追従)",
        r"(adapt|adjust|change|track)",
        r"(状況に応じて|柔軟|対応)",
        r"(flexible|responsive|dynamic)",
        r"(学習|成長|進化)",
    ],
    "emer": [
        r"(創発|自己組織|カオス|予測不能)",
        r"(emergent|self-organize|chaos|unpredictable)",
        r"(新しいパターン|突然|予想外)",
        r"(new pattern|sudden|unexpected)",
        r"(複雑系|非線形|臨界)",
    ],
}

# P4 Tekhnē derivative patterns
P4_PATTERNS: Dict[str, List[str]] = {
    "manu": [
        r"(手動|手作業|人力|職人)",
        r"(manual|handwork|artisan|craft)",
        r"(自分で|直接|ハンズオン)",
        r"(by hand|direct|hands-on)",
        r"(熟練|技|スキル)",
    ],
    "mech": [
        r"(ツール|機械|支援|補助)",
        r"(tool|machine|assist|support)",
        r"(半自動|人間.*機械|効率化)",
        r"(semi-auto|human.*machine|efficiency)",
        r"(拡張|増幅|レバレッジ)",
    ],
    "auto": [
        r"(自動|AI|無人|自律)",
        r"(auto|AI|unmanned|autonomous)",
        r"(完全自動|ロボット|エージェント)",
        r"(fully automated|robot|agent)",
        r"(人間不要|24時間|スケール)",
    ],
}


# =============================================================================
# K-series Keyword Patterns (Kairos / Context)
# =============================================================================

# K1 Eukairia derivative patterns
K1_PATTERNS: Dict[str, List[str]] = {
    "urge": [
        r"(緊急|急いで|今すぐ|待てない)",
        r"(urgent|ASAP|immediately|hurry)",
        r"(締め切り|デッドライン|期限)",
        r"(deadline|due|closing)",
        r"(窓が閉じる|逃すと|チャンスを逃す)",
    ],
    "opti": [
        r"(最適|ベストタイミング|ちょうど良い)",
        r"(optimal|best timing|right moment)",
        r"(準備完了|機が熟した|条件が揃った)",
        r"(ready|ripe|conditions met)",
        r"(Kairos|カイロス|好機)",
    ],
    "miss": [
        r"(逃した|遅かった|もう遅い)",
        r"(missed|too late|lost)",
        r"(後悔|機会損失|やっておけば)",
        r"(regret|opportunity cost|should have)",
        r"(待機|保留|次の機会)",
    ],
}

# K2 Chronos derivative patterns
K2_PATTERNS: Dict[str, List[str]] = {
    "shor": [
        r"(今日|明日|今週|すぐ)",
        r"(today|tomorrow|this week|soon)",
        r"(短期|即時|当面)",
        r"(short-term|immediate|tactical)",
        r"(秒|分|時間単位)",
    ],
    "medi": [
        r"(来週|来月|数週間|数ヶ月)",
        r"(next week|next month|weeks|months)",
        r"(中期|プロジェクト単位|四半期)",
        r"(medium-term|quarterly|project)",
        r"(スプリント|マイルストーン)",
    ],
    "long": [
        r"(来年|数年|長期|永続)",
        r"(next year|years|long-term|permanent)",
        r"(戦略|ビジョン|10年)",
        r"(strategy|vision|decade)",
        r"(生涯|キャリア|レガシー)",
    ],
}

# K3 Telos derivative patterns
K3_PATTERNS: Dict[str, List[str]] = {
    "intr": [
        r"(楽しい|面白い|やりがい|成長)",
        r"(fun|interesting|rewarding|growth)",
        r"(それ自体|その瞬間|プロセス)",
        r"(for its own sake|in the moment|process)",
        r"(自己実現|autonomy|達成感)",
    ],
    "inst": [
        r"(〜のため|手段|ステップ|橋)",
        r"(for|means|step|bridge)",
        r"(〜に繋がる|〜に向けて|中間目標)",
        r"(leads to|towards|intermediate)",
        r"(お金|昇進|資格)",
    ],
    "ulti": [
        r"(人生|使命|意義|大目的)",
        r"(life|mission|meaning|purpose)",
        r"(Eudaimonia|幸福|flourishing)",
        r"(究極|最終|根本)",
        r"(なぜ生きる|legacy|遺産)",
    ],
}

# K4 Sophia derivative patterns
K4_PATTERNS: Dict[str, List[str]] = {
    "taci": [
        r"(直感|感覚|体で覚える|経験)",
        r"(intuition|feeling|embodied|experience)",
        r"(言葉にできない|暗黙知|tacit)",
        r"(know-how|skill|熟練)",
        r"(無意識|自動的|身体)",
    ],
    "expl": [
        r"(文書|マニュアル|明示|形式)",
        r"(document|manual|explicit|formal)",
        r"(言語化|コード化|共有可能)",
        r"(articulate|codify|shareable)",
        r"(データ|論理|証拠)",
    ],
    "meta": [
        r"(知識について|認識|メタ)",
        r"(about knowledge|epistemic|meta)",
        r"(何が分からない|限界|不確実)",
        r"(don't know what|limits|uncertainty)",
        r"(自己認識|振り返り|reflection)",
    ],
}


# =============================================================================
# A-series Keyword Patterns (Akribeia / Precision)
# =============================================================================

# A1 Pathos derivative patterns
A1_PATTERNS: Dict[str, List[str]] = {
    "prim": [
        r"(最初の|第一印象|直感的|自動的)",
        r"(first|initial|automatic|gut)",
        r"(怒り|恐れ|喜び|悲しみ)",
        r"(anger|fear|joy|sadness)",
        r"(瞬間的|反射的|本能的)",
    ],
    "seco": [
        r"(メタ感情|二次的|振り返り)",
        r"(meta-emotion|secondary|reflection)",
        r"(罪悪感|恥|誇り|後悔)",
        r"(guilt|shame|pride|regret)",
        r"(自分の感情について|気づき)",
    ],
    "regu": [
        r"(調整|制御|コントロール|管理)",
        r"(regulate|control|manage|modulate)",
        r"(再評価|リフレーミング|Reappraisal)",
        r"(落ち着く|冷静|距離を置く)",
        r"(cognitive reappraisal|Stoic)",
    ],
}

# A2 Krisis derivative patterns
A2_PATTERNS: Dict[str, List[str]] = {
    "affi": [
        r"(肯定|はい|Yes|賛成|認める)",
        r"(affirm|accept|approve|endorse)",
        r"(確信|決断|コミット)",
        r"(confident|decided|certain)",
        r"(採用|実行|Go)",
    ],
    "nega": [
        r"(否定|いいえ|No|反対|拒否)",
        r"(negate|reject|decline|refuse)",
        r"(却下|中止|Stop)",
        r"(wrong|incorrect|false)",
        r"(ダメ|無理|不可)",
    ],
    "susp": [
        r"(保留|判断停止|Epochē|待ち)",
        r"(suspend|hold|postpone|defer)",
        r"(分からない|不明|不確実)",
        r"(uncertain|unclear|unknown)",
        r"(もっと情報|要調査|要検討)",
    ],
}

# A3 Gnōmē derivative patterns
A3_PATTERNS: Dict[str, List[str]] = {
    "conc": [
        r"(具体的|このケース|この状況)",
        r"(concrete|specific|this case)",
        r"(今回|ここでは|この例)",
        r"(particular|example|instance)",
        r"(実践的|actionable)",
    ],
    "abst": [
        r"(抽象的|一般的|原則)",
        r"(abstract|general|principle)",
        r"(パターン|法則|ルール)",
        r"(pattern|rule|tendency)",
        r"(〜場合は|〜のとき)",
    ],
    "univ": [
        r"(普遍的|永遠|不変|絶対)",
        r"(universal|eternal|absolute)",
        r"(真理|法則|公理)",
        r"(truth|law|axiom)",
        r"(いつでも|どこでも|すべて)",
    ],
}

# A4 Epistēmē derivative patterns
A4_PATTERNS: Dict[str, List[str]] = {
    "tent": [
        r"(暫定的|仮説|推測|たぶん)",
        r"(tentative|hypothesis|guess|maybe)",
        r"(検証が必要|要確認|uncertain)",
        r"(preliminary|initial|draft)",
        r"(〜かもしれない|〜の可能性)",
    ],
    "just": [
        r"(正当化|根拠|エビデンス|証拠)",
        r"(justified|evidence|reason|warrant)",
        r"(合理的|論理的|妥当)",
        r"(rational|logical|valid)",
        r"(信頼できる|確からしい)",
    ],
    "cert": [
        r"(確実|確定|間違いない|必然)",
        r"(certain|definite|sure|necessary)",
        r"(知っている|事実|真実)",
        r"(know|fact|truth)",
        r"(疑いなく|絶対に|100%)",
    ],
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DerivativeRecommendation:
    """Result of derivative selection."""
    theorem: str              # O1, O2, O3, O4
    derivative: str           # nous, phro, meta, etc.
    confidence: float         # 0.0-1.0
    rationale: str            # Reason for recommendation
    alternatives: List[str]   # Alternative derivatives


# =============================================================================
# Encoding Functions
# =============================================================================

def encode_for_derivative_selection(
    problem_text: str,
    theorem: Literal["O1", "O2", "O3", "O4"]
) -> Tuple[int, int, int]:
    """
    Encode problem text for derivative selection.
    
    Returns:
        Tuple of (abstraction_level, context_dependency, reflection_need)
        Each value is 0, 1, or 2.
    
    Example:
        >>> encode_for_derivative_selection("この概念の本質は？", "O1")
        (2, 0, 0)  # High abstraction, low context, low reflection
    """
    text_lower = problem_text.lower()
    
    # Abstraction level (0=concrete, 1=mixed, 2=abstract)
    abstract_keywords = ["本質", "原理", "根本", "普遍", "概念", "定義", "抽象", "理論"]
    practical_keywords = ["具体", "実際", "現場", "状況", "ケース", "事例", "この場合", "特定"]
    
    abstract_score = sum(1 for k in abstract_keywords if k in text_lower)
    practical_score = sum(1 for k in practical_keywords if k in text_lower)
    
    if abstract_score > practical_score:
        abstraction_level = 2
    elif practical_score > abstract_score:
        abstraction_level = 0
    else:
        abstraction_level = 1
    
    # Context dependency (0=universal, 1=some context, 2=highly contextual)
    context_keywords = ["この場合", "今回", "特定の", "において", "状況", "ここで"]
    context_count = sum(1 for k in context_keywords if k in text_lower)
    context_dependency = min(context_count, 2)
    
    # Reflection need (0=none, 1=some, 2=high)
    reflection_keywords = ["確かか", "信頼", "再考", "見直し", "本当に", "疑問", "どう思う"]
    reflection_count = sum(1 for k in reflection_keywords if k in text_lower)
    reflection_need = min(reflection_count, 2)
    
    return (abstraction_level, context_dependency, reflection_need)


def _calculate_pattern_score(text: str, patterns: List[str]) -> int:
    """Calculate how many patterns match in the text."""
    score = 0
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 1
    return score


# =============================================================================
# LLM Fallback Selection (v3.1 新規)
# =============================================================================

# Derivative mappings for each theorem
THEOREM_DERIVATIVES: Dict[str, List[str]] = {
    "O1": ["nous", "phro", "meta"],
    "O2": ["desir", "voli", "akra"],
    "O3": ["anom", "hypo", "eval"],
    "O4": ["flow", "prax", "pois"],
    "S1": ["cont", "disc", "abst"],
    "S2": ["comp", "inve", "adap"],
    "S3": ["norm", "empi", "rela"],
    "S4": ["prax", "pois", "temp"],
    "H1": ["appr", "avoi", "arre"],
    "H2": ["subj", "inte", "obje"],
    "H3": ["targ", "acti", "stat"],
    "H4": ["sens", "conc", "form"],
    "P1": ["phys", "conc", "rela"],
    "P2": ["line", "bran", "cycl"],
    "P3": ["fixe", "adap", "emer"],
    "P4": ["manu", "mech", "auto"],
    "K1": ["urge", "opti", "miss"],
    "K2": ["shor", "medi", "long"],
    "K3": ["intr", "inst", "ulti"],
    "K4": ["taci", "expl", "meta"],
    "A1": ["prim", "seco", "regu"],
    "A2": ["affi", "nega", "susp"],
    "A3": ["conc", "abst", "univ"],
    "A4": ["tent", "just", "cert"],
}

DERIVATIVE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "O1": {
        "nous": "本質・原理の直観的把握 (Nous poietikos → theoretikos)",
        "phro": "実践的判断・具体状況での適切な判断 (Phronēsis)",
        "meta": "認知プロセスへの反省・信頼性評価 (Metanoēsis)",
    },
    "O2": {
        "desir": "純粋な欲求の把握 (Epithymia)",
        "voli": "複数欲動の意志統合 (Hekousios)",
        "akra": "意志の弱さへの対処 (Akrasia)",
    },
    # ... 他の定理も同様
}


def _select_with_llm(theorem: str, problem: str) -> Optional[Tuple[str, float]]:
    """
    Select derivative using LLM (Gemini Flash free tier).
    
    Returns:
        Tuple of (derivative, confidence) or None if LLM fails
    """
    if not LLM_FALLBACK_ENABLED or not GEMINI_AVAILABLE or not GEMINI_CLIENT:
        return None
    
    derivatives = THEOREM_DERIVATIVES.get(theorem, [])
    if not derivatives:
        return None
    
    # Build concise prompt (Gemini 3 style: less is more)
    prompt = f"""定理 {theorem} の派生を選べ。

派生候補: {', '.join(derivatives)}

入力: {problem}

回答形式: 派生コードのみ (例: {derivatives[0]})"""

    try:
        response = GEMINI_CLIENT.models.generate_content(
            model=LLM_DERIVATIVE_MODEL,
            contents=prompt,
        )
        
        if response and response.text:
            result = response.text.strip().lower()
            # Extract derivative code from response
            for deriv in derivatives:
                if deriv in result:
                    return (deriv, 0.85)  # LLM confidence = 85%
        
        return None
    except Exception as e:
        logger.warning(f"LLM derivative selection failed: {e}")
        return None


def _hybrid_select(
    theorem: str,
    problem: str,
    keyword_result: "DerivativeRecommendation"
) -> "DerivativeRecommendation":
    """
    Hybrid selection: LLM fallback when keyword confidence is low.
    
    Returns original keyword result if:
    - Keyword confidence >= threshold
    - LLM fallback is disabled
    - LLM call fails
    
    Otherwise returns LLM result with higher confidence.
    """
    # If keyword confidence is high enough, use it
    if keyword_result.confidence >= LLM_FALLBACK_THRESHOLD:
        return keyword_result
    
    # Try LLM fallback
    llm_result = _select_with_llm(theorem, problem)
    
    if llm_result:
        derivative, confidence = llm_result
        
        return DerivativeRecommendation(
            theorem=theorem,
            derivative=derivative,
            confidence=confidence,
            rationale=f"LLM fallback (keyword confidence {keyword_result.confidence:.0%} < {LLM_FALLBACK_THRESHOLD:.0%})",
            alternatives=keyword_result.alternatives,
        )

    
    # LLM failed, return keyword result
    return keyword_result


def _log_selection(
    theorem: str,
    problem: str,
    result: "DerivativeRecommendation",
    method: str = "keyword"
) -> None:
    """
    派生選択をログに記録 (v3.2 学習基盤)
    
    Args:
        theorem: 定理コード (O1, S2, etc.)
        problem: 問題文 (最大100文字)
        result: 選択結果
        method: 選択方法 ("keyword" or "llm")
    """
    if not SELECTION_LOG_ENABLED:
        return
    
    try:
        # ログディレクトリ確保
        SELECTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # エントリ作成
        entry = {
            "timestamp": datetime.now().isoformat(),
            "theorem": theorem,
            "problem": problem[:100] if len(problem) > 100 else problem,
            "derivative": result.derivative,
            "confidence": round(result.confidence, 2),
            "method": method,
        }
        
        # 既存ログを読み込み
        existing = []
        if SELECTION_LOG_PATH.exists():
            with open(SELECTION_LOG_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data.get("selections"), list):
                    existing = data["selections"]
        
        # 追記
        existing.append(entry)
        
        # 保存 (最新1000件のみ保持)
        with open(SELECTION_LOG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(
                {"selections": existing[-1000:]},
                f,
                allow_unicode=True,
                default_flow_style=False,
            )
    except Exception as e:
        logger.warning(f"Failed to log derivative selection: {e}")


# =============================================================================
# Selection Functions
# =============================================================================

def select_derivative(
    theorem: Literal["O1", "O2", "O3", "O4", "S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    problem_context: str,
    use_fep: bool = False,
    use_llm_fallback: bool = True  # v3.1: Enable LLM hybrid selection
) -> DerivativeRecommendation:
    """
    Select the optimal derivative for the given theorem and problem context.
    
    v3.1: Hybrid selection - uses LLM fallback when keyword confidence < 50%
    
    Args:
        theorem: O-series (O1-O4), S-series (S1-S4), or H-series (H1-H4) theorem
        problem_context: Problem description (user input)
        use_fep: Use FEP agent for selection (future enhancement)
        use_llm_fallback: Enable LLM hybrid selection (default: True)
    
    Returns:
        DerivativeRecommendation with selected derivative and confidence
    
    Example:
        >>> result = select_derivative("O1", "この原理の本質を把握したい")
        >>> result.derivative
        'nous'
        >>> result = select_derivative("S2", "既存のライブラリを組み合わせたい")
        >>> result.derivative
        'comp'
        >>> result = select_derivative("H1", "この選択肢に惹かれる")
        >>> result.derivative
        'appr'
    """
    
    # Get keyword-based result first
    keyword_result: Optional[DerivativeRecommendation] = None
    
    # O-series
    if theorem == "O1":
        keyword_result = _select_o1_derivative(problem_context)
    elif theorem == "O2":
        keyword_result = _select_o2_derivative(problem_context)
    elif theorem == "O3":
        keyword_result = _select_o3_derivative(problem_context)
    elif theorem == "O4":
        keyword_result = _select_o4_derivative(problem_context)
    # S-series
    elif theorem == "S1":
        keyword_result = _select_s1_derivative(problem_context)
    elif theorem == "S2":
        keyword_result = _select_s2_derivative(problem_context)
    elif theorem == "S3":
        keyword_result = _select_s3_derivative(problem_context)
    elif theorem == "S4":
        keyword_result = _select_s4_derivative(problem_context)
    # H-series
    elif theorem == "H1":
        keyword_result = _select_h1_derivative(problem_context)
    elif theorem == "H2":
        keyword_result = _select_h2_derivative(problem_context)
    elif theorem == "H3":
        keyword_result = _select_h3_derivative(problem_context)
    elif theorem == "H4":
        keyword_result = _select_h4_derivative(problem_context)
    # P-series
    elif theorem == "P1":
        keyword_result = _select_p1_derivative(problem_context)
    elif theorem == "P2":
        keyword_result = _select_p2_derivative(problem_context)
    elif theorem == "P3":
        keyword_result = _select_p3_derivative(problem_context)
    elif theorem == "P4":
        keyword_result = _select_p4_derivative(problem_context)
    # K-series
    elif theorem == "K1":
        keyword_result = _select_k1_derivative(problem_context)
    elif theorem == "K2":
        keyword_result = _select_k2_derivative(problem_context)
    elif theorem == "K3":
        keyword_result = _select_k3_derivative(problem_context)
    elif theorem == "K4":
        keyword_result = _select_k4_derivative(problem_context)
    # A-series
    elif theorem == "A1":
        keyword_result = _select_a1_derivative(problem_context)
    elif theorem == "A2":
        keyword_result = _select_a2_derivative(problem_context)
    elif theorem == "A3":
        keyword_result = _select_a3_derivative(problem_context)
    elif theorem == "A4":
        keyword_result = _select_a4_derivative(problem_context)
    else:
        raise ValueError(f"Unknown theorem: {theorem}. Expected O1-O4, S1-S4, H1-H4, P1-P4, K1-K4, or A1-A4.")
    
    # v3.1: Apply Hybrid selection (LLM fallback for low confidence)
    if use_llm_fallback and keyword_result is not None:
        result = _hybrid_select(theorem, problem_context, keyword_result)
        method = "llm" if "LLM" in result.rationale else "keyword"
        _log_selection(theorem, problem_context, result, method)
        return result
    
    # v3.2: Log keyword selection
    if keyword_result is not None:
        _log_selection(theorem, problem_context, keyword_result, "keyword")
    
    return keyword_result






def _select_o1_derivative(text: str) -> DerivativeRecommendation:
    """Select O1 Noēsis derivative: nous, phro, or meta."""
    scores = {
        "nous": _calculate_pattern_score(text, O1_PATTERNS["nous"]),
        "phro": _calculate_pattern_score(text, O1_PATTERNS["phro"]),
        "meta": _calculate_pattern_score(text, O1_PATTERNS["meta"]),
    }
    
    # Encoding-based boost
    obs = encode_for_derivative_selection(text, "O1")
    if obs[2] >= 2:  # High reflection need
        scores["meta"] += 2
    elif obs[0] >= 2:  # High abstraction
        scores["nous"] += 2
    elif obs[1] >= 1:  # Context dependency
        scores["phro"] += 1
    
    # Select highest score
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Confidence based on score dominance
    total = sum(scores.values()) or 1
    confidence = 0.5 + 0.1 * max_score
    confidence = min(confidence, 0.95)
    
    # Default if no patterns matched
    if total == 0:
        selected = "nous"
        confidence = 0.5
    
    alternatives = [d for d in ["nous", "phro", "meta"] if d != selected]
    rationale = _generate_o1_rationale(selected, obs)
    
    return DerivativeRecommendation(
        theorem="O1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_o2_derivative(text: str) -> DerivativeRecommendation:
    """Select O2 Boulēsis derivative: desir, voli, or akra."""
    scores = {
        "desir": _calculate_pattern_score(text, O2_PATTERNS["desir"]),
        "voli": _calculate_pattern_score(text, O2_PATTERNS["voli"]),
        "akra": _calculate_pattern_score(text, O2_PATTERNS["akra"]),
    }
    
    # Priority boost for akra (意志-行為乖離 is often the core problem)
    if scores["akra"] >= 2:
        scores["akra"] += 1
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to desir if no patterns matched
    if sum(scores.values()) == 0:
        selected = "desir"
        confidence = 0.5
    else:
        confidence = 0.5 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["desir", "voli", "akra"] if d != selected]
    rationale = _generate_o2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="O2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_o3_derivative(text: str) -> DerivativeRecommendation:
    """Select O3 Zētēsis derivative: anom, hypo, or eval."""
    scores = {
        "anom": _calculate_pattern_score(text, O3_PATTERNS["anom"]),
        "hypo": _calculate_pattern_score(text, O3_PATTERNS["hypo"]),
        "eval": _calculate_pattern_score(text, O3_PATTERNS["eval"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to anom (inquiry starts with anomaly detection)
    if sum(scores.values()) == 0:
        selected = "anom"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["anom", "hypo", "eval"] if d != selected]
    rationale = _generate_o3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="O3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_o4_derivative(text: str) -> DerivativeRecommendation:
    """Select O4 Energeia derivative: flow, prax, or pois."""
    scores = {
        "flow": _calculate_pattern_score(text, O4_PATTERNS["flow"]),
        "prax": _calculate_pattern_score(text, O4_PATTERNS["prax"]),
        "pois": _calculate_pattern_score(text, O4_PATTERNS["pois"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to pois (production is common in development context)
    if sum(scores.values()) == 0:
        selected = "pois"
        confidence = 0.55
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["flow", "prax", "pois"] if d != selected]
    rationale = _generate_o4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="O4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================
# S-series Selection Functions
# =============================================================================

def _select_s1_derivative(text: str) -> DerivativeRecommendation:
    """Select S1 Metron derivative: cont, disc, or abst."""
    scores = {
        "cont": _calculate_pattern_score(text, S1_PATTERNS["cont"]),
        "disc": _calculate_pattern_score(text, S1_PATTERNS["disc"]),
        "abst": _calculate_pattern_score(text, S1_PATTERNS["abst"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to abst (abstraction level is most common)
    if sum(scores.values()) == 0:
        selected = "abst"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["cont", "disc", "abst"] if d != selected]
    rationale = _generate_s1_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="S1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_s2_derivative(text: str) -> DerivativeRecommendation:
    """Select S2 Mekhanē derivative: comp, inve, or adap."""
    scores = {
        "comp": _calculate_pattern_score(text, S2_PATTERNS["comp"]),
        "inve": _calculate_pattern_score(text, S2_PATTERNS["inve"]),
        "adap": _calculate_pattern_score(text, S2_PATTERNS["adap"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to comp (composition is most common)
    if sum(scores.values()) == 0:
        selected = "comp"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["comp", "inve", "adap"] if d != selected]
    rationale = _generate_s2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="S2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_s3_derivative(text: str) -> DerivativeRecommendation:
    """Select S3 Stathmos derivative: norm, empi, or rela."""
    scores = {
        "norm": _calculate_pattern_score(text, S3_PATTERNS["norm"]),
        "empi": _calculate_pattern_score(text, S3_PATTERNS["empi"]),
        "rela": _calculate_pattern_score(text, S3_PATTERNS["rela"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to empi (empirical criteria is most common)
    if sum(scores.values()) == 0:
        selected = "empi"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["norm", "empi", "rela"] if d != selected]
    rationale = _generate_s3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="S3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_s4_derivative(text: str) -> DerivativeRecommendation:
    """Select S4 Praxis derivative: prax, pois, or temp."""
    scores = {
        "prax": _calculate_pattern_score(text, S4_PATTERNS["prax"]),
        "pois": _calculate_pattern_score(text, S4_PATTERNS["pois"]),
        "temp": _calculate_pattern_score(text, S4_PATTERNS["temp"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to pois (production is most common in development context)
    if sum(scores.values()) == 0:
        selected = "pois"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["prax", "pois", "temp"] if d != selected]
    rationale = _generate_s4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="S4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================
# H-series Selection Functions (Hormē / Impulse)
# =============================================================================

def _select_h1_derivative(text: str) -> DerivativeRecommendation:
    """Select H1 Propatheia derivative: appr, avoi, or arre."""
    scores = {
        "appr": _calculate_pattern_score(text, H1_PATTERNS["appr"]),
        "avoi": _calculate_pattern_score(text, H1_PATTERNS["avoi"]),
        "arre": _calculate_pattern_score(text, H1_PATTERNS["arre"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to arre (suspension is safest default)
    if sum(scores.values()) == 0:
        selected = "arre"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["appr", "avoi", "arre"] if d != selected]
    rationale = _generate_h1_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="H1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_h2_derivative(text: str) -> DerivativeRecommendation:
    """Select H2 Pistis derivative: subj, inte, or obje."""
    scores = {
        "subj": _calculate_pattern_score(text, H2_PATTERNS["subj"]),
        "inte": _calculate_pattern_score(text, H2_PATTERNS["inte"]),
        "obje": _calculate_pattern_score(text, H2_PATTERNS["obje"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to subj (subjective is most common starting point)
    if sum(scores.values()) == 0:
        selected = "subj"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["subj", "inte", "obje"] if d != selected]
    rationale = _generate_h2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="H2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_h3_derivative(text: str) -> DerivativeRecommendation:
    """Select H3 Orexis derivative: targ, acti, or stat."""
    scores = {
        "targ": _calculate_pattern_score(text, H3_PATTERNS["targ"]),
        "acti": _calculate_pattern_score(text, H3_PATTERNS["acti"]),
        "stat": _calculate_pattern_score(text, H3_PATTERNS["stat"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to targ (target-oriented is most explicit)
    if sum(scores.values()) == 0:
        selected = "targ"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["targ", "acti", "stat"] if d != selected]
    rationale = _generate_h3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="H3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_h4_derivative(text: str) -> DerivativeRecommendation:
    """Select H4 Doxa derivative: sens, conc, or form."""
    scores = {
        "sens": _calculate_pattern_score(text, H4_PATTERNS["sens"]),
        "conc": _calculate_pattern_score(text, H4_PATTERNS["conc"]),
        "form": _calculate_pattern_score(text, H4_PATTERNS["form"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to sens (sensory is most basic)
    if sum(scores.values()) == 0:
        selected = "sens"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["sens", "conc", "form"] if d != selected]
    rationale = _generate_h4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="H4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================
# P-series Selection Functions (Perigraphē / Environment)
# =============================================================================

def _select_p1_derivative(text: str) -> DerivativeRecommendation:
    """Select P1 Khōra derivative: phys, conc, or rela."""
    scores = {
        "phys": _calculate_pattern_score(text, P1_PATTERNS["phys"]),
        "conc": _calculate_pattern_score(text, P1_PATTERNS["conc"]),
        "rela": _calculate_pattern_score(text, P1_PATTERNS["rela"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to phys (physical is most concrete)
    if sum(scores.values()) == 0:
        selected = "phys"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["phys", "conc", "rela"] if d != selected]
    rationale = _generate_p1_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="P1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_p2_derivative(text: str) -> DerivativeRecommendation:
    """Select P2 Hodos derivative: line, bran, or cycl."""
    scores = {
        "line": _calculate_pattern_score(text, P2_PATTERNS["line"]),
        "bran": _calculate_pattern_score(text, P2_PATTERNS["bran"]),
        "cycl": _calculate_pattern_score(text, P2_PATTERNS["cycl"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to line (linear is most common)
    if sum(scores.values()) == 0:
        selected = "line"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["line", "bran", "cycl"] if d != selected]
    rationale = _generate_p2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="P2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_p3_derivative(text: str) -> DerivativeRecommendation:
    """Select P3 Trokhia derivative: fixe, adap, or emer."""
    scores = {
        "fixe": _calculate_pattern_score(text, P3_PATTERNS["fixe"]),
        "adap": _calculate_pattern_score(text, P3_PATTERNS["adap"]),
        "emer": _calculate_pattern_score(text, P3_PATTERNS["emer"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to adap (adaptive is most common)
    if sum(scores.values()) == 0:
        selected = "adap"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["fixe", "adap", "emer"] if d != selected]
    rationale = _generate_p3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="P3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_p4_derivative(text: str) -> DerivativeRecommendation:
    """Select P4 Tekhnē derivative: manu, mech, or auto."""
    scores = {
        "manu": _calculate_pattern_score(text, P4_PATTERNS["manu"]),
        "mech": _calculate_pattern_score(text, P4_PATTERNS["mech"]),
        "auto": _calculate_pattern_score(text, P4_PATTERNS["auto"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to mech (tool-assisted is most common)
    if sum(scores.values()) == 0:
        selected = "mech"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["manu", "mech", "auto"] if d != selected]
    rationale = _generate_p4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="P4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================
# K-series Selection Functions
# =============================================================================

def _select_k1_derivative(text: str) -> DerivativeRecommendation:
    """Select K1 Eukairia derivative: urge, opti, or miss."""
    scores = {
        "urge": _calculate_pattern_score(text, K1_PATTERNS["urge"]),
        "opti": _calculate_pattern_score(text, K1_PATTERNS["opti"]),
        "miss": _calculate_pattern_score(text, K1_PATTERNS["miss"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to opti (optimal timing is most common)
    if sum(scores.values()) == 0:
        selected = "opti"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["urge", "opti", "miss"] if d != selected]
    rationale = _generate_k1_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="K1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_k2_derivative(text: str) -> DerivativeRecommendation:
    """Select K2 Chronos derivative: shor, medi, or long."""
    scores = {
        "shor": _calculate_pattern_score(text, K2_PATTERNS["shor"]),
        "medi": _calculate_pattern_score(text, K2_PATTERNS["medi"]),
        "long": _calculate_pattern_score(text, K2_PATTERNS["long"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to medi (medium-term is most common)
    if sum(scores.values()) == 0:
        selected = "medi"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["shor", "medi", "long"] if d != selected]
    rationale = _generate_k2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="K2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_k3_derivative(text: str) -> DerivativeRecommendation:
    """Select K3 Telos derivative: intr, inst, or ulti."""
    scores = {
        "intr": _calculate_pattern_score(text, K3_PATTERNS["intr"]),
        "inst": _calculate_pattern_score(text, K3_PATTERNS["inst"]),
        "ulti": _calculate_pattern_score(text, K3_PATTERNS["ulti"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to inst (instrumental is most common)
    if sum(scores.values()) == 0:
        selected = "inst"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["intr", "inst", "ulti"] if d != selected]
    rationale = _generate_k3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="K3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_k4_derivative(text: str) -> DerivativeRecommendation:
    """Select K4 Sophia derivative: taci, expl, or meta."""
    scores = {
        "taci": _calculate_pattern_score(text, K4_PATTERNS["taci"]),
        "expl": _calculate_pattern_score(text, K4_PATTERNS["expl"]),
        "meta": _calculate_pattern_score(text, K4_PATTERNS["meta"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to expl (explicit knowledge is most common)
    if sum(scores.values()) == 0:
        selected = "expl"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["taci", "expl", "meta"] if d != selected]
    rationale = _generate_k4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="K4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================
# A-series Selection Functions
# =============================================================================

def _select_a1_derivative(text: str) -> DerivativeRecommendation:
    """Select A1 Pathos derivative: prim, seco, or regu."""
    scores = {
        "prim": _calculate_pattern_score(text, A1_PATTERNS["prim"]),
        "seco": _calculate_pattern_score(text, A1_PATTERNS["seco"]),
        "regu": _calculate_pattern_score(text, A1_PATTERNS["regu"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to prim (primary emotion is most common)
    if sum(scores.values()) == 0:
        selected = "prim"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["prim", "seco", "regu"] if d != selected]
    rationale = _generate_a1_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="A1",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_a2_derivative(text: str) -> DerivativeRecommendation:
    """Select A2 Krisis derivative: affi, nega, or susp."""
    scores = {
        "affi": _calculate_pattern_score(text, A2_PATTERNS["affi"]),
        "nega": _calculate_pattern_score(text, A2_PATTERNS["nega"]),
        "susp": _calculate_pattern_score(text, A2_PATTERNS["susp"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to susp (suspend is safest)
    if sum(scores.values()) == 0:
        selected = "susp"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["affi", "nega", "susp"] if d != selected]
    rationale = _generate_a2_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="A2",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_a3_derivative(text: str) -> DerivativeRecommendation:
    """Select A3 Gnōmē derivative: conc, abst, or univ."""
    scores = {
        "conc": _calculate_pattern_score(text, A3_PATTERNS["conc"]),
        "abst": _calculate_pattern_score(text, A3_PATTERNS["abst"]),
        "univ": _calculate_pattern_score(text, A3_PATTERNS["univ"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to conc (concrete is most actionable)
    if sum(scores.values()) == 0:
        selected = "conc"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["conc", "abst", "univ"] if d != selected]
    rationale = _generate_a3_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="A3",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


def _select_a4_derivative(text: str) -> DerivativeRecommendation:
    """Select A4 Epistēmē derivative: tent, just, or cert."""
    scores = {
        "tent": _calculate_pattern_score(text, A4_PATTERNS["tent"]),
        "just": _calculate_pattern_score(text, A4_PATTERNS["just"]),
        "cert": _calculate_pattern_score(text, A4_PATTERNS["cert"]),
    }
    
    selected = max(scores, key=scores.get)
    max_score = scores[selected]
    
    # Default to just (justified is most common)
    if sum(scores.values()) == 0:
        selected = "just"
        confidence = 0.5
    else:
        confidence = 0.55 + 0.1 * max_score
        confidence = min(confidence, 0.95)
    
    alternatives = [d for d in ["tent", "just", "cert"] if d != selected]
    rationale = _generate_a4_rationale(selected, scores)
    
    return DerivativeRecommendation(
        theorem="A4",
        derivative=selected,
        confidence=confidence,
        rationale=rationale,
        alternatives=alternatives
    )


# =============================================================================

def _generate_o1_rationale(derivative: str, obs: Tuple[int, int, int]) -> str:
    """Generate rationale for O1 derivative selection."""
    rationales = {
        "nous": f"抽象度 {obs[0]}/2 が高く、本質・原理の直観的把握が適切",
        "phro": f"文脈依存度 {obs[1]}/2 が高く、実践的判断が適切",
        "meta": f"反省必要度 {obs[2]}/2 が高く、メタ認識的反省が適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_o2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for O2 derivative selection."""
    rationales = {
        "desir": f"スコア {scores['desir']} — 明確な葛藤なし、欲動の表出段階",
        "voli": f"スコア {scores['voli']} — 複数欲動が競合、意志統合が必要",
        "akra": f"スコア {scores['akra']} — 意志と行為の乖離検出、克服戦略が必要",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_o3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for O3 derivative selection."""
    rationales = {
        "anom": f"スコア {scores['anom']} — 異常・驚きが検出され、問題化段階として適切",
        "hypo": f"スコア {scores['hypo']} — 仮説生成の必要性が示唆されている",
        "eval": f"スコア {scores['eval']} — 複数の選択肢が存在し、評価段階として適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_o4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for O4 derivative selection."""
    rationales = {
        "flow": f"スコア {scores['flow']} — 没入・最適経験への志向が検出された",
        "prax": f"スコア {scores['prax']} — 行為それ自体が目的である状況",
        "pois": f"スコア {scores['pois']} — 外部成果物の産出が目的である状況",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# S-series Rationale Generation

def _generate_s1_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for S1 derivative selection."""
    rationales = {
        "cont": f"スコア {scores['cont']} — 連続的測定（時間・空間・距離）が適切",
        "disc": f"スコア {scores['disc']} — 離散的測定（個数・回数）が適切",
        "abst": f"スコア {scores['abst']} — 抽象度・粒度のレベル選択が適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_s2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for S2 derivative selection."""
    rationales = {
        "comp": f"スコア {scores['comp']} — 既存要素の組み合わせ・統合が適切",
        "inve": f"スコア {scores['inve']} — 新規方法の創出・発明が必要",
        "adap": f"スコア {scores['adap']} — 既存方法の適応・カスタマイズが適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_s3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for S3 derivative selection."""
    rationales = {
        "norm": f"スコア {scores['norm']} — 規範的基準（理想・原則）との比較が適切",
        "empi": f"スコア {scores['empi']} — 経験的基準（データ・実績）との比較が適切",
        "rela": f"スコア {scores['rela']} — 相対的基準（競合・他者比較）が適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_s4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for S4 derivative selection."""
    rationales = {
        "prax": f"スコア {scores['prax']} — 内在的目的（Praxis：行為自体が目的）が適切",
        "pois": f"スコア {scores['pois']} — 外的目的（Poiesis：成果物産出）が適切",
        "temp": f"スコア {scores['temp']} — 時間構造（Sequential/Iterative/Parallel）の選択が必要",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# H-series Rationale Generation

def _generate_h1_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for H1 derivative selection."""
    rationales = {
        "appr": f"スコア {scores['appr']} — 接近反応（Approach：ポジティブ動機）が検出",
        "avoi": f"スコア {scores['avoi']} — 回避反応（Avoidance：ネガティブ動機）が検出",
        "arre": f"スコア {scores['arre']} — 保留反応（Arrest：判断停止）が適切",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_h2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for H2 derivative selection."""
    rationales = {
        "subj": f"スコア {scores['subj']} — 主観的確信（Subjective：個人経験）が検出",
        "inte": f"スコア {scores['inte']} — 間主観的確信（Intersubjective：合意）が検出",
        "obje": f"スコア {scores['obje']} — 客観的確信（Objective：証拠）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_h3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for H3 derivative selection."""
    rationales = {
        "targ": f"スコア {scores['targ']} — 対象志向（Target：特定対象への欲求）が検出",
        "acti": f"スコア {scores['acti']} — 活動志向（Activity：行為自体への欲求）が検出",
        "stat": f"スコア {scores['stat']} — 状態志向（State：状態達成への欲求）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_h4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for H4 derivative selection."""
    rationales = {
        "sens": f"スコア {scores['sens']} — 感覚的信念（Sensory：知覚ベース）が検出",
        "conc": f"スコア {scores['conc']} — 概念的信念（Conceptual：カテゴリベース）が検出",
        "form": f"スコア {scores['form']} — 形式的信念（Formal：論理ベース）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# P-series Rationale Generation

def _generate_p1_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for P1 derivative selection."""
    rationales = {
        "phys": f"スコア {scores['phys']} — 物理的空間（Physical：地理・配置）が検出",
        "conc": f"スコア {scores['conc']} — 概念的空間（Conceptual：設計・モデル）が検出",
        "rela": f"スコア {scores['rela']} — 関係的空間（Relational：ネットワーク）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_p2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for P2 derivative selection."""
    rationales = {
        "line": f"スコア {scores['line']} — 線形経路（Linear：逐次処理）が検出",
        "bran": f"スコア {scores['bran']} — 分岐経路（Branching：条件分岐）が検出",
        "cycl": f"スコア {scores['cycl']} — 循環経路（Cyclical：反復処理）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_p3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for P3 derivative selection."""
    rationales = {
        "fixe": f"スコア {scores['fixe']} — 固定パターン（Fixed：安定ルーティン）が検出",
        "adap": f"スコア {scores['adap']} — 適応パターン（Adaptive：動的調整）が検出",
        "emer": f"スコア {scores['emer']} — 創発パターン（Emergent：自己組織）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_p4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for P4 derivative selection."""
    rationales = {
        "manu": f"スコア {scores['manu']} — 手動操作（Manual：職人技）が検出",
        "mech": f"スコア {scores['mech']} — 機械支援（Mechanical：ツール活用）が検出",
        "auto": f"スコア {scores['auto']} — 自動化（Automated：AI駆動）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# =============================================================================
# K-series Rationale Functions
# =============================================================================

def _generate_k1_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for K1 derivative selection."""
    rationales = {
        "urge": f"スコア {scores['urge']} — 緊急機会（Urgent：今すぐ行動）が検出",
        "opti": f"スコア {scores['opti']} — 最適機会（Optimal：好機を待つ）が検出",
        "miss": f"スコア {scores['miss']} — 逸失機会（Missed：機会損失）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_k2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for K2 derivative selection."""
    rationales = {
        "shor": f"スコア {scores['shor']} — 短期視点（Short：即時対応）が検出",
        "medi": f"スコア {scores['medi']} — 中期視点（Medium：計画的）が検出",
        "long": f"スコア {scores['long']} — 長期視点（Long：戦略的）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_k3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for K3 derivative selection."""
    rationales = {
        "intr": f"スコア {scores['intr']} — 内在目的（Intrinsic：行為自体が目的）が検出",
        "inst": f"スコア {scores['inst']} — 手段目的（Instrumental：手段として）が検出",
        "ulti": f"スコア {scores['ulti']} — 究極目的（Ultimate：人生の意義）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_k4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for K4 derivative selection."""
    rationales = {
        "taci": f"スコア {scores['taci']} — 暗黙知（Tacit：体験的知識）が検出",
        "expl": f"スコア {scores['expl']} — 明示知（Explicit：形式知）が検出",
        "meta": f"スコア {scores['meta']} — メタ知識（Meta：知識についての知識）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# =============================================================================
# A-series Rationale Functions
# =============================================================================

def _generate_a1_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for A1 derivative selection."""
    rationales = {
        "prim": f"スコア {scores['prim']} — 一次感情（Primary：自動的感情反応）が検出",
        "seco": f"スコア {scores['seco']} — 二次感情（Secondary：メタ感情）が検出",
        "regu": f"スコア {scores['regu']} — 調整感情（Regulated：認知的再評価）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_a2_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for A2 derivative selection."""
    rationales = {
        "affi": f"スコア {scores['affi']} — 肯定判定（Affirm：コミットメント）が検出",
        "nega": f"スコア {scores['nega']} — 否定判定（Negate：拒否）が検出",
        "susp": f"スコア {scores['susp']} — 保留判定（Suspend：Epochē）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_a3_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for A3 derivative selection."""
    rationales = {
        "conc": f"スコア {scores['conc']} — 具体的知恵（Concrete：ケース固有）が検出",
        "abst": f"スコア {scores['abst']} — 抽象的原則（Abstract：一般化）が検出",
        "univ": f"スコア {scores['univ']} — 普遍的法則（Universal：永遠的）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


def _generate_a4_rationale(derivative: str, scores: Dict[str, int]) -> str:
    """Generate rationale for A4 derivative selection."""
    rationales = {
        "tent": f"スコア {scores['tent']} — 暫定知識（Tentative：仮説）が検出",
        "just": f"スコア {scores['just']} — 正当化知識（Justified：根拠あり）が検出",
        "cert": f"スコア {scores['cert']} — 確実知識（Certain：必然）が検出",
    }
    return rationales.get(derivative, "パターンマッチング選択")


# =============================================================================
# Derivative Information
# =============================================================================

DERIVATIVE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    # O-series
    "O1": {
        "nous": "本質・原理の直観的把握（Nous poietikos → theoretikos）",
        "phro": "文脈的実践的判断（Phronēsis：経験 + 文脈感受性）",

        "meta": "メタ認識的反省（認識の認識、信頼度評価）",
    },
    "O2": {
        "desir": "第一次欲動の表出（環境刺激への反応的願望）",
        "voli": "第二次意志による調整と自我統一（Frankfurt階層意志）",
        "akra": "意志-行為乖離の診断と克服（Akrasia対策）",
    },
    "O3": {
        "anom": "異常認識と問題化（Diaporesis → 問い立て）",
        "hypo": "創造的仮説生成（Peirce Abduction Phase 1）",
        "eval": "仮説評価と優先順位付け（Pursuitworthiness）",
    },
    "O4": {
        "flow": "Flow状態の最適化（スキル-チャレンジ均衡）",
        "prax": "自己目的的実践行為（Praxis：内在的目的）",
        "pois": "技能的産出活動（Poiesis：外部成果物）",
    },
    # S-series
    "S1": {
        "cont": "連続量の測定（時間・空間・距離の連続的評価）",
        "disc": "離散量の測定（個数・回数・段階の離散的評価）",
        "abst": "抽象度レベルの選択（Micro/Meso/Macro の粒度決定）",
    },
    "S2": {
        "comp": "既存要素の組立・統合（Method Assembly）",
        "inve": "新規方法の創出・発明（Method Invention）",
        "adap": "既存方法の適応・最適化（Method Adaptation）",
    },
    "S3": {
        "norm": "規範的基準（理想・原則に基づく評価）",
        "empi": "経験的基準（データ・実績に基づく評価）",
        "rela": "相対的基準（競合・比較に基づく評価）",
    },
    "S4": {
        "prax": "内在的目的の実践（Praxis：行為それ自体が目的）",
        "pois": "外的目的の産出（Poiesis：成果物が目的）",
        "temp": "時間構造の選択（Sequential/Iterative/Parallel）",
    },
    # H-series
    "H1": {
        "appr": "接近反応（Approach：Dopamine-driven 探索・接近）",
        "avoi": "回避反応（Avoidance：Noradrenaline-driven 危険回避）",
        "arre": "保留反応（Arrest：判断を停止し同意を与えない）",
    },
    "H2": {
        "subj": "主観的確信（Subjective：個人経験に基づく低精度信念）",
        "inte": "間主観的確信（Intersubjective：社会的合意に基づく中精度信念）",
        "obje": "客観的確信（Objective：証拠に基づく高精度信念）",
    },
    "H3": {
        "targ": "対象志向欲求（Target：特定対象への Epithumia）",
        "acti": "活動志向欲求（Activity：行為自体への Boulēsis）",
        "stat": "状態志向欲求（State：ホメオスタシス維持への Thumos）",
    },
    "H4": {
        "sens": "感覚的信念（Sensory：System 1 / Implicit / Pattern-based）",
        "conc": "概念的信念（Conceptual：Semantic network / Categorical）",
        "form": "形式的信念（Formal：System 2 / Explicit / Rule-based）",
    },
    # P-series
    "P1": {
        "phys": "物理的空間（Physical：Lefebvre perceived space / 地理的配置）",
        "conc": "概念的空間（Conceptual：Lefebvre conceived space / 設計・モデル）",
        "rela": "関係的空間（Relational：Lefebvre lived space / ネットワーク）",
    },
    "P2": {
        "line": "線形経路（Linear：DAG / Sequential / Waterfall）",
        "bran": "分岐経路（Branching：Decision tree / Conditional）",
        "cycl": "循環経路（Cyclical：Feedback loop / Iterative）",
    },
    "P3": {
        "fixe": "固定パターン（Fixed：Fixed point attractor / Homeostasis）",
        "adap": "適応パターン（Adaptive：Limit cycle / Allostatic control）",
        "emer": "創発パターン（Emergent：Strange attractor / Self-organized criticality）",
    },
    "P4": {
        "manu": "手動操作（Manual：Zuhandenheit / 熟練職人）",
        "mech": "機械支援（Mechanical：Human-in-the-loop / ツール活用）",
        "auto": "自動化（Automated：Autonomous agent / AI駆動）",
    },
    # K-series
    "K1": {
        "urge": "緊急機会（Urgent：Window closing / 今すぐ行動）",
        "opti": "最適機会（Optimal：Right moment / 好機を待つ）",
        "miss": "逸失機会（Missed：Opportunity cost / 機会損失）",
    },
    "K2": {
        "shor": "短期視点（Short：秒〜分 / Tactical response）",
        "medi": "中期視点（Medium：週〜月 / Planning horizon）",
        "long": "長期視点（Long：年〜永続 / Strategic vision）",
    },
    "K3": {
        "intr": "内在目的（Intrinsic：Autonomy-driven / 行為自体が目的）",
        "inst": "手段目的（Instrumental：Means-ends / 他目的への手段）",
        "ulti": "究極目的（Ultimate：Eudaimonia / 人生の意義）",
    },
    "K4": {
        "taci": "暗黙知（Tacit：Embodied / 体験的知識）",
        "expl": "明示知（Explicit：Codified / 形式知）",
        "meta": "メタ知識（Meta：Epistemic / 知識についての知識）",
    },
    # A-series
    "A1": {
        "prim": "一次感情（Primary：Propatheia / 自動的感情反応）",
        "seco": "二次感情（Secondary：Metacognitive / メタ感情）",
        "regu": "調整感情（Regulated：Reappraisal / 認知的再評価）",
    },
    "A2": {
        "affi": "肯定判定（Affirm：Doxa assertion / コミットメント）",
        "nega": "否定判定（Negate：Rejection / 拒否）",
        "susp": "保留判定（Suspend：Epochē / 判断停止）",
    },
    "A3": {
        "conc": "具体的知恵（Concrete：Gnōmē / ケース固有）",
        "abst": "抽象的原則（Abstract：Principle / 一般化可能）",
        "univ": "普遍的法則（Universal：Epistēmē-like / 永遠的真理）",
    },
    "A4": {
        "tent": "暫定知識（Tentative：Hypothesis / 仮説・推測）",
        "just": "正当化知識（Justified：JTB / 根拠あり）",
        "cert": "確実知識（Certain：Epistēmē / 必然的真理）",
    },
}



def get_derivative_description(theorem: str, derivative: str) -> str:
    """Get human-readable description of a derivative."""
    return DERIVATIVE_DESCRIPTIONS.get(theorem, {}).get(derivative, "Unknown derivative")


def list_derivatives(theorem: str) -> List[str]:
    """List all derivatives for a theorem."""
    return list(DERIVATIVE_DESCRIPTIONS.get(theorem, {}).keys())


# =============================================================================
# FEP Integration (Future Enhancement)
# =============================================================================

def update_derivative_selector(
    theorem: str,
    derivative: str,
    problem_context: str,
    success: bool
) -> None:
    """
    Record feedback for derivative selection learning.
    
    Future enhancement: integrate with Dirichlet learning in FEP agent
    to improve derivative selection based on outcomes.
    
    Args:
        theorem: O-series theorem
        derivative: Selected derivative
        problem_context: Problem description
        success: Whether the derivative was effective
    """
    # TODO: Integrate with HegemonikónFEPAgent.update_A_dirichlet()
    # This will require:
    # 1. Derivative-specific state space in FEP
    # 2. Observation encoding for derivative context
    # 3. Persistence of learned derivative preferences
    pass
