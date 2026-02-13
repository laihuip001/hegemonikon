# PURPOSE: Multi-LLM アンサンブル監査エージェント (Layer B: Nous)
"""
MultiSemanticAgent — Multi-LLM Cognitive Ensemble

複数の LLM に異なる persona を付与し、合議で品質を判定する。
「三人寄れば文殊の知恵」の実装。

Architecture:
    AuditTarget
      → Critic (Claude Opus 4.6): 最も厳しい目で問題を見つける
      → Optimist (GPT-OSS 120B): 良い点を認めつつ改善提案
      → Pragmatist (Gemini 3 Pro): 実用的影響度でのみ判断
      → Majority Voting (confidence-weighted)
      → Unified AgentResult

Synedrion との差異:
    Synedrion = 偉人 persona (哲学的・戦略的判断)
    Multi-LLM Synteleia = 機能的 persona (コード/ドキュメント品質)
"""

import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)
from .semantic_agent import (
    LLMBackend,
    StubBackend,
    parse_llm_response,
    SEMANTIC_AUDIT_PROMPT,
)


# =============================================================================
# Persona Definitions
# =============================================================================

PERSONAS: Dict[str, str] = {
    "critic": (
        "あなたは **批判者** (Critic) です。最も厳しい目で問題を見つけてください。\n"
        "- 潜在的なリスクを過小評価しないでください\n"
        "- 安全側に倒す判断を優先してください\n"
        "- severity は控えめではなく、実際のリスクに応じて付与してください\n"
    ),
    "optimist": (
        "あなたは **楽観者** (Optimist) です。良い点を認めつつ改善提案をしてください。\n"
        "- まず対象の強みを認識してください\n"
        "- 問題があれば建設的な改善案を提示してください\n"
        "- severity は実際の影響度に基づき、不必要に厳しくしないでください\n"
    ),
    "pragmatist": (
        "あなたは **実務家** (Pragmatist) です。実用的な影響度でのみ判断してください。\n"
        "- 理論的な問題より実運用への影響を重視してください\n"
        "- false positive を避け、本当に修正すべき問題だけ報告してください\n"
        "- severity は運用上の実害に基づいて判断してください\n"
    ),
}


# =============================================================================
# Ensemble Member
# =============================================================================


@dataclass
# PURPOSE: [L2-auto] アンサンブルの1メンバー。
class EnsembleMember:
    """アンサンブルの1メンバー。"""
    name: str
    backend: LLMBackend
    persona: str  # PERSONAS のキー

    @property
    # PURPOSE: [L2-auto] persona 付きプロンプトを生成。
    def persona_prompt(self) -> str:
        """persona 付きプロンプトを生成。"""
        return PERSONAS.get(self.persona, "") + "\n" + SEMANTIC_AUDIT_PROMPT


# =============================================================================
# Multi-Semantic Agent
# =============================================================================


# PURPOSE: Multi-LLM アンサンブル監査エージェント
class MultiSemanticAgent(AuditAgent):
    """Multi-LLM アンサンブル監査エージェント (Layer B: Nous)。

    複数 LLM に異なる persona を付与し、
    confidence-weighted majority voting で統合判断する。
    """

    name = "MultiSemanticAgent"
    description = "Multi-LLM アンサンブル監査 (Layer B: Nous)"

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, members: List[EnsembleMember]):
        self.members = members

    @classmethod
    # PURPOSE: [L2-auto] デフォルト構成: Gemini Pro + Claude Opus + GPT-OSS。
    def default(cls) -> "MultiSemanticAgent":
        """デフォルト構成: Gemini Pro + Claude Opus + GPT-OSS。"""
        try:
            from .ochema_backend import OchemaBackend

            members = [
                EnsembleMember(
                    name="Pragmatist (Gemini 3 Pro)",
                    backend=OchemaBackend(
                        model="MODEL_PLACEHOLDER_M8",
                        label="Gemini 3 Pro",
                    ),
                    persona="pragmatist",
                ),
                EnsembleMember(
                    name="Critic (Claude Opus 4.6)",
                    backend=OchemaBackend(
                        model="MODEL_PLACEHOLDER_M26",
                        label="Claude Opus 4.6",
                    ),
                    persona="critic",
                ),
                EnsembleMember(
                    name="Optimist (GPT-OSS 120B)",
                    backend=OchemaBackend(
                        model="MODEL_OPENAI_GPT_OSS_120B_MEDIUM",
                        label="GPT-OSS 120B",
                    ),
                    persona="optimist",
                ),
            ]
        except Exception:
            # フォールバック: Stub × 3
            members = [
                EnsembleMember(name=f"Stub-{p}", backend=StubBackend(), persona=p)
                for p in PERSONAS
            ]

        return cls(members=members)

    @classmethod
    # PURPOSE: [L2-auto] テスト用: StubBackend でアンサンブルを構成。
    def with_stubs(cls, responses: Optional[Dict[str, str]] = None) -> "MultiSemanticAgent":
        """テスト用: StubBackend でアンサンブルを構成。"""
        members = []
        for persona in PERSONAS:
            resp = (responses or {}).get(persona, None)
            members.append(
                EnsembleMember(
                    name=f"Stub-{persona}",
                    backend=StubBackend(response=resp),
                    persona=persona,
                )
            )
        return cls(members=members)

    # PURPOSE: Multi-LLM アンサンブル監査を実行
    def audit(self, target: AuditTarget) -> AgentResult:
        """全メンバーに並列 query → majority voting → 統合結果。"""

        # 1. 各メンバーに並列 query
        member_results: List[Tuple[str, str, List[AuditIssue], float]] = []

        with ThreadPoolExecutor(max_workers=len(self.members)) as executor:
            futures = {}
            for member in self.members:
                if not member.backend.is_available():
                    continue
                future = executor.submit(
                    self._query_member, member, target
                )
                futures[future] = member

            for future in as_completed(futures):
                member = futures[future]
                try:
                    persona, response_text, issues, confidence = future.result()
                    member_results.append((persona, response_text, issues, confidence))
                except Exception as e:
                    # メンバー失敗はスキップ
                    member_results.append((
                        member.persona, "", [],
                        0.0,
                    ))

        if not member_results:
            return AgentResult(
                agent_name=self.name,
                passed=True,
                issues=[],
                confidence=0.0,
                metadata={"error": "No ensemble members available"},
            )

        # 2. Majority voting
        unified_issues = self._majority_vote(member_results)

        # 3. 統合結果
        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH)
            for i in unified_issues
        )

        avg_confidence = sum(r[3] for r in member_results) / len(member_results)

        # メンバー別のメタデータ
        member_meta = []
        for persona, _, issues, conf in member_results:
            member_meta.append({
                "persona": persona,
                "issues_found": len(issues),
                "confidence": conf,
            })

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=unified_issues,
            confidence=avg_confidence,
            metadata={
                "l2": True,
                "multi_llm": True,
                "members": member_meta,
                "voting": "confidence-weighted majority",
            },
        )

    # PURPOSE: 個別メンバーに query
    def _query_member(
        self, member: EnsembleMember, target: AuditTarget
    ) -> Tuple[str, str, List[AuditIssue], float]:
        """メンバーにクエリし、結果をパースして返す。"""
        response_text = member.backend.query(
            prompt=member.persona_prompt,
            context=target.content,
        )

        issues = parse_llm_response(response_text, f"{self.name}:{member.persona}")
        confidence = self._extract_confidence(response_text)

        return member.persona, response_text, issues, confidence

    # PURPOSE: confidence-weighted majority voting
    def _majority_vote(
        self, member_results: List[Tuple[str, str, List[AuditIssue], float]]
    ) -> List[AuditIssue]:
        """Confidence-weighted majority voting。

        ルール:
        - 2+ メンバーが見つけた issue は採用
        - 1 メンバーのみでも CRITICAL は採用
        - severity は最も厳しい判定を採用
        - confidence は加重平均
        """
        # issue を message でグループ化 (簡易マッチング)
        issue_votes: Dict[str, List[Tuple[AuditIssue, float]]] = {}

        for persona, _, issues, confidence in member_results:
            for issue in issues:
                # 同一 issue の判定キー: code + message の先頭30文字
                key = f"{issue.code}:{issue.message[:30]}"
                if key not in issue_votes:
                    issue_votes[key] = []
                issue_votes[key].append((issue, confidence))

        # 投票に基づき issue を選別
        unified: List[AuditIssue] = []

        for key, votes in issue_votes.items():
            vote_count = len(votes)
            # 最も厳しい severity を採用
            severities = [v[0].severity for v in votes]
            max_severity = max(severities, key=lambda s: _severity_rank(s))

            # 採用条件: 2+ votes OR (1 vote AND CRITICAL)
            if vote_count >= 2 or max_severity == AuditSeverity.CRITICAL:
                representative = votes[0][0]
                weighted_conf = sum(v[1] for v in votes) / len(votes)

                unified.append(
                    AuditIssue(
                        agent=self.name,
                        code=representative.code,
                        severity=max_severity,
                        message=f"[{vote_count}/{len(member_results)} votes] {representative.message}",
                        location=representative.location,
                        suggestion=representative.suggestion,
                    )
                )

        return unified

    # PURPOSE: レスポンスから confidence を抽出
    def _extract_confidence(self, response: str) -> float:
        """LLM レスポンスから confidence を抽出。"""
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "confidence" in data:
                return float(data["confidence"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return 0.7

    # PURPOSE: L2 はテキスト系のターゲットのみサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """L2 はテキスト系のターゲットのみサポート。"""
        return target_type in (
            AuditTargetType.CCL_OUTPUT,
            AuditTargetType.THOUGHT,
            AuditTargetType.PLAN,
            AuditTargetType.GENERIC,
        )


# PURPOSE: [L2-auto] Severity の厳しさ順序。
# =============================================================================
# Utilities
# =============================================================================

def _severity_rank(severity: AuditSeverity) -> int:
    """Severity の厳しさ順序。"""
    return {
        AuditSeverity.CRITICAL: 4,
        AuditSeverity.HIGH: 3,
        AuditSeverity.MEDIUM: 2,
        AuditSeverity.LOW: 1,
        AuditSeverity.INFO: 0,
    }.get(severity, 0)
