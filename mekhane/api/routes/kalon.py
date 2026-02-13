#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Kalon 判定 API — Fix(G∘F) 判定の記録と参照
"""
Kalon Router — 概念の Kalon 判定を保存・取得する

エンドポイント:
  POST /kalon/judge   — 判定を記録
  GET  /kalon/history — 判定履歴
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["kalon"])

# --- Storage ---
_KALON_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "kalon"


# PURPOSE: の統一的インターフェースを実現する
class KalonJudgeRequest(BaseModel):
    concept: str
    g_test: bool  # G テスト (蒸留): True = 不変
    f_test: bool  # F テスト (展開): True = 3+ 導出可
    notes: str = ""


# PURPOSE: [L2-auto] G/F テスト結果から判定を返す。
def _verdict(g: bool, f: bool) -> str:
    """G/F テスト結果から判定を返す。"""
    if g and f:
        return "◎"  # kalon
    if not g and f:
        return "◯"  # 許容
    return "✗"  # 自明 or 要蒸留


# PURPOSE: [L2-auto] 内部処理: verdict_label
def _verdict_label(g: bool, f: bool) -> str:
    if g and f:
        return "kalon — Fix(G∘F) に到達"
    if g and not f:
        return "自明 — lim だが colim なし (π パターン)"
    if not g and f:
        return "許容 — もう一回 G∘F を回すと改善"
    return "要蒸留 — Fix から遠い"


# PURPOSE: kalon の kalon judge 処理を実行する
@router.post("/kalon/judge")
async def kalon_judge(req: KalonJudgeRequest) -> dict[str, Any]:
    """Kalon 判定を記録する。"""
    _KALON_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    verdict = _verdict(req.g_test, req.f_test)
    label = _verdict_label(req.g_test, req.f_test)

    # Markdown ファイルとして保存（概念名を先にサニタイズ）
    safe_concept = "".join(c if c.isalnum() or c in "-_" else "_" for c in req.concept)[:60]
    safe_filename = f"kalon_{safe_concept}_{now.strftime('%Y-%m-%d_%H%M')}.md"

    content = f"""# Kalon 判定: {req.concept}

> **判定**: {verdict} {label}
> **日時**: {now.isoformat()}

## テスト結果

| テスト | 結果 | 意味 |
|:-------|:-----|:-----|
| G テスト (蒸留) | {'✅ 不変' if req.g_test else '❌ 圧縮可能'} | これ以上蒸留しても変化しないか |
| F テスト (展開) | {'✅ 3+ 導出可' if req.f_test else '❌ 展開なし'} | 3つ以上の新概念を導出できるか |

## 属性チェック

- **Fix(G∘F)**: {'✅ 到達' if (req.g_test and req.f_test) else '❌ 未到達'}
- **Presheaf**: {'✅ 多面的表現あり' if req.f_test else '❌ 単面的'}
- **Self-referential**: {'✅ 自己説明的' if (req.g_test and req.f_test) else '❌ 外部依存'}

{f'## メモ{chr(10)}{chr(10)}{req.notes}' if req.notes else ''}
"""

    filepath = _KALON_DIR / safe_filename
    filepath.write_text(content, encoding="utf-8")

    logger.info("Kalon judgment recorded: %s → %s", req.concept, verdict)

    return {
        "concept": req.concept,
        "verdict": verdict,
        "label": label,
        "g_test": req.g_test,
        "f_test": req.f_test,
        "timestamp": now.isoformat(),
        "filename": safe_filename,
    }


# PURPOSE: kalon の kalon history 処理を実行する
@router.get("/kalon/history")
async def kalon_history(limit: int = 50) -> dict[str, Any]:
    """Kalon 判定履歴を返す。"""
    if not _KALON_DIR.exists():
        return {"judgments": [], "total": 0}

    files = sorted(
        [f for f in _KALON_DIR.iterdir() if f.suffix in (".md", ".json")],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    judgments: list[dict[str, Any]] = []
    for f in files[:limit]:
        content = f.read_text(encoding="utf-8")
        # タイトルからコンセプト名を抽出
        concept = f.stem.replace("kalon_", "").rsplit("_", 2)[0]
        # 判定記号を検出
        verdict = "?"
        for line in content.split("\n"):
            if "**判定**:" in line:
                for v in ("◎", "◯", "✗"):
                    if v in line:
                        verdict = v
                        break
                break

        judgments.append({
            "concept": concept,
            "verdict": verdict,
            "filename": f.name,
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })

    return {
        "judgments": judgments,
        "total": len(files),
    }
