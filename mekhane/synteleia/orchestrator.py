# PROOF: [L2/インフラ] <- mekhane/synteleia/ Synteleia 2層オーケストレーター
"""
Synteleia Orchestrator

Poiēsis (生成層) と Dokimasia (審査層) を統合処理する。

CCL:
- @syn·  内積モード（両層を独立実行し統合）
- @syn×  外積モード（3×3 交差検証）
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from .base import (
    AgentResult,
    AuditAgent,
    AuditResult,
    AuditSeverity,
    AuditTarget,
)

# Poiēsis 生成層
from .poiesis import OusiaAgent, SchemaAgent, HormeAgent

# Dokimasia 審査層
from .dokimasia import (
    PerigrapheAgent,
    KairosAgent,
    OperatorAgent,
    LogicAgent,
    CompletenessAgent,
)


# PURPOSE: Synteleia 2層オーケストレーター
class SynteleiaOrchestrator:
    """Synteleia 2層オーケストレーター"""

    # PURPOSE: [L2-auto] 初期化。
    def __init__(
        self,
        poiesis_agents: Optional[List[AuditAgent]] = None,
        dokimasia_agents: Optional[List[AuditAgent]] = None,
        parallel: bool = True,
    ):
        """
        初期化。

        Args:
            poiesis_agents: 生成層エージェント（省略時はデフォルト3エージェント、空リストで0エージェント）
            dokimasia_agents: 審査層エージェント（省略時はデフォルト5エージェント、空リストで0エージェント）
            parallel: 並列実行するか
        """
        self.poiesis_agents = [
            OusiaAgent(),
            SchemaAgent(),
            HormeAgent(),
        ] if poiesis_agents is None else poiesis_agents
        self.dokimasia_agents = [
            PerigrapheAgent(),
            KairosAgent(),
            OperatorAgent(),
            LogicAgent(),
            CompletenessAgent(),
        ] if dokimasia_agents is None else dokimasia_agents
        self.parallel = parallel

    # PURPOSE: 全エージェントを返す（互換性維持）
    @property
    def agents(self) -> List[AuditAgent]:
        """全エージェントを返す（互換性維持）"""
        return self.poiesis_agents + self.dokimasia_agents

    # PURPOSE: L1 + L2 統合監査 (/dia+ 用ファクトリ)
    @classmethod
    def with_l2(cls, backend=None) -> "SynteleiaOrchestrator":
        """
        L1 全エージェント + L2 SemanticAgent を含むオーケストレータを生成。

        /dia+ ワークフローから呼ばれる想定。
        L2 バックエンドが利用不可の場合も安全にフォールバック。

        Args:
            backend: LLM バックエンド（省略時は自動選択）

        Returns:
            SynteleiaOrchestrator: L1+L2 統合オーケストレータ
        """
        from .dokimasia.semantic_agent import SemanticAgent

        orchestrator = cls()  # L1 デフォルト構成
        semantic = SemanticAgent(backend=backend)
        orchestrator.dokimasia_agents.append(semantic)
        return orchestrator

    @classmethod
    # PURPOSE: [L2-auto] L1 全エージェント + Layer B Multi-LLM アンサンブルを含むオーケストレータ。
    def with_multi_l2(cls) -> "SynteleiaOrchestrator":
        """
        L1 全エージェント + Layer B Multi-LLM アンサンブルを含むオーケストレータ。

        3 LLM (Gemini Pro / Claude Opus / GPT-OSS) に異なる persona を付与し、
        confidence-weighted majority voting で統合判断する。

        CRITICAL/HIGH 検出時に自動発動される想定。

        Returns:
            SynteleiaOrchestrator: L1 + Multi-L2 統合オーケストレータ
        """
        from .dokimasia.multi_semantic_agent import MultiSemanticAgent

        orchestrator = cls()  # L1 デフォルト構成
        multi_agent = MultiSemanticAgent.default()
        orchestrator.dokimasia_agents.append(multi_agent)
        return orchestrator

    # PURPOSE: 監査を実行。
    def audit(self, target: AuditTarget) -> AuditResult:
        """
        監査を実行。

        Args:
            target: 監査対象

        Returns:
            AuditResult: 統合監査結果
        """
        agent_results: List[AgentResult] = []

        if self.parallel and len(self.agents) > 1:
            # 並列実行
            agent_results = self._audit_parallel(target)
        else:
            # 逐次実行
            agent_results = self._audit_sequential(target)

        # 結果を統合
        return self._aggregate_results(target, agent_results)

    # PURPOSE: [L2-auto] 並列監査
    def _audit_parallel(self, target: AuditTarget) -> List[AgentResult]:
        """並列監査"""
        results = []

        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            futures = {
                executor.submit(agent.audit, target): agent
                for agent in self.agents
                if agent.supports(target.target_type)
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    agent = futures[future]
                    results.append(
                        AgentResult(
                            agent_name=agent.name,
                            passed=False,
                            issues=[],
                            confidence=0.0,
                            metadata={"error": str(e)},
                        )
                    )

        return results

    # PURPOSE: [L2-auto] 逐次監査
    def _audit_sequential(self, target: AuditTarget) -> List[AgentResult]:
        """逐次監査"""
        results = []

        for agent in self.agents:
            if agent.supports(target.target_type):
                try:
                    result = agent.audit(target)
                    results.append(result)
                except Exception as e:
                    results.append(
                        AgentResult(
                            agent_name=agent.name,
                            passed=False,
                            issues=[],
                            confidence=0.0,
                            metadata={"error": str(e)},
                        )
                    )

        return results

    # PURPOSE: [L2-auto] 結果を統合
    def _aggregate_results(
        self, target: AuditTarget, agent_results: List[AgentResult]
    ) -> AuditResult:
        """結果を統合"""
        # 全エージェントが PASS なら PASS
        all_passed = all(ar.passed for ar in agent_results)

        # サマリー生成
        total_issues = sum(len(ar.issues) for ar in agent_results)
        critical_count = sum(
            1
            for ar in agent_results
            for i in ar.issues
            if i.severity == AuditSeverity.CRITICAL
        )
        high_count = sum(
            1
            for ar in agent_results
            for i in ar.issues
            if i.severity == AuditSeverity.HIGH
        )

        if all_passed:
            summary = f"✅ PASS — {len(agent_results)} agents, {total_issues} issues (none critical/high)"
        else:
            summary = f"❌ FAIL — {critical_count} critical, {high_count} high issues"

        return AuditResult(
            target=target,
            agent_results=agent_results,
            passed=all_passed,
            summary=summary,
        )

    # PURPOSE: 高速監査（LogicAgent のみ）。
    def audit_quick(self, target: AuditTarget) -> AuditResult:
        """
        高速監査（LogicAgent のみ）。

        CCL: /audit-
        """
        quick_orchestrator = SynteleiaOrchestrator(
            poiesis_agents=[],
            dokimasia_agents=[LogicAgent()],
            parallel=False,
        )
        return quick_orchestrator.audit(target)

    # PURPOSE: 監査結果をフォーマット
    def format_report(self, result: AuditResult) -> str:
        """監査結果をフォーマット"""
        lines = [
            "=" * 60,
            "Hegemonikón Audit Report",
            "=" * 60,
            "",
            f"Target: {result.target.target_type.value}",
            f"Status: {result.summary}",
            "",
        ]

        for ar in result.agent_results:
            lines.append(f"--- {ar.agent_name} ---")
            lines.append(f"Passed: {'✅' if ar.passed else '❌'}")
            lines.append(f"Confidence: {ar.confidence:.0%}")

            if ar.issues:
                lines.append(f"Issues ({len(ar.issues)}):")
                for issue in ar.issues:
                    severity_icon = {
                        AuditSeverity.CRITICAL: "🔴",
                        AuditSeverity.HIGH: "🟠",
                        AuditSeverity.MEDIUM: "🟡",
                        AuditSeverity.LOW: "🟢",
                        AuditSeverity.INFO: "⚪",
                    }.get(issue.severity, "⚪")
                    lines.append(f"  {severity_icon} [{issue.code}] {issue.message}")
                    if issue.suggestion:
                        lines.append(f"      💡 {issue.suggestion}")
            lines.append("")

        return "\n".join(lines)

    # PURPOSE: 監査結果から Sympatheia WBC アラートを生成
    def to_wbc_alert(self, result: AuditResult) -> Optional[dict]:
        """
        監査結果を Sympatheia WBC アラート形式に変換。

        HIGH/CRITICAL が検出された場合のみアラートを生成。
        それ以外は None を返す。

        Returns:
            dict | None: WBC アラートパラメータ or None
        """
        if result.critical_count == 0 and result.high_count == 0:
            return None

        # severity 決定: CRITICAL > HIGH
        severity = "critical" if result.critical_count > 0 else "high"

        # 問題サマリー
        issue_lines = []
        for ar in result.agent_results:
            for issue in ar.issues:
                if issue.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH):
                    issue_lines.append(
                        f"[{issue.severity.value}] {ar.agent_name}: {issue.message}"
                    )

        details = (
            f"Synteleia 監査: {result.critical_count} CRITICAL, "
            f"{result.high_count} HIGH 検出\n"
            + "\n".join(issue_lines[:10])  # 最大10件
        )

        return {
            "details": details,
            "severity": severity,
            "source": "synteleia",
            "files": [result.target.source] if result.target.source else [],
        }
