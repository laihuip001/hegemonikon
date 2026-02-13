# PROOF: [L2/インフラ] <- hermeneus/src/ Multi-Agent Debate 検証器
"""
Hermēneus Verifier — Convergent Multi-Agent Debate による検証

複数のAIエージェント (Proposer, Critic, Arbiter) が
CCL実行結果を **収束するまでラリー** し、合意形成を行う。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
Refactor: 2026-02-13 Convergent Debate (単発独白 → 収束型ラリー)
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# Types
# =============================================================================

# PURPOSE: [L2-auto] エージェントの役割
class AgentRole(Enum):
    """エージェントの役割"""
    PROPOSER = "proposer"    # 主張を支持
    CRITIC = "critic"        # 批判・反論
    ARBITER = "arbiter"      # 最終判定


# PURPOSE: [L2-auto] 判定タイプ
class VerdictType(Enum):
    """判定タイプ"""
    ACCEPT = "accept"        # 受理
    REJECT = "reject"        # 拒否
    UNCERTAIN = "uncertain"  # 不確定


@dataclass
# PURPOSE: ラリーの1ターン
class RallyTurn:
    """ラリーの1ターン — debate の最小単位"""
    speaker: AgentRole
    content: str
    confidence: float  # 0.0-1.0
    turn_number: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
# PURPOSE: [L2-auto] ディベート引数 (後方互換)
class DebateArgument:
    """ディベート引数"""
    agent_role: AgentRole
    content: str
    confidence: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
# PURPOSE: [L2-auto] 判定結果
class Verdict:
    """判定結果"""
    type: VerdictType
    reasoning: str
    confidence: float
    arbiter_notes: Optional[str] = None


@dataclass
# PURPOSE: [L2-auto] ディベートラウンド (ラリー履歴付き)
class DebateRound:
    """ディベートラウンド — ラリーの全履歴を保持"""
    round_number: int
    rally: List[RallyTurn]                   # ラリーの全ターン
    converged: bool = False                  # このラウンドで収束したか
    convergence_reason: str = ""             # 収束理由
    proposition: Optional[DebateArgument] = None   # 後方互換: 初回提案
    critiques: List[DebateArgument] = field(default_factory=list)
    rebuttal: Optional[DebateArgument] = None


@dataclass
# PURPOSE: [L2-auto] 合意結果
class ConsensusResult:
    """合意結果"""
    accepted: bool
    confidence: float          # 最終確信度
    majority_ratio: float      # 多数派比率
    verdict: Verdict
    dissent_reasons: List[str]
    rounds: List[DebateRound]
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Debate Agent
# =============================================================================

# PURPOSE: [L2-auto] ディベートエージェント
class DebateAgent:
    """ディベートエージェント
    
    役割に応じて主張生成、批判、判定を行う。
    会話履歴を引き継いでラリーが可能。
    """
    
    # PURPOSE: Initialize instance
    def __init__(
        self,
        role: AgentRole,
        model: str = "auto",
        temperature: float = 0.7
    ):
        self.role = role
        self.model = model
        self.temperature = temperature
        self._executor = self._create_executor()
        self._llm_available = self._executor is not None
    
    # PURPOSE: LMQLExecutor を作成 (5プロバイダー自動フォールバック)
    def _create_executor(self):
        """LMQLExecutor を作成。失敗時は None を返す。"""
        try:
            from hermeneus.src.runtime import LMQLExecutor, ExecutionConfig
            config = ExecutionConfig(
                model=self.model,
                temperature=self.temperature,
                workspace="synteleia-sandbox",  # verifier はサンドボックス WS で実行
            )
            return LMQLExecutor(config)
        except Exception:
            return None
    
    # PURPOSE: LLM が利用可能か確認 (後方互換)
    def _check_llm(self) -> bool:
        """LLM が利用可能か確認"""
        return self._executor is not None
    
    # =========================================================================
    # ラリー対応メソッド (新規)
    # =========================================================================
    
    # PURPOSE: 会話履歴を踏まえた応答生成
    async def respond(
        self,
        claim: str,
        rally_history: List[RallyTurn],
        context: str = "",
    ) -> RallyTurn:
        """会話履歴を踏まえた応答を生成
        
        @Proposer / @Critic が互いの主張を読み、引用しながらラリーする。
        """
        history_text = self._format_rally_history(rally_history)
        turn_number = len(rally_history) + 1
        
        if self.role == AgentRole.PROPOSER:
            system_context = (
                "あなたは「@Proposer（支持者）」です。\n"
                "以下の主張を支持する立場から議論してください。\n"
                "@Critic の批判がある場合は、それに具体的に反論してください。\n"
                "反論は @Critic の具体的な指摘を引用して行ってください。\n"
                "もし @Critic の指摘が正しいと認めざるを得ない場合は、素直に認めてください。"
            )
        elif self.role == AgentRole.CRITIC:
            system_context = (
                "あなたは「@Critic（批評者）」です。\n"
                "以下の主張と @Proposer の論拠に対して批判的分析を行ってください。\n"
                "批判の観点:\n"
                "1. 論理的な飛躍や誤謬\n"
                "2. 証拠の不足\n"
                "3. 代替解釈の可能性\n"
                "4. 潜在的リスク\n\n"
                "@Proposer の反論がある場合は、それを踏まえて再批判してください。\n"
                "もし @Proposer の反論が妥当と認めざるを得ない場合は、素直に認めてください。"
            )
        else:  # ARBITER
            system_context = (
                "あなたは「@Arbiter（調停者）」です。\n"
                "以下の debate 全体を評価し、最終判定を下してください。"
            )
        
        prompt = f"""{system_context}

## 主張
{claim}

## コンテキスト
{context if context else "(なし)"}

## これまでの議論
{history_text if history_text else "(初回発言 — あなたが最初です)"}

## あなたの番です
上記の議論を踏まえて、あなたの立場から発言してください。
前回の相手の発言に具体的に言及すること。
"""
        response = await self._generate(prompt)
        confidence = self._estimate_confidence(response)
        
        return RallyTurn(
            speaker=self.role,
            content=response,
            confidence=confidence,
            turn_number=turn_number,
        )
    
    # PURPOSE: Arbiter として全履歴を見て判定
    async def arbitrate_with_history(
        self,
        claim: str,
        rally_history: List[RallyTurn],
        context: str = "",
    ) -> Verdict:
        """全ラリー履歴を見て最終判定"""
        history_text = self._format_rally_history(rally_history)
        
        prompt = f"""あなたは「@Arbiter（調停者）」として、以下の debate 全体を評価し最終判定を下してください。

## 主張
{claim}

## コンテキスト
{context if context else "(なし)"}

## 完全な議論履歴
{history_text}

## 判定指示
上記の @Proposer と @Critic の議論全体を読み、以下の形式で判定してください:

判定: [ACCEPT/REJECT/UNCERTAIN]
確信度: [0-100]%
理由: [判定の根拠 — どの議論ポイントが決め手となったか]
"""
        response = await self._generate(prompt)
        verdict_type, confidence, reasoning = self._parse_verdict(response)
        
        return Verdict(
            type=verdict_type,
            reasoning=reasoning,
            confidence=confidence,
            arbiter_notes=response,
        )
    
    # PURPOSE: ラリー履歴をテキストにフォーマット
    def _format_rally_history(self, history: List[RallyTurn]) -> str:
        """ラリー履歴を @メンション付きテキストにフォーマット"""
        if not history:
            return ""
        
        lines = []
        for turn in history:
            role_label = f"@{turn.speaker.value.capitalize()}"
            lines.append(f"### Turn {turn.turn_number} — {role_label}")
            lines.append(turn.content)
            lines.append("")
        
        return "\n".join(lines)
    
    # =========================================================================
    # レガシーメソッド (後方互換)
    # =========================================================================
    
    # PURPOSE: 主張を支持する論拠を生成 (後方互換)
    async def propose(self, claim: str, context: str = "") -> DebateArgument:
        """主張を支持する論拠を生成"""
        turn = await self.respond(claim, [], context)
        return DebateArgument(
            agent_role=AgentRole.PROPOSER,
            content=turn.content,
            confidence=turn.confidence,
        )
    
    # PURPOSE: 批判・反論を生成 (後方互換)
    async def critique(
        self,
        claim: str,
        supporting_argument: str,
        context: str = ""
    ) -> DebateArgument:
        """批判・反論を生成"""
        # 過去のやり取りとして Proposer の主張を入れる
        fake_history = [RallyTurn(
            speaker=AgentRole.PROPOSER,
            content=supporting_argument,
            confidence=0.7,
            turn_number=1,
        )]
        turn = await self.respond(claim, fake_history, context)
        return DebateArgument(
            agent_role=AgentRole.CRITIC,
            content=turn.content,
            confidence=turn.confidence,
        )
    
    # PURPOSE: 最終判定を下す (後方互換)
    async def arbitrate(
        self,
        claim: str,
        for_arguments: List[str],
        against_arguments: List[str],
        context: str = ""
    ) -> Verdict:
        """最終判定を下す"""
        # for/against を RallyTurn に変換
        history: List[RallyTurn] = []
        turn_num = 0
        for arg in for_arguments:
            turn_num += 1
            history.append(RallyTurn(
                speaker=AgentRole.PROPOSER,
                content=arg,
                confidence=0.7,
                turn_number=turn_num,
            ))
        for arg in against_arguments:
            turn_num += 1
            history.append(RallyTurn(
                speaker=AgentRole.CRITIC,
                content=arg,
                confidence=0.7,
                turn_number=turn_num,
            ))
        
        return await self.arbitrate_with_history(claim, history, context)
    
    # PURPOSE: 反論を生成 (後方互換)
    async def rebut(
        self,
        claim: str,
        critique: str,
        original_argument: str
    ) -> DebateArgument:
        """反論を生成"""
        fake_history = [
            RallyTurn(
                speaker=AgentRole.PROPOSER,
                content=original_argument,
                confidence=0.7,
                turn_number=1,
            ),
            RallyTurn(
                speaker=AgentRole.CRITIC,
                content=critique,
                confidence=0.7,
                turn_number=2,
            ),
        ]
        turn = await self.respond(claim, fake_history)
        return DebateArgument(
            agent_role=AgentRole.PROPOSER,
            content=turn.content,
            confidence=turn.confidence,
        )
    
    # =========================================================================
    # 内部メソッド
    # =========================================================================
    
    # PURPOSE: LLM で生成 (LMQLExecutor 経由、5プロバイダー自動フォールバック)
    async def _generate(self, prompt: str) -> str:
        """LLM で生成
        
        LMQLExecutor を使用して対応プロバイダー順に試行:
        1. Antigravity LS (API key 不要)
        2. Anthropic Claude
        3. Google Gemini
        4. OpenAI
        5. Vertex AI
        """
        if not self._llm_available or self._executor is None:
            return self._fallback_generate(prompt)
        
        try:
            result = await self._executor.generate_text_async(prompt)
            if result and result.output:
                return result.output
            return self._fallback_generate(prompt)
        except Exception as e:
            return f"[Error: {e}] " + self._fallback_generate(prompt)
    
    # PURPOSE: フォールバック生成 (LLM なし)
    def _fallback_generate(self, prompt: str) -> str:
        """フォールバック生成 (LLM なし)"""
        if self.role == AgentRole.PROPOSER:
            return "この主張は論理的に妥当であり、支持できる。"
        elif self.role == AgentRole.CRITIC:
            return "この主張には検証が必要な仮定が含まれている。"
        else:
            return "判定: UNCERTAIN\n確信度: 50%\n理由: 十分な情報がない。"
    
    # PURPOSE: テキストから確信度を推定
    def _estimate_confidence(self, text: str) -> float:
        """テキストから確信度を推定"""
        high_conf = ["確実", "明確", "definitely", "certainly", "clearly"]
        low_conf = ["おそらく", "かもしれない", "maybe", "perhaps", "possibly"]
        
        text_lower = text.lower()
        
        high_count = sum(1 for w in high_conf if w in text_lower)
        low_count = sum(1 for w in low_conf if w in text_lower)
        
        if high_count > low_count:
            return min(0.9, 0.7 + high_count * 0.05)
        elif low_count > high_count:
            return max(0.3, 0.5 - low_count * 0.05)
        return 0.6
    
    # PURPOSE: 判定テキストをパース
    def _parse_verdict(self, text: str) -> tuple:
        """判定テキストをパース"""
        text_lower = text.lower()
        
        # 判定タイプ
        if "accept" in text_lower or "受理" in text:
            verdict_type = VerdictType.ACCEPT
        elif "reject" in text_lower or "拒否" in text:
            verdict_type = VerdictType.REJECT
        else:
            verdict_type = VerdictType.UNCERTAIN
        
        # 確信度
        conf_match = re.search(r'(\d+)\s*%', text)
        if conf_match:
            confidence = int(conf_match.group(1)) / 100.0
        else:
            confidence = 0.5
        
        # 理由
        reason_match = re.search(r'理由[:：]\s*(.+)', text, re.DOTALL)
        if reason_match:
            reasoning = reason_match.group(1).strip()[:200]
        else:
            reasoning = "判定理由が抽出できませんでした。"
        
        return verdict_type, confidence, reasoning


# =============================================================================
# Convergence Detection
# =============================================================================

# PURPOSE: 収束判定
class ConvergenceDetector:
    """ラリーの収束を検出
    
    CCL ~* (convergent oscillation) の実装:
    Proposer ↔ Critic が振動し、収束するまで繰り返す。
    """
    
    # 同意を示すキーワード
    AGREEMENT_MARKERS = [
        "同意", "認める", "妥当", "正しい", "おっしゃる通り",
        "その通り", "確かに", "agree", "valid point", "concede",
        "認めざるを得ない", "受け入れる", "修正する",
    ]
    
    # 固執を示すキーワード
    INSISTENCE_MARKERS = [
        "しかし", "だが", "反論", "依然として", "nevertheless",
        "however", "still", "disagree", "認められない",
    ]
    
    @classmethod
    def check(
        cls,
        history: List[RallyTurn],
        min_turns: int = 3,
    ) -> tuple:
        """収束判定
        
        Returns:
            (converged: bool, reason: str)
        """
        if len(history) < min_turns:
            return False, "最低ターン数未達"
        
        # 直近2ターンを見る
        recent = history[-2:]
        
        # 1. 相互同意: 直近2ターンの両者が同意系キーワードを含む
        both_agreeing = all(
            cls._has_agreement(turn.content) for turn in recent
        )
        if both_agreeing:
            return True, "相互同意 — 双方が合意に達した"
        
        # 2. Critic が同意に傾いた: 最後のターンが Critic で同意系
        last = history[-1]
        if (last.speaker == AgentRole.CRITIC
                and cls._has_agreement(last.content)
                and not cls._has_insistence(last.content)):
            return True, "@Critic が @Proposer の論拠を認めた"
        
        # 3. Proposer が修正を認めた: 最後のターンが Proposer で同意系
        if (last.speaker == AgentRole.PROPOSER
                and cls._has_agreement(last.content)
                and not cls._has_insistence(last.content)):
            return True, "@Proposer が @Critic の指摘を受け入れた"
        
        # 4. 意見の収束: 直近2ターンの確信度差が小さい
        if len(history) >= 4:
            recent_confs = [t.confidence for t in history[-4:]]
            conf_range = max(recent_confs) - min(recent_confs)
            if conf_range < 0.1:
                return True, f"確信度が収束 (変動幅: {conf_range:.2f})"
        
        return False, "未収束"
    
    @classmethod
    def _has_agreement(cls, text: str) -> bool:
        """同意系キーワードを含むか"""
        text_lower = text.lower()
        return any(m in text_lower for m in cls.AGREEMENT_MARKERS)
    
    @classmethod
    def _has_insistence(cls, text: str) -> bool:
        """固執系キーワードを含むか"""
        text_lower = text.lower()
        count = sum(1 for m in cls.INSISTENCE_MARKERS if m in text_lower)
        # 固執キーワードが2つ以上あれば「まだ譲らない」と判定
        return count >= 2


# =============================================================================
# Debate Engine
# =============================================================================

# PURPOSE: [L2-auto] ディベートエンジン (収束型ラリー)
class DebateEngine:
    """ディベートエンジン — 収束型ラリー
    
    Phase 1: @Proposer ↔ @Critic が収束するまでラリー (~*)
    Phase 2: @Arbiter が全ラリー履歴を見て最終判定
    """
    
    # PURPOSE: Initialize instance
    def __init__(
        self,
        proposer_model: str = "auto",
        critic_model: str = "auto",
        arbiter_model: str = "auto",
        num_critics: int = 1,  # ラリーでは1対1が基本
    ):
        self.proposer = DebateAgent(AgentRole.PROPOSER, proposer_model)
        self.critics = [
            DebateAgent(AgentRole.CRITIC, critic_model)
            for _ in range(num_critics)
        ]
        self.arbiter = DebateAgent(AgentRole.ARBITER, arbiter_model)
    
    # PURPOSE: 収束型ディベートを実行
    async def debate(
        self,
        claim: str,
        context: str = "",
        max_rounds: int = 3,
        max_rally_turns: int = 6,
        early_stop_threshold: float = 0.9,
        min_rally_turns: int = 3,
    ) -> ConsensusResult:
        """収束型ディベートを実行
        
        Args:
            claim: 検証する主張
            context: 追加コンテキスト
            max_rounds: 最大ラウンド数 (通常1で十分)
            max_rally_turns: ラリーの最大ターン数
            early_stop_threshold: 早期終了の確信度閾値
            min_rally_turns: 収束判定を開始する最低ターン数
        """
        rounds: List[DebateRound] = []
        
        for round_num in range(1, max_rounds + 1):
            rally_history: List[RallyTurn] = []
            converged = False
            convergence_reason = ""
            
            # Phase 1: Proposer ↔ Critic ラリー
            for turn_idx in range(max_rally_turns):
                if turn_idx % 2 == 0:
                    # Proposer のターン
                    turn = await self.proposer.respond(
                        claim, rally_history, context
                    )
                else:
                    # Critic のターン (最初の Critic を使用)
                    turn = await self.critics[0].respond(
                        claim, rally_history, context
                    )
                
                rally_history.append(turn)
                
                # 収束判定 (最低ターン数以降)
                converged, convergence_reason = ConvergenceDetector.check(
                    rally_history,
                    min_turns=min_rally_turns,
                )
                if converged:
                    break
            
            # 未収束の場合
            if not converged:
                convergence_reason = f"最大ターン数 ({max_rally_turns}) 到達"
            
            # DebateRound を構築 (後方互換フィールドも埋める)
            proposition = DebateArgument(
                agent_role=AgentRole.PROPOSER,
                content=rally_history[0].content if rally_history else "",
                confidence=rally_history[0].confidence if rally_history else 0.5,
            ) if rally_history else None
            
            critiques = [
                DebateArgument(
                    agent_role=AgentRole.CRITIC,
                    content=t.content,
                    confidence=t.confidence,
                )
                for t in rally_history if t.speaker == AgentRole.CRITIC
            ]
            
            rebuttal_turns = [
                t for t in rally_history
                if t.speaker == AgentRole.PROPOSER and t.turn_number > 1
            ]
            rebuttal = DebateArgument(
                agent_role=AgentRole.PROPOSER,
                content=rebuttal_turns[-1].content,
                confidence=rebuttal_turns[-1].confidence,
            ) if rebuttal_turns else None
            
            round_result = DebateRound(
                round_number=round_num,
                rally=rally_history,
                converged=converged,
                convergence_reason=convergence_reason,
                proposition=proposition,
                critiques=critiques,
                rebuttal=rebuttal,
            )
            rounds.append(round_result)
            
            # 早期終了: 高確信度で収束
            if converged and rally_history:
                last_conf = rally_history[-1].confidence
                if last_conf > early_stop_threshold:
                    break
        
        # Phase 2: Arbiter が全ラリー履歴を見て最終判定
        all_rally = []
        for r in rounds:
            all_rally.extend(r.rally)
        
        verdict = await self.arbiter.arbitrate_with_history(
            claim, all_rally, context
        )
        
        return self._build_consensus(claim, rounds, verdict)
    
    # PURPOSE: 合意結果を構築
    def _build_consensus(
        self,
        claim: str,
        rounds: List[DebateRound],
        verdict: Verdict
    ) -> ConsensusResult:
        """合意結果を構築"""
        # 多数派比率を計算
        all_confidences = []
        for r in rounds:
            for turn in r.rally:
                if turn.speaker == AgentRole.PROPOSER:
                    all_confidences.append(turn.confidence)
                elif turn.speaker == AgentRole.CRITIC:
                    all_confidences.append(1.0 - turn.confidence)  # 批判は反転
        
        if all_confidences:
            avg_support = sum(all_confidences) / len(all_confidences)
        else:
            avg_support = 0.5
        
        # 反対意見を収集
        dissent = []
        for r in rounds:
            for turn in r.rally:
                if turn.speaker == AgentRole.CRITIC and turn.confidence > 0.6:
                    summary = turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
                    dissent.append(summary)
        
        # メタデータにラリー情報を追加
        total_turns = sum(len(r.rally) for r in rounds)
        convergence_info = {
            "total_rally_turns": total_turns,
            "rounds": len(rounds),
            "converged": any(r.converged for r in rounds),
            "convergence_reasons": [
                r.convergence_reason for r in rounds if r.converged
            ],
        }
        
        return ConsensusResult(
            accepted=verdict.type == VerdictType.ACCEPT,
            confidence=verdict.confidence,
            majority_ratio=avg_support,
            verdict=verdict,
            dissent_reasons=dissent[:3],  # 上位3件
            rounds=rounds,
            metadata=convergence_info,
        )


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: CCL 実行結果を非同期検証
async def verify_execution_async(
    ccl: str,
    execution_output: str,
    context: str = "",
    debate_rounds: int = 1,  # ラリー型ではラウンド1で十分
    max_rally_turns: int = 6,
    min_confidence: float = 0.7
) -> ConsensusResult:
    """CCL 実行結果を非同期検証
    
    Args:
        ccl: CCL 式
        execution_output: 実行結果
        context: 追加コンテキスト
        debate_rounds: ディベートラウンド数 (ラリー型では通常1)
        max_rally_turns: ラリーの最大ターン数
        min_confidence: 最低確信度閾値
        
    Returns:
        ConsensusResult
    """
    claim = f"CCL '{ccl}' の実行結果 '{execution_output[:100]}...' は正確かつ信頼できる。"
    
    engine = DebateEngine()
    result = await engine.debate(
        claim,
        context=f"CCL: {ccl}\n出力: {execution_output}\n{context}",
        max_rounds=debate_rounds,
        max_rally_turns=max_rally_turns,
    )
    
    return result


# PURPOSE: CCL 実行結果を同期検証
def verify_execution(
    ccl: str,
    execution_output: str,
    context: str = "",
    debate_rounds: int = 1,
    max_rally_turns: int = 6,
    min_confidence: float = 0.7
) -> ConsensusResult:
    """CCL 実行結果を同期検証"""
    return asyncio.run(verify_execution_async(
        ccl, execution_output, context,
        debate_rounds, max_rally_turns, min_confidence
    ))


# PURPOSE: クイック検証 (単純な受理/拒否)
def quick_verify(claim: str, context: str = "") -> bool:
    """クイック検証 (単純な受理/拒否)"""
    result = asyncio.run(verify_execution_async(
        "quick_check",
        claim,
        context,
        debate_rounds=1,
        max_rally_turns=3,  # クイックは3ターンで判定
    ))
    return result.accepted


# =============================================================================
# Audit (unchanged)
# =============================================================================

@dataclass
class AuditRecord:
    """監査記録"""
    id: str
    timestamp: datetime
    ccl: str
    input_hash: str
    output_hash: str
    consensus: ConsensusResult
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuditStore:
    """監査記録のストア"""
    
    def __init__(self):
        self._records: List[AuditRecord] = []
    
    def record(self, audit: AuditRecord):
        """記録を追加"""
        self._records.append(audit)
    
    def get(self, audit_id: str) -> Optional[AuditRecord]:
        """ID で取得"""
        for r in self._records:
            if r.id == audit_id:
                return r
        return None
    
    def query(
        self,
        ccl: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 10
    ) -> List[AuditRecord]:
        """クエリ"""
        results = self._records
        if ccl:
            results = [r for r in results if r.ccl == ccl]
        if since:
            results = [r for r in results if r.timestamp >= since]
        return results[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """統計"""
        if not self._records:
            return {"total": 0, "accept_rate": 0.0}
        
        accepted = sum(1 for r in self._records if r.consensus.accepted)
        return {
            "total": len(self._records),
            "accept_rate": accepted / len(self._records),
        }


class AuditReporter:
    """監査レポーター"""
    
    @staticmethod
    def parse_period(period_str: str) -> Optional[datetime]:
        """期間文字列をパース"""
        now = datetime.now()
        if period_str == "today":
            return now.replace(hour=0, minute=0, second=0)
        elif period_str == "last_24h":
            from datetime import timedelta
            return now - timedelta(hours=24)
        elif period_str == "last_7_days":
            from datetime import timedelta
            return now - timedelta(days=7)
        elif period_str == "last_30_days":
            from datetime import timedelta
            return now - timedelta(days=30)
        return None
