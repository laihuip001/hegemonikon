#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ 後方互換ラッパー（非推奨）
# lineage: 旧 check_proof.py → dendron/checker.py へ昇華 (2026-02-01)
"""
DEPRECATED: Use `python -m dendron.cli check mekhane/` instead.

このスクリプトは後方互換性のために維持されています。
新規利用は dendron CLI を推奨します。

History:
  - 2026-01-XX: 初版 (mekhane 固定スコープ)
  - 2026-02-01: 非推奨化、dendron CLI への委譲
"""

import subprocess
import sys
import warnings
from pathlib import Path


# PURPOSE: CLI エントリポイント — 運用ツールの直接実行
def main():
    # 非推奨警告
    warnings.warn(
        "check_proof.py is deprecated. Use 'python -m dendron.cli check mekhane/' instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # hegemonikon ルートを特定
    script_dir = Path(__file__).resolve().parent
    hegemonikon_root = script_dir.parent.parent  # mekhane/scripts/ → hegemonikon/

    # dendron CLI を呼び出し
    cmd = [
        sys.executable,
        "-m",
        "dendron.cli",
        "check",
        "mekhane/",
        "--format",
        "ci" if "--ci" in sys.argv else "text",
    ]

    # verbose/stats オプションの対応
    # dendron は --stats を持たないが、text 形式でレベル統計を出力する
    if "--stats" in sys.argv or "-s" in sys.argv:
        cmd[5] = "text"  # 統計は text 形式で表示

    result = subprocess.run(
        cmd,
        cwd=hegemonikon_root,
        env={**__import__("os").environ, "PYTHONPATH": str(hegemonikon_root)},
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
