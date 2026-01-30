# PROOF: [L2/インフラ] A0→消化処理が必要→pipeline が担う
"""
Digestor Pipeline - Gnosis → /eat 連携パイプライン

収集された論文を消化候補として選定し、
Hegemonikón 形式に変換して /eat ワークフローに渡す。
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from .selector import DigestorSelector, DigestCandidate


@dataclass
class DigestResult:
    """消化パイプライン実行結果"""
    timestamp: str
    source: str
    total_papers: int
    candidates_selected: int
    candidates: list[DigestCandidate]
    dry_run: bool
    

class DigestorPipeline:
    """Gnosis → /eat 連携パイプライン"""
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        selector: Optional[DigestorSelector] = None
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
    
    def _default_output_dir(self) -> Path:
        """デフォルトの出力ディレクトリ"""
        return Path.home() / ".hegemonikon" / "digestor"
    
    def _fetch_from_gnosis(
        self,
        topics: Optional[list[str]] = None,
        max_papers: int = 50
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
                    t.get("query", "")
                    for t in topics_list
                    if t.get("id") in topics
                ]
            else:
                # 全トピックから上位3つ
                queries = [t.get("query", "") for t in topics_list[:3]]
            
            # 各クエリで検索
            for query in queries:
                if query:
                    results = collector.search(query, max_results=max_papers // len(queries))
                    papers.extend(results)
            
            # 重複除去 (arXiv ID or URL ベース)
            seen_ids = set()
            unique_papers = []
            for paper in papers:
                paper_id = getattr(paper, 'arxiv_id', None) or getattr(paper, 'url', None) or paper.id
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
    
    def _generate_eat_input(self, candidate: DigestCandidate) -> dict:
        """
        /eat ワークフロー用の入力を生成
        
        Returns:
            /eat が処理できる形式の辞書
        """
        return {
            "素材名": candidate.paper.title,
            "ソース": candidate.paper.source,
            "URL": candidate.paper.url or "",
            "概要": candidate.paper.abstract[:500] if candidate.paper.abstract else "",
            "マッチトピック": candidate.matched_topics,
            "スコア": candidate.score,
            "消化先候補": self._suggest_digest_targets(candidate),
        }
    
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
    
    def run(
        self,
        topics: Optional[list[str]] = None,
        max_papers: int = 50,
        max_candidates: int = 10,
        dry_run: bool = True
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
        
        # 2. 消化候補選定
        print("[Digestor] Phase 2: Selecting candidates...")
        candidates = self.selector.select_candidates(
            papers,
            max_candidates=max_candidates,
            topic_filter=topics
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
                }
                for c in result.candidates
            ]
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_path
    
    def _generate_eat_batch(self, candidates: list[DigestCandidate]) -> None:
        """
        /eat 用のバッチ入力を生成
        
        将来: LLM に /eat を実行させるプロンプトを生成
        現時点: 消化レポートに含める
        """
        batch_path = self.output_dir / "eat_batch.json"
        
        batch_data = [self._generate_eat_input(c) for c in candidates]
        
        with open(batch_path, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        print(f"[Digestor] /eat batch saved: {batch_path}")


# CLI エントリポイント
def main():
    """CLI エントリポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Digestor Pipeline")
    parser.add_argument("--topics", nargs="+", help="対象トピック")
    parser.add_argument("--max-papers", type=int, default=50, help="最大論文数")
    parser.add_argument("--max-candidates", type=int, default=10, help="最大候補数")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run モード")
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
