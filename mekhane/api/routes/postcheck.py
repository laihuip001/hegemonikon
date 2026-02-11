# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/postcheck/* — WF ポストチェックエンドポイント
"""
Postcheck Routes — wf_postcheck モジュールのラッパー

POST /api/postcheck/run   — ポストチェック実行
GET  /api/postcheck/list  — 全WF の SEL 一覧
"""

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# PURPOSE: リクエスト/レスポンスモデル
class PostcheckRequest(BaseModel):
    """ポストチェック実行リクエスト。"""
    wf_name: str = Field(description="ワークフロー名 (例: dia, noe, boot)")
    mode: str = Field(default="", description="モード (+, -, *, 空)")
    content: str = Field(description="チェック対象テキスト")


# PURPOSE: の統一的インターフェースを実現する
class PostcheckResult(BaseModel):
    """個別チェック結果。"""
    requirement: str
    passed: bool
    detail: str = ""


# PURPOSE: の統一的インターフェースを実現する
class PostcheckResponse(BaseModel):
    """ポストチェック結果。"""
    wf_name: str
    mode: str
    passed: bool
    checks: list[PostcheckResult]
    formatted: str = ""


# PURPOSE: の統一的インターフェースを実現する
class SELItem(BaseModel):
    """SEL enforcement 項目。"""
    wf_name: str
    modes: dict[str, Any] = {}


# PURPOSE: の統一的インターフェースを実現する
class SELListResponse(BaseModel):
    """全WF の SEL enforcement 一覧。"""
    items: list[SELItem]
    total: int


router = APIRouter(prefix="/postcheck", tags=["postcheck"])


# PURPOSE: postcheck を実行する
@router.post("/run", response_model=PostcheckResponse)
async def run_postcheck(req: PostcheckRequest) -> PostcheckResponse:
    """ワークフロー出力の品質検証を実行。"""
    from scripts.wf_postcheck import postcheck

    result = await asyncio.to_thread(postcheck, req.wf_name, req.mode, req.content)

    checks = [
        PostcheckResult(
            requirement=c.get("requirement", ""),
            passed=c.get("passed", False),
            detail=c.get("detail", c.get("reason", "")),
        )
        for c in result.get("checks", [])
    ]

    return PostcheckResponse(
        wf_name=req.wf_name,
        mode=req.mode,
        passed=result.get("passed", False),
        checks=checks,
        formatted=result.get("formatted", ""),
    )


# PURPOSE: postcheck の list sel 処理を実行する
@router.get("/list", response_model=SELListResponse)
async def list_sel() -> SELListResponse:
    """全WF の sel_enforcement を一覧表示。"""
    from scripts.wf_postcheck import list_all_sel_enforcement

    all_sel = await asyncio.to_thread(list_all_sel_enforcement)

    items = [
        SELItem(wf_name=name, modes=enforcement)
        for name, enforcement in all_sel.items()
    ]

    return SELListResponse(items=items, total=len(items))
