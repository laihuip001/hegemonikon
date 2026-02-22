# PROOF: [L2/Mekhane] <- mekhane/dendron/doc_staleness.py A0→Necessity
"""
S7: Doc Staleness Checker

PURPOSE: ドキュメント間の依存関係と鮮度を管理し、
古くなった情報 (Stale Documentation) を検出する。

- Frontmatter `depends_on` を解析
- 上流ドキュメントの更新日/バージョンと比較
- 循環依存の検出
- EPTスコアへの統合 (Doc Health %)
"""

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yaml
from packaging.version import parse as _parse_version


class StalenessStatus(Enum):
    OK = "ok"
    STALE = "stale"       # 上流が更新されている / バージョン不整合
    WARNING = "warning"   # 日付が古い (閾値超過)
    CIRCULAR = "circular" # 循環依存


@dataclass
class DocDependency:
    doc_id: str
    min_version: str = "0.0.0"


@dataclass
class DocInfo:
    doc_id: str
    version: str
    path: Path
    updated: str
    depends_on: List[DocDependency]


@dataclass
class StalenessResult:
    doc_id: str
    upstream_id: str
    status: StalenessStatus
    detail: str


class DocStalenessChecker:
    """ドキュメントの依存関係と鮮度をチェックするクラス."""

    STALE_DAYS_THRESHOLD = 90  # 3ヶ月

    def __init__(self):
        self._docs: dict[str, DocInfo] = {}
        self._results: list[StalenessResult] = []
        self._warnings: list[str] = []

    # PURPOSE: doc_id 重複などの警告リストを返す
    @property
    def warnings(self) -> list[str]:
        """警告リストを返す."""
        return self._warnings

    # PURPOSE: 指定ディレクトリ以下の Markdown ファイルをスキャンし、メタデータを収集する
    def scan(self, root_dir: Path) -> None:
        """ディレクトリを再帰的にスキャンしてドキュメント情報を収集する."""
        if not root_dir.exists():
            return

        for path in root_dir.rglob("*.md"):
            doc = self._parse_doc(path)
            if doc:
                if doc.doc_id in self._docs:
                    self._warnings.append(
                        f"Duplicate doc_id '{doc.doc_id}': {path} vs {self._docs[doc.doc_id].path}"
                    )
                else:
                    self._docs[doc.doc_id] = doc

    # PURPOSE: Markdown ファイルの frontmatter を解析して DocInfo を生成する
    def _parse_doc(self, path: Path) -> Optional[DocInfo]:
        """Markdown ファイルの frontmatter を解析."""
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            meta = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None

        if not isinstance(meta, dict):
            return None

        doc_id = meta.get("doc_id")
        version = meta.get("version")
        if not doc_id or not version:
            return None

        depends_on: list[DocDependency] = []
        raw_deps = meta.get("depends_on", [])
        if isinstance(raw_deps, list):
            for dep in raw_deps:
                if isinstance(dep, dict) and "doc_id" in dep:
                    depends_on.append(DocDependency(
                        doc_id=dep["doc_id"],
                        min_version=str(dep.get("min_version", "0.0.0")),
                    ))

        return DocInfo(
            doc_id=str(doc_id),
            version=str(version),
            path=path,
            updated=str(meta.get("updated", "")),
            depends_on=depends_on,
        )

    # PURPOSE: 依存グラフを走査し、全辺の STALE/WARNING/CIRCULAR を判定する
    def check(self) -> List[StalenessResult]:
        """依存グラフを検査して StalenessResult 一覧を返す."""
        self._results.clear()

        # 循環検出用
        edges: dict[str, set[str]] = {}
        for doc in self._docs.values():
            edges[doc.doc_id] = {d.doc_id for d in doc.depends_on}

        circular_pairs = self._detect_circular(edges)

        for doc in self._docs.values():
            for dep in doc.depends_on:
                # 循環チェック
                if (doc.doc_id, dep.doc_id) in circular_pairs:
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        upstream_id=dep.doc_id,
                        status=StalenessStatus.CIRCULAR,
                        detail=f"循環依存: {doc.doc_id} ↔ {dep.doc_id}",
                    ))
                    continue

                upstream = self._docs.get(dep.doc_id)
                if not upstream:
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        upstream_id=dep.doc_id,
                        status=StalenessStatus.STALE,
                        detail=f"上流 {dep.doc_id} が見つからない",
                    ))
                    continue

                # Version 比較 (packaging.version)
                upstream_ver = _parse_version(upstream.version)
                min_ver = _parse_version(dep.min_version)

                if upstream_ver > min_ver:
                    self._results.append(StalenessResult(
                        doc_id=doc.doc_id,
                        upstream_id=dep.doc_id,
                        status=StalenessStatus.STALE,
                        detail=(
                            f"上流 {dep.doc_id} v{upstream.version} > "
                            f"下流 min_version {dep.min_version}"
                        ),
                    ))
                    continue

                # 日付差チェック
                up_str = upstream.updated or ""
                dn_str = doc.updated or ""
                if up_str and dn_str:
                    try:
                        up_date = datetime.strptime(up_str, "%Y-%m-%d")
                        dn_date = datetime.strptime(dn_str, "%Y-%m-%d")
                        diff = abs((up_date - dn_date).days)
                        if diff > self.STALE_DAYS_THRESHOLD:
                            self._results.append(StalenessResult(
                                doc_id=doc.doc_id,
                                upstream_id=dep.doc_id,
                                status=StalenessStatus.WARNING,
                                detail=f"日付差 {diff}日 (>{self.STALE_DAYS_THRESHOLD}日)",
                            ))
                            continue
                    except ValueError:
                        pass  # 日付パース失敗は無視

                self._results.append(StalenessResult(
                    doc_id=doc.doc_id,
                    upstream_id=dep.doc_id,
                    status=StalenessStatus.OK,
                    detail="最新",
                ))

        return self._results

    # PURPOSE: 有向グラフの循環辺を検出し、CIRCULAR ステータスの判定材料にする
    @staticmethod
    def _detect_circular(edges: dict[str, set[str]]) -> set[tuple[str, str]]:
        """循環する辺ペアの集合を返す."""
        circular: set[tuple[str, str]] = set()
        for src, dsts in edges.items():
            for dst in dsts:
                if dst in edges and src in edges.get(dst, set()):
                    circular.add((src, dst))
                    circular.add((dst, src))
        return circular

    # PURPOSE: STALE でない依存辺の割合を計算し、EPT スコア統合の入力にする
    def doc_health_pct(self) -> float:
        """Doc Health %: STALE でない割合."""
        if not self._results:
            return 100.0
        ok_count = sum(
            1 for r in self._results
            if r.status in (StalenessStatus.OK, StalenessStatus.WARNING)
        )
        return (ok_count / len(self._results)) * 100.0

    # PURPOSE: CLI 実行時に人間が読めるレポートを標準出力に表示する
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
    def generate_mermaid(self) -> str:
        """Mermaid 形式の依存グラフを生成."""
        if not self._docs:
            return "graph TD\n    Target[チェック対象なし]"

        lines = ["graph TD"]
        # ノード定義とエッジ
        # バージョン情報を含める: DocID<br/>(v1.0.0)
        for doc in self._docs.values():
            safe_id = doc.doc_id.replace("-", "_")  # Mermaid ID safety
            lines.append(f'    {safe_id}["{doc.doc_id}<br/>(v{doc.version})"]')
            for dep in doc.depends_on:
                dep_safe_id = dep.doc_id.replace("-", "_")
                # リンクにもラベル (min_version) をつけると情報過多かも？ 一旦なしで。
                lines.append(f"    {safe_id} --> {dep_safe_id}")

        # スタイリング (STALE=Red, WARNING=Gold, CIRCULAR=Purple)
        # 判定結果に基づいてノードを色分けする
        stale_ids = {
            r.doc_id.replace("-", "_") for r in self._results
            if r.status == StalenessStatus.STALE
        }
        warning_ids = {
            r.doc_id.replace("-", "_") for r in self._results
            if r.status == StalenessStatus.WARNING
        }
        circular_ids = {
            r.doc_id.replace("-", "_") for r in self._results
            if r.status == StalenessStatus.CIRCULAR
        }

        # 赤 (STALE)
        for nid in stale_ids:
            lines.append(f"    style {nid} stroke:red,stroke-width:3px")

        # 黄 (WARNING) - STALE 優先
        for nid in warning_ids - stale_ids:
            lines.append(f"    style {nid} stroke:gold,stroke-width:3px")

        # 紫 (CIRCULAR)
        for nid in circular_ids:
            lines.append(f"    style {nid} stroke:purple,stroke-width:3px,stroke-dasharray: 5 5")

        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────


# PURPOSE: CLI エントリポイント — --check で staleness 検査を実行する
def main() -> None:
    parser = argparse.ArgumentParser(description="Doc Staleness Checker")
    parser.add_argument(
        "--check", action="store_true", help="Run staleness check",
    )
    parser.add_argument(
        "--root", type=str, default=None,
        help="Project root (default: auto-detect)",
    )
    parser.add_argument(
        "--graph", action="store_true", help="Output Mermaid graph",
    )
    parser.add_argument(
        "--reverse-deps", type=str, metavar="DOC_ID",
        help="Find documents that depend on DOC_ID",
    )
    args = parser.parse_args()

    if not args.check and not args.graph and not args.reverse_deps:
        parser.print_help()
        return

    root = Path(args.root) if args.root else Path(__file__).parent.parent.parent
    checker = DocStalenessChecker()
    checker.scan(root)
    results = checker.check()

    if args.reverse_deps:
        target = args.reverse_deps
        print(f"🔎 Reverse dependencies for '{target}':")
        found = []
        for doc in checker._docs.values():
            for dep in doc.depends_on:
                if dep.doc_id == target:
                    found.append(doc)
                    break
        if found:
            for doc in found:
                print(f"  - {doc.doc_id} (v{doc.version}) in {doc.path.relative_to(root)}")
        else:
            print("  (None found)")
        return

    if args.graph:
        print(checker.generate_mermaid())
        return

    print(checker.format_report())

    stale_count = sum(1 for r in results if r.status == StalenessStatus.STALE)
    sys.exit(1 if stale_count > 0 else 0)


if __name__ == "__main__":
    main()
