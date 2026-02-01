# PROOF: [L2/インフラ] Synteleia 2層オーケストレーター
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


class SynteleiaOrchestrator:
    """Synteleia 2層オーケストレーター"""

    def __init__(
        self,
        poiesis_agents: Optional[List[AuditAgent]] = None,
        dokimasia_agents: Optional[List[AuditAgent]] = None,
        parallel: bool = True,
    ):
        """
        初期化。

        Args:
            poiesis_agents: 生成層エージェント（省略時はデフォルト3エージェント）
            dokimasia_agents: 審査層エージェント（省略時はデフォルト5エージェント）
            parallel: 並列実行するか
        """
        self.poiesis_agents = poiesis_agents or [
            OusiaAgent(),
            SchemaAgent(),
            HormeAgent(),
        ]
        self.dokimasia_agents = dokimasia_agents or [
            PerigrapheAgent(),
            KairosAgent(),
            OperatorAgent(),
            LogicAgent(),
            CompletenessAgent(),
        ]
        self.parallel = parallel

    @property
    def agents(self) -> List[AuditAgent]:
        """全エージェントを返す（互換性維持）"""
        return self.poiesis_agents + self.dokimasia_agents

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

    def audit_quick(self, target: AuditTarget) -> AuditResult:
        """
        高速監査（LogicAgent のみ）。

        CCL: /audit-
        """
        quick_orchestrator = AuditOrchestrator(
            agents=[LogicAgent()],
            parallel=False,
        )
        return quick_orchestrator.audit(target)

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
