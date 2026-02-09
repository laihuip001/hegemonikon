# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/dendron/* — コード品質・存在証明エンドポイント
"""
Dendron Routes — dendron/checker モジュールのラッパー

GET  /api/dendron/report          — 全体レポート (サマリー)
GET  /api/dendron/report?detail=full — 全体レポート (詳細)
POST /api/dendron/check            — 個別ファイルチェック
"""

import asyncio
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# PURPOSE: レスポンスモデル
class DendronFileResult(BaseModel):
    """個別ファイルのチェック結果。"""
    path: str
    has_proof: bool
    level: str = ""
    parent: str = ""
    issues: list[str] = []


# PURPOSE: レポートサマリーモデル
class DendronSummary(BaseModel):
    """Dendron レポートサマリー。"""
    total_files: int = 0
    files_with_proof: int = 0
    files_without_proof: int = 0
    coverage_percent: float = 0.0
    total_dirs: int = 0
    dirs_with_proof: int = 0
    issues: list[str] = []


# PURPOSE: レポート全体モデル
class DendronReportResponse(BaseModel):
    """Dendron レポート。"""
    summary: DendronSummary
    file_results: list[DendronFileResult] = Field(
        default_factory=list,
        description="detail=full 時のみ展開",
    )


class DendronCheckRequest(BaseModel):
    """個別ファイルチェックリクエスト。"""
    path: str = Field(description="チェック対象のファイルパス")


class DendronCheckResponse(BaseModel):
    """個別ファイルチェック結果。"""
    path: str
    result: DendronFileResult | None = None
    error: str = ""


router = APIRouter(prefix="/dendron", tags=["dendron"])


# PURPOSE: DendronChecker の結果をサマリーに変換
def _checker_to_summary(checker, target_dir: Path) -> tuple[DendronSummary, list[DendronFileResult]]:
    """DendronChecker の結果をレスポンス型に変換。"""
    file_results: list[DendronFileResult] = []
    issues: list[str] = []
    files_with = 0
    files_without = 0
    total_dirs = 0
    dirs_with = 0

    # ファイルチェック
    py_files = list(target_dir.rglob("*.py"))
    for f in py_files:
        if f.name.startswith("__"):
            continue
        proof = checker.check_file_proof(f)
        has_proof = proof.has_proof if hasattr(proof, "has_proof") else bool(proof)

        if has_proof:
            files_with += 1
        else:
            files_without += 1
            issues.append(f"Missing PROOF: {f.relative_to(target_dir)}")

        file_results.append(DendronFileResult(
            path=str(f.relative_to(target_dir)),
            has_proof=has_proof,
            level=str(getattr(proof, "level", "") or ""),
            parent=str(getattr(proof, "parent", "") or ""),
        ))

    # ディレクトリチェック
    for d in target_dir.rglob("*"):
        if d.is_dir() and not d.name.startswith((".", "__")):
            total_dirs += 1
            proof_md = d / "PROOF.md"
            if proof_md.exists():
                dirs_with += 1

    total = files_with + files_without
    coverage = (files_with / total * 100) if total > 0 else 0.0

    summary = DendronSummary(
        total_files=total,
        files_with_proof=files_with,
        files_without_proof=files_without,
        coverage_percent=round(coverage, 1),
        total_dirs=total_dirs,
        dirs_with_proof=dirs_with,
        issues=issues[:20],  # 上位20件に制限
    )

    return summary, file_results


@router.get("/report", response_model=DendronReportResponse)
async def dendron_report(
    detail: str = Query("summary", description="summary | full"),
) -> DendronReportResponse:
    """Dendron コード品質レポート。"""
    from mekhane.dendron.checker import DendronChecker

    target_dir = Path(__file__).resolve().parents[3]  # hegemonikon/
    checker = DendronChecker(root=target_dir)

    summary, file_results = await asyncio.to_thread(
        _checker_to_summary, checker, target_dir / "mekhane"
    )

    return DendronReportResponse(
        summary=summary,
        file_results=file_results if detail == "full" else [],
    )


@router.post("/check", response_model=DendronCheckResponse)
async def dendron_check(req: DendronCheckRequest) -> DendronCheckResponse:
    """個別ファイルの PROOF チェック。"""
    from mekhane.dendron.checker import DendronChecker

    file_path = Path(req.path)
    if not file_path.exists():
        return DendronCheckResponse(
            path=req.path,
            error=f"File not found: {req.path}",
        )

    target_dir = Path(__file__).resolve().parents[3]
    checker = DendronChecker(root=target_dir)

    proof = await asyncio.to_thread(checker.check_file_proof, file_path)

    has_proof = proof.has_proof if hasattr(proof, "has_proof") else bool(proof)

    return DendronCheckResponse(
        path=req.path,
        result=DendronFileResult(
            path=req.path,
            has_proof=has_proof,
            level=str(getattr(proof, "level", "") or ""),
            parent=str(getattr(proof, "parent", "") or ""),
        ),
    )
