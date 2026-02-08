#!/usr/bin/env python3
"""
Gnōsis Knowledge Index — 自動更新スクリプト

Usage:
  # 手動実行
  python scripts/gnosis_index_update.py

  # systemd timer で定期実行
  # → scripts/gnosis-index.timer を参照

  # 強制再インデックス
  python scripts/gnosis_index_update.py --force
"""

import sys
import time
from pathlib import Path

# Hegemonikon root
HEGEMONIKON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HEGEMONIKON_ROOT))


def main():
    import argparse
    import fcntl

    parser = argparse.ArgumentParser(description="Gnōsis Knowledge Index Update")
    parser.add_argument(
        "--force", action="store_true", help="Force reindex all files"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Minimal output"
    )
    args = parser.parse_args()

    # GPU 排他制御 — Chat 使用中に timer 発火しても OOM しない
    lock_path = Path("/tmp/gnosis_embedder.lock")
    try:
        lock_file = open(lock_path, "w")
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, OSError):
        if not args.quiet:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Skipped: embedder locked")
        return 0

    try:
        from mekhane.anamnesis.gnosis_chat import KnowledgeIndexer

        if not args.quiet:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Gnōsis Index Update", flush=True)

        t0 = time.time()
        added = KnowledgeIndexer.index_knowledge(force_reindex=args.force)
        elapsed = time.time() - t0

        if not args.quiet:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Done: {added} new chunks in {elapsed:.1f}s")
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
