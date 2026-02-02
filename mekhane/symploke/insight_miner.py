#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A3→知恵を蓄積する必要→insight_miner が担う
"""
Insight Miner - 会話ログから埋もれた洞察を発掘

Usage:
    python insight_miner.py                    # 全ログから洞察を抽出
    python insight_miner.py --limit 10         # 最新10件のみ
    python insight_miner.py --pattern gnome    # 格言パターン
"""

import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.kairos_ingest import get_conversation_files


@dataclass
class Insight:
    """抽出された洞察"""

    text: str
    category: str  # gnome, principle, discovery, decision
    source_file: str
    context: str  # 周辺のコンテキスト
    confidence: float  # 抽出の確信度


# 洞察を示唆するパターン
INSIGHT_PATTERNS = {
    "gnome": [
        # 格言・教訓パターン
        r"(?:重要な?教訓|今日の発見|今日の学び|キーインサイト)[:：]?\s*[「『]?(.{10,100})[」』]?",
        r"(?:本質は|核心は|要は)[:：]?\s*[「『]?(.{10,80})[」』]?",
        r"> \*\*(.{10,100})\*\*",  # 強調された引用
    ],
    "principle": [
        # 原則パターン
        r"(?:原則|ルール|方針)[:：]?\s*(.{10,100})",
        r"(?:〜すべき|〜べきだ|〜が鉄則)(.{5,50})",
        r"(?:必ず|絶対に|常に)(.{5,80})(?:すること|する)",
    ],
    "discovery": [
        # 発見パターン
        r"(?:発見した|気づいた|わかった)[:：]?\s*(.{10,100})",
        r"(?:判明した|明らかになった)[:：]?\s*(.{10,100})",
        r"(?:面白いことに|興味深いことに)(.{10,100})",
    ],
    "decision": [
        # 決定パターン
        r"(?:決定した|採用した|決めた)[:：]?\s*(.{10,100})",
        r"(?:方針を|設計を|実装を)(.{10,80})(?:に決定|とした)",
    ],
}


def extract_context(content: str, match_start: int, context_size: int = 200) -> str:
    """マッチ周辺のコンテキストを抽出"""
    start = max(0, match_start - context_size)
    end = min(len(content), match_start + context_size)
    return content[start:end].strip()


def score_insight_quality(text: str) -> float:
    """洞察の品質をスコアリング (0.0 - 1.0)"""
    score = 0.5  # ベーススコア

    # ポジティブ要因
    if any(c in text for c in "。！？"):  # 文が完結している
        score += 0.15
    if len(text) >= 30:  # 十分な長さ
        score += 0.1
    if any(kw in text for kw in ["である", "だ。", "こと。", "べき"]):
        score += 0.1  # 結論調の表現

    # ネガティブ要因
    if text.startswith(("ない", "なかった", "...", "だ。\n")):
        score -= 0.3  # 不完全な文頭
    if "\n## 🤖" in text or "\n##" in text:
        score -= 0.4  # マークダウン構造が混入
    if len(text) < 20:
        score -= 0.2  # 短すぎ
    if text.count("\n") > 3:
        score -= 0.2  # 改行が多すぎ（複数文）
    if any(
        noise in text for noise in ["Claude", "Thought for", "Progress", "Files Edited"]
    ):
        score -= 0.5  # UIノイズ

    return max(0.0, min(1.0, score))


def clean_insight_text(text: str) -> str:
    """洞察テキストをクリーニング"""
    # 末尾のノイズを除去
    text = re.sub(r"\n## 🤖.*$", "", text, flags=re.DOTALL)
    text = re.sub(r"\n\n+", "\n", text)
    text = text.strip()

    # 最初の文だけを抽出（複数文の場合）
    if "。" in text:
        first_sentence_end = text.find("。") + 1
        if first_sentence_end < len(text) and first_sentence_end > 10:
            text = text[:first_sentence_end]

    return text.strip()


def mine_insights(
    file_path: Path, categories: Optional[List[str]] = None, min_quality: float = 0.4
) -> List[Insight]:
    """会話ログから洞察を抽出（フィルタリング付き）"""
    content = file_path.read_text(encoding="utf-8")
    insights = []

    categories = categories or list(INSIGHT_PATTERNS.keys())

    for category in categories:
        if category not in INSIGHT_PATTERNS:
            continue

        for pattern in INSIGHT_PATTERNS[category]:
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                text = match.group(1) if match.groups() else match.group(0)
                text = clean_insight_text(text)

                # 短すぎるものは除外
                if len(text) < 15:
                    continue

                # 品質スコアリング
                quality = score_insight_quality(text)
                if quality < min_quality:
                    continue

                # 重複チェック
                if any(i.text == text for i in insights):
                    continue

                insights.append(
                    Insight(
                        text=text,
                        category=category,
                        source_file=file_path.name,
                        context=extract_context(content, match.start()),
                        confidence=quality,
                    )
                )

    return insights


def mine_all_logs(
    limit: Optional[int] = None, categories: Optional[List[str]] = None
) -> List[Insight]:
    """全ログから洞察を抽出"""
    files = get_conversation_files()
    if limit:
        files = files[:limit]

    all_insights = []
    for f in files:
        insights = mine_insights(f, categories)
        all_insights.extend(insights)

    return all_insights


def generate_ki_candidates(insights: List[Insight]) -> str:
    """KI候補レポートを生成"""
    lines = ["# 埋もれた洞察レポート\n"]
    lines.append(f"抽出件数: {len(insights)} 件\n")

    # カテゴリ別に整理
    by_category = {}
    for i in insights:
        by_category.setdefault(i.category, []).append(i)

    for cat, items in by_category.items():
        lines.append(f"\n## {cat.upper()} ({len(items)} 件)\n")
        for item in items[:10]:  # 各カテゴリ上位10件
            lines.append(f"- **{item.text}**")
            lines.append(f"  - Source: `{item.source_file}`\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Mine insights from conversation logs")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    parser.add_argument(
        "--pattern",
        type=str,
        choices=list(INSIGHT_PATTERNS.keys()),
        help="Filter by insight category",
    )
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    categories = [args.pattern] if args.pattern else None

    print(f"🔍 Mining insights from conversation logs...")
    insights = mine_all_logs(limit=args.limit, categories=categories)

    print(f"📊 Found {len(insights)} insights")

    # カテゴリ別サマリー
    by_cat = {}
    for i in insights:
        by_cat.setdefault(i.category, []).append(i)

    for cat, items in by_cat.items():
        print(f"  {cat}: {len(items)} 件")

    # 上位の洞察を表示
    print("\n🏆 Top Insights:")
    for insight in insights[:5]:
        print(f"  [{insight.category}] {insight.text}")
        print(f"           ← {insight.source_file}")

    # レポート生成
    if args.output:
        report = generate_ki_candidates(insights)
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"\n💾 Report saved: {args.output}")


if __name__ == "__main__":
    main()
