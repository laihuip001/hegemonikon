# PROOF: [L2/インフラ] <- hermeneus/src/ CCL → LMQL 翻訳器
"""
Hermēneus Translator — AST を LMQL プログラムに変換

PoC (mekhane/ccl/lmql_translator.py) から正式版へリファクタ。
SEL (Semantic Enforcement Layer) 義務を LMQL 制約に変換。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

from typing import Any, Dict, List
from .ccl_ast import (
    OpType, Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation,
    ForLoop, IfCondition, WhileLoop, Lambda
)
from .macros import expand_macro
from .parser import CCLParser


# =============================================================================
# Workflow Prompts
# =============================================================================

WORKFLOW_PROMPTS = {
    # Ousia Series
    "noe": "深い認識 (Noēsis): 以下について多角的に分析し、本質を把握してください。",
    "o1": "深い認識 (Noēsis): 以下について多角的に分析し、本質を把握してください。",
    "bou": "意志確認 (Boulēsis): あなたは何を望んでいますか？目的を明確にしてください。",
    "o2": "意志確認 (Boulēsis): あなたは何を望んでいますか？目的を明確にしてください。",
    "zet": "問い発見 (Zētēsis): 何を問うべきですか？重要な問いを発見してください。",
    "o3": "問い発見 (Zētēsis): 何を問うべきですか？重要な問いを発見してください。",
    "ene": "実行 (Energeia): 以下を具体的なステップで実行してください。",
    "o4": "実行 (Energeia): 以下を具体的なステップで実行してください。",
    
    # Schema Series
    "s": "設計 (Schema): 以下を体系的に設計してください。",
    "mek": "方法配置 (Mekhanē): 適切な手法・ツールを選択し配置してください。",
    "s2": "方法配置 (Mekhanē): 適切な手法・ツールを選択し配置してください。",
    
    # Akribeia Series
    "dia": "判定 (Krisis): 以下を批判的に評価してください。",
    "a2": "判定 (Krisis): 以下を批判的に評価してください。",
    
    # Kairos Series
    "sop": "調査 (Sophia): 以下について詳細に調査してください。",
    "k4": "調査 (Sophia): 以下について詳細に調査してください。",
    
    # Meta
    "u": "主観的意見: あなたの本音を述べてください。",
    "syn": "評議会 (Synedrion): 複数の視点から批評してください。",
    "pan": "パノラマ: 盲点を発見し、メタ認知を実行してください。",
}

# 演算子 → LMQL 制約
OPERATOR_CONSTRAINTS = {
    OpType.DEEPEN: {
        "instruction": "詳細に、3つ以上の視点で、根拠を明示して",
        "constraint": "len(RESULT) > 500 and '理由' in RESULT",
    },
    OpType.CONDENSE: {
        "instruction": "簡潔に、要点のみ、3文以内で",
        "constraint": "len(RESULT) < 300",
    },
    OpType.ASCEND: {
        "instruction": "メタ的に、前提を検証しながら",
        "constraint": "'前提' in RESULT or 'メタ' in RESULT",
    },
    OpType.INVERT: {
        "instruction": "批判的に、反対の視点から",
        "constraint": "'しかし' in RESULT or '問題' in RESULT",
    },
    OpType.EXPAND: {
        "instruction": "全ての派生を網羅的に",
        "constraint": "len(RESULT) > 800",
    },
}


class LMQLTranslator:
    """CCL AST → LMQL プログラム変換"""
    
    def __init__(self, model: str = "openai/gpt-4o"):
        self.model = model
    
    def translate(self, ast: Any) -> str:
        """AST を LMQL プログラムに変換"""
        if isinstance(ast, ConvergenceLoop):
            return self._translate_convergence(ast)
        elif isinstance(ast, Sequence):
            return self._translate_sequence(ast)
        elif isinstance(ast, Fusion):
            return self._translate_fusion(ast)
        elif isinstance(ast, Oscillation):
            return self._translate_oscillation(ast)
        elif isinstance(ast, ForLoop):
            return self._translate_for(ast)
        elif isinstance(ast, IfCondition):
            return self._translate_if(ast)
        elif isinstance(ast, WhileLoop):
            return self._translate_while(ast)
        elif isinstance(ast, Lambda):
            return self._translate_lambda(ast)
        elif isinstance(ast, MacroRef):
            return self._translate_macro(ast)
        elif isinstance(ast, Workflow):
            return self._translate_workflow(ast)
        else:
            raise ValueError(f"Unknown AST node: {type(ast)}")
    
    def _translate_macro(self, macro: MacroRef) -> str:
        """マクロ参照を LMQL に変換（Synteleia 統合または展開）"""
        name = macro.name
        args = macro.args
        
        # Synteleia マクロ: @syn, @syn·, @syn×, @poiesis, @dokimasia, @S
        if name in ("syn", "syn·", "poiesis", "dokimasia", "S"):
            return self._translate_synteleia_macro(name, args)
        
        # 引数解析 (位置引数とキーワード引数の分離)
        pos_args = []
        kw_args = {}
        for arg in args:
            if "=" in arg:
                key, val = arg.split("=", 1)
                kw_args[key.strip()] = val.strip()
            else:
                pos_args.append(arg)

        # マクロ展開
        expanded_ccl = expand_macro(name, pos_args, kw_args)

        if expanded_ccl:
            try:
                # 展開された CCL をパースして AST に変換
                parser = CCLParser()
                expanded_ast = parser.parse(expanded_ccl)

                # 再帰的に翻訳
                return self.translate(expanded_ast)
            except Exception as e:
                # 展開失敗時 (パースエラーなど) はフォールバック
                # またはエラーメッセージを含む LMQL を返す
                return f'''
# Error expanding macro @{name}: {str(e)}
@lmql.query
def macro_error(context: str):
    """マクロ展開エラー"""
    argmax
        "Error: {str(e)}"
        "[RESULT]"
    from "{self.model}"
'''

        # 未定義マクロの場合 (フォールバック)
        return f'''
# CCL マクロ: @{name} (未定義または展開不可)
# TODO: マクロ展開 → 他の CCL 式に変換
@lmql.query
def macro_{name}(context: str):
    """マクロ @{name} の実行"""
    argmax
        "マクロ @{name} を実行: コンテキスト: {{context}}"
        "[RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_synteleia_macro(self, name: str, args: list) -> str:
        """Synteleia マクロを LMQL + Python に変換"""
        # 層選択を決定
        if name == "poiesis":
            layers = "poiesis_only=True"
            desc = "生成層 (O,S,H) のみ"
        elif name == "dokimasia":
            layers = "dokimasia_only=True"
            desc = "審査層 (P,K,A) のみ"
        elif name == "S" and args:
            # @S{O,A,K} 形式: 特定エージェント選択
            agents_str = args[0] if args else "O,S,H,P,K,A"
            agents_list = agents_str.replace(',', "', '")
            layers = f"agents=['{agents_list}']"
            desc = f"選択エージェント: {agents_str}"
        else:
            # @syn または @syn· (内積)
            layers = ""
            desc = "全エージェント (内積モード)"
        
        return f'''
# CCL Synteleia: @{name}
# 説明: {desc}

from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
from mekhane.synteleia.base import AuditTarget, AuditTargetType

def synteleia_audit(context: str):
    \"\"\"Synteleia 監査を実行\"\"\"
    orch = SynteleiaOrchestrator({layers})
    target = AuditTarget(
        content=context,
        target_type=AuditTargetType.GENERIC
    )
    result = orch.audit(target)
    return orch.format_report(result)

# LMQL 統合
@lmql.query
def synteleia_integrated(context: str):
    \"\"\"Synteleia 統合監査\"\"\"
    argmax
        # Python 関数呼び出し
        audit_result = synteleia_audit(context)
        "Synteleia 監査結果:\\n{{audit_result}}"
        "分析と推奨: [ANALYSIS]"
    where
        len(ANALYSIS) > 100
    from
        "{self.model}"
'''
    
    def _translate_lambda(self, node: Lambda) -> str:
        """Lambda を LMQL に変換"""
        params = ", ".join(node.params)
        return f'''
# CCL Lambda: L:[{params}]{{body}}
@lmql.query
def lambda_execution({params}, context: str):
    \"\"\"CCL Lambda 実行\"\"\"
    argmax
        "Lambda パラメータ: {params}"
        "コンテキスト: {{context}}"
        "[RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_workflow(self, wf: Workflow) -> str:
        """ワークフローを LMQL に変換"""
        prompt = WORKFLOW_PROMPTS.get(wf.id, f"/{wf.id} を実行:")
        
        # 演算子による修飾
        instructions = []
        constraints = []
        
        for op in wf.operators:
            if op in OPERATOR_CONSTRAINTS:
                spec = OPERATOR_CONSTRAINTS[op]
                instructions.append(spec["instruction"])
                constraints.append(spec["constraint"])
        
        instruction_str = "。".join(instructions) if instructions else ""
        constraint_str = " and ".join(constraints) if constraints else "len(RESULT) > 100"
        
        # モード追加
        mode_str = f" モード: {wf.mode}" if wf.mode else ""
        
        return f'''
@lmql.query
def ccl_{wf.id}(context: str):
    """CCL /{wf.id} の実行"""
    argmax
        "{prompt}{mode_str}"
        "{instruction_str}"
        "コンテキスト: {{context}}"
        "[RESULT]"
    where
        {constraint_str}
    from
        "{self.model}"
'''
    
    def _translate_convergence(self, node: ConvergenceLoop) -> str:
        """収束ループを LMQL に変換"""
        cond = node.condition
        wf_id = node.body.id if isinstance(node.body, Workflow) else "workflow"
        
        return f'''
# CCL 収束ループ: {wf_id} >> {cond.var} {cond.op} {cond.value}

import lmql

MAX_ITERATIONS = {node.max_iterations}

@lmql.query
def convergence_loop(context: str):
    """収束するまで繰り返す"""
    argmax
        V = 1.0  # 初期不確実性
        iteration = 0
        
        while V {cond.op.replace('<', '>')} {cond.value} and iteration < MAX_ITERATIONS:
            # ワークフロー実行
            "Iteration {{iteration}}: /{wf_id} を実行"
            "[STEP_RESULT]"
            where len(STEP_RESULT) > 50
            
            # 不確実性評価
            "現在の不確実性レベル (0.0-1.0): [V_ESTIMATE]"
            where V_ESTIMATE in ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
            
            V = float(V_ESTIMATE)
            iteration += 1
        
        "収束完了。最終結果: [FINAL_RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_sequence(self, node: Sequence) -> str:
        """シーケンスを LMQL に変換"""
        steps = []
        for i, step in enumerate(node.steps):
            if isinstance(step, Workflow):
                prompt = WORKFLOW_PROMPTS.get(step.id, f"/{step.id}")
                steps.append(f'        "Step {i+1}: {prompt}"')
                steps.append(f'        "[STEP_{i}_RESULT]"')
        
        steps_str = "\n".join(steps)
        
        return f'''
@lmql.query
def sequence_execution(context: str):
    """CCL シーケンス実行"""
    argmax
        "コンテキスト: {{context}}"
{steps_str}
        "全ステップ完了。統合結果: [FINAL_RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_fusion(self, node: Fusion) -> str:
        """融合を LMQL に変換"""
        left_id = node.left.id if isinstance(node.left, Workflow) else "A"
        right_id = node.right.id if isinstance(node.right, Workflow) else "B"
        
        meta_instruction = ""
        if node.meta_display:
            meta_instruction = '"[META_EXPLANATION]"\nwhere len(META_EXPLANATION) > 100 and "融合" in META_EXPLANATION'
        
        return f'''
@lmql.query
def fusion_execution(context: str):
    """CCL 融合: {left_id} * {right_id}"""
    argmax
        "コンテキスト: {{context}}"
        "/{left_id} と /{right_id} を融合して実行:"
        "[FUSED_RESULT]"
        {meta_instruction}
    where
        len(FUSED_RESULT) > 200
    from
        "{self.model}"
'''
    
    def _translate_oscillation(self, node: Oscillation) -> str:
        """振動を LMQL に変換"""
        left_id = node.left.id if isinstance(node.left, Workflow) else "A"
        right_id = node.right.id if isinstance(node.right, Workflow) else "B"
        
        return f'''
@lmql.query
def oscillation_execution(context: str):
    """CCL 振動: {left_id} ~ {right_id}"""
    argmax
        "コンテキスト: {{context}}"
        
        "Phase 1: /{left_id} を実行"
        "[PHASE_1_RESULT]"
        
        "Phase 2: /{right_id} の視点から Phase 1 を検証・拡張"
        "[PHASE_2_RESULT]"
        
        "Phase 3: 両視点を統合した最終結果"
        "[FINAL_RESULT]"
    where
        len(FINAL_RESULT) > 300
    from
        "{self.model}"
'''
    
    def _translate_for(self, node: ForLoop) -> str:
        """FOR ループを LMQL に変換"""
        if isinstance(node.iterations, int):
            iter_desc = f"{node.iterations}回"
        else:
            iter_desc = f"各要素 {node.iterations}"
        
        return f'''
@lmql.query
def for_loop_execution(context: str):
    """CCL FOR ループ: {iter_desc}"""
    argmax
        "コンテキスト: {{context}}"
        # 反復実行
        for i in range({node.iterations if isinstance(node.iterations, int) else len(node.iterations)}):
            "反復 {{i+1}}: "[ITER_RESULT]"
            where len(ITER_RESULT) > 50
        
        "全反復完了。統合結果: [FINAL_RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_if(self, node: IfCondition) -> str:
        """IF 条件分岐を LMQL に変換"""
        cond = node.condition
        
        return f'''
@lmql.query
def if_condition_execution(context: str, {cond.var.replace("[]", "")}: float):
    """CCL IF 条件分岐: {cond.var} {cond.op} {cond.value}"""
    argmax
        "コンテキスト: {{context}}"
        
        if {cond.var.replace("[]", "")} {cond.op} {cond.value}:
            "条件成立: THEN ブランチを実行"
            "[THEN_RESULT]"
        else:
            "条件不成立: ELSE ブランチを実行"
            "[ELSE_RESULT]"
    from
        "{self.model}"
'''
    
    def _translate_while(self, node: WhileLoop) -> str:
        """WHILE ループを LMQL に変換"""
        cond = node.condition
        
        return f'''
@lmql.query
def while_loop_execution(context: str):
    """CCL WHILE ループ: {cond.var} {cond.op} {cond.value}"""
    argmax
        "コンテキスト: {{context}}"
        {cond.var.replace("[]", "")} = 1.0
        iteration = 0
        MAX_ITER = 10
        
        while {cond.var.replace("[]", "")} {cond.op} {cond.value} and iteration < MAX_ITER:
            "反復 {{iteration}}: "[ITER_RESULT]"
            "現在値: [{cond.var.replace("[]", "")}_EST]"
            where {cond.var.replace("[]", "")}_EST in ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
            {cond.var.replace("[]", "")} = float({cond.var.replace("[]", "")}_EST)
            iteration += 1
        
        "ループ完了。最終結果: [FINAL_RESULT]"
    from
        "{self.model}"
'''


# =============================================================================
# Convenience Function
# =============================================================================

def translate_to_lmql(ast: Any, model: str = "openai/gpt-4o") -> str:
    """AST を LMQL に変換 (便利関数)"""
    translator = LMQLTranslator(model=model)
    return translator.translate(ast)
