# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → WF turbo ブロック間でデータを受け渡す仕組みが必要
   → シェル環境変数 ${O1_OUT} 等は quoting 問題がある
   → JSON ファイルベースのコンテキストストアで解決
   → wf_env_bridge.py が担う

Q.E.D.

---

WF Environment Bridge — WF turbo ブロック間コンテキスト共有

Peras WF (/o, /s, /h, /p, /k, /a) の turbo ブロック間で
定理出力を共有するためのコンテキストストア。

シェル環境変数 ${O1_OUT} の問題:
  - マルチライン出力が壊れる
  - 日本語のクォーティングが不安定
  - シェルの文字数制限

解決策:
  - /tmp/hgk_wf_ctx_{session_id}.json にコンテキストを永続化
  - set_output / get_output で読み書き
  - cone_bridge.py はこのストアから読む

Usage:
    # Pythonから
    from mekhane.fep.wf_env_bridge import WFContext
    ctx = WFContext()
    ctx.set_output("O1", "深い認識の出力")
    ctx.set_output("O2", "意志の出力")
    o1 = ctx.get_output("O1")

    # CLIから (turbo block)
    PYTHONPATH=. .venv/bin/python -m mekhane.fep.wf_env_bridge set O1 "深い認識の出力"
    PYTHONPATH=. .venv/bin/python -m mekhane.fep.wf_env_bridge get O1
    PYTHONPATH=. .venv/bin/python -m mekhane.fep.wf_env_bridge dump --series O
    PYTHONPATH=. .venv/bin/python -m mekhane.fep.wf_env_bridge clear
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# Context file location
_DEFAULT_DIR = Path(tempfile.gettempdir())


def _ctx_path(session_id: Optional[str] = None) -> Path:
    """Get the context file path for the given session."""
    sid = session_id or os.environ.get("HGK_SESSION_ID", "default")
    return _DEFAULT_DIR / f"hgk_wf_ctx_{sid}.json"


@dataclass
class WFStepRecord:
    """Record of a single WF step's output."""

    theorem_id: str        # e.g. "O1"
    output: str            # 定理出力テキスト
    timestamp: str = ""    # ISO 8601
    pw: float = 0.0        # Precision Weighting [-1, +1]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class WFContext:
    """WF turbo ブロック間のコンテキストストア。

    JSON ファイルベースで永続化し、複数のturboブロック間で
    定理出力をやり取りする。

    Design:
      - set_output: 定理出力を保存
      - get_output: 定理出力を取得
      - get_series_outputs: シリーズ全定理の出力を取得
      - clear: セッション終了時にクリア
    """

    session_id: Optional[str] = None
    outputs: Dict[str, WFStepRecord] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._path = _ctx_path(self.session_id)
        self._load()

    def _load(self):
        """ファイルからコンテキストを読み込む。"""
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for tid, rec in data.get("outputs", {}).items():
                    self.outputs[tid] = WFStepRecord(**rec)
                self.meta = data.get("meta", {})
            except (json.JSONDecodeError, TypeError, KeyError):
                pass

    def _save(self):
        """コンテキストをファイルに保存。"""
        data = {
            "session_id": self.session_id or "default",
            "outputs": {k: asdict(v) for k, v in self.outputs.items()},
            "meta": self.meta,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def set_output(self, theorem_id: str, output: str, *,
                   pw: float = 0.0,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """定理出力を保存。

        Args:
            theorem_id: 定理ID (e.g. "O1", "S2")
            output: 出力テキスト
            pw: Precision Weighting [-1, +1]
            metadata: 追加メタデータ
        """
        self.outputs[theorem_id] = WFStepRecord(
            theorem_id=theorem_id,
            output=output,
            pw=pw,
            metadata=metadata or {},
        )
        self._save()

    def get_output(self, theorem_id: str) -> Optional[str]:
        """定理出力を取得。存在しなければ None。"""
        rec = self.outputs.get(theorem_id)
        return rec.output if rec else None

    def get_record(self, theorem_id: str) -> Optional[WFStepRecord]:
        """定理レコード全体を取得。"""
        return self.outputs.get(theorem_id)

    def get_series_outputs(self, series: str) -> Dict[str, str]:
        """シリーズ全定理の出力を Dict で返す。

        Args:
            series: "O", "S", "H", "P", "K", "A"

        Returns:
            e.g. {"O1": "output1", "O2": "output2", ...}
        """
        return {
            tid: rec.output
            for tid, rec in self.outputs.items()
            if tid.startswith(series)
        }

    def get_series_pw(self, series: str) -> Dict[str, float]:
        """シリーズ全定理の PW を Dict で返す。"""
        return {
            tid: rec.pw
            for tid, rec in self.outputs.items()
            if tid.startswith(series)
        }

    def set_meta(self, key: str, value: Any) -> None:
        """メタデータを設定。"""
        self.meta[key] = value
        self._save()

    def get_meta(self, key: str, default: Any = None) -> Any:
        """メタデータを取得。"""
        return self.meta.get(key, default)

    def list_outputs(self) -> List[str]:
        """保存されている全定理IDのリスト。"""
        return sorted(self.outputs.keys())

    def clear(self) -> None:
        """コンテキストをクリア。"""
        self.outputs.clear()
        self.meta.clear()
        if self._path.exists():
            self._path.unlink()

    def to_cone_input(self, series: str) -> Dict[str, str]:
        """cone_bridge.py 互換の入力辞書を生成。

        cone_bridge.py --file と組み合わせて使用。
        """
        return self.get_series_outputs(series)

    def export_for_cone(self, series: str) -> Path:
        """cone_bridge.py --file 用の JSON ファイルを生成。

        Returns:
            生成した JSON ファイルのパス
        """
        data = self.to_cone_input(series)
        pw = self.get_series_pw(series)
        out_path = _DEFAULT_DIR / f"hgk_cone_{series}.json"
        payload = {"outputs": data, "pw": pw}
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return out_path


# =============================================================================
# CLI Interface
# =============================================================================


def _cli():
    """CLI entrypoint for turbo blocks."""
    parser = argparse.ArgumentParser(
        description="WF Environment Bridge — turbo block context sharing",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # set
    p_set = sub.add_parser("set", help="Set theorem output")
    p_set.add_argument("theorem_id", help="Theorem ID (e.g. O1)")
    p_set.add_argument("output", help="Output text")
    p_set.add_argument("--pw", type=float, default=0.0, help="PW [-1,+1]")

    # get
    p_get = sub.add_parser("get", help="Get theorem output")
    p_get.add_argument("theorem_id", help="Theorem ID (e.g. O1)")

    # dump
    p_dump = sub.add_parser("dump", help="Dump all or series outputs")
    p_dump.add_argument("--series", "-s", default=None, help="Series filter")
    p_dump.add_argument("--json", action="store_true", help="JSON output")

    # clear
    sub.add_parser("clear", help="Clear all context")

    # export
    p_export = sub.add_parser("export", help="Export series for cone_bridge")
    p_export.add_argument("series", help="Series to export (O/S/H/P/K/A)")

    # list
    sub.add_parser("list", help="List stored theorem IDs")

    args = parser.parse_args()
    ctx = WFContext()

    if args.command == "set":
        ctx.set_output(args.theorem_id, args.output, pw=args.pw)
        print(f"✅ {args.theorem_id} saved")

    elif args.command == "get":
        out = ctx.get_output(args.theorem_id)
        if out is None:
            print(f"⚠️ {args.theorem_id} not found", file=sys.stderr)
            sys.exit(1)
        print(out)

    elif args.command == "dump":
        if args.series:
            outputs = ctx.get_series_outputs(args.series)
        else:
            outputs = {tid: rec.output for tid, rec in ctx.outputs.items()}

        if args.json:
            print(json.dumps(outputs, ensure_ascii=False, indent=2))
        else:
            for tid, out in sorted(outputs.items()):
                print(f"[{tid}] {out[:80]}{'...' if len(out) > 80 else ''}")

    elif args.command == "clear":
        ctx.clear()
        print("✅ Context cleared")

    elif args.command == "export":
        path = ctx.export_for_cone(args.series)
        print(f"✅ Exported to {path}")

    elif args.command == "list":
        ids = ctx.list_outputs()
        if ids:
            print("\n".join(ids))
        else:
            print("(empty)")


if __name__ == "__main__":
    _cli()
