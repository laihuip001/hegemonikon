#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Synteleia 監査エンドポイント — 6視点認知アンサンブルによる多角監査
"""
Synteleia Routes — 監査 REST API

POST   /api/synteleia/audit       — 統合監査 (全8エージェント)
POST   /api/synteleia/audit-quick — 高速監査 (LogicAgent のみ)
GET    /api/synteleia/agents      — エージェント一覧
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.synteleia")
router = APIRouter(prefix="/synteleia", tags=["synteleia"])


# --- Pydantic Models ---


# PURPOSE: 監査リクエスト
class AuditRequest(BaseModel):
    """監査対象の入力。"""
    content: str = Field(..., min_length=1, description="監査対象のテキスト")
    target_type: str = Field(
        default="generic",
        description="対象種類: ccl_output, code, thought, plan, proof, generic",
    )
    source: Optional[str] = Field(
        default=None, description="ソース識別子（ファイルパス等）"
    )


# PURPOSE: 検出された問題
class IssueItem(BaseModel):
    """監査で検出された1件の問題。"""
    agent: str
    code: str
    severity: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


# PURPOSE: エージェント個別結果
class AgentResultItem(BaseModel):
    """単一エージェントの監査結果。"""
    agent_name: str
    passed: bool
    confidence: float
    issues: list[IssueItem] = Field(default_factory=list)


# PURPOSE: 統合監査レスポンス
class AuditResponse(BaseModel):
    """統合監査レスポンス。"""
    passed: bool
    summary: str
    critical_count: int = 0
    high_count: int = 0
    total_issues: int = 0
    agent_results: list[AgentResultItem] = Field(default_factory=list)
    report: str = Field(default="", description="フォーマット済みレポート")


# PURPOSE: エージェント情報
class AgentInfo(BaseModel):
    """エージェントの基本情報。"""
    name: str
    description: str
    layer: str = Field(description="poiesis | dokimasia")


# --- Routes ---


@router.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest):
    """統合監査を実行（全8エージェント）。"""
    try:
        from mekhane.synteleia import (
            SynteleiaOrchestrator,
            AuditTarget,
            AuditTargetType,
        )

        # target_type を Enum に変換
        try:
            tt = AuditTargetType(request.target_type)
        except ValueError:
            tt = AuditTargetType.GENERIC

        target = AuditTarget(
            content=request.content,
            target_type=tt,
            source=request.source,
        )

        orchestrator = SynteleiaOrchestrator()
        result = orchestrator.audit(target)

        # レスポンス構築
        agent_results = []
        for ar in result.agent_results:
            issues = [
                IssueItem(
                    agent=i.agent,
                    code=i.code,
                    severity=i.severity.value,
                    message=i.message,
                    location=i.location,
                    suggestion=i.suggestion,
                )
                for i in ar.issues
            ]
            agent_results.append(
                AgentResultItem(
                    agent_name=ar.agent_name,
                    passed=ar.passed,
                    confidence=ar.confidence,
                    issues=issues,
                )
            )

        return AuditResponse(
            passed=result.passed,
            summary=result.summary,
            critical_count=result.critical_count,
            high_count=result.high_count,
            total_issues=len(result.all_issues),
            agent_results=agent_results,
            report=orchestrator.format_report(result),
        )
    except Exception as exc:
        logger.error("Synteleia audit failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Audit failed: {exc}")


@router.post("/audit-quick", response_model=AuditResponse)
async def audit_quick(request: AuditRequest):
    """高速監査（LogicAgent のみ）。"""
    try:
        from mekhane.synteleia import (
            SynteleiaOrchestrator,
            AuditTarget,
            AuditTargetType,
        )
        from mekhane.synteleia.dokimasia import LogicAgent

        try:
            tt = AuditTargetType(request.target_type)
        except ValueError:
            tt = AuditTargetType.GENERIC

        target = AuditTarget(
            content=request.content,
            target_type=tt,
            source=request.source,
        )

        # LogicAgent のみで高速実行
        orchestrator = SynteleiaOrchestrator(
            poiesis_agents=[],
            dokimasia_agents=[LogicAgent()],
            parallel=False,
        )
        result = orchestrator.audit(target)

        agent_results = []
        for ar in result.agent_results:
            issues = [
                IssueItem(
                    agent=i.agent,
                    code=i.code,
                    severity=i.severity.value,
                    message=i.message,
                    location=i.location,
                    suggestion=i.suggestion,
                )
                for i in ar.issues
            ]
            agent_results.append(
                AgentResultItem(
                    agent_name=ar.agent_name,
                    passed=ar.passed,
                    confidence=ar.confidence,
                    issues=issues,
                )
            )

        return AuditResponse(
            passed=result.passed,
            summary=result.summary,
            critical_count=result.critical_count,
            high_count=result.high_count,
            total_issues=len(result.all_issues),
            agent_results=agent_results,
            report=orchestrator.format_report(result),
        )
    except Exception as exc:
        logger.error("Synteleia quick audit failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Quick audit failed: {exc}")


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    """利用可能な監査エージェントの一覧を取得。"""
    try:
        from mekhane.synteleia import SynteleiaOrchestrator

        orchestrator = SynteleiaOrchestrator()
        agents = []

        for agent in orchestrator.poiesis_agents:
            agents.append(
                AgentInfo(
                    name=agent.name,
                    description=agent.description,
                    layer="poiesis",
                )
            )
        for agent in orchestrator.dokimasia_agents:
            agents.append(
                AgentInfo(
                    name=agent.name,
                    description=agent.description,
                    layer="dokimasia",
                )
            )

        return agents
    except Exception as exc:
        logger.error("Synteleia agent list failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Agent list failed: {exc}")
