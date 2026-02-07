# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 知識の自動取り込みがプッシュ型表面化の前提
→ Syncthing 同期フォルダの変更検出
→ sync_watcher.py が担う

# PURPOSE: Syncthing 同期フォルダの変更を検出し LanceDB にインデキシングする
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_PKS_DIR = Path(__file__).resolve().parent
_MEKHANE_DIR = _PKS_DIR.parent
_HEGEMONIKON_ROOT = _MEKHANE_DIR.parent

if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))


@dataclass
class FileChange:
    """ファイル変更の記録"""

    path: Path
    change_type: str  # "added", "modified", "deleted"
    checksum: str = ""


class SyncWatcher:
    """Syncthing 同期フォルダの変更検出 + LanceDB 差分インデキシング

    Polling ベースの変更検出（inotify は Linux 固有のため、
    クロスプラットフォーム対応で polling を採用）。

    状態ファイルにチェックサムを保持し、差分のみを処理する。
    """

    STATE_FILE = "sync_state.json"

    def __init__(
        self,
        watch_dirs: list[Path],
        extensions: tuple[str, ...] = (".md",),
        state_dir: Optional[Path] = None,
    ):
        self.watch_dirs = [d.resolve() for d in watch_dirs]
        self.extensions = extensions
        self.state_dir = state_dir or _PKS_DIR
        self._state: dict[str, str] = {}  # path -> checksum
        self._load_state()

    def _load_state(self) -> None:
        """前回の状態を読み込み"""
        state_path = self.state_dir / self.STATE_FILE
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                self._state = json.load(f)

    def _save_state(self) -> None:
        """現在の状態を保存"""
        state_path = self.state_dir / self.STATE_FILE
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _file_checksum(path: Path) -> str:
        """ファイルの MD5 チェックサム"""
        try:
            content = path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except (OSError, IOError):
            return ""

    def detect_changes(self) -> list[FileChange]:
        """変更のあったファイルを検出"""
        changes = []
        current_files: dict[str, str] = {}

        # 現在のファイルをスキャン
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                continue

            for ext in self.extensions:
                for path in watch_dir.rglob(f"*{ext}"):
                    str_path = str(path)
                    checksum = self._file_checksum(path)
                    current_files[str_path] = checksum

                    if str_path not in self._state:
                        changes.append(
                            FileChange(
                                path=path,
                                change_type="added",
                                checksum=checksum,
                            )
                        )
                    elif self._state[str_path] != checksum:
                        changes.append(
                            FileChange(
                                path=path,
                                change_type="modified",
                                checksum=checksum,
                            )
                        )

        # 削除されたファイルを検出
        for str_path in self._state:
            if str_path not in current_files:
                changes.append(
                    FileChange(
                        path=Path(str_path),
                        change_type="deleted",
                    )
                )

        return changes

    def apply_changes(self, changes: list[FileChange]) -> None:
        """変更を状態に反映"""
        for change in changes:
            str_path = str(change.path)
            if change.change_type == "deleted":
                self._state.pop(str_path, None)
            else:
                self._state[str_path] = change.checksum

        self._save_state()

    def ingest_changes(self, changes: list[FileChange]) -> int:
        """変更ファイルを LanceDB にインデキシング

        Note:
            現段階ではリンクインデックスの更新のみ。
            LanceDB へのベクトルインデキシングは将来の Anamnesis 拡張で実装。
        """
        ingested = 0

        for change in changes:
            if change.change_type == "deleted":
                continue

            if change.path.suffix in self.extensions:
                print(f"  [{change.change_type}] {change.path.name}")
                ingested += 1

        return ingested

    def run_once(self) -> list[FileChange]:
        """一回の検出 + 状態更新サイクル"""
        changes = self.detect_changes()

        if changes:
            print(f"[SyncWatcher] {len(changes)} changes detected:")
            ingested = self.ingest_changes(changes)
            self.apply_changes(changes)
            print(f"[SyncWatcher] {ingested} files processed")
        else:
            print("[SyncWatcher] No changes detected")

        return changes

    def run_polling(self, interval_seconds: int = 60, max_cycles: int = 0) -> None:
        """Polling ループ（デーモンモード）

        Args:
            interval_seconds: ポーリング間隔（秒）
            max_cycles: 最大サイクル数（0 = 無限）
        """
        cycle = 0
        print(f"[SyncWatcher] Polling started (interval: {interval_seconds}s)")
        print(f"[SyncWatcher] Watching: {[str(d) for d in self.watch_dirs]}")

        try:
            while max_cycles == 0 or cycle < max_cycles:
                self.run_once()
                cycle += 1
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[SyncWatcher] Stopped by user")
