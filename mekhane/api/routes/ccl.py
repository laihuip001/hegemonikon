# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/ccl/* — CCL パース/実行、WF レジストリ
"""
CCL Routes — Hermēneus dispatch/executor と WorkflowRegistry を API 化

POST /api/ccl/parse     — CCL 式 → AST ツリー + WF パス
POST /api/ccl/execute   — CCL 式 → Coordinator 経由実行
GET  /api/wf/list       — WorkflowRegistry 全 WF 一覧
GET  /api/wf/{name}     — WF 定義詳細
"""

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


# --- Pydantic Models ---

class CCLParseRequest(BaseModel):
    ccl: str = Field(description="CCL 式 (例: '/noe+ >> /met')")

class CCLParseResponse(BaseModel):
    success: bool
    ccl: str
    tree: Optional[str] = None
    workflows: list[str] = []
    wf_paths: dict[str, str] = {}
    plan_template: Optional[str] = None
    error: Optional[str] = None

class CCLExecuteRequest(BaseModel):
    ccl: str = Field(description="CCL 式")
    context: str = Field(default="", description="実行コンテキスト")

class CCLExecuteResponse(BaseModel):
    success: bool
    ccl: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None

class WFSummary(BaseModel):
    name: str
    description: str
    ccl: str = ""
    modes: list[str] = []

class WFListResponse(BaseModel):
    total: int
    workflows: list[WFSummary]

class WFDetailResponse(BaseModel):
    name: str
    description: str
    ccl: str = ""
    stages: list[dict[str, Any]] = []
    modes: list[str] = []
    source_path: Optional[str] = None
    raw_content: Optional[str] = None
    metadata: dict[str, Any] = {}


# --- Router ---

router = APIRouter(tags=["ccl"])


@router.post("/ccl/parse", response_model=CCLParseResponse)
async def parse_ccl(request: CCLParseRequest) -> CCLParseResponse:
    """CCL 式をパースし、AST ツリー + WF パスを返す。"""
    try:
        from hermeneus.src.dispatch import dispatch
        result = dispatch(request.ccl)
        return CCLParseResponse(
            success=result.get("success", False),
            ccl=request.ccl,
            tree=result.get("tree"),
            workflows=result.get("workflows", []),
            wf_paths=result.get("wf_paths", {}),
            plan_template=result.get("plan_template"),
            error=result.get("error"),
        )
    except Exception as e:
        return CCLParseResponse(
            success=False,
            ccl=request.ccl,
            error=str(e),
        )


@router.post("/ccl/execute", response_model=CCLExecuteResponse)
async def execute_ccl(request: CCLExecuteRequest) -> CCLExecuteResponse:
    """CCL 式を Synergeia Coordinator 経由で実行する。"""
    try:
        from synergeia.coordinator import coordinate
        result = coordinate(request.ccl, context=request.context)
        return CCLExecuteResponse(
            success=True,
            ccl=request.ccl,
            result=result,
        )
    except Exception as e:
        return CCLExecuteResponse(
            success=False,
            ccl=request.ccl,
            error=str(e),
        )


@router.get("/wf/list", response_model=WFListResponse)
async def list_workflows() -> WFListResponse:
    """WorkflowRegistry から全 WF 一覧を取得。"""
    try:
        from hermeneus.src.registry import get_default_registry
        registry = get_default_registry()
        all_wfs = registry.load_all()

        summaries = []
        for wf in all_wfs.values():
            summaries.append(WFSummary(
                name=wf.name,
                description=wf.description,
                ccl=wf.ccl,
                modes=wf.modes,
            ))

        return WFListResponse(
            total=len(summaries),
            workflows=sorted(summaries, key=lambda w: w.name),
        )
    except Exception as e:
        return WFListResponse(total=0, workflows=[])


@router.get("/wf/{name}", response_model=WFDetailResponse)
async def get_workflow(name: str) -> WFDetailResponse:
    """WF 定義の詳細を取得。"""
    try:
        from hermeneus.src.registry import get_default_registry
        registry = get_default_registry()
        wf = registry.get(name)

        if wf is None:
            return WFDetailResponse(
                name=name,
                description="Not found",
                metadata={"error": f"Workflow '{name}' not found"},
            )

        return WFDetailResponse(
            name=wf.name,
            description=wf.description,
            ccl=wf.ccl,
            stages=[{"name": s.name, "description": s.description} for s in wf.stages],
            modes=wf.modes,
            source_path=str(wf.source_path) if wf.source_path else None,
            metadata=wf.metadata,
        )
    except Exception as e:
        return WFDetailResponse(
            name=name,
            description="Error",
            metadata={"error": str(e)},
        )
