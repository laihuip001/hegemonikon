# PROOF: [L2/Mekhane] <- mekhane/api/routes/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/API] <- mekhane/api/routes/
# PURPOSE: Theorem Usage API — Dashboard 向け定理使用頻度データ
"""
Theorem Usage API Endpoints

Exposes theorem usage statistics and recommendations for the Dashboard.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["theorem"])


@router.get("/theorem/usage")
async def theorem_usage() -> dict:
    """Get theorem usage summary for dashboard display."""
    from mekhane.fep.theorem_recommender import usage_summary, THEOREM_KEYWORDS
    summary = usage_summary()

    # Enrich with series info for dashboard rendering
    series_info = {}
    series_names = {
        "O": "Ousia", "S": "Schema", "H": "Hormē",
        "P": "Perigraphē", "K": "Kairos", "A": "Akribeia",
    }
    series_colors = {
        "O": "#38bdf8", "S": "#22c55e", "H": "#f97316",
        "P": "#a855f7", "K": "#eab308", "A": "#ef4444",
    }

    for series_key, name in series_names.items():
        theorems_in_series = [
            {
                "id": t["id"],
                "name": t["name"],
                "command": t["command"],
                "question": t["question"],
                "usage_count": summary["by_theorem"].get(t["id"], 0),
            }
            for t in THEOREM_KEYWORDS if t["series"] == series_key
        ]
        series_info[series_key] = {
            "name": name,
            "color": series_colors[series_key],
            "total_usage": summary["by_series"].get(series_key, 0),
            "theorems": theorems_in_series,
        }

    return {
        "total_usage": summary["total"],
        "total_theorems": 24,
        "unused_count": summary["unused_count"],
        "usage_rate": round((24 - summary["unused_count"]) / 24 * 100, 1),
        "series": series_info,
        "most_used": [
            {"theorem_id": tid, "count": cnt}
            for tid, cnt in summary["most_used"]
        ],
    }


@router.get("/theorem/today")
async def theorem_today() -> dict:
    """Get today's theorem suggestions."""
    from mekhane.fep.theorem_recommender import todays_theorem
    suggestions = todays_theorem(n=2)
    return {"suggestions": suggestions}


@router.get("/theorem/suggest")
async def theorem_suggest(q: str = "", max_results: int = 3) -> dict:
    """Suggest theorems based on text input."""
    from mekhane.fep.theorem_recommender import suggest_theorems
    results = suggest_theorems(q, max_results=max_results)
    return {
        "query": q,
        "suggestions": [
            {
                "theorem_id": s.theorem_id,
                "name": s.name,
                "series": s.series,
                "command": s.command,
                "question": s.question,
                "score": s.score,
                "matched_keywords": s.matched_keywords,
            }
            for s in results
        ],
    }
