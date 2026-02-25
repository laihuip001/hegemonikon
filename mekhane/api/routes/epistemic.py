#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/api/routes/ A0->Auto->AddedByCI
# PROOF: [L2/Epistemic] <- mekhane/api/routes/
# PURPOSE: Epistemic Status API — 認識論的地位レジストリの提供
"""
Epistemic Routes — epistemic_status.yaml の内容を API で提供。

Dashboard カードおよび健全性チェックに使用。
"""

from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter

import yaml

router = APIRouter(prefix="/epistemic", tags=["epistemic"])

PROJECT_ROOT = Path.home() / "oikos" / "hegemonikon"
REGISTRY_PATH = PROJECT_ROOT / "kernel" / "epistemic_status.yaml"


@router.get("/status")
async def epistemic_status():
    """認識論的地位の全パッチ情報を返す"""
    if not REGISTRY_PATH.exists():
        return {"status": "no_data", "patches": [], "summary": {}}

    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        patches = data.get("patches", {})

        # Summary statistics
        status_counts: dict[str, int] = {}
        for patch in patches.values():
            s = patch.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        # Convert to list format for frontend
        patch_list = []
        for patch_id, patch in patches.items():
            patch_list.append({
                "id": patch_id,
                "claim": patch.get("claim", ""),
                "status": patch.get("status", "unknown"),
                "file": patch.get("file", ""),
                "line": patch.get("line", 0),
                "source": patch.get("source", ""),
                "falsification": patch.get("falsification", ""),
                "updated": patch.get("updated", ""),
            })

        return {
            "total": len(patches),
            "summary": status_counts,
            "patches": patch_list,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/health")
async def epistemic_health():
    """認識論的健全性スコアを計算"""
    if not REGISTRY_PATH.exists():
        return {"score": 0, "details": "Registry not found"}

    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        patches = data.get("patches", {})
        if not patches:
            return {"score": 100, "details": "No patches to evaluate"}

        # Health scoring: higher = better epistemic quality
        # empirical: 100, reference: 75, analogue: 50, hypothesis: 25
        score_map = {
            "empirical": 100,
            "reference": 75,
            "analogue": 50,
            "hypothesis": 25,
        }

        total_score = sum(
            score_map.get(p.get("status", ""), 0)
            for p in patches.values()
        )
        avg_score = total_score / len(patches)

        # Check for falsification coverage
        has_falsification = sum(
            1 for p in patches.values()
            if p.get("falsification", "").strip()
        )
        falsification_coverage = has_falsification / len(patches) * 100

        return {
            "score": round(avg_score, 1),
            "total_patches": len(patches),
            "falsification_coverage": round(falsification_coverage, 1),
            "grade": (
                "A" if avg_score >= 80 else
                "B" if avg_score >= 60 else
                "C" if avg_score >= 40 else
                "D"
            ),
        }
    except Exception as e:
        return {"score": 0, "details": str(e)}
