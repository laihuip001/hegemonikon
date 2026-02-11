# PROOF: [L2/インフラ] <- hermeneus/src/ Multi-Agent Debate 検証器
"""
Hermēneus Verifier — Multi-Agent Debate による検証

複数のAIエージェント (Proposer, Critic, Arbiter) が
CCL実行結果を相互検証し、合意形成を行う。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# =============================================================================
# Types
# =============================================================================

# Regex patterns for parsing verdicts
CONFIDENCE_PATTERN = re.compile(r'(\d+)\s*%')
REASONING_PATTERN = re.compile(r'理由[:：]\s*(.+)', re.DOTALL)


class AgentRole(Enum):
    """エージェントの役割"""
    PROPOSER = "proposer"    # 主張を支持
    CRITIC = "critic"        # 批判・反論
    ARBITER = "arbiter"      # 最終判定


class VerdictType(Enum):
    """判定タイプ"""
    ACCEPT = "accept"        # 受理
    REJECT = "reject"        # 拒否
    UNCERTAIN = "uncertain"  # 不確定


@dataclass
class DebateArgument:
    """ディベート引数"""
    agent_role: AgentRole
    content: str
    confidence: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Verdict:
    """判定結果"""
    type: VerdictType
    reasoning: str
    confidence: float
    arbiter_notes: Optional[str] = None


@dataclass
class DebateRound:
    """ディベートラウンド"""
    round_number: int
    proposition: DebateArgument
    critiques: List[DebateArgument]
    rebuttal: Optional[DebateArgument] = None


@dataclass
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

class DebateAgent:
    """ディベートエージェント
    
    役割に応じて主張生成、批判、判定を行う。
    """
    
    def __init__(
        self,
        role: AgentRole,
        model: str = "openai/gpt-4o",
        temperature: float = 0.7
    ):
        self.role = role
        self.model = model
        self.temperature = temperature
        self._llm_available = self._check_llm()
    
    def _check_llm(self) -> bool:
        """LLM が利用可能か確認"""
        try:
            from openai import OpenAI  # noqa: F401
            return True
        except ImportError:
            return False
    
    async def propose(self, claim: str, context: str = "") -> DebateArgument:
        """主張を支持する論拠を生成"""
        prompt = f"""
あなたは「支持者 (Proposer)」として、以下の主張を支持する論拠を提示してください。

主張: {claim}

コンテキスト: {context}

論拠を3-5点、明確に述べてください。
"""
        response = await self._generate(prompt)
        return DebateArgument(
            agent_role=AgentRole.PROPOSER,
            content=response,
            confidence=self._estimate_confidence(response)
        )
    
    async def critique(
        self,
        claim: str,
        supporting_argument: str,
        context: str = ""
    ) -> DebateArgument:
        """批判・反論を生成"""
        prompt = f"""
あなたは「批評者 (Critic)」として、以下の主張と論拠に対して批判的分析を行ってください。

主張: {claim}

支持論拠:
{supporting_argument}

コンテキスト: {context}

以下の観点から批判してください:
1. 論理的な飛躍や誤謬
2. 証拠の不足
3. 代替解釈の可能性
4. 潜在的リスク
"""
        response = await self._generate(prompt)
        return DebateArgument(
            agent_role=AgentRole.CRITIC,
            content=response,
            confidence=self._estimate_confidence(response)
        )
    
    async def arbitrate(
        self,
        claim: str,
        for_arguments: List[str],
        against_arguments: List[str],
        context: str = ""
    ) -> Verdict:
        """最終判定を下す"""
        for_text = "\n".join(f"- {arg}" for arg in for_arguments)
        against_text = "\n".join(f"- {arg}" for arg in against_arguments)
        
        prompt = f"""
あなたは「調停者 (Arbiter)」として、以下の主張について最終判定を下してください。

主張: {claim}

【支持論拠】
{for_text}

【反対論拠】
{against_text}

コンテキスト: {context}

以下の形式で判定してください:
判定: [ACCEPT/REJECT/UNCERTAIN]
確信度: [0-100]%
理由: [判定の根拠を簡潔に]
"""
        response = await self._generate(prompt)
        verdict_type, confidence, reasoning = self._parse_verdict(response)
        
        return Verdict(
            type=verdict_type,
            reasoning=reasoning,
            confidence=confidence,
            arbiter_notes=response
        )
    
    async def rebut(
        self,
        claim: str,
        critique: str,
        original_argument: str
    ) -> DebateArgument:
        """反論を生成"""
        prompt = f"""
あなたは「支持者 (Proposer)」として、批判に対して反論してください。

元の主張: {claim}

あなたの元の論拠:
{original_argument}

批判:
{critique}

批判に対する反論を述べてください。
"""
        response = await self._generate(prompt)
        return DebateArgument(
            agent_role=AgentRole.PROPOSER,
            content=response,
            confidence=self._estimate_confidence(response)
        )
    
    async def _generate(self, prompt: str) -> str:
        """LLM で生成"""
        if not self._llm_available:
            return self._fallback_generate(prompt)
        
        import os
        from openai import AsyncOpenAI
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return self._fallback_generate(prompt)
        
        client = AsyncOpenAI(api_key=api_key)
        
        try:
            response = await client.chat.completions.create(
                model=self.model.replace("openai/", ""),
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Error: {e}] " + self._fallback_generate(prompt)
    
    def _fallback_generate(self, prompt: str) -> str:
        """フォールバック生成 (LLM なし)"""
        if self.role == AgentRole.PROPOSER:
            return "この主張は論理的に妥当であり、支持できる。"
        elif self.role == AgentRole.CRITIC:
            return "この主張には検証が必要な仮定が含まれている。"
        else:
            return "判定: UNCERTAIN\n確信度: 50%\n理由: 十分な情報がない。"
    
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
        conf_match = CONFIDENCE_PATTERN.search(text)
        if conf_match:
            confidence = int(conf_match.group(1)) / 100.0
        else:
            confidence = 0.5
        
        # 理由
        reason_match = REASONING_PATTERN.search(text)
        if reason_match:
            reasoning = reason_match.group(1).strip()[:200]
        else:
            reasoning = "判定理由が抽出できませんでした。"
        
        return verdict_type, confidence, reasoning


# =============================================================================
# Debate Engine
# =============================================================================

class DebateEngine:
    """ディベートエンジン
    
    複数エージェント間のディベートを管理し、合意形成を行う。
    """
    
    def __init__(
        self,
        proposer_model: str = "openai/gpt-4o",
        critic_model: str = "openai/gpt-4o",
        arbiter_model: str = "openai/gpt-4o",
        num_critics: int = 2
    ):
        self.proposer = DebateAgent(AgentRole.PROPOSER, proposer_model)
        self.critics = [
            DebateAgent(AgentRole.CRITIC, critic_model)
            for _ in range(num_critics)
        ]
        self.arbiter = DebateAgent(AgentRole.ARBITER, arbiter_model)
    
    async def debate(
        self,
        claim: str,
        context: str = "",
        max_rounds: int = 3,
        early_stop_threshold: float = 0.9
    ) -> ConsensusResult:
        """ディベートを実行"""
        rounds: List[DebateRound] = []
        for_arguments: List[str] = []
        against_arguments: List[str] = []
        
        for round_num in range(1, max_rounds + 1):
            # 1. Proposer が主張を支持
            proposition = await self.proposer.propose(claim, context)
            for_arguments.append(proposition.content)
            
            # 2. Critics が批判
            critique_tasks = [
                critic.critique(claim, proposition.content, context)
                for critic in self.critics
            ]
            critiques = await asyncio.gather(*critique_tasks)
            against_arguments.extend([c.content for c in critiques])
            
            # 3. Proposer が反論
            if critiques:
                rebuttal = await self.proposer.rebut(
                    claim,
                    critiques[0].content,
                    proposition.content
                )
                for_arguments.append(rebuttal.content)
            else:
                rebuttal = None
            
            round_result = DebateRound(
                round_number=round_num,
                proposition=proposition,
                critiques=list(critiques),
                rebuttal=rebuttal
            )
            rounds.append(round_result)
            
            # 4. 早期終了チェック
            if proposition.confidence > early_stop_threshold:
                break
        
        # 5. Arbiter が最終判定
        verdict = await self.arbiter.arbitrate(
            claim,
            for_arguments,
            against_arguments,
            context
        )
        
        # 6. 合意結果を構築
        return self._build_consensus(claim, rounds, verdict)
    
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
            all_confidences.append(r.proposition.confidence)
            for c in r.critiques:
                all_confidences.append(1.0 - c.confidence)  # 批判は反転
        
        if all_confidences:
            avg_support = sum(all_confidences) / len(all_confidences)
        else:
            avg_support = 0.5
        
        # 反対意見を収集
        dissent = []
        for r in rounds:
            for c in r.critiques:
                if c.confidence > 0.6:  # 強い批判のみ
                    summary = c.content[:100] + "..." if len(c.content) > 100 else c.content
                    dissent.append(summary)
        
        return ConsensusResult(
            accepted=verdict.type == VerdictType.ACCEPT,
            confidence=verdict.confidence,
            majority_ratio=avg_support,
            verdict=verdict,
            dissent_reasons=dissent[:3],  # 上位3件
            rounds=rounds
        )


# =============================================================================
# Convenience Functions
# =============================================================================

async def verify_execution_async(
    ccl: str,
    execution_output: str,
    context: str = "",
    debate_rounds: int = 3,
    min_confidence: float = 0.7
) -> ConsensusResult:
    """CCL 実行結果を非同期検証
    
    Args:
        ccl: CCL 式
        execution_output: 実行結果
        context: 追加コンテキスト
        debate_rounds: ディベートラウンド数
        min_confidence: 最低確信度閾値
        
    Returns:
        ConsensusResult
    """
    claim = f"CCL '{ccl}' の実行結果 '{execution_output[:100]}...' は正確かつ信頼できる。"
    
    engine = DebateEngine()
    result = await engine.debate(
        claim,
        context=f"CCL: {ccl}\n出力: {execution_output}\n{context}",
        max_rounds=debate_rounds
    )
    
    return result


def verify_execution(
    ccl: str,
    execution_output: str,
    context: str = "",
    debate_rounds: int = 3,
    min_confidence: float = 0.7
) -> ConsensusResult:
    """CCL 実行結果を同期検証"""
    return asyncio.run(verify_execution_async(
        ccl, execution_output, context, debate_rounds, min_confidence
    ))


def quick_verify(claim: str, context: str = "") -> bool:
    """クイック検証 (単純な受理/拒否)"""
    result = asyncio.run(verify_execution_async(
        "quick_check",
        claim,
        context,
        debate_rounds=1
    ))
    return result.accepted
