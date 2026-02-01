# PROOF: [L2/インフラ] CCL 省略形展開器
"""
Hermēneus Expander — CCL 省略形を正式形に展開

Human 構文（省略形）を Machine 構文（正式形）に変換する。
MacroRegistry と連携して @macro を展開する。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import re
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass


@dataclass
class ExpansionResult:
    """展開結果"""
    original: str          # 元の式
    expanded: str          # 展開後の式
    formal: str            # 正式形 (SEL 付き)
    expansions: List[str]  # 適用された展開のログ


# =============================================================================
# Workflow Mappings
# =============================================================================

# ワークフロー省略形 → 正式形マッピング
WORKFLOW_FORMAL = {
    # Ousia Series
    "noe": "/o1",   # Noēsis
    "bou": "/o2",   # Boulēsis  
    "zet": "/o3",   # Zētēsis
    "ene": "/o4",   # Energeia
    # Schema Series
    "s": "/s",      # Schema (hub)
    "met": "/s1",   # Metron
    "mek": "/s2",   # Mekhanē
    "sta": "/s3",   # Stathmos
    "pra": "/s4",   # Praxis
    # Hormē Series
    "h": "/h",      # Hormē (hub)
    "pro": "/h1",   # Propatheia
    "pis": "/h2",   # Pistis
    "ore": "/h3",   # Orexis
    "dox": "/h4",   # Doxa
    # Perigraphē Series
    "p": "/p",      # Perigraphē (hub)
    "kho": "/p1",   # Khōra
    "hod": "/p2",   # Hodos
    "tro": "/p3",   # Trokhia
    "tek": "/p4",   # Tekhnē
    # Kairos Series
    "k": "/k",      # Kairos (hub)
    "euk": "/k1",   # Eukairia
    "chr": "/k2",   # Chronos
    "tel": "/k3",   # Telos
    "sop": "/k4",   # Sophia
    # Akribeia Series
    "a": "/a",      # Akribeia (hub)
    "pat": "/a1",   # Pathos
    "dia": "/a2",   # Krisis
    "gno": "/a3",   # Gnōmē
    "epi": "/a4",   # Epistēmē
    # Meta Workflows
    "boot": "/boot",
    "bye": "/bye",
    "ax": "/ax",
    "u": "/u",
    "syn": "/syn",
    "pan": "/pan",
}

# 演算子 → SEL 義務マッピング
OPERATOR_SEL = {
    "+": {
        "description": "詳細実行。3倍以上の情報量で出力。",
        "minimum_requirements": ["詳細な根拠提示", "複数の視点", "具体例"]
    },
    "-": {
        "description": "縮約実行。要点のみ簡潔に。",
        "minimum_requirements": ["核心のみ", "説明省略可"]
    },
    "^": {
        "description": "メタ化。前提・構造を検証。",
        "minimum_requirements": ["前提の明示", "構造の説明"]
    },
    "!": {
        "description": "全展開。全派生を並列実行。",
        "minimum_requirements": ["全派生の列挙", "各派生の実行"]
    },
}


class Expander:
    """CCL 省略形展開器"""
    
    # パターン定義
    WORKFLOW_PATTERN = re.compile(r'^/?([a-z]+)([\+\-\^\?\!\'\\]*)(.*)$')
    CONVERGENCE_PATTERN = re.compile(r'(.+)\s*>>\s*(.+)$')
    SEQUENCE_PATTERN = re.compile(r'(.+)\s*_\s*(.+)')
    MACRO_PATTERN = re.compile(r'@(\w+)')
    
    def __init__(self, macro_registry: Optional[Dict[str, str]] = None):
        """
        Args:
            macro_registry: マクロ名 → CCL 式のマッピング
        """
        self.macro_registry = macro_registry or {}
        self.expansions: List[str] = []
    
    def expand(self, ccl: str) -> ExpansionResult:
        """CCL 式を展開"""
        self.expansions = []
        original = ccl.strip()
        
        # Step 1: マクロ展開
        expanded = self._expand_macros(original)
        
        # Step 2: >> を lim 形式に展開 (オプショナル)
        formal = self._to_formal(expanded)
        
        return ExpansionResult(
            original=original,
            expanded=expanded,
            formal=formal,
            expansions=self.expansions.copy()
        )
    
    def _expand_macros(self, ccl: str) -> str:
        """@macro を展開"""
        result = ccl
        for match in self.MACRO_PATTERN.finditer(ccl):
            name = match.group(1)
            if name in self.macro_registry:
                replacement = self.macro_registry[name]
                result = result.replace(f"@{name}", replacement)
                self.expansions.append(f"@{name} → {replacement}")
        return result
    
    def _to_formal(self, ccl: str) -> str:
        """省略形を正式形に変換"""
        # 収束ループ: A >> cond → lim[cond]{A}
        conv_match = self.CONVERGENCE_PATTERN.match(ccl)
        if conv_match:
            body = conv_match.group(1).strip()
            cond = conv_match.group(2).strip()
            formal = f"lim[{cond}]{{{body}}}"
            self.expansions.append(f"{ccl} → {formal}")
            return formal
        
        # ワークフロー省略形展開
        wf_match = self.WORKFLOW_PATTERN.match(ccl)
        if wf_match:
            wf_id = wf_match.group(1)
            operators = wf_match.group(2)
            rest = wf_match.group(3)
            
            if wf_id in WORKFLOW_FORMAL:
                formal_id = WORKFLOW_FORMAL[wf_id]
                formal = f"{formal_id}{operators}{rest}"
                if formal != ccl:
                    self.expansions.append(f"/{wf_id} → {formal_id}")
                return formal
        
        return ccl
    
    def get_sel_requirements(self, ccl: str) -> Dict[str, any]:
        """CCL 式から SEL 義務を抽出"""
        requirements = {
            "description": "",
            "minimum_requirements": []
        }
        
        wf_match = self.WORKFLOW_PATTERN.match(ccl)
        if wf_match:
            operators = wf_match.group(2)
            for op in operators:
                if op in OPERATOR_SEL:
                    sel = OPERATOR_SEL[op]
                    requirements["description"] += sel["description"] + " "
                    requirements["minimum_requirements"].extend(sel["minimum_requirements"])
        
        return requirements


# =============================================================================
# Convenience Function
# =============================================================================

def expand_ccl(ccl: str, macros: Optional[Dict[str, str]] = None) -> ExpansionResult:
    """CCL 式を展開 (便利関数)"""
    expander = Expander(macro_registry=macros)
    return expander.expand(ccl)


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        "/noe+",
        "/bou-",
        "/noe+ >> V[] < 0.3",
        "@think",
    ]
    
    # デモ用マクロ
    demo_macros = {
        "think": "/noe+ >> V[] < 0.3",
        "tak": "/s+_/ene",
    }
    
    expander = Expander(macro_registry=demo_macros)
    
    for ccl in test_cases:
        result = expander.expand(ccl)
        print(f"\n{'='*60}")
        print(f"Original: {result.original}")
        print(f"Expanded: {result.expanded}")
        print(f"Formal:   {result.formal}")
        if result.expansions:
            print(f"Expansions: {result.expansions}")
