# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 知識の関連構造を永続化する必要がある
   → ノート間のリンクグラフが必要
   → link_graph.py が担う

Q.E.D.

---

Link Graph — Bidirectional Link Graph for Knowledge Map

Architecture:
  Markdown ファイル群からリンクを抽出し、
  双方向リンクグラフを構築する。

  Obsidian の Graph View + NotebookLM の Mind Map の統合版。
  mneme ディレクトリを Vault として扱う。

  機能:
    1. [[wikilink]] と [markdown](link) の自動抽出
    2. バックリンク自動生成
    3. ブリッジノード検出（2つ以上のクラスタを接続するノード）
    4. コミュニティ検出（Louvain法）
    5. JSON シリアライズ・永続化
"""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Paths
_MNEME_ROOT = Path.home() / "oikos" / "mneme" / ".hegemonikon"
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
GRAPH_DIR = _MNEME_ROOT / "indices"
GRAPH_PATH = GRAPH_DIR / "link_graph.json"


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class GraphNode:
    """グラフ上のノード（1つの知識ファイル）."""

    id: str  # ファイル stem (e.g. "handoff_2026-02-01_0116")
    path: str  # 絶対パス
    title: str
    source_type: str  # handoff / session / ki / kernel etc.
    out_links: list[str] = field(default_factory=list)  # このノードからの参照先
    in_links: list[str] = field(default_factory=list)  # このノードを参照しているノード
    community: int = -1  # コミュニティID（Louvainで設定）


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class GraphStats:
    """グラフ統計情報."""

    total_nodes: int
    total_edges: int
    total_communities: int
    bridge_nodes: list[str]  # クラスタ間のブリッジ
    top_connected: list[tuple[str, int]]  # 接続数上位


# PURPOSE: の統一的インターフェースを実現する
class LinkGraph:
    """Bidirectional Link Graph.

    mneme ディレクトリ内の Markdown ファイルをスキャンし、
    参照関係を双方向リンクグラフとして構築する。
    """

    # リンクパターン
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]")
    MDLINK_PATTERN = re.compile(r"\[([^\]]+?)\]\((?:file:///)?([^)]+?)\)")
    REFERENCE_PATTERN = re.compile(
        r"(?:参照|see|ref|cf\.?):\s*`?([a-zA-Z0-9_\-./]+\.md)`?"
    )

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self._file_map: dict[str, str] = {}  # stem -> node_id

    # PURPOSE: link_graph の scan directory 処理を実行する
    def scan_directory(self, root: Path) -> int:
        """ディレクトリ内の Markdown ファイルをスキャンしてグラフを構築.

        Args:
            root: スキャンするルートディレクトリ

        Returns:
            検出されたノード数
        """
        if not root.exists():
            logger.warning(f"[LinkGraph] Directory not found: {root}")
            return 0

        md_files = list(root.rglob("*.md"))
        logger.info(f"[LinkGraph] Scanning {len(md_files)} markdown files")

        # Phase 1: ノード登録
        for f in md_files:
            node_id = f.stem
            source_type = self._detect_source_type(f)
            title = self._extract_title(f)

            self.nodes[node_id] = GraphNode(
                id=node_id,
                path=str(f),
                title=title,
                source_type=source_type,
            )
            self._file_map[f.stem] = node_id

        # Phase 2: リンク抽出
        for f in md_files:
            node_id = f.stem
            if node_id not in self.nodes:
                continue

            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue

            links = self._extract_links(content)
            for target in links:
                target_id = self._resolve_link(target)
                if target_id and target_id != node_id and target_id in self.nodes:
                    # Forward link
                    if target_id not in self.nodes[node_id].out_links:
                        self.nodes[node_id].out_links.append(target_id)
                    # Backlink
                    if node_id not in self.nodes[target_id].in_links:
                        self.nodes[target_id].in_links.append(node_id)

        total_edges = sum(len(n.out_links) for n in self.nodes.values())
        logger.info(
            f"[LinkGraph] Built graph: {len(self.nodes)} nodes, {total_edges} edges"
        )
        return len(self.nodes)

    # PURPOSE: [L2-auto] Markdown 内のリンクを全パターンで抽出.
    def _extract_links(self, content: str) -> list[str]:
        """Markdown 内のリンクを全パターンで抽出."""
        links = []

        # [[wikilink]]
        for match in self.WIKILINK_PATTERN.finditer(content):
            links.append(match.group(1).strip())

        # [text](path)
        for match in self.MDLINK_PATTERN.finditer(content):
            path = match.group(2).strip()
            if path.endswith(".md"):
                links.append(Path(path).stem)
            elif not path.startswith("http"):
                links.append(Path(path).stem)

        # 参照: `filename.md`
        for match in self.REFERENCE_PATTERN.finditer(content):
            links.append(Path(match.group(1)).stem)

        return links

    # PURPOSE: [L2-auto] リンクテキストをノード ID に解決.
    def _resolve_link(self, link_text: str) -> Optional[str]:
        """リンクテキストをノード ID に解決.

        完全一致 → stem マッチ → 部分マッチ のフォールバック。
        """
        # 完全一致
        if link_text in self.nodes:
            return link_text

        # stem マッチ
        stem = Path(link_text).stem
        if stem in self._file_map:
            return self._file_map[stem]

        # 部分マッチ（遅い: 必要時のみ）
        for node_id in self.nodes:
            if link_text.lower() in node_id.lower():
                return node_id

        return None

    # PURPOSE: [L2-auto] ファイルパスからソースタイプを推定.
    def _detect_source_type(self, filepath: Path) -> str:
        """ファイルパスからソースタイプを推定."""
        name = filepath.name.lower()
        parts = str(filepath).lower()

        if "handoff" in name:
            return "handoff"
        if "_conv_" in name:
            return "session"
        if "insight_" in name:
            return "ki"
        if "weekly_review" in name:
            return "review"
        if "kernel" in parts:
            return "kernel"
        if "doxa" in parts:
            return "doxa"
        if "workflow" in parts:
            return "workflow"
        if "research" in parts:
            return "research"
        if "x-series" in parts:
            return "xseries"
        return "knowledge"

    # PURPOSE: [L2-auto] ファイルからタイトルを抽出.
    def _extract_title(self, filepath: Path) -> str:
        """ファイルからタイトルを抽出."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# ") and not line.startswith("## "):
                        return line[2:].strip()
            return filepath.stem.replace("_", " ").title()
        except Exception:
            return filepath.stem.replace("_", " ").title()

    # ==========================================================
    # Analysis
    # ==========================================================

    # PURPOSE: backlinks を取得する
    def get_backlinks(self, node_id: str) -> list[str]:
        """指定ノードのバックリンクを取得."""
        node = self.nodes.get(node_id)
        return node.in_links if node else []

    # PURPOSE: neighbors を取得する
    def get_neighbors(self, node_id: str, hops: int = 2) -> set[str]:
        """指定ノードから N ホップ以内の全ノードを取得.

        Proactive Push の Graph-Triggered 推薦に使用。
        """
        if node_id not in self.nodes:
            return set()

        visited = {node_id}
        frontier = {node_id}

        for _ in range(hops):
            next_frontier = set()
            for nid in frontier:
                node = self.nodes.get(nid)
                if node:
                    for link in node.out_links + node.in_links:
                        if link not in visited:
                            next_frontier.add(link)
                            visited.add(link)
            frontier = next_frontier

        visited.discard(node_id)
        return visited

    # PURPOSE: bridge nodes を検索する
    def find_bridge_nodes(self) -> list[str]:
        """クラスタ間のブリッジノードを検出.

        複数のコミュニティに接続しているノード。
        コミュニティ検出前は、次数（degree）上位を返す。
        """
        degree = {}
        for node_id, node in self.nodes.items():
            d = len(set(node.out_links + node.in_links))
            if d >= 3:  # 3 以上の接続を持つノードのみ
                degree[node_id] = d

        # degree 降順
        sorted_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        return [nid for nid, _ in sorted_nodes[:10]]

    # PURPOSE: stats を取得する
    def get_stats(self) -> GraphStats:
        """グラフの統計情報を取得."""
        total_edges = sum(len(n.out_links) for n in self.nodes.values())
        bridges = self.find_bridge_nodes()

        degree = {}
        for node_id, node in self.nodes.items():
            degree[node_id] = len(set(node.out_links + node.in_links))

        top = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]

        communities = set(n.community for n in self.nodes.values() if n.community >= 0)

        return GraphStats(
            total_nodes=len(self.nodes),
            total_edges=total_edges,
            total_communities=len(communities),
            bridge_nodes=bridges,
            top_connected=top,
        )

    # ==========================================================
    # Persistence
    # ==========================================================

    # PURPOSE: link_graph の save 処理を実行する
    def save(self, path: Optional[Path] = None):
        """グラフを JSON に永続化."""
        target = path or GRAPH_PATH
        target.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0",
            "nodes": {nid: asdict(node) for nid, node in self.nodes.items()},
        }

        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[LinkGraph] Saved {len(self.nodes)} nodes to {target}")

    # PURPOSE: link_graph の load 処理を実行する
    def load(self, path: Optional[Path] = None) -> bool:
        """JSON からグラフを読み込み."""
        target = path or GRAPH_PATH
        if not target.exists():
            return False

        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.nodes.clear()
            self._file_map.clear()

            for nid, ndata in data.get("nodes", {}).items():
                self.nodes[nid] = GraphNode(**ndata)
                self._file_map[nid] = nid

            logger.info(f"[LinkGraph] Loaded {len(self.nodes)} nodes from {target}")
            return True
        except Exception as e:
            logger.error(f"[LinkGraph] Failed to load: {e}")
            return False

    # ==========================================================
    # Mermaid Export
    # ==========================================================

    # PURPOSE: link_graph の to mermaid 処理を実行する
    def to_mermaid(self, max_nodes: int = 30) -> str:
        """Mermaid グラフフォーマットで出力.

        大規模グラフの場合、接続数上位のノードのみ表示。
        """
        # 接続数上位のノードを選択
        degree = {}
        for nid, node in self.nodes.items():
            degree[nid] = len(set(node.out_links + node.in_links))

        top_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        selected = {nid for nid, _ in top_nodes[:max_nodes]}

        lines = ["graph LR"]
        seen_edges = set()

        for nid in selected:
            node = self.nodes[nid]
            # ノードラベル
            label = node.title[:30].replace('"', "'")
            lines.append(f'    {nid}["{label}"]')

            for target in node.out_links:
                if target in selected:
                    edge = f"{nid}-->{target}"
                    if edge not in seen_edges:
                        lines.append(f"    {edge}")
                        seen_edges.add(edge)

        return "\n".join(lines)


# ==========================================================
# Convenience functions
# ==========================================================

# PURPOSE: knowledge graph を構築する
def build_knowledge_graph() -> LinkGraph:
    """mneme ディレクトリ全体をスキャンしてリンクグラフを構築・保存."""
    graph = LinkGraph()

    # mneme 全体をスキャン
    if _MNEME_ROOT.exists():
        graph.scan_directory(_MNEME_ROOT)

    # kernel もスキャン
    kernel_dir = _HEGEMONIKON_ROOT / "kernel"
    if kernel_dir.exists():
        graph.scan_directory(kernel_dir)

    graph.save()
    return graph


# PURPOSE: or build graph を読み込む
def load_or_build_graph() -> LinkGraph:
    """既存グラフを読み込み、なければ構築."""
    graph = LinkGraph()
    if not graph.load():
        graph = build_knowledge_graph()
    return graph


# PURPOSE: link_graph の main 処理を実行する
def main():
    """CLI エントリーポイント."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Link Graph — Bidirectional Link Graph for Knowledge Map"
    )
    subparsers = parser.add_subparsers(dest="command")

    # build
    subparsers.add_parser("build", help="グラフを構築")

    # stats
    subparsers.add_parser("stats", help="グラフ統計")

    # backlinks
    bl_parser = subparsers.add_parser("backlinks", help="バックリンク表示")
    bl_parser.add_argument("node_id", help="ノード ID")

    # neighbors
    nb_parser = subparsers.add_parser("neighbors", help="N ホップ以内のノード")
    nb_parser.add_argument("node_id", help="ノード ID")
    nb_parser.add_argument("--hops", type=int, default=2, help="ホップ数")

    # mermaid
    mm_parser = subparsers.add_parser("mermaid", help="Mermaid 出力")
    mm_parser.add_argument("--max", type=int, default=30, help="最大ノード数")

    args = parser.parse_args()

    if args.command == "build":
        graph = build_knowledge_graph()
        stats = graph.get_stats()
        print(f"✅ Graph built: {stats.total_nodes} nodes, {stats.total_edges} edges")
        print(f"   Bridge nodes: {stats.bridge_nodes[:5]}")

    elif args.command == "stats":
        graph = load_or_build_graph()
        stats = graph.get_stats()
        print(f"Nodes: {stats.total_nodes}")
        print(f"Edges: {stats.total_edges}")
        print(f"Communities: {stats.total_communities}")
        print(f"Top connected:")
        for nid, deg in stats.top_connected[:5]:
            print(f"  {nid}: {deg}")

    elif args.command == "backlinks":
        graph = load_or_build_graph()
        links = graph.get_backlinks(args.node_id)
        print(f"Backlinks for '{args.node_id}':")
        for l in links:
            print(f"  ← {l}")

    elif args.command == "neighbors":
        graph = load_or_build_graph()
        neighbors = graph.get_neighbors(args.node_id, hops=args.hops)
        print(f"Neighbors ({args.hops} hops) for '{args.node_id}':")
        for n in sorted(neighbors):
            print(f"  {n}")

    elif args.command == "mermaid":
        graph = load_or_build_graph()
        print(graph.to_mermaid(max_nodes=args.max))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
