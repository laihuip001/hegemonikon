"""
CCL Generator (v2.0)

Enhanced CCL generation with:
  P1: Loop inference (implicit + explicit)
  P2: Oscillation detection
  P3: Conditional synthesis
  P4: Macro resolution

Usage:
    from mekhane.ccl_generator import generate_ccl
    ccl = generate_ccl("分類と見積を収束まで調整してからGapあれば調査")
    # Output: F:{/sta~/chr} _ ?gap{/sop}
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class CCLResult:
    """CCL 生成結果"""
    ccl: str
    source: str  # "llm" | "doxa" | "heuristic"
    explanation: List[str] = None
    
    def __post_init__(self):
        if self.explanation is None:
            self.explanation = []


# =============================================================================
# P1: ループ推論 (Loop Inference)
# =============================================================================

LOOP_PATTERNS = [
    # 明示的ループ (回数指定)
    (r"(\d+)回", lambda m: f"F:×{m.group(1)}"),
    
    # 暗黙的ループ (収束条件)
    (r"収束(する)?まで", lambda m: "F:"),
    (r"安定するまで", lambda m: "F:"),
    (r"繰り返し(て|し|ながら)?", lambda m: "F:"),
    (r"ループ(して|する)?", lambda m: "F:"),
    (r"何度も", lambda m: "F:"),
]


def detect_loop(intent: str) -> Tuple[bool, str, str]:
    """
    ループパターンを検出
    
    Returns:
        (has_loop, loop_prefix, remaining_intent)
    """
    for pattern, formatter in LOOP_PATTERNS:
        match = re.search(pattern, intent)
        if match:
            prefix = formatter(match)
            # ループ部分を除去した意図
            remaining = re.sub(pattern, "", intent).strip()
            return True, prefix, remaining
    
    return False, "", intent


# =============================================================================
# P2: 振動パターン検出 (Oscillation Detection)
# =============================================================================

OSCILLATION_PATTERNS = [
    # "AとBを調整" → A~/B
    r"(.+?)と(.+?)を(調整|往復|対話|やりとり|交互に)",
    # "AしながらB" → A~/B
    r"(.+?)(しながら|しつつ)(.+?)(する|を)?$",
    # "A↔B" → A~/B
    r"(.+?)↔(.+?)",
]

# ワークフロー名マッピング
WF_KEYWORDS = {
    "分類": "/sta",
    "評価": "/sta",
    "見積": "/chr",
    "時間": "/chr",
    "構造": "/kho",
    "スコープ": "/kho",
    "Gap": "/zet",
    "不足": "/zet",
    "分析": "/s",
    "調査": "/sop",    # 修正: /s ではなく /sop
    "検索": "/sop",
    "リサーチ": "/sop",
    "実行": "/ene",
    "設計": "/s",
    "判定": "/dia",
}


def keyword_to_wf(keyword: str) -> str:
    """キーワードをワークフロー名に変換"""
    for k, v in WF_KEYWORDS.items():
        if k in keyword:
            return v
    return f"/{keyword[:3]}"  # フォールバック


def detect_oscillation(intent: str) -> Tuple[bool, str, str]:
    """
    振動パターンを検出
    
    Returns:
        (has_oscillation, ccl_fragment, remaining_intent)
    """
    for pattern in OSCILLATION_PATTERNS:
        match = re.search(pattern, intent)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                wf1 = keyword_to_wf(groups[0])
                wf2 = keyword_to_wf(groups[1] if len(groups) > 1 else groups[-1])
                ccl = f"{wf1}~{wf2}"
                remaining = re.sub(pattern, "", intent).strip()
                return True, ccl, remaining
    
    return False, "", intent


# =============================================================================
# P3: 条件分岐合成 (Conditional Synthesis)
# =============================================================================

CONDITION_PATTERNS = [
    # "Xがあれば/いればY" → ?x{Y}
    (r"(.+?)が(あれば|いれば|ある場合)(.+)", 
     lambda m: (m.group(1).strip(), m.group(3).strip())),
    
    # "もしXならY" → ?x{Y}
    (r"もし(.+?)(なら|であれば)(.+)",
     lambda m: (m.group(1).strip(), m.group(3).strip())),
    
    # "Xの場合Y" → ?x{Y}
    (r"(.+?)の場合(.+)",
     lambda m: (m.group(1).strip(), m.group(2).strip())),
]

CONDITION_KEYWORDS = {
    "Gap": "gap",
    "不足": "gap",
    "エラー": "error",
    "失敗": "fail",
    "問題": "issue",
    "未完了": "incomplete",
}


def condition_to_name(condition: str) -> str:
    """条件をCCL条件名に変換"""
    for k, v in CONDITION_KEYWORDS.items():
        if k in condition:
            return v
    # フォールバック: 最初の2文字
    return condition[:2].lower()


def detect_condition(intent: str) -> Tuple[bool, str, str]:
    """
    条件分岐を検出
    
    Returns:
        (has_condition, ccl_fragment, remaining_intent)
    """
    for pattern, extractor in CONDITION_PATTERNS:
        match = re.search(pattern, intent)
        if match:
            condition, action = extractor(match)
            cond_name = condition_to_name(condition)
            # action の CCL を生成 (キーワードマッピング使用)
            action_wf = keyword_to_wf(action)
            ccl = f"?{cond_name}{{{action_wf}}}"
            remaining = re.sub(pattern, "", intent).strip()
            return True, ccl, remaining
    
    return False, "", intent


# =============================================================================
# P4: マクロ参照・展開 (Macro Resolution)
# =============================================================================

# 組み込みマクロ定義
BUILTIN_MACROS = {
    "@tak": "/s1 _ F:3{/sta~/chr} _ F:3{/kho~/zet} _ ?gap{/sop} _ /euk _ /bou",
    "@考": "/noe- _ /zet- _ /dia-",
    "@u": "/u+",
}


def resolve_macro(name: str) -> Optional[str]:
    """
    マクロ名を CCL 式に展開
    
    1. 組み込みマクロを検索
    2. Doxa パターンを検索 (将来)
    """
    # 組み込み
    if name in BUILTIN_MACROS:
        return BUILTIN_MACROS[name]
    
    # Doxa 検索 (将来実装)
    # try:
    #     from mekhane.doxa_persistence import DoxaStore
    #     doxa = DoxaStore.load()
    #     pattern = doxa.find(f"ccl_{name[1:]}_pattern")
    #     if pattern:
    #         return pattern.content
    # except:
    #     pass
    
    return None


def detect_macro(intent: str) -> Tuple[bool, str, str]:
    """
    マクロ参照を検出
    
    Returns:
        (has_macro, macro_ccl, remaining_intent)
    """
    # @name パターン
    match = re.search(r"(@\w+)", intent)
    if match:
        macro_name = match.group(1)
        # 演算子の検出
        operator = ""
        if re.search(rf"{macro_name}\+", intent):
            operator = "+"
        elif re.search(rf"{macro_name}\^", intent):
            operator = "^"
        
        remaining = re.sub(rf"{macro_name}[\+\^]?", "", intent).strip()
        return True, f"{macro_name}{operator}", remaining
    
    return False, "", intent


# =============================================================================
# 基本 WF 検出 (Base Workflow Detection)
# =============================================================================

KEYWORD_MAP = {
    # O-Series
    r"(分析|調査|理解|把握)": "/s",
    r"(認識|本質|意味)": "/noe",
    r"(意志|目標|ゴール|望み)": "/bou",
    r"(問い|疑問|探求|リサーチ)": "/zet",
    r"(実行|作成|実装|やる)": "/ene",
    
    # S-Series
    r"(設計|計画|戦略|構成)": "/s",
    r"(方法|ツール|手段)": "/mek",
    r"(基準|評価|テスト|チェック)": "/dia",
    
    # Modifiers
    r"(詳細|詳しく|具体的|深堀り)": "+",
    r"(要約|シンプル|簡単|概要)": "-",
    r"(メタ|俯瞰|全体|なぜ)": "^",
}


def generate_simple_ccl(intent: str) -> str:
    """
    シンプルな CCL 生成 (ループ・振動・条件なし)
    """
    ops = []
    
    for pattern, ccl in KEYWORD_MAP.items():
        if re.search(pattern, intent):
            ops.append(ccl)
    
    if not ops:
        return "/u"  # フォールバック
    
    # 重複排除して順次結合
    seen = set()
    unique_ops = []
    for op in ops:
        if op not in seen:
            seen.add(op)
            unique_ops.append(op)
    
    return "_".join(unique_ops)


# =============================================================================
# 統合生成関数 (Main Generator)
# =============================================================================

def generate_ccl(intent: str) -> CCLResult:
    """
    自然言語の意図から CCL 式を生成
    
    処理順序:
      1. マクロ参照の検出
      2. ループの検出
      3. 振動パターンの検出
      4. 条件分岐の検出
      5. 基本WFの検出
      6. 結合
    """
    parts = []
    explanations = []
    remaining = intent.lower()
    
    # 1. マクロ参照
    has_macro, macro_ccl, remaining = detect_macro(remaining)
    if has_macro:
        parts.append(macro_ccl)
        explanations.append(f"マクロ: {macro_ccl}")
    
    # 2. ループ検出
    has_loop, loop_prefix, remaining = detect_loop(remaining)
    
    # 3. 振動パターン
    has_osc, osc_ccl, remaining = detect_oscillation(remaining)
    if has_osc:
        if has_loop:
            parts.append(f"{loop_prefix}{{{osc_ccl}}}")
            explanations.append(f"ループ振動: {loop_prefix}{{{osc_ccl}}}")
        else:
            parts.append(osc_ccl)
            explanations.append(f"振動: {osc_ccl}")
    elif has_loop:
        # ループあるが振動なし
        inner = generate_simple_ccl(remaining)
        parts.append(f"{loop_prefix}{{{inner}}}")
        explanations.append(f"ループ: {loop_prefix}{{{inner}}}")
        remaining = ""
    
    # 4. 条件分岐
    has_cond, cond_ccl, remaining = detect_condition(remaining)
    if has_cond:
        parts.append(cond_ccl)
        explanations.append(f"条件: {cond_ccl}")
    
    # 5. 残りの基本WF
    if remaining.strip():
        base_ccl = generate_simple_ccl(remaining)
        if base_ccl != "/u":
            parts.append(base_ccl)
            explanations.append(f"基本: {base_ccl}")
    
    # 6. 結合
    if not parts:
        return CCLResult("/u", "heuristic", ["フォールバック: ユーザー問い合わせ"])
    
    ccl = " _ ".join(parts)
    return CCLResult(ccl, "heuristic", explanations)


# =============================================================================
# エントリポイント
# =============================================================================

if __name__ == "__main__":
    import sys
    
    test_cases = [
        "3回分析する",
        "収束まで評価する",
        "分類と見積を調整しながら",
        "Gapがあれば調査する",
        "@tak を詳細に実行",
        "分類と見積を収束まで調整してからGapあれば調査",
    ]
    
    if len(sys.argv) > 1:
        test_cases = [" ".join(sys.argv[1:])]
    
    for tc in test_cases:
        result = generate_ccl(tc)
        print(f"入力: {tc}")
        print(f"CCL:  {result.ccl}")
        print(f"解釈: {result.explanation}")
        print()
