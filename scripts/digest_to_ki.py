#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- scripts/ 「回す」パイプライン: 論文→消化→KI
"""
digest_to_ki.py — Digestor → Sophia KI 自動パイプライン

Digestor で論文候補を収集し、Sophia KI (kernel/knowledge/) に保存する。
「回す」仕組みの最初の1サイクル。

Usage:
    python scripts/digest_to_ki.py --topics active-inference --max 5 --dry-run
    python scripts/digest_to_ki.py --topics active-inference chain-of-thought --max 3
    python scripts/digest_to_ki.py --all --max 10

Options:
    --topics    : 対象トピック (スペース区切り)
    --all       : 全トピックを対象
    --max       : 最大候補数 (default: 5)
    --min-score : 最小スコア (default: 0.6)
    --dry-run   : レポート表示のみ、KI 保存しない
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("digest_to_ki")

# KI storage
KNOWLEDGE_DIR = PROJECT_ROOT / "kernel" / "knowledge"

# Digestor config
DIGESTOR_DIR = Path.home() / ".hegemonikon" / "digestor"

# Available topics (from Digestor MCP config)
TOPICS = [
    "agent-architecture",
    "active-inference",
    "structured-prompting",
    "chain-of-thought",
    "tool-use",
    "self-correction",
    "stoic-philosophy",
    "free-energy-principle",
    "metacognition",
]

# WF mapping per topic
TOPIC_WF_MAP = {
    "agent-architecture": ["/noe", "/s"],
    "active-inference": ["/noe", "/bou"],
    "structured-prompting": ["/mek"],
    "chain-of-thought": ["/noe", "/dia"],
    "tool-use": ["/ene", "/mek"],
    "self-correction": ["/dia"],
    "stoic-philosophy": ["/noe", "/bou"],
    "free-energy-principle": ["/bou", "/ore"],
    "metacognition": ["/dia"],
}


def slugify(title: str) -> str:
    """Generate URL-safe slug from title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:80] if slug else "untitled"


def build_ki_content(candidate: dict, topic: str) -> tuple[str, str]:
    """Build KI markdown content from a digest candidate.
    
    Returns (title, markdown_content).
    """
    title = candidate["title"]
    source = candidate.get("source", "gnosis")
    url = candidate.get("url", "")
    score = candidate.get("score", 0.0)
    rationale = candidate.get("rationale", "")
    matched = candidate.get("matched_topics", [topic])
    wf_tags = TOPIC_WF_MAP.get(topic, [])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    content = dedent(f"""\
        # {title}

        > 自動消化パイプライン (digest_to_ki) により生成

        ## メタデータ

        | 項目 | 値 |
        |------|-----|
        | ソース | {source} |
        | URL | {url or '—'} |
        | スコア | {score:.2f} |
        | トピック | {', '.join(matched)} |
        | 関連 WF | {', '.join(wf_tags)} |
        | 消化日 | {now} |

        ## 選定理由

        {rationale or '（自動選定 — 理由未記載）'}

        ## 消化メモ

        > TODO: /eat で深掘り消化を実行

        ## 参照

        - [[{topic}]]
    """)

    return title, content


def save_ki(title: str, content: str, source_type: str = "digest") -> Path:
    """Save KI to kernel/knowledge/ with YAML frontmatter."""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    ki_id = slugify(title)
    path = KNOWLEDGE_DIR / f"{ki_id}.md"

    # Dedupe: add suffix if exists
    counter = 1
    original_id = ki_id
    while path.exists():
        ki_id = f"{original_id}-{counter}"
        path = KNOWLEDGE_DIR / f"{ki_id}.md"
        counter += 1

    now = datetime.now(timezone.utc).isoformat()
    frontmatter = dedent(f"""\
        ---
        title: "{title}"
        source_type: {source_type}
        created: "{now}"
        updated: "{now}"
        ---
    """)

    path.write_text(frontmatter + content, encoding="utf-8")
    return path


def run_digestor(topics: list[str] | None, max_candidates: int) -> list[dict]:
    """Run DigestorPipeline and return candidates. Falls back to Gnōsis search."""
    candidates: list[dict] = []
    try:
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
        pipeline = DigestorPipeline()
        result = pipeline.run(
            topics=topics,
            max_papers=max_candidates * 5,
            max_candidates=max_candidates,
            dry_run=False,
        )
        for c in result.candidates:
            candidates.append({
                "title": c.paper.title,
                "source": c.paper.source,
                "url": c.paper.url or "",
                "score": c.score,
                "matched_topics": c.matched_topics,
                "rationale": getattr(c, "rationale", ""),
            })
    except ImportError:
        logger.warning("DigestorPipeline not found.")
    except Exception as e:
        logger.warning("DigestorPipeline failed: %s", e)

    if not candidates:
        logger.info("DigestorPipeline returned 0 candidates, falling back to Gnōsis search...")
        candidates = _fallback_gnosis_search(topics, max_candidates)

    return candidates


def _fallback_gnosis_search(topics: list[str] | None, max_candidates: int) -> list[dict]:
    """Fallback: use Gnōsis index directly for paper search."""
    try:
        from mekhane.anamnesis.index import GnosisIndex
        idx = GnosisIndex()
        results = []
        search_topics = topics or TOPICS[:3]
        seen_titles: set[str] = set()

        for topic in search_topics:
            query = topic.replace("-", " ")
            papers = idx.search(query, k=max_candidates)
            for p in papers:
                title = p.get("title", "Unknown")
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                results.append({
                    "title": title,
                    "source": p.get("source", "gnosis"),
                    "url": p.get("url", ""),
                    "score": p.get("score", 0.5),
                    "matched_topics": [topic],
                    "rationale": (p.get("abstract", "") or "")[:300],
                })
        return results[:max_candidates]
    except Exception as e:
        logger.error("Gnōsis fallback search failed: %s", e)
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Digestor → Sophia KI pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--topics", nargs="+", choices=TOPICS,
        help="Target topics (space-separated)",
    )
    parser.add_argument(
        "--all", action="store_true", dest="all_topics",
        help="Process all topics",
    )
    parser.add_argument(
        "--max", type=int, default=5, dest="max_candidates",
        help="Max candidates (default: 5)",
    )
    parser.add_argument(
        "--min-score", type=float, default=0.3,
        help="Minimum score threshold (default: 0.3, Gnōsis scores ~0.1-0.5)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report only, do not save KIs",
    )
    args = parser.parse_args()

    if args.all_topics:
        topics = TOPICS
    elif args.topics:
        topics = args.topics
    else:
        topics = None

    logger.info("=== digest_to_ki: 「回す」パイプライン ===")
    logger.info("Topics: %s", topics or "all (pipeline default)")
    logger.info("Max candidates: %d", args.max_candidates)
    logger.info("Min score: %.2f", args.min_score)
    logger.info("Dry run: %s", args.dry_run)
    logger.info("")

    # Step 1: Collect candidates
    logger.info("Step 1: 候補収集中...")
    candidates = run_digestor(topics, args.max_candidates)
    logger.info("  → %d 件の候補を取得", len(candidates))

    if not candidates:
        logger.warning("候補が見つかりませんでした。")
        return

    # Step 2: Filter by score
    filtered = [c for c in candidates if c["score"] >= args.min_score]
    logger.info("Step 2: スコアフィルタ (>= %.2f): %d → %d 件",
                args.min_score, len(candidates), len(filtered))

    if not filtered:
        logger.warning("スコア基準を満たす候補がありません。")
        return

    # Step 3: Display report
    logger.info("")
    logger.info("━━━ 候補レポート ━━━")
    for i, c in enumerate(filtered, 1):
        primary_topic = c["matched_topics"][0] if c["matched_topics"] else "unknown"
        logger.info("  [%d] %.2f | %s", i, c["score"], c["title"])
        logger.info("      topics: %s | source: %s",
                     ", ".join(c["matched_topics"]), c["source"])
        if c.get("url"):
            logger.info("      url: %s", c["url"])
    logger.info("")

    if args.dry_run:
        logger.info("🔍 Dry run — KI 保存はスキップ")
        return

    # Step 4: Save to KI
    logger.info("Step 4: KI 保存中...")
    saved = []
    for c in filtered:
        primary_topic = c["matched_topics"][0] if c["matched_topics"] else "unknown"
        title, content = build_ki_content(c, primary_topic)
        path = save_ki(title, content, source_type="digest")
        saved.append((title, path))
        logger.info("  ✅ %s → %s", title[:50], path.name)

    logger.info("")
    logger.info("━━━ 結果 ━━━")
    logger.info("  収集: %d 件", len(candidates))
    logger.info("  フィルタ通過: %d 件", len(filtered))
    logger.info("  KI 保存: %d 件", len(saved))
    logger.info("")
    for title, path in saved:
        logger.info("  📄 %s", path)

    # Step 5: Save run log + DigestorPipeline 互換レポート
    DIGESTOR_DIR.mkdir(parents=True, exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 5a: 互換レポート (Dashboard /api/digestor/latest 用)
    report_path = DIGESTOR_DIR / f"digest_report_{ts_str}.json"
    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "digest_to_ki",
        "total_papers": len(candidates),
        "candidates_selected": len(filtered),
        "dry_run": False,
        "candidates": [
            {
                "title": c["title"],
                "source": c.get("source", "gnosis"),
                "url": c.get("url", ""),
                "score": c["score"],
                "matched_topics": c.get("matched_topics", []),
                "rationale": c.get("rationale", ""),
                "suggested_templates": [],
            }
            for c in filtered
        ],
    }
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False))
    logger.info("  📋 Digest report: %s", report_path)

    # 5b: 実行ログ
    log_dir = DIGESTOR_DIR / "runs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"ki_pipeline_{ts_str}.json"
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topics": topics,
        "max_candidates": args.max_candidates,
        "min_score": args.min_score,
        "candidates_total": len(candidates),
        "candidates_filtered": len(filtered),
        "ki_saved": len(saved),
        "saved_files": [str(p) for _, p in saved],
    }
    log_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False))
    logger.info("  📊 Run log: %s", log_path)


if __name__ == "__main__":
    main()
