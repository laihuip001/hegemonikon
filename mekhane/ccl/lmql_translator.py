# PROOF: [L2/インフラ] <- mekhane/ccl/ CCL → LMQL 翻訳層 PoC
"""
CCL to LMQL Translator - Proof of Concept

CCL 式を LMQL プログラムに変換し、制約付き生成を実現する。

Architecture:
    CCL Human → Expander → Parser → AST → LMQL Template

Example:
    Input:  /noe+ >> V[] < 0.3
    Output: LMQL program with constraints
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Dict, Any
import re

# =============================================================================
# AST Nodes
# =============================================================================


# PURPOSE: CCL 演算子タイプ
class OpType(Enum):
    """CCL 演算子タイプ"""

    DEEPEN = auto()  # +
    CONDENSE = auto()  # -
    ASCEND = auto()  # ^
    DESCEND = auto()  # /
    QUERY = auto()  # ?
    INVERT = auto()  # \
    DIFF = auto()  # '
    ROOT = auto()  # √
    FUSE = auto()  # *
    OSC = auto()  # ~
    SEQ = auto()  # _
    CONVERGE = auto()  # >> or →
    EXPAND = auto()  # !


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: ワークフローノード
class Workflow:
    """ワークフローノード"""

    id: str
    operators: List[OpType]
    modifiers: Dict[str, Any]  # e.g., {"s1": 2, "k2": 1}
    selector: Optional[str] = None


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: 条件ノード
class Condition:
    """条件ノード"""

    var: str  # e.g., "V[]"
    op: str  # e.g., "<", ">", "="
    value: float


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: 収束ループ: A >> cond
class ConvergenceLoop:
    """収束ループ: A >> cond"""

    body: Any  # Workflow or Expression
    condition: Condition


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: シーケンス: A _ B
class Sequence:
    """シーケンス: A _ B"""

    steps: List[Any]


# =============================================================================
# Simple Parser (PoC)
# =============================================================================


# PURPOSE: CCL 簡易パーサー（PoC）
class CCLParser:
    """CCL 簡易パーサー（PoC）"""

    WORKFLOWS = {
        "noe",
        "bou",
        "zet",
        "ene",
        "s",
        "mek",
        "met",
        "sta",
        "pra",
        "h",
        "pro",
        "pis",
        "ore",
        "dox",
        "p",
        "kho",
        "hod",
        "tro",
        "tek",
        "k",
        "euk",
        "chr",
        "tel",
        "sop",
        "a",
        "pat",
        "dia",
        "gno",
        "epi",
        "boot",
        "bye",
        "ax",
        "u",
        "syn",
        "pan",
        "pre",
        "poc",
        "why",
    }

    UNARY_OPS = {
        "+": OpType.DEEPEN,
        "-": OpType.CONDENSE,
        "^": OpType.ASCEND,
        "/": OpType.DESCEND,
        "?": OpType.QUERY,
        "\\": OpType.INVERT,
        "'": OpType.DIFF,
        "!": OpType.EXPAND,
    }

    # PURPOSE: CCL 式をパース
    def parse(self, ccl: str) -> Any:
        """CCL 式をパース"""
        ccl = ccl.strip()

        # 収束ループ: A >> cond
        if ">>" in ccl:
            parts = ccl.split(">>", 1)
            body = self._parse_workflow(parts[0].strip())
            condition = self._parse_condition(parts[1].strip())
            return ConvergenceLoop(body=body, condition=condition)

        # シーケンス: A _ B
        if "_" in ccl:
            parts = ccl.split("_")
            steps = [self._parse_workflow(p.strip()) for p in parts]
            return Sequence(steps=steps)

        return self._parse_workflow(ccl)

    # PURPOSE: ワークフロー式をパース
    def _parse_workflow(self, expr: str) -> Workflow:
        """ワークフロー式をパース"""
        # /wf+- 形式
        match = re.match(r"^/?([a-z]+)([\+\-\^\?\!\'\\]*)", expr)
        if not match:
            raise ValueError(f"Invalid workflow: {expr}")

        wf_id = match.group(1)
        ops_str = match.group(2)

        operators = [self.UNARY_OPS[op] for op in ops_str if op in self.UNARY_OPS]

        return Workflow(id=wf_id, operators=operators, modifiers={})

    # PURPOSE: 条件式をパース
    def _parse_condition(self, expr: str) -> Condition:
        """条件式をパース"""
        # V[] < 0.3 形式
        match = re.match(r"(V\[\]|E\[\])\s*([<>=]+)\s*([\d.]+)", expr)
        if match:
            return Condition(
                var=match.group(1), op=match.group(2), value=float(match.group(3))
            )
        return Condition(var="V[]", op="<", value=0.5)


# =============================================================================
# LMQL Translator
# PURPOSE: CCL AST → LMQL プログラム変換
# =============================================================================


# PURPOSE: [L2-auto] CCL AST → LMQL プログラム変換
class LMQLTranslator:
    """CCL AST → LMQL プログラム変換"""

    # ワークフロー → プロンプトテンプレート
    WORKFLOW_PROMPTS = {
        "noe": "深い認識: 以下について多角的に分析してください。",
        "bou": "意志確認: あなたは何を望んでいますか？",
        "zet": "問い発見: 何を問うべきですか？",
        "dia": "判定: 以下を批判的に評価してください。",
        "s": "設計: 以下を設計してください。",
        "ene": "実行: 以下を具体的なステップで実行してください。",
        "sop": "調査: 以下について調査してください。",
    }

    # PURPOSE: AST を LMQL プログラムに変換
    def translate(self, ast: Any) -> str:
        """AST を LMQL プログラムに変換"""
        if isinstance(ast, ConvergenceLoop):
            return self._translate_convergence(ast)
        elif isinstance(ast, Sequence):
            return self._translate_sequence(ast)
        elif isinstance(ast, Workflow):
            return self._translate_workflow(ast)
        else:
            raise ValueError(f"Unknown AST node: {type(ast)}")

    # PURPOSE: ワークフローを LMQL に変換
    def _translate_workflow(self, wf: Workflow) -> str:
        """ワークフローを LMQL に変換"""
        prompt = self.WORKFLOW_PROMPTS.get(wf.id, f"/{wf.id} を実行:")

        # 演算子による修飾
        depth_instruction = ""
        if OpType.DEEPEN in wf.operators:
            depth_instruction = "詳細に、3つ以上の視点で、根拠を明示して"
        elif OpType.CONDENSE in wf.operators:
            depth_instruction = "簡潔に、要点のみ"

        return f'''
@lmql.query
def ccl_{wf.id}(context: str):
    """CCL /{wf.id} の実行"""
    argmax
        "{prompt} {depth_instruction}"
        "コンテキスト: {{context}}"
        "[RESULT]"
    where
        len(RESULT) > 100 and
        not "不明" in RESULT
    from
        "openai/gpt-4o"
'''

    # PURPOSE: 収束ループを LMQL に変換
    def _translate_convergence(self, node: ConvergenceLoop) -> str:
        """収束ループを LMQL に変換"""
        body = self._translate_workflow(node.body)
        cond = node.condition

        return f'''
# CCL 収束ループ: {node.body.id} >> {cond.var} {cond.op} {cond.value}

import lmql

MAX_ITERATIONS = 5

@lmql.query
def convergence_loop(context: str):
    """収束するまで繰り返す"""
    argmax
        V = 1.0  # 初期不確実性
        iteration = 0
        
        while V {cond.op.replace('<', '>')} {cond.value} and iteration < MAX_ITERATIONS:
            # ワークフロー実行
            "Iteration {{iteration}}: /{node.body.id} を実行"
            "[STEP_RESULT]"
            where len(STEP_RESULT) > 50
            
            # 不確実性評価
            "現在の不確実性レベル (0.0-1.0): [V_ESTIMATE]"
            where V_ESTIMATE in ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
            
            V = float(V_ESTIMATE)
            iteration += 1
        
        "収束完了。最終結果: [FINAL_RESULT]"
    from
        "openai/gpt-4o"
'''

    # PURPOSE: シーケンスを LMQL に変換
    def _translate_sequence(self, node: Sequence) -> str:
        """シーケンスを LMQL に変換"""
        steps = "\n".join(
            [
                f'        "Step {i+1}: /{step.id} を実行"'
                f'\n        "[STEP_{i}_RESULT]"'
                for i, step in enumerate(node.steps)
            ]
        )

        return f'''
@lmql.query
def sequence_execution(context: str):
    """CCL シーケンス実行"""
    argmax
        "コンテキスト: {{context}}"
{steps}
        "全ステップ完了。統合結果: [FINAL_RESULT]"
    from
        "openai/gpt-4o"
'''
# PURPOSE: CCL 式を LMQL プログラムに変換


# =============================================================================
# Main: CCL → LMQL Pipeline
# =============================================================================


# PURPOSE: CCL 式を LMQL プログラムに変換
def ccl_to_lmql(ccl_expr: str) -> str:
    """CCL 式を LMQL プログラムに変換"""
    parser = CCLParser()
    translator = LMQLTranslator()

    ast = parser.parse(ccl_expr)
    lmql_code = translator.translate(ast)

    return lmql_code


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        "/noe+",
        "/bou-",
        "/s+_/ene",
        "/noe+ >> V[] < 0.3",
    ]

    for ccl in test_cases:
        print(f"\n{'='*60}")
        print(f"CCL: {ccl}")
        print(f"{'='*60}")
        try:
            lmql = ccl_to_lmql(ccl)
            print(lmql)
        except Exception as e:
            print(f"Error: {e}")
