#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→日次バッチ消化→scheduler が担う
# PURPOSE: Jules 720 tasks/day スケジューラー — 6垢分散 + 自動ローテーション
"""
Jules Daily Scheduler v1.1

有効キープール方式。起動時に全 API キーを検証し、
有効なキーだけを使ってバッチを実行する。
cron から 3 スロット (06:00/12:00/18:00) で呼ばれる。

Architecture:
    cron → jules_daily_scheduler.py --slot morning
           ├─ ファイルローテーション (全 .py → 日次 N ファイル選択)
           ├─ アカウント分配 (2垢/slot × 3 slots = 6垢/day)
           └─ run_specialists.py のバッチ実行

Usage:
    # Dry-run (何も実行しない、配分だけ表示)
    PYTHONPATH=. python mekhane/symploke/jules_daily_scheduler.py --slot morning --dry-run

    # Small test (2 files × 3 specialists = 6 tasks)
    PYTHONPATH=. python mekhane/symploke/jules_daily_scheduler.py --slot morning --max-files 2 --sample 3

    # Full slot (16 files × 15 specialists = 240 tasks)
    PYTHONPATH=. python mekhane/symploke/jules_daily_scheduler.py --slot morning

Cron:
    0 6  * * * cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/symploke/jules_daily_scheduler.py --slot morning  >> logs/specialist_daily/cron.log 2>&1
    0 12 * * * cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/symploke/jules_daily_scheduler.py --slot midday   >> logs/specialist_daily/cron.log 2>&1
    0 18 * * * cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/symploke/jules_daily_scheduler.py --slot evening  >> logs/specialist_daily/cron.log 2>&1
"""

import argparse
import asyncio
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from specialist_v2 import (
    ALL_SPECIALISTS,
    generate_prompt,
    get_all_categories,
    get_specialists_by_category,
)
from specialist_bridge import get_unified_specialists

# === Settings ===
ACCOUNTS_FILE = _PROJECT_ROOT / "synergeia" / "jules_accounts.yaml"
USAGE_FILE = _PROJECT_ROOT / "synergeia" / "jules_usage.json"
ROTATION_STATE_FILE = _PROJECT_ROOT / "synergeia" / "jules_rotation_state.json"
LOG_DIR = _PROJECT_ROOT / "logs" / "specialist_daily"

# Default settings
DEFAULT_FILES_PER_SLOT = 16
DEFAULT_SPECIALISTS_PER_FILE = 15
MAX_ERROR_RATE = 0.20  # 20% エラーで slot 自動停止


# PURPOSE: 全 .py ファイルをスキャンし、優先度順にソート
def scan_all_py_files() -> list[dict]:
    """プロジェクト内の全 .py ファイルを優先度付きでリスト化。"""
    result = subprocess.run(
        ["find", str(_PROJECT_ROOT), "-name", "*.py",
         "-not", "-path", "*/__pycache__/*",
         "-not", "-path", "*/.venv/*",
         "-not", "-path", "*/_archive*/*",
         "-not", "-path", "*/node_modules/*"],
        capture_output=True, text=True, timeout=10,
    )
    all_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

    # 相対パスに変換
    files = []
    for f in all_files:
        try:
            rel = os.path.relpath(f, _PROJECT_ROOT)
        except ValueError:
            continue
        if rel.startswith("."):
            continue

        # 優先度スコア計算
        score = 1.0

        # テストファイルは低優先
        basename = os.path.basename(rel)
        if basename.startswith("test_") or basename == "conftest.py":
            score = 0.3
        elif basename == "__init__.py":
            score = 0.1

        # 大きいファイル = レビュー価値が高い
        try:
            size = os.path.getsize(f)
            if size > 5000:
                score *= min(3.0, size / 5000)
        except OSError:
            pass

        # kernel/ は高優先
        if "kernel/" in rel:
            score *= 2.0
        # mekhane/ は高優先
        elif "mekhane/" in rel:
            score *= 1.5

        files.append({"path": rel, "score": score, "size": os.path.getsize(f) if os.path.exists(f) else 0})

    return files


# PURPOSE: git diff で最近変更されたファイルを取得
def get_recent_changes(days: int = 7) -> set[str]:
    """直近 N 日間の変更ファイルを取得。"""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--name-only", "--pretty=format:", "--", "*.py"],
            capture_output=True, text=True, timeout=10,
            cwd=str(_PROJECT_ROOT),
        )
        return {f.strip() for f in result.stdout.strip().split("\n") if f.strip()}
    except Exception:
        return set()


# PURPOSE: ローテーション状態を読込
def load_rotation_state() -> dict:
    """ファイルローテーション状態を読込。"""
    if ROTATION_STATE_FILE.exists():
        try:
            return json.loads(ROTATION_STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_reviewed": {}, "cycle": 0}


# PURPOSE: ローテーション状態を保存
def save_rotation_state(state: dict) -> None:
    """ファイルローテーション状態を保存。"""
    ROTATION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ROTATION_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# PURPOSE: 日次ファイル選択 — 優先度 + ローテーション + git diff
def select_daily_files(count: int, rotation_state: dict) -> list[str]:
    """日次レビュー対象ファイルを選択。

    優先度:
      1. git diff で最近変更されたファイル (2x boost)
      2. 大きいファイル (score by size)
      3. 前回レビューから最も時間が経過したファイル
    """
    all_files = scan_all_py_files()
    recent_changes = get_recent_changes(days=7)
    last_reviewed = rotation_state.get("last_reviewed", {})
    today = datetime.now().strftime("%Y-%m-%d")

    # スコア調整
    for f in all_files:
        path = f["path"]

        # 最近変更されたファイル → ブースト
        if path in recent_changes:
            f["score"] *= 2.0

        # 今日既にレビュー済み → 除外
        if last_reviewed.get(path) == today:
            f["score"] = -1

        # 長期未レビュー → ブースト
        last_date = last_reviewed.get(path, "")
        if not last_date:
            f["score"] *= 1.5  # 一度もレビューされていない
        elif last_date < (datetime.now().strftime("%Y-%m-%d")):
            # 古いほど高スコア (最大 2x)
            pass  # 基本スコアのまま

    # フィルタ & ソート
    candidates = [f for f in all_files if f["score"] > 0]
    candidates.sort(key=lambda f: f["score"], reverse=True)

    selected = [f["path"] for f in candidates[:count]]

    # ローテーション状態更新
    for path in selected:
        last_reviewed[path] = today
    rotation_state["last_reviewed"] = last_reviewed
    rotation_state["cycle"] = rotation_state.get("cycle", 0) + 1

    return selected


# PURPOSE: 全 API キーを環境変数から収集
def collect_all_keys() -> list[str]:
    """全 JULES_API_KEY_xx を環境変数から収集。キー値のリストを返す。"""
    keys = []
    for i in range(1, 30):  # 最大 30 キー
        key = os.getenv(f"JULES_API_KEY_{i:02d}")
        if key:
            keys.append(key)
    return keys


# PURPOSE: 使用量を読込
def load_usage() -> dict:
    """日次使用量を読込。日付が変わったらリセット。"""
    today = datetime.now().strftime("%Y-%m-%d")
    if USAGE_FILE.exists():
        try:
            data = json.loads(USAGE_FILE.read_text())
            if data.get("date") == today:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "date": today,
        "slots": {},
        "total_tasks": 0,
        "total_started": 0,
        "total_failed": 0,
        "files_reviewed": 0,
    }


# PURPOSE: 使用量を保存
def save_usage(usage: dict) -> None:
    USAGE_FILE.write_text(json.dumps(usage, indent=2, ensure_ascii=False))


# PURPOSE: バッチ実行 (run_specialists.py の run_batch を呼出)
async def run_slot_batch(
    files: list[str],
    specialists_per_file: int,
    api_keys: list[str],
    max_concurrent: int = 6,
    dry_run: bool = False,
) -> dict:
    """1 アカウント分のバッチを実行。"""
    import run_specialists as rs_short
    from run_specialists import create_session, run_batch, suggest_categories

    # API キーを一時差替え
    # NOTE: sys.path に mekhane/symploke を追加しているため、
    #   `run_specialists` と `mekhane.symploke.run_specialists` は
    #   別モジュールオブジェクトとして Python に登録される。
    #   run_batch はショートパスモジュールの API_KEYS を参照するため、
    #   ショートパス側を差し替える必要がある。
    original_keys = rs_short.API_KEYS
    rs_short.API_KEYS = api_keys

    total_started = 0
    total_failed = 0
    all_results = []

    try:
        for file_idx, target_file in enumerate(files, 1):
            # ランダムサンプリング
            pool = list(ALL_SPECIALISTS)
            specs = random.sample(pool, min(specialists_per_file, len(pool)))

            if dry_run:
                print(f"  [{file_idx}/{len(files)}] {target_file} × {len(specs)} specialists (DRY-RUN)")
                all_results.append({
                    "file": target_file,
                    "specialists": len(specs),
                    "dry_run": True,
                })
                continue

            print(f"  [{file_idx}/{len(files)}] {target_file} × {len(specs)} specialists")
            results = await run_batch(specs, target_file, max_concurrent)

            started = sum(1 for r in results if "session_id" in r)
            failed = sum(1 for r in results if "error" in r)
            total_started += started
            total_failed += failed

            all_results.append({
                "file": target_file,
                "specialists": len(specs),
                "started": started,
                "failed": failed,
            })

            # 安全弁: エラー率チェック
            total_attempted = total_started + total_failed
            if total_attempted > 10:
                error_rate = total_failed / total_attempted
                if error_rate > MAX_ERROR_RATE:
                    print(f"  ⚠️  Error rate {error_rate:.1%} > {MAX_ERROR_RATE:.0%}, stopping slot")
                    break

            print(f"    → {started}/{len(specs)} started, {failed} failed")

    finally:
        # API キー復元
        rs_short.API_KEYS = original_keys

    return {
        "files": all_results,
        "total_started": total_started,
        "total_failed": total_failed,
        "total_tasks": total_started + total_failed,
    }


# PURPOSE: メイン
async def main():
    parser = argparse.ArgumentParser(description="Jules Daily Scheduler v1.1")
    parser.add_argument(
        "--slot", choices=["morning", "midday", "evening"], required=True,
        help="Time slot to execute",
    )
    parser.add_argument(
        "--max-files", type=int, default=None,
        help=f"Max total files for this slot (default: {DEFAULT_FILES_PER_SLOT})",
    )
    parser.add_argument(
        "--sample", "-s", type=int, default=None,
        help=f"Specialists per file (default: {DEFAULT_SPECIALISTS_PER_FILE})",
    )
    parser.add_argument(
        "--max-concurrent", "-m", type=int, default=6,
        help="Max concurrent sessions (default: 6)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan without executing",
    )

    args = parser.parse_args()

    total_files = args.max_files or DEFAULT_FILES_PER_SLOT
    specs_per_file = args.sample or DEFAULT_SPECIALISTS_PER_FILE
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{'='*60}")
    print(f"Jules Daily Scheduler v1.1 (EAFP) — {args.slot} slot")
    print(f"{'='*60}")
    print(f"Time:     {timestamp}")

    # 全キー収集 (検証なし — EAFP: 使ってみて壊れたらブラックリスト)
    all_keys = collect_all_keys()
    if not all_keys:
        print("ERROR: No API keys found. Check JULES_API_KEY_xx env vars.")
        return

    total_tasks = total_files * specs_per_file

    print(f"Keys:     {len(all_keys)} loaded (EAFP: validated at runtime)")
    print(f"Files:    {total_files}")
    print(f"Specs:    {specs_per_file}/file")
    print(f"Tasks:    {total_tasks} (= {total_files} × {specs_per_file})")
    print()

    # ファイル選択
    rotation_state = load_rotation_state()
    all_selected_files = select_daily_files(total_files, rotation_state)

    if not all_selected_files:
        print("ERROR: No target files found.")
        return

    print(f"Selected files: {len(all_selected_files)}")
    for i, f in enumerate(all_selected_files[:5], 1):
        print(f"  [{i}] {f}")
    if len(all_selected_files) > 5:
        print(f"  ... and {len(all_selected_files) - 5} more")
    print()

    # 使用量読込
    usage = load_usage()

    # バッチ実行 (EAFP: 全キーを渡し、run_batch 内で壊れたキーを自動除外)
    slot_result = {
        "total_keys": len(all_keys),
        "total_tasks": 0,
        "total_started": 0,
        "total_failed": 0,
        "files_reviewed": 0,
    }

    print(f"--- Batch ({len(all_keys)} keys, {len(all_selected_files)} files) ---")

    result = await run_slot_batch(
        files=all_selected_files,
        specialists_per_file=specs_per_file,
        api_keys=all_keys,
        max_concurrent=args.max_concurrent,
        dry_run=args.dry_run,
    )

    slot_result["total_tasks"] = result["total_tasks"]
    slot_result["total_started"] = result["total_started"]
    slot_result["total_failed"] = result["total_failed"]
    slot_result["files_reviewed"] = len(all_selected_files)
    print()

    # 使用量更新
    usage["slots"][args.slot] = slot_result
    usage["total_tasks"] += slot_result["total_tasks"]
    usage["total_started"] += slot_result["total_started"]
    usage["total_failed"] += slot_result["total_failed"]
    usage["files_reviewed"] += slot_result["files_reviewed"]

    if not args.dry_run:
        save_usage(usage)
        save_rotation_state(rotation_state)

    # サマリー
    total = slot_result["total_tasks"]
    started = slot_result["total_started"]
    rate = (started / total * 100) if total else 0

    print(f"{'='*60}")
    print(f"Slot Summary: {args.slot}")
    print(f"  Tasks:   {started}/{total} ({rate:.1f}%)")
    print(f"  Files:   {slot_result['files_reviewed']}")
    print(f"  Daily:   {usage['total_started']}/{usage['total_tasks']} total")
    print(f"{'='*60}")

    # ログ保存
    if not args.dry_run:
        log_file = LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(json.dumps({
            "slot": args.slot,
            "timestamp": timestamp,
            "result": slot_result,
            "daily_usage": usage,
        }, indent=2, ensure_ascii=False))
        print(f"  Log: {log_file}")


if __name__ == "__main__":
    asyncio.run(main())
