# PROOF: [L2/インフラ] <- mekhane/dendron/ A0→Quality
"""
S2 Doc Staleness Checker (v1.0)

Purpose:
  - 依存グラフ (upstream → downstream) を構築
  - 上流の更新日時 > 下流の更新日時 を検出 (STALE)
  - 循環依存を検出 (CIRCULAR)
  - 人間可読レポート & Mermaid グラフ生成

Usage:
  python -m mekhane.dendron.doc_staleness check .
  python -m mekhane.dendron.doc_staleness mermaid . > graph.mmd
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


# PURPOSE: ドキュメントの鮮度状態を定義する列挙型
class StalenessStatus(Enum):
    """ドキュメントの鮮度状態."""
    OK = "OK"
    STALE = "STALE"
    WARNING = "WARNING"
    CIRCULAR = "CIRCULAR"


# PURPOSE: ドキュメントのメタ情報 (ID, パス, 更新日時, 上流依存) を統合管理する
@dataclass
class DocInfo:
    """ドキュメント情報."""
    doc_id: str
    path: Path
    mtime: float
    upstreams: List[str] = field(default_factory=list)
    title: str = ""


# PURPOSE: 鮮度チェックの結果 (状態, 詳細) を統合管理する
@dataclass
class StalenessResult:
    """鮮度チェック結果."""
    doc_id: str
    status: StalenessStatus
    upstream_id: Optional[str] = None
    detail: str = ""


# PURPOSE: ドキュメント依存グラフを構築し、更新日時と構造的健全性を検証するチェッカー
class DocStalenessChecker:
    """依存グラフに基づきドキュメントの鮮度を検証する."""

    # 無視するディレクトリ
    EXCLUDE_DIRS = {".git", ".venv", "node_modules", "__pycache__"}

    # 上流参照パターンの定義 (拡張可能)
    # 例: "upstream: [doc_id]"
    UPSTREAM_PATTERN = re.compile(r"upstream:\s*\[(.*?)\]")

    # 例: "A0 -> B0" (PROOFヘッダ等)
    PROOF_PATTERN = re.compile(r"([A-Z][0-9])\s*->\s*([A-Z][0-9])")

    # Frontmatter の doc_id
    ID_PATTERN = re.compile(r"^id:\s*(.+)$", re.MULTILINE)

    def __init__(self) -> None:
        self._docs: Dict[str, DocInfo] = {}
        self._results: List[StalenessResult] = []
        self._warnings: List[str] = []

    # PURPOSE: scan 時の警告 (doc_id 重複等).
    @property
    def warnings(self) -> List[str]:
        """scan 時の警告 (doc_id 重複等)."""
        return list(self._warnings)

    # PURPOSE: プロジェクト内の全 .md ファイルから frontmatter を収集し、依存グラフ構築の材料にする
    def scan(self, root: Path) -> List[DocInfo]:
        """全 .md ファイルの YAML frontmatter をパースして DocInfo 一覧を構築."""
        self._docs.clear()
        self._warnings.clear()
        for md_path in sorted(root.rglob("*.md")):
            # 除外ディレクトリ判定
            if any(part in self.EXCLUDE_DIRS for part in md_path.parts):
                continue
            doc_info = self._parse_frontmatter(md_path)
            if doc_info:
                # doc_id 重複検出
                if doc_info.doc_id in self._docs:
                    existing = self._docs[doc_info.doc_id]
                    self._warnings.append(
                        f"doc_id 重複: '{doc_info.doc_id}' "
                        f"({existing.path} と {doc_info.path})"
                    )
                self._docs[doc_info.doc_id] = doc_info
        return list(self._docs.values())

    def _parse_frontmatter(self, path: Path) -> Optional[DocInfo]:
        """ファイルの先頭 YAML ブロック (または独自記法) を解析."""
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None

        # YAML frontmatter (--- ... ---)
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            # PROOF header fallback (簡易)
            # # PROOF: [L1/Theory] <- kernel/ A0->B0
            # A0->B0 のような関係があれば A0 を upstream とみなす... は複雑なので
            # ここでは明示的な frontmatter のみを対象とする (S2仕様)
            return None

        try:
            data = yaml.safe_load(fm_match.group(1))
        except yaml.YAMLError:
            return None

        doc_id = data.get("id")
        if not doc_id:
            return None

        # upstreams: 文字列 or リスト
        ups = data.get("upstream", [])
        if isinstance(ups, str):
            # "A0, B0" -> ["A0", "B0"]
            ups = [u.strip() for u in ups.split(",")]

        return DocInfo(
            doc_id=str(doc_id),
            path=path,
            mtime=path.stat().st_mtime,
            upstreams=[str(u) for u in ups if u],
            title=data.get("title", "")
        )

    # PURPOSE: 構築された依存グラフをトラバースし、Stale (更新遅れ) や循環依存を検出する
    def check(self) -> List[StalenessResult]:
        """依存グラフの健全性をチェック."""
        self._results.clear()

        # 1. 依存先解決チェック
        for doc in self._docs.values():
            for up_id in doc.upstreams:
                if up_id not in self._docs:
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        status=StalenessStatus.WARNING,
                        upstream_id=up_id,
                        detail=f"依存先 ID '{up_id}' が見つかりません"
                    ))
                    continue

                upstream = self._docs[up_id]

                # 2. Staleness チェック
                # upstream が downstream より新しい場合 = STALE
                # (1秒程度の誤差は許容してもよいが、ここでは厳密比較)
                if upstream.mtime > doc.mtime:
                    diff_sec = upstream.mtime - doc.mtime
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        status=StalenessStatus.STALE,
                        upstream_id=up_id,
                        detail=f"上流が {diff_sec:.0f}秒 新しい ({upstream.path.name})"
                    ))
                else:
                    # OK (明示的に記録する場合)
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        status=StalenessStatus.OK,
                        upstream_id=up_id
                    ))

        # 3. 循環参照チェック (DFS)
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        # PURPOSE: DFS 再帰関数 (内部関数)
        def dfs(curr_id: str):
            visited.add(curr_id)
            recursion_stack.add(curr_id)

            curr_doc = self._docs.get(curr_id)
            if curr_doc:
                for up_id in curr_doc.upstreams:
                    if up_id not in self._docs:
                        continue
                    if up_id in recursion_stack:
                        self._results.append(StalenessResult(
                            doc_id=curr_id,
                            status=StalenessStatus.CIRCULAR,
                            upstream_id=up_id,
                            detail=f"循環依存検出: {curr_id} -> ... -> {up_id}"
                        ))
                    elif up_id not in visited:
                        dfs(up_id)

            recursion_stack.remove(curr_id)

        for doc_id in self._docs:
            if doc_id not in visited:
                dfs(doc_id)

        return self._results

    # PURPOSE: ドキュメント全体の健全性スコア (OK率) を計算する
    def doc_health_pct(self) -> float:
        """健全性スコア (OK率)."""
        if not self._results:
            return 100.0

        # OK 以外のレコード数をカウント (同じドキュメントの複数エラー含む)
        negatives = sum(1 for r in self._results if r.status != StalenessStatus.OK)
        total_checks = len(self._results)

        return 100.0 * (1.0 - (negatives / total_checks))

    # PURPOSE: チェック結果をレポートとして整形し、CIや人間が読める形式で出力する
    def format_report(self) -> str:
        """人間可読なレポートをフォーマット."""
        if not self._results:
            return "📄 Doc Staleness: チェック対象なし"

        stale = [r for r in self._results if r.status == StalenessStatus.STALE]
        warnings = [r for r in self._results if r.status == StalenessStatus.WARNING]
        circular = [r for r in self._results if r.status == StalenessStatus.CIRCULAR]
        ok = [r for r in self._results if r.status == StalenessStatus.OK]

        lines: list[str] = []
        pct = self.doc_health_pct()
        total = len(self._results)
        lines.append(
            f"📄 **Doc Health**: {pct:.0f}% "
            f"({len(ok)}/{total} OK, {len(stale)} STALE, "
            f"{len(warnings)} WARNING, {len(circular)} CIRCULAR)"
        )

        for r in stale:
            lines.append(f"  ❌ {r.doc_id} ← {r.upstream_id}: {r.detail}")
        for r in warnings:
            lines.append(f"  ⚠️ {r.doc_id} ← {r.upstream_id}: {r.detail}")
        for r in circular:
            lines.append(f"  🔄 {r.doc_id} ← {r.upstream_id}: {r.detail}")

        # doc_id 重複警告
        for w in self._warnings:
            lines.append(f"  ⚠️ {w}")

        return "\n".join(lines)

    # PURPOSE: 依存関係を Mermaid グラフ形式で出力する (F6)
    def to_mermaid(self) -> str:
        """Mermaid 形式のグラフ定義を出力."""
        lines = ["graph TD"]

        # ノード定義 (Stale 状態等で色分けしたい場合はクラス定義を追加)
        for doc in self._docs.values():
            safe_id = doc.doc_id.replace("-", "_").replace(".", "_")
            lines.append(f"    {safe_id}[\"{doc.doc_id}<br>{doc.title}\"]")

            for up_id in doc.upstreams:
                if up_id in self._docs:
                    safe_up = up_id.replace("-", "_").replace(".", "_")
                    # up -> down (更新フロー)
                    # 実際は upstream が古ければ下流が腐る
                    lines.append(f"    {safe_up} --> {safe_id}")

        return "\n".join(lines)


if __name__ == "__main__":
    # 簡易 CLI
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["check", "mermaid"])
    parser.add_argument("path", default=".")
    args = parser.parse_args()

    checker = DocStalenessChecker()
    checker.scan(Path(args.path))

    if args.command == "check":
        checker.check()
        print(checker.format_report())
        if any(r.status != StalenessStatus.OK for r in checker._results):
            sys.exit(1)
    elif args.command == "mermaid":
        print(checker.to_mermaid())
