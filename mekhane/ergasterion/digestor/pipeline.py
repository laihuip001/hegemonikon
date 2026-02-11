# PROOF: [L2/インフラ] <- mekhane/ergasterion/digestor/ A0→消化処理が必要→pipeline が担う
"""
Digestor Pipeline - Gnosis → /eat 連携パイプライン

収集された論文を消化候補として選定し、
Hegemonikón 形式に変換して /eat ワークフローに渡す。

改善:
- B: 既存インデックスとの重複排除（偽陽性 > 偽陰性）
- D: 出力フォーマット強化（/eat Phase 0 対応）
- E: Exponential backoff 付きリトライ
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import numpy as np

from .selector import DigestorSelector, DigestCandidate


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: 消化パイプライン実行結果
class DigestResult:
    """消化パイプライン実行結果"""

    timestamp: str
    source: str
    total_papers: int
    candidates_selected: int
    candidates: list[DigestCandidate]
    dry_run: bool


# PURPOSE: Gnosis → /eat 連携パイプライン
class DigestorPipeline:
    """Gnosis → /eat 連携パイプライン"""

    # PURPOSE: Args:
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        selector: Optional[DigestorSelector] = None,
    ):
        """
        Args:
            output_dir: 消化レポート出力ディレクトリ
            selector: カスタム Selector（省略時は標準設定）
        """
        self.output_dir = output_dir or self._default_output_dir()
        self.selector = selector or DigestorSelector()

        # 出力ディレクトリ作成
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # PURPOSE: デフォルトの出力ディレクトリ
    def _default_output_dir(self) -> Path:
        """デフォルトの出力ディレクトリ"""
        return Path.home() / ".hegemonikon" / "digestor"

    # PURPOSE: Gnosis から論文を取得
    def _fetch_from_gnosis(
        self, topics: Optional[list[str]] = None, max_papers: int = 50
    ) -> list:
        """
        Gnosis から論文を取得

        現時点では arXiv/Semantic Scholar から直接取得
        将来: Gnosis インデックスから取得
        """
        papers = []

        try:
            from mekhane.anamnesis.collectors.arxiv import ArxivCollector

            collector = ArxivCollector()

            # トピック定義からクエリを取得
            topics_list = self.selector.get_topics()
            queries = []

            if topics:
                # 指定トピックのクエリのみ
                queries = [
                    t.get("query", "") for t in topics_list if t.get("id") in topics
                ]
            else:
                # 全トピックから上位3つ
                queries = [t.get("query", "") for t in topics_list[:3]]

            # 各クエリで検索 (exponential backoff 付き)
            import time as _time

            for i, query in enumerate(queries):
                if not query:
                    continue
                if i > 0:
                    _time.sleep(3)  # arXiv API rate limit: クエリ間 3秒

                # Exponential backoff: 3s → 6s → 12s (max 3 retries)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        results = collector.search(
                            query, max_results=max_papers // len(queries)
                        )
                        papers.extend(results)
                        break  # 成功したらリトライループを抜ける
                    except Exception as e:
                        wait = 3 * (2 ** attempt)  # 3s, 6s, 12s
                        if attempt < max_retries - 1:
                            print(f"[Digestor] Query '{query[:30]}...' failed (attempt {attempt + 1}/{max_retries}): {e}")
                            print(f"[Digestor]   → Retrying in {wait}s...")
                            _time.sleep(wait)
                        else:
                            print(f"[Digestor] Query '{query[:30]}...' failed after {max_retries} attempts: {e}")
                            # 最終リトライも失敗 → このクエリをスキップ

            # 重複除去 (arXiv ID or URL ベース)
            seen_ids = set()
            unique_papers = []
            for paper in papers:
                paper_id = (
                    getattr(paper, "arxiv_id", None)
                    or getattr(paper, "url", None)
                    or paper.id
                )
                if paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    unique_papers.append(paper)
            papers = unique_papers
            print(f"[Digestor]   → Deduplicated: {len(papers)} unique papers")

        except ImportError:
            print("[Digestor] Warning: Gnosis collectors not available")
        except Exception as e:
            print(f"[Digestor] Error fetching from Gnosis: {e}")

        return papers

    # ═══ B: 既存インデックスとの重複排除 ═══════════════════

    # 設計原則: 偽陽性 > 偽陰性
    # 候補が多すぎるのは減らせるが、候補がないのは増やせない
    DEDUP_SIMILARITY_THRESHOLD = 0.92  # 高閾値 = ほぼ同一論文のみ除外

    # PURPOSE: 既存インデックスとの重複排除
    def _deduplicate_against_indices(self, papers: list) -> list:
        """既存インデックスとの重複排除

        2段階フィルタ:
        1. primary_key 完全一致 → 確実に除外
        2. ベクトル類似度 > 0.92 → ほぼ同一論文のみ除外 (WARNING 付き)

        設計原則: 偽陽性 > 偽陰性
        高い閾値 = 「似てるけど違う」論文は通す
        """
        if not papers:
            return papers

        original_count = len(papers)

        # === Stage 1: primary_key 完全一致 ===
        existing_keys = self._load_existing_keys()
        if existing_keys:
            before = len(papers)
            papers = [
                p for p in papers
                if getattr(p, 'primary_key', p.id) not in existing_keys
            ]
            removed = before - len(papers)
            if removed > 0:
                print(f"[Digestor]   → Stage 1 (primary_key): {removed} duplicates removed")

        # === Stage 2: ベクトル類似度 ===
        try:
            papers = self._deduplicate_by_similarity(papers)
        except Exception as e:
            print(f"[Digestor]   → Stage 2 (similarity) skipped: {e}")

        total_removed = original_count - len(papers)
        if total_removed > 0:
            print(f"[Digestor]   → Total dedup: {original_count} → {len(papers)} papers")

        return papers

    # PURPOSE: 既存インデックスから primary_key を収集
    def _load_existing_keys(self) -> set[str]:
        """既存インデックスから primary_key を収集"""
        keys: set[str] = set()

        # Gnōsis LanceDB index
        try:
            gnosis_path = Path.home() / ".hegemonikon" / "gnosis"
            if gnosis_path.exists():
                for json_file in gnosis_path.glob("*.json"):
                    try:
                        with open(json_file, "r") as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    pk = item.get("primary_key") or item.get("id", "")
                                    if pk:
                                        keys.add(pk)
                        elif isinstance(data, dict):
                            pk = data.get("primary_key") or data.get("id", "")
                            if pk:
                                keys.add(pk)
                    except Exception:
                        continue
        except Exception as e:
            print(f"[Digestor]   → Gnōsis keys load failed: {e}")

        # Sophia pkl index — メタデータから title を取得
        try:
            sophia_path = Path.home() / ".hegemonikon" / "sophia" / "sophia.pkl"
            if sophia_path.exists():
                import pickle
                with open(sophia_path, "rb") as f:
                    data = pickle.load(f)
                metadata = data.get("metadata", {})
                for _id, meta in metadata.items():
                    if isinstance(meta, dict):
                        title = meta.get("title", "")
                        if title:
                            keys.add(f"title:{title}")
        except Exception as e:
            print(f"[Digestor]   → Sophia keys load failed: {e}")

        if keys:
            print(f"[Digestor]   → Loaded {len(keys)} existing keys for dedup")

        return keys

    # PURPOSE: ベクトル類似度による重複検出
    def _deduplicate_by_similarity(self, papers: list) -> list:
        """ベクトル類似度による重複検出

        Sophia index のベクトルと比較し、
        cosine > 0.92 の論文を「ほぼ同一」として除外する。
        """
        sophia_path = Path.home() / ".hegemonikon" / "sophia" / "sophia.pkl"
        if not sophia_path.exists():
            return papers

        try:
            from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            adapter = EmbeddingAdapter()

            # Sophia index のベクトルをロード
            import pickle
            with open(sophia_path, "rb") as f:
                data = pickle.load(f)
            existing_vectors = data.get("vectors", [])

            if not existing_vectors:
                return papers

            # 各論文のベクトルを計算して既存と比較
            filtered = []
            for paper in papers:
                text = f"{paper.title} {paper.abstract[:500]}"
                paper_vec = adapter.encode([text])[0]
                norm = np.linalg.norm(paper_vec)
                if norm > 0:
                    paper_vec = paper_vec / norm

                # 最大類似度を計算
                max_sim = 0.0
                for existing_vec in existing_vectors:
                    ev = np.array(existing_vec)
                    ev_norm = np.linalg.norm(ev)
                    if ev_norm > 0:
                        ev = ev / ev_norm
                    sim = float(np.dot(paper_vec, ev))
                    if sim > max_sim:
                        max_sim = sim

                if max_sim >= self.DEDUP_SIMILARITY_THRESHOLD:
                    print(
                        f"[Digestor]   ⚠ Stage 2: '{paper.title[:40]}...' "
                        f"(sim={max_sim:.3f}) — dedup as near-duplicate"
                    )
                else:
                    filtered.append(paper)

            removed = len(papers) - len(filtered)
            if removed > 0:
                print(f"[Digestor]   → Stage 2 (similarity): {removed} near-duplicates removed")
            return filtered

        except ImportError:
            print("[Digestor]   → Stage 2 skipped: EmbeddingAdapter not available")
            return papers
        except Exception as e:
            print(f"[Digestor]   → Stage 2 failed: {e}")
            return papers

    # PURPOSE: /eat ワークフロー用の入力を生成
    def _generate_eat_input(self, candidate: DigestCandidate) -> dict:
        """
        /eat ワークフロー用の入力を生成

        Returns:
            /eat が処理できる形式の辞書
        """
        templates = []
        if hasattr(candidate, 'suggested_templates') and candidate.suggested_templates:
            templates = [
                {"id": tid, "score": round(score, 3)}
                for tid, score in candidate.suggested_templates
            ]

        return {
            "素材名": candidate.paper.title,
            "ソース": candidate.paper.source,
            "URL": candidate.paper.url or "",
            "概要": candidate.paper.abstract[:500] if candidate.paper.abstract else "",
            "マッチトピック": candidate.matched_topics,
            "スコア": candidate.score,
            "消化先候補": self._suggest_digest_targets(candidate),
            "推奨テンプレート": templates,
        }

    # PURPOSE: 消化先ワークフローを推薦
    def _suggest_digest_targets(self, candidate: DigestCandidate) -> list[str]:
        """消化先ワークフローを推薦"""
        targets = []

        # トピック定義から digest_to を取得
        topics_list = self.selector.get_topics()
        for topic in topics_list:
            if topic.get("id") in candidate.matched_topics:
                digest_to = topic.get("digest_to", [])
                targets.extend(digest_to)

        # 重複除去
        return list(set(targets))

    # PURPOSE: 消化パイプライン実行
    def run(
        self,
        topics: Optional[list[str]] = None,
        max_papers: int = 50,
        max_candidates: int = 10,
        dry_run: bool = True,
    ) -> DigestResult:
        """
        消化パイプライン実行

        Args:
            topics: 対象トピック（None = 全トピック）
            max_papers: 取得する最大論文数
            max_candidates: 選定する最大候補数
            dry_run: True の場合、レポート生成のみ（実際の消化は行わない）

        Returns:
            DigestResult
        """
        print(f"[Digestor] Starting pipeline (dry_run={dry_run})")

        # 1. Gnosis から論文取得
        print("[Digestor] Phase 1: Fetching from Gnosis...")
        papers = self._fetch_from_gnosis(topics, max_papers)
        print(f"[Digestor]   → {len(papers)} papers fetched")

        # 1.5 B: 既存インデックスとの重複排除
        print("[Digestor] Phase 1.5: Deduplicating against existing indices...")
        papers = self._deduplicate_against_indices(papers)
        print(f"[Digestor]   → {len(papers)} papers after dedup")

        # 2. 消化候補選定
        print("[Digestor] Phase 2: Selecting candidates...")
        candidates = self.selector.select_candidates(
            papers, max_candidates=max_candidates, topic_filter=topics
        )
        print(f"[Digestor]   → {len(candidates)} candidates selected")

        # 3. レポート生成
        result = DigestResult(
            timestamp=datetime.now().isoformat(),
            source="gnosis",
            total_papers=len(papers),
            candidates_selected=len(candidates),
            candidates=candidates,
            dry_run=dry_run,
        )

        # 4. レポート保存
        report_path = self._save_report(result)
        print(f"[Digestor] Report saved: {report_path}")

        # 5. 実行（dry_run でない場合）
        if not dry_run and candidates:
            print("[Digestor] Phase 3: Generating /eat inputs...")
            self._generate_eat_batch(candidates)

        return result

    # PURPOSE: 消化レポートを保存
    def _save_report(self, result: DigestResult) -> Path:
        """消化レポートを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"digest_report_{timestamp}.json"

        # シリアライズ可能な形式に変換
        report_data = {
            "timestamp": result.timestamp,
            "source": result.source,
            "total_papers": result.total_papers,
            "candidates_selected": result.candidates_selected,
            "dry_run": result.dry_run,
            "candidates": [
                {
                    "title": c.paper.title,
                    "source": c.paper.source,
                    "url": c.paper.url,
                    "score": c.score,
                    "matched_topics": c.matched_topics,
                    "rationale": c.rationale,
                    "suggested_templates": [
                        {"id": tid, "score": round(s, 3)}
                        for tid, s in (c.suggested_templates or [])
                    ],
                }
                for c in result.candidates
            ],
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return report_path

    # PURPOSE: /eat 用のバッチ入力を生成
    def _generate_eat_batch(self, candidates: list[DigestCandidate]) -> None:
        """
        /eat 用のバッチ入力を生成

        1. eat_batch.json — 一括参照用
        2. incoming/ — 個別 .md ファイル（/eat 消費用）
        """
        # 1. JSON バッチ
        batch_path = self.output_dir / "eat_batch.json"
        batch_data = [self._generate_eat_input(c) for c in candidates]

        with open(batch_path, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        print(f"[Digestor] /eat batch saved: {batch_path}")

        # 2. incoming/ に個別 .md ファイル配置
        incoming_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "incoming"
        incoming_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        for i, c in enumerate(candidates[:5], 1):  # 上位5件のみ
            safe_title = "".join(ch if ch.isalnum() or ch in "-_ " else "" for ch in c.paper.title[:40]).strip().replace(" ", "_")
            filename = f"eat_{timestamp}_{i:02d}_{safe_title}.md"
            filepath = incoming_dir / filename

            # 既に同日の同タイトルがあればスキップ
            if filepath.exists():
                continue

            abstract = c.paper.abstract[:300] if c.paper.abstract else "(no abstract)"
            targets = self._suggest_digest_targets(c)
            targets_str = ", ".join(targets) if targets else "未定"

            # C: テンプレート推奨情報
            template_info = ""
            if hasattr(c, 'suggested_templates') and c.suggested_templates:
                template_info = "\n".join(
                    f"  - {tid}: {score:.2f}"
                    for tid, score in c.suggested_templates
                )
            else:
                template_info = "  - (未分析)"

            # D: /eat Phase 0 対応の強化テンプレート
            content = f"""---
title: "{c.paper.title}"
source: {c.paper.source}
url: {c.paper.url or 'N/A'}
score: {c.score:.2f}
matched_topics: [{', '.join(c.matched_topics)}]
digest_to: [{targets_str}]
generated: {timestamp}
---

# /eat 候補: {c.paper.title}

> **Score**: {c.score:.2f} | **Topics**: {', '.join(c.matched_topics)}
> **Source**: {c.paper.source} | **URL**: {c.paper.url or 'N/A'}
> **消化先候補**: {targets_str}

## 推奨テンプレート

{template_info}

## Abstract

{abstract}

## Phase 0: 圏の特定 (テンプレート)

| 項目 | 内容 |
|:-----|:-----|
| 圏 Ext (外部構造) | <!-- 論文の属する学問圏 --> |
| 圏 Int (内部構造) | <!-- HGK 内の対応する圏 --> |
| 関手 F (取込) | <!-- Ext → Int へのマッピング --> |
| 関手 G (忘却) | <!-- Int → Ext への写像 --> |
| η (情報保存) | <!-- 取り込んで忘却→元情報をどの程度復元できるか --> |
| ε (構造保存) | <!-- 忘却して取込→HGK構造がどの程度維持されるか --> |

## /fit チェックリスト

- [ ] η 検証: 原論文の主張が HGK 内で再現可能
- [ ] ε 検証: HGK 既存構造との整合性確認
- [ ] Drift 測定: 1-ε の許容範囲内

---

*Auto-generated by Digestor Pipeline ({timestamp})*
*消化するには: `/eat` で読み込み、上記のテンプレートに従って統合*
"""
            filepath.write_text(content, encoding="utf-8")
            print(f"[Digestor]   → incoming/{filename}")

        print(f"[Digestor] {min(len(candidates), 5)} files placed in incoming/")


# CLI エントリポイント
# PURPOSE: CLI エントリポイント
def main():
    """CLI エントリポイント"""
    import argparse

    parser = argparse.ArgumentParser(description="Digestor Pipeline")
    parser.add_argument("--topics", nargs="+", help="対象トピック")
    parser.add_argument("--max-papers", type=int, default=50, help="最大論文数")
    parser.add_argument("--max-candidates", type=int, default=10, help="最大候補数")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run モード"
    )
    parser.add_argument("--execute", action="store_true", help="実際に消化を実行")

    args = parser.parse_args()

    pipeline = DigestorPipeline()
    result = pipeline.run(
        topics=args.topics,
        max_papers=args.max_papers,
        max_candidates=args.max_candidates,
        dry_run=not args.execute,
    )

    print(f"\n[Digestor] Complete: {result.candidates_selected} candidates selected")

    for i, c in enumerate(result.candidates, 1):
        print(f"  {i}. [{c.score:.2f}] {c.paper.title[:60]}...")


if __name__ == "__main__":
    main()
