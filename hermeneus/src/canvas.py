# PROOF: [L2/Canvas-CoT] <- hermeneus/src/ 思考ノード管理
"""
Canvas — Canvas-CoT ノードツリー管理

arXiv 2602.10494 に基づく非単調推論のノード管理。
推論トレースを append-only ログではなく、ID アドレス可能なツリーとして管理。
TapeWriter と連携してノード操作を JSONL に記録。

Usage:
    from hermeneus.src.canvas import Canvas
    from mekhane.tape import TapeWriter
    
    tape = TapeWriter()
    canvas = Canvas(tape, "/noe+")
    
    h1 = canvas.insert("仮説A: FEP は汎用的")
    h2 = canvas.insert("仮説B: FEP は限定的", parent=h1)
    canvas.modify(h1, "修正: FEP は条件付き汎用的", reason="反証あり")
    canvas.delete(h2, reason="仮説A に統合")
    
    print(canvas.active_nodes())
    print(canvas.summary())
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThoughtNode:
    """Canvas-CoT の思考ノード。"""
    id: str                 # H1, H2, ...
    content: str            # 仮説・主張の内容
    status: str = "active"  # active | modified | deleted
    source: str = "expansion"  # expansion | council | critique | external
    confidence: int = 50    # 0-100
    parent: str = ""        # 親ノード ID
    history: list[str] = field(default_factory=list)  # 修正履歴


class Canvas:
    """Canvas-CoT ノードツリー管理。

    CRUD 操作でノードを管理し、TapeWriter に操作ログを記録する。
    """

    def __init__(self, tape=None, wf: str = ""):
        """Initialize Canvas.

        Args:
            tape: TapeWriter instance (None なら記録しない)
            wf: 関連ワークフロー名 (例: "/noe+")
        """
        self._nodes: dict[str, ThoughtNode] = {}
        self._tape = tape
        self._wf = wf
        self._counter = 0

    def insert(
        self,
        content: str,
        source: str = "expansion",
        confidence: int = 50,
        parent: str = "",
    ) -> str:
        """新しい思考ノードを追加。

        Returns:
            ノード ID (H1, H2, ...)
        """
        self._counter += 1
        node_id = f"H{self._counter}"
        node = ThoughtNode(
            id=node_id,
            content=content,
            status="active",
            source=source,
            confidence=confidence,
            parent=parent,
        )
        self._nodes[node_id] = node
        self._log("NODE_INSERT", node_id=node_id, content=content[:200], source=source)
        return node_id

    def modify(self, node_id: str, new_content: str, reason: str = "") -> bool:
        """ノードの内容を修正。修正履歴を保持。"""
        node = self._nodes.get(node_id)
        if not node or node.status == "deleted":
            return False

        old = node.content
        node.history.append(f"{old} → {new_content} (reason: {reason})")
        node.content = new_content
        node.status = "modified"
        self._log("NODE_MODIFY", node_id=node_id, old=old[:100], new=new_content[:100], reason=reason)
        return True

    def delete(self, node_id: str, reason: str = "") -> bool:
        """ノードを論理削除。"""
        node = self._nodes.get(node_id)
        if not node or node.status == "deleted":
            return False

        node.status = "deleted"
        self._log("NODE_DELETE", node_id=node_id, reason=reason)
        return True

    def replace(self, node_id: str, new_content: str, reason: str = "") -> bool:
        """ノード全体を置換 (パラダイムシフト)。"""
        node = self._nodes.get(node_id)
        if not node:
            return False

        old = node.content
        node.history.append(f"REPLACED: {old} → {new_content} (reason: {reason})")
        node.content = new_content
        node.status = "active"
        node.source = "critique"
        self._log("NODE_REPLACE", node_id=node_id, old=old[:100], new=new_content[:100], reason=reason)
        return True

    def active_nodes(self) -> list[ThoughtNode]:
        """生存中のノード一覧。"""
        return [n for n in self._nodes.values() if n.status != "deleted"]

    def get(self, node_id: str) -> Optional[ThoughtNode]:
        """ノードを取得。"""
        return self._nodes.get(node_id)

    def all_nodes(self) -> list[ThoughtNode]:
        """全ノード (削除済み含む)。"""
        return list(self._nodes.values())

    def summary(self) -> dict:
        """Canvas の統計サマリー。"""
        total = len(self._nodes)
        active = len([n for n in self._nodes.values() if n.status == "active"])
        modified = len([n for n in self._nodes.values() if n.status == "modified"])
        deleted = len([n for n in self._nodes.values() if n.status == "deleted"])
        alive = [n.id for n in self._nodes.values() if n.status != "deleted"]
        return {
            "total": total,
            "active": active,
            "modified": modified,
            "deleted": deleted,
            "alive_nodes": alive,
        }

    def _log(self, step: str, **kwargs) -> None:
        """TapeWriter にノード操作を記録。"""
        if self._tape:
            try:
                self._tape.log(wf=self._wf, step=step, **kwargs)
            except Exception:
                pass  # Tape failure should not block Canvas operations
