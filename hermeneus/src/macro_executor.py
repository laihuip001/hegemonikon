# PROOF: [L1/定理] <- hermeneus/src/ マクロ自動実行エンジン
"""
Hermēneus Macro Executor — CCL マクロを AST walk で自動実行

Forward pass: マクロ → 展開 → AST → 各ノードを再帰実行
Backward pass: 確信度スコアから各ステップの帰責値 (gradient) を計算

アナロジー:
  - Forward pass  = ニューラルネットの順伝播 = 拡散モデルのデノイジング
  - Loss function = /pis (確信度) = FEP の自由エネルギー
  - Backward pass = 逆伝播 = 信用割り当て

Origin: 2026-02-09 — /v マクロ化 → 合成エンジン設計
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from enum import Enum
import time
import re


# =============================================================================
# Types
# =============================================================================

class StepType(Enum):
    """実行ステップのタイプ"""
    WORKFLOW = "workflow"       # 定理 WF 実行
    MACRO = "macro"            # マクロ展開 → 再帰実行
    SEQUENCE = "sequence"      # 順次実行コンテナ
    FOR_LOOP = "for_loop"      # F:N{body} ループ
    IF_COND = "if_cond"        # I:cond{body} 条件
    OSCILLATION = "oscillation" # A~B 振動
    FUSION = "fusion"          # A*B 融合


@dataclass
class ExecutionContext:
    """ステップ間のコンテキスト (作業記憶)

    各ステップの出力が次ステップの入力になる。
    $scope, $findings 等の WM 変数を保持。
    """
    initial_input: str = ""
    current_output: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    step_outputs: List[str] = field(default_factory=list)
    depth: int = 0  # ネスト深度

    def push(self, output: str, step_name: str = ""):
        """ステップ出力を記録し、current を更新"""
        self.step_outputs.append(output)
        self.current_output = output
        if step_name:
            self.variables[f"${step_name}"] = output

    def fork(self) -> "ExecutionContext":
        """子コンテキストを生成 (ループ/条件の内部用)"""
        return ExecutionContext(
            initial_input=self.current_output,
            current_output=self.current_output,
            variables=dict(self.variables),
            step_outputs=[],
            depth=self.depth + 1,
        )


@dataclass
class StepResult:
    """個別ステップの実行結果 (forward pass の出力)"""
    step_type: StepType
    node_id: str               # ノード識別子 (e.g., "/kho", "@fix")
    output: str                # 出力テキスト
    entropy_before: float      # 実行前エントロピー (0.0-1.0)
    entropy_after: float       # 実行後エントロピー (0.0-1.0)
    duration_ms: float = 0.0   # 実行時間
    gradient: float = 0.0      # 逆伝播で計算される帰責値
    children: List["StepResult"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def entropy_reduction(self) -> float:
        """エントロピー削減量 (denoising 量)"""
        return max(0, self.entropy_before - self.entropy_after)


@dataclass
class ExecutionResult:
    """マクロ実行全体の結果"""
    ccl: str                   # 元の CCL 式
    expanded_ccl: str          # マクロ展開後の CCL
    steps: List[StepResult] = field(default_factory=list)
    final_output: str = ""
    final_confidence: float = 0.0  # /pis の確信度 (= 1 - final_entropy)
    total_entropy_reduction: float = 0.0
    total_duration_ms: float = 0.0

    # === Backward pass results ===
    bottleneck_step: Optional[str] = None  # gradient 最大のステップ
    gradient_map: Dict[str, float] = field(default_factory=dict)

    def summary(self) -> str:
        """人間可読なサマリー"""
        lines = [
            f"CCL: {self.ccl}",
            f"展開: {self.expanded_ccl}",
            f"ステップ数: {len(self.steps)}",
            f"確信度: {self.final_confidence:.0%}",
            f"エントロピー削減: {self.total_entropy_reduction:.2f}",
            f"実行時間: {self.total_duration_ms:.0f}ms",
        ]
        if self.bottleneck_step:
            lines.append(f"ボトルネック: {self.bottleneck_step} (gradient: {self.gradient_map.get(self.bottleneck_step, 0):.2f})")

        lines.append("\nステップ別:")
        for s in self.steps:
            arrow = "↓" if s.entropy_reduction > 0 else "→"
            lines.append(
                f"  {arrow} {s.node_id:15s} "
                f"Δε={s.entropy_reduction:+.2f} "
                f"g={s.gradient:.2f} "
                f"({s.duration_ms:.0f}ms)"
            )
        return "\n".join(lines)


# =============================================================================
# Entropy Estimator
# =============================================================================

class EntropyEstimator:
    """エントロピー推定器

    LLM 出力のヒューリスティック分析でエントロピーを推定。
    拡散モデルの「ノイズレベル推定」に相当。
    """

    # 不確実性を示すマーカー
    UNCERTAINTY_MARKERS = [
        "不明", "不確実", "おそらく", "かもしれない", "推測",
        "未確認", "要確認", "TODO", "FIXME", "不明確",
        "uncertain", "maybe", "probably", "unknown", "unclear",
    ]
    # 確信を示すマーカー
    CONFIDENCE_MARKERS = [
        "確認済み", "検証済み", "完了", "成功", "✅",
        "confirmed", "verified", "passed", "success", "done",
    ]

    @classmethod
    def estimate(cls, text: str, context: Optional[ExecutionContext] = None) -> float:
        """テキストからエントロピーを推定 (0.0=確実, 1.0=完全不確実)

        推定方法:
        1. 不確実性マーカーの頻度
        2. 疑問文の頻度
        3. 出力の構造化度
        4. コンテキストの充実度
        """
        if not text:
            return 1.0  # 出力なし = 最大不確実性

        text_lower = text.lower()
        word_count = max(1, len(text.split()))

        # 1. 不確実性マーカー頻度
        uncertainty_count = sum(
            1 for m in cls.UNCERTAINTY_MARKERS if m in text_lower
        )
        uncertainty_ratio = min(1.0, uncertainty_count / (word_count * 0.1 + 1))

        # 2. 確信マーカー頻度
        confidence_count = sum(
            1 for m in cls.CONFIDENCE_MARKERS if m in text_lower
        )
        confidence_ratio = min(1.0, confidence_count / (word_count * 0.1 + 1))

        # 3. 疑問文頻度
        question_count = text.count("?") + text.count("？")
        question_ratio = min(1.0, question_count / max(1, text.count(".")))

        # 4. 構造化度 (テーブル, リスト, コードブロック → 低エントロピー)
        structure_markers = (
            text.count("|") + text.count("- ") + text.count("```")
        )
        structure_ratio = min(1.0, structure_markers / (word_count * 0.05 + 1))

        # 統合: 重み付き平均
        entropy = (
            0.3 * uncertainty_ratio
            - 0.3 * confidence_ratio
            + 0.2 * question_ratio
            - 0.2 * structure_ratio
            + 0.5  # ベースライン (情報がなければ0.5)
        )

        return max(0.0, min(1.0, entropy))


# =============================================================================
# WF Resolver
# =============================================================================

class WFResolver:
    """WF 名からファイルパスと定義テキストを解決"""

    WF_DIR = Path.home() / "oikos" / "hegemonikon" / ".agent" / "workflows"

    @classmethod
    def resolve(cls, wf_id: str) -> Optional[Path]:
        """WF ID からファイルパスを解決"""
        path = cls.WF_DIR / f"{wf_id}.md"
        return path if path.exists() else None

    @classmethod
    def load_definition(cls, wf_id: str) -> Optional[str]:
        """WF 定義テキストを読み込む"""
        path = cls.resolve(wf_id)
        if path:
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                return None
        return None

    @classmethod
    def extract_description(cls, wf_id: str) -> str:
        """WF の description (frontmatter) を抽出"""
        text = cls.load_definition(wf_id)
        if not text:
            return f"WF /{wf_id} (定義ファイル未発見)"
        match = re.search(r"description:\s*(.+)", text)
        return match.group(1).strip() if match else f"WF /{wf_id}"


# =============================================================================
# AST Walker (Forward Pass)
# =============================================================================

class ASTWalker:
    """AST を再帰的に辿り、各ノードを実行する

    ニューラルネットの forward pass に相当。
    各ステップでエントロピーを計測し、StepResult を生成。
    """

    def __init__(
        self,
        step_handler: Optional[Callable] = None,
        entropy_estimator: Optional[EntropyEstimator] = None,
    ):
        """
        Args:
            step_handler: WF ステップの実行関数
                signature: (wf_id: str, params: dict, ctx: ExecutionContext) -> str
                None の場合はデフォルトハンドラ (定義テキスト返却) を使用
            entropy_estimator: エントロピー推定器
        """
        self.step_handler = step_handler or self._default_handler
        self.estimator = entropy_estimator or EntropyEstimator()

    def walk(self, node: Any, ctx: ExecutionContext) -> StepResult:
        """AST ノードを実行 (forward pass)"""
        from hermeneus.src.ccl_ast import (
            Workflow, MacroRef, Sequence, ForLoop, IfCondition,
            Oscillation, Fusion, Program,
        )

        if isinstance(node, Program):
            return self._walk_program(node, ctx)
        elif isinstance(node, Sequence):
            return self._walk_sequence(node, ctx)
        elif isinstance(node, Workflow):
            return self._walk_workflow(node, ctx)
        elif isinstance(node, MacroRef):
            return self._walk_macro(node, ctx)
        elif isinstance(node, ForLoop):
            return self._walk_for(node, ctx)
        elif isinstance(node, IfCondition):
            return self._walk_if(node, ctx)
        elif isinstance(node, Oscillation):
            return self._walk_oscillation(node, ctx)
        elif isinstance(node, Fusion):
            return self._walk_fusion(node, ctx)
        else:
            return StepResult(
                step_type=StepType.WORKFLOW,
                node_id=f"unknown({type(node).__name__})",
                output=str(node),
                entropy_before=0.5,
                entropy_after=0.5,
            )

    def _walk_program(self, node, ctx: ExecutionContext) -> StepResult:
        """Program ノード: 全式を順次実行"""
        children = []
        for expr in node.expressions:
            child = self.walk(expr, ctx)
            children.append(child)
            ctx.push(child.output)

        return StepResult(
            step_type=StepType.SEQUENCE,
            node_id="program",
            output=ctx.current_output,
            entropy_before=children[0].entropy_before if children else 0.5,
            entropy_after=children[-1].entropy_after if children else 0.5,
            children=children,
        )

    def _walk_sequence(self, node, ctx: ExecutionContext) -> StepResult:
        """Sequence (_ チェイン): ステップを順次実行"""
        children = []
        initial_entropy = self.estimator.estimate(ctx.current_output)

        for step in node.steps:
            child = self.walk(step, ctx)
            children.append(child)
            ctx.push(child.output)

        return StepResult(
            step_type=StepType.SEQUENCE,
            node_id="sequence",
            output=ctx.current_output,
            entropy_before=initial_entropy,
            entropy_after=children[-1].entropy_after if children else initial_entropy,
            children=children,
        )

    def _walk_workflow(self, node, ctx: ExecutionContext) -> StepResult:
        """Workflow ノード: 単一 WF を実行"""
        start = time.monotonic()
        entropy_before = self.estimator.estimate(ctx.current_output)

        # パラメータ抽出
        params = dict(node.modifiers) if node.modifiers else {}
        if node.mode:
            params["mode"] = node.mode

        # 実行
        output = self.step_handler(node.id, params, ctx)

        entropy_after = self.estimator.estimate(output)
        duration = (time.monotonic() - start) * 1000

        return StepResult(
            step_type=StepType.WORKFLOW,
            node_id=f"/{node.id}",
            output=output,
            entropy_before=entropy_before,
            entropy_after=entropy_after,
            duration_ms=duration,
            metadata={"params": params},
        )

    def _walk_macro(self, node, ctx: ExecutionContext) -> StepResult:
        """MacroRef: マクロを展開して再帰実行"""
        from mekhane.ccl.macro_registry import MacroRegistry
        from hermeneus.src.parser import CCLParser

        registry = MacroRegistry()
        macro = registry.get(node.name)

        if not macro:
            return StepResult(
                step_type=StepType.MACRO,
                node_id=f"@{node.name}",
                output=f"[Error: Macro @{node.name} not found]",
                entropy_before=1.0,
                entropy_after=1.0,
            )

        # マクロ展開 → パース → 再帰実行
        parser = CCLParser()
        expanded_ast = parser.parse(macro.ccl)
        child_ctx = ctx.fork()
        child_result = self.walk(expanded_ast, child_ctx)

        # 子の出力を親コンテキストに反映
        ctx.push(child_result.output, node.name)

        return StepResult(
            step_type=StepType.MACRO,
            node_id=f"@{node.name}",
            output=child_result.output,
            entropy_before=child_result.entropy_before,
            entropy_after=child_result.entropy_after,
            duration_ms=child_result.duration_ms,
            children=child_result.children if child_result.children else [child_result],
            metadata={"expanded_ccl": macro.ccl},
        )

    def _walk_for(self, node, ctx: ExecutionContext) -> StepResult:
        """ForLoop: N回繰り返し"""
        children = []
        initial_entropy = self.estimator.estimate(ctx.current_output)

        iterations = node.iterations if isinstance(node.iterations, int) else len(node.iterations)

        for i in range(iterations):
            child_ctx = ctx.fork()
            child_ctx.variables["$i"] = i
            if isinstance(node.iterations, list) and i < len(node.iterations):
                child_ctx.variables["$item"] = node.iterations[i]

            child = self.walk(node.body, child_ctx)
            children.append(child)
            ctx.push(child.output)

        return StepResult(
            step_type=StepType.FOR_LOOP,
            node_id=f"F:{iterations}",
            output=ctx.current_output,
            entropy_before=initial_entropy,
            entropy_after=children[-1].entropy_after if children else initial_entropy,
            children=children,
        )

    def _walk_if(self, node, ctx: ExecutionContext) -> StepResult:
        """IfCondition: 条件分岐"""
        initial_entropy = self.estimator.estimate(ctx.current_output)

        # 条件評価 (ヒューリスティック: コンテキスト内のキーワード検索)
        cond_var = node.condition.var if hasattr(node.condition, 'var') else ""
        condition_met = cond_var.lower() in ctx.current_output.lower() if cond_var else True

        if condition_met:
            child = self.walk(node.then_branch, ctx)
        elif node.else_branch:
            child = self.walk(node.else_branch, ctx)
        else:
            child = StepResult(
                step_type=StepType.IF_COND,
                node_id="I:skip",
                output=ctx.current_output,
                entropy_before=initial_entropy,
                entropy_after=initial_entropy,
            )

        return StepResult(
            step_type=StepType.IF_COND,
            node_id=f"I:{cond_var}",
            output=child.output,
            entropy_before=initial_entropy,
            entropy_after=child.entropy_after,
            children=[child],
        )

    def _walk_oscillation(self, node, ctx: ExecutionContext) -> StepResult:
        """Oscillation (A~B): 2つのノードを交互実行 (収束まで)"""
        children = []
        initial_entropy = self.estimator.estimate(ctx.current_output)
        max_iters = getattr(node, 'max_iterations', 3)

        for i in range(max_iters):
            left = self.walk(node.left, ctx)
            ctx.push(left.output)
            children.append(left)

            right = self.walk(node.right, ctx)
            ctx.push(right.output)
            children.append(right)

            # 収束チェック: エントロピー変化が小さければ停止
            if i > 0 and abs(right.entropy_after - children[-3].entropy_after) < 0.05:
                break

        return StepResult(
            step_type=StepType.OSCILLATION,
            node_id="oscillation",
            output=ctx.current_output,
            entropy_before=initial_entropy,
            entropy_after=children[-1].entropy_after if children else initial_entropy,
            children=children,
        )

    def _walk_fusion(self, node, ctx: ExecutionContext) -> StepResult:
        """Fusion (A*B): 2つのノードの出力を統合"""
        initial_entropy = self.estimator.estimate(ctx.current_output)

        left = self.walk(node.left, ctx)
        right = self.walk(node.right, ctx)

        # 融合: 両方の出力を結合
        fused = f"[Fusion]\n{left.output}\n---\n{right.output}"
        ctx.push(fused)

        return StepResult(
            step_type=StepType.FUSION,
            node_id="fusion",
            output=fused,
            entropy_before=initial_entropy,
            entropy_after=min(left.entropy_after, right.entropy_after),
            children=[left, right],
        )

    @staticmethod
    def _default_handler(wf_id: str, params: dict, ctx: ExecutionContext) -> str:
        """デフォルト WF ハンドラ: CognitiveStepHandler に委譲"""
        return CognitiveStepHandler.handle(wf_id, params, ctx)


# =============================================================================
# Cognitive Step Handler (認知シミュレーター)
# =============================================================================

class CognitiveStepHandler:
    """各定理 WF の認知効果をシミュレートするハンドラ

    各定理シリーズは固有のエントロピー削減パターンを持つ:
    - O-series (本質): 認識深化 → 不確実性マーカー除去、構造追加
    - S-series (様態): 配置・構造化 → リスト/テーブル追加
    - H-series (傾向): 確信度変動 → 確信/不確信マーカー追加
    - P-series (条件): スコープ縮小 → 対象限定、境界定義
    - K-series (文脈): 文脈補完 → 情報追加
    - A-series (精密): 精密評価 → 検証済みマーカー追加

    出力テキスト内のマーカーを EntropyEstimator が検出し、
    エントロピーが自然に降下する仕組み。
    """

    # 定理→シリーズマッピング
    THEOREM_SERIES: Dict[str, str] = {
        # O-series (本質)
        "noe": "O", "bou": "O", "zet": "O", "ene": "O",
        # S-series (様態)
        "met": "S", "mek": "S", "sta": "S", "pra": "S",
        # H-series (傾向)
        "pro": "H", "pis": "H", "ore": "H", "dox": "H",
        # P-series (条件)
        "kho": "P", "hod": "P", "tro": "P", "tek": "P",
        # K-series (文脈)
        "euk": "K", "chr": "K", "tel": "K", "sop": "K",
        # A-series (精密)
        "pat": "A", "dia": "A", "gno": "A", "epi": "A",
    }

    # シリーズ別の認知効果テンプレート
    SERIES_EFFECTS: Dict[str, Dict] = {
        "O": {
            "action": "認識深化",
            "entropy_impact": -0.15,  # 高い削減
            "markers": ["確認済み: 本質を把握", "構造が明確化"],
            "template": "本質分析完了。{context_summary}\n"
                       "- 確認済み: 対象の本質的構造を特定\n"
                       "- 核心: {param_detail}\n"
                       "| 要素 | 状態 |\n|---|---|\n| 認識 | 完了 |",
        },
        "S": {
            "action": "構造配置",
            "entropy_impact": -0.12,
            "markers": ["配置完了", "構造化済み"],
            "template": "構造配置完了。\n"
                       "- 確認済み: {param_detail} の構造を定義\n"
                       "- 方法論を選択済み\n"
                       "| ステップ | 内容 | 状態 |\n|---|---|---|\n"
                       "| 1 | 分析 | 完了 |\n| 2 | 設計 | 完了 |",
        },
        "H": {
            "action": "確信度評価",
            "entropy_impact": -0.10,
            "markers": ["確信度", "検証済み"],
            "template": "傾向評価。\n"
                       "- 確信度: 75%\n"
                       "- 検証済み: {param_detail}\n"
                       "- 根拠: コンテキスト分析に基づく",
        },
        "P": {
            "action": "スコープ限定",
            "entropy_impact": -0.18,  # 最高削減 (範囲を狭める)
            "markers": ["スコープ確定", "対象限定", "確認済み"],
            "template": "スコープ限定完了。\n"
                       "- 確認済み: 対象を {param_detail} に限定\n"
                       "- 対象限定: 不要な領域を除外\n"
                       "- 境界: 明確に定義済み\n"
                       "| 範囲 | 状態 |\n|---|---|\n| 対象 | 確定 |",
        },
        "K": {
            "action": "文脈補完",
            "entropy_impact": -0.08,  # 中程度
            "markers": ["文脈追加", "情報補完"],
            "template": "文脈補完。\n"
                       "- 追加情報: {param_detail}\n"
                       "- 時間的文脈を確認\n"
                       "- 背景知識を統合",
        },
        "A": {
            "action": "精密評価",
            "entropy_impact": -0.20,  # 最高 (最終判定)
            "markers": ["検証済み", "成功", "確認済み", "✅"],
            "template": "精密評価完了。✅\n"
                       "- 検証済み: {param_detail}\n"
                       "- 判定: 成功\n"
                       "- 確認済み: 品質基準を満たす\n"
                       "| 基準 | 結果 |\n|---|---|\n| 正確性 | ✅ |\n| 完全性 | ✅ |",
        },
    }

    @classmethod
    def handle(cls, wf_id: str, params: dict, ctx: ExecutionContext) -> str:
        """WF の認知効果をシミュレートした出力を生成"""
        series = cls.THEOREM_SERIES.get(wf_id, "O")
        effect = cls.SERIES_EFFECTS.get(series, cls.SERIES_EFFECTS["O"])

        # パラメータからコンテキスト詳細を構築
        param_detail = ", ".join(f"{v}" for v in params.values()) if params else wf_id
        context_summary = ctx.current_output[:100] if ctx.current_output else "初期状態"

        # テンプレートを適用
        output = effect["template"].format(
            param_detail=param_detail,
            context_summary=context_summary,
        )

        # コンテキスト蓄積: 前のステップの確認事項を引き継ぐ
        step_count = len(ctx.step_outputs)
        if step_count > 0:
            output += f"\n前ステップからの引き継ぎ: {step_count}件の確認済み事項"

        # 深度に応じた確信度上昇
        if step_count >= 3:
            output += "\n累積確信度: 高 — 複数ステップの検証を経由"

        return output


# =============================================================================
# Backward Pass (Credit Assignment)
# =============================================================================

class BackwardPass:
    """逆伝播: 確信度スコアから各ステップの帰責値を計算

    ニューラルネットの逆伝播に相当。
    損失関数 = 1 - final_confidence。
    各ステップの gradient = そのステップのエントロピー削減の寄与率。
    """

    @staticmethod
    def compute(steps: List[StepResult], final_confidence: float) -> Dict[str, float]:
        """逆伝播を実行

        Args:
            steps: forward pass の全ステップ結果
            final_confidence: 最終確信度 (0.0-1.0)

        Returns:
            {node_id: gradient} の辞書
        """
        loss = 1.0 - final_confidence  # 損失 = 1 - 確信度
        gradient_map: Dict[str, float] = {}

        # 全ステップのエントロピー削減量を収集
        flat_steps = BackwardPass._flatten(steps)
        total_reduction = sum(s.entropy_reduction for s in flat_steps) or 1.0

        # 各ステップの寄与率 (= gradient)
        for step in flat_steps:
            if step.step_type in (StepType.SEQUENCE, StepType.FOR_LOOP):
                continue  # コンテナはスキップ

            contribution = step.entropy_reduction / total_reduction
            gradient = loss * contribution  # 損失に対する寄与
            step.gradient = gradient
            gradient_map[step.node_id] = gradient

        return gradient_map

    @staticmethod
    def _flatten(steps: List[StepResult]) -> List[StepResult]:
        """ネストされたステップをフラット化"""
        flat = []
        for s in steps:
            if s.children:
                flat.extend(BackwardPass._flatten(s.children))
            else:
                flat.append(s)
        return flat


# =============================================================================
# Macro Executor (統合エントリーポイント)
# =============================================================================

class MacroExecutor:
    """CCL マクロ自動実行エンジン

    Usage:
        executor = MacroExecutor()
        result = executor.execute("@v", context="fix shape mismatch")
        print(result.summary())

        # カスタムハンドラ (LLM API 呼び出し等)
        executor = MacroExecutor(step_handler=my_llm_handler)
    """

    def __init__(
        self,
        step_handler: Optional[Callable] = None,
        estimator: Optional[EntropyEstimator] = None,
    ):
        self.walker = ASTWalker(
            step_handler=step_handler,
            entropy_estimator=estimator,
        )

    def execute(self, ccl: str, context: str = "") -> ExecutionResult:
        """CCL 式 (マクロ含む) を実行

        1. マクロ展開
        2. AST パース
        3. Forward pass (AST walk + エントロピー計測)
        4. Backward pass (帰責計算)
        """
        from mekhane.ccl.macro_expander import MacroExpander
        from mekhane.ccl.macro_registry import MacroRegistry
        from hermeneus.src.parser import CCLParser

        start = time.monotonic()

        # Step 1: マクロ展開
        registry = MacroRegistry()
        expander = MacroExpander(registry)
        expanded, _ = expander.expand(ccl)

        # ネストされたマクロも展開 (最大3回)
        for _ in range(3):
            re_expanded, did = expander.expand(expanded)
            if not did:
                break
            expanded = re_expanded

        # Step 2: AST パース
        parser = CCLParser()
        ast = parser.parse(expanded)

        # Step 3: Forward pass
        ctx = ExecutionContext(
            initial_input=context,
            current_output=context,
        )
        root_result = self.walker.walk(ast, ctx)

        # Step 4: Backward pass
        all_steps = root_result.children if root_result.children else [root_result]
        final_confidence = 1.0 - root_result.entropy_after
        gradient_map = BackwardPass.compute(all_steps, final_confidence)

        # ボトルネック特定
        bottleneck = max(gradient_map, key=gradient_map.get) if gradient_map else None

        total_duration = (time.monotonic() - start) * 1000

        return ExecutionResult(
            ccl=ccl,
            expanded_ccl=expanded,
            steps=all_steps,
            final_output=root_result.output,
            final_confidence=final_confidence,
            total_entropy_reduction=root_result.entropy_reduction,
            total_duration_ms=total_duration,
            bottleneck_step=bottleneck,
            gradient_map=gradient_map,
        )

    def execute_and_retry(
        self,
        ccl: str,
        context: str = "",
        min_confidence: float = 0.7,
        max_retries: int = 3,
    ) -> ExecutionResult:
        """実行 + 確信度が低ければボトルネックを再実行

        拡散モデルの「段階的デノイジング」に相当。
        """
        result = self.execute(ccl, context)

        for attempt in range(max_retries):
            if result.final_confidence >= min_confidence:
                break

            # ボトルネックのステップだけ再実行
            if result.bottleneck_step:
                enhanced_context = (
                    f"{context}\n\n"
                    f"[Retry {attempt + 1}] Previous attempt identified "
                    f"'{result.bottleneck_step}' as bottleneck "
                    f"(gradient={result.gradient_map.get(result.bottleneck_step, 0):.2f}). "
                    f"Focus on improving this step."
                )
                result = self.execute(ccl, enhanced_context)

        return result


# =============================================================================
# Convenience Functions
# =============================================================================

def execute_macro(ccl: str, context: str = "") -> ExecutionResult:
    """マクロを実行 (便利関数)"""
    return MacroExecutor().execute(ccl, context)


def execute_and_explain(ccl: str, context: str = "") -> str:
    """マクロを実行し、人間可読な説明を返す"""
    result = execute_macro(ccl, context)
    return result.summary()
