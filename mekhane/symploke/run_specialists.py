#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→実行スクリプトが必要→run_specialists が担う
"""
Jules 専門家バッチ実行スクリプト v4.0

Specialist v2（純化された知性）統合版。
140人の専門家、21カテゴリ対応。

v4.0 拡張:
  - 動的ターゲット選択 (git-diff / priority / fixed)
  - 複数ファイル一括バッチ
  - 結果統合パイプライン対応
"""

import asyncio
import aiohttp
import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ローカルモジュールインポート
try:
    from specialist_v2 import (
        ALL_SPECIALISTS,
        Specialist,
        generate_prompt,
        get_all_categories,
        get_specialists_by_category,
    )
    from specialists_tier1 import (
        TIER1_SPECIALISTS,
        get_tier1_by_category,
        get_tier1_categories,
        derive_specialist,
        get_all_derivatives,
        Scope,
        Intent,
    )
    from specialist_bridge import get_unified_specialists
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from specialist_v2 import (
        ALL_SPECIALISTS,
        Specialist,
        generate_prompt,
        get_all_categories,
        get_specialists_by_category,
    )
    from specialists_tier1 import (
        TIER1_SPECIALISTS,
        get_tier1_by_category,
        get_tier1_categories,
        derive_specialist,
        get_all_derivatives,
        Scope,
        Intent,
    )
    from specialist_bridge import get_unified_specialists


# === 設定 ===
REPO_SOURCE = os.getenv("JULES_REPO_SOURCE", "sources/github/laihuip001/hegemonikon")
BRANCH = os.getenv("JULES_BRANCH", "master")
TASKS_PER_KEY = int(os.getenv("JULES_TASKS_PER_KEY", "80"))

# Rate limiting: burst 防止のためリクエスト間ディレイ (秒)
REQUEST_DELAY = float(os.getenv("JULES_REQUEST_DELAY", "1.5"))
# リトライ: FAILED_PRECONDITION (400) / RATE_LIMIT (429) 時の最大リトライ数
MAX_RETRIES = int(os.getenv("JULES_MAX_RETRIES", "3"))
# リトライ基底遅延 (秒) — 指数バックオフ: base * 2^retry
RETRY_BASE_DELAY = float(os.getenv("JULES_RETRY_BASE_DELAY", "3.0"))

# API キー（環境変数から取得）
# .env の命名規則: JULES_API_KEY_01, JULES_API_KEY_02, ..., JULES_API_KEY_17
API_KEYS = [
    os.getenv(f"JULES_API_KEY_{i:02d}")
    for i in range(1, 20)
    if os.getenv(f"JULES_API_KEY_{i:02d}")
]

# RETRYABLE エラーコード
_RETRYABLE_CODES = {400, 429, 500, 503}

# ファイル拡張子→カテゴリ マッピング (動的ターゲット選択用)
_FILE_CATEGORY_HINTS = {
    "test_": ["testing", "edge_case"],
    "mcp_": ["api_design", "async", "error_handling"],
    "specialist": ["hegemonikon", "naming", "aesthetics"],
    "kernel/": ["hegemonikon", "documentation"],
    "security": ["security"],
}


# PURPOSE: 動的ターゲット選択 — git diff / priority file / fixed
def select_targets(
    mode: str = "fixed",
    fixed_target: str = "",
    priority_file: str = "",
    max_files: int = 10,
) -> list[str]:
    """ターゲットファイルを選択する

    Modes:
      - fixed: 単一ファイル指定 (従来互換)
      - git-diff: git diff で変更ファイルを自動取得
      - priority: 優先度ファイルから読み込み
    """
    if mode == "fixed":
        return [fixed_target] if fixed_target else []

    elif mode == "git-diff":
        try:
            # 直近コミットの変更ファイル
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1..HEAD", "--", "*.py"],
                capture_output=True, text=True, timeout=10,
            )
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

            if not files:
                # HEAD~1 が存在しない場合、直近の変更ファイルを取得
                result = subprocess.run(
                    ["git", "diff", "--name-only", "--cached", "--", "*.py"],
                    capture_output=True, text=True, timeout=10,
                )
                files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

            # テスト/設定ファイルを除外し、実体ファイルを優先
            scored = []
            for f in files:
                score = 1
                if "test_" in f or "conftest" in f:
                    score = 0.3
                elif "__init__" in f:
                    score = 0.1
                elif f.endswith(".py"):
                    # 大きいファイル = レビュー価値が高い
                    try:
                        size = Path(f).stat().st_size
                        score = min(5.0, size / 1000)
                    except (FileNotFoundError, OSError):
                        score = 1.0
                scored.append((score, f))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [f for _, f in scored[:max_files]]

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"WARNING: git-diff failed: {e}, falling back to fixed")
            return [fixed_target] if fixed_target else []

    elif mode == "priority":
        if not priority_file or not Path(priority_file).exists():
            print(f"WARNING: priority file '{priority_file}' not found")
            return [fixed_target] if fixed_target else []

        with open(priority_file) as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return lines[:max_files]

    else:
        print(f"WARNING: unknown target mode '{mode}', using fixed")
        return [fixed_target] if fixed_target else []


# PURPOSE: ファイルパスからカテゴリヒントを推定
def suggest_categories(filepath: str) -> list[str]:
    """ファイルパスから関連カテゴリを推定する"""
    hints = []
    for pattern, cats in _FILE_CATEGORY_HINTS.items():
        if pattern in filepath:
            hints.extend(cats)
    # ヒントがなければ全カテゴリ
    return list(set(hints)) if hints else []


# PURPOSE: Jules セッションを作成 (リトライ付き)
async def create_session(
    key: str,
    spec: Specialist,
    target_file: str,
    retries: int = 0,
) -> dict:
    """Jules セッションを作成 (リトライ付き)"""
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}

    prompt = generate_prompt(spec, target_file)

    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": REPO_SOURCE,
            "githubRepoContext": {"startingBranch": BRANCH},
        },
        "automationMode": "AUTO_CREATE_PR",
        "requirePlanApproval": False,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://jules.googleapis.com/v1alpha/sessions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "id": spec.id,
                        "name": spec.name,
                        "category": spec.category,
                        "archetype": spec.archetype.value,
                        "session_id": data.get("id"),
                        "url": data.get("url"),
                        "status": "started",
                        "retries": retries,
                    }
                else:
                    error_text = await resp.text()
                    # リトライ判定
                    if resp.status in _RETRYABLE_CODES and retries < MAX_RETRIES:
                        delay = RETRY_BASE_DELAY * (2 ** retries)
                        print(f"  ↻ Retry {retries + 1}/{MAX_RETRIES} "
                              f"(HTTP {resp.status}, wait {delay:.0f}s)")
                        await asyncio.sleep(delay)
                        return await create_session(
                            key, spec, target_file, retries=retries + 1
                        )
                    return {
                        "id": spec.id,
                        "name": spec.name,
                        "category": spec.category,
                        "error": resp.status,
                        "error_text": error_text[:200],
                        "retries": retries,
                    }
    except Exception as e:
        return {
            "id": spec.id,
            "name": spec.name,
            "category": spec.category,
            "error": str(e),
            "retries": retries,
        }


# PURPOSE: 専門家バッチ実行 (レート制限 + リトライ付き)
async def run_batch(
    specialists: list[Specialist],
    target_file: str,
    max_concurrent: int = 3,
) -> list[dict]:
    """専門家バッチ実行 (レート制限 + リトライ付き)

    対策:
      1. global semaphore で同時接続数を制限
      2. per-key semaphore でキーあたりの同時リクエストを制限
      3. リクエスト間に REQUEST_DELAY の間隔を挿入
      4. 400/429 エラー時に指数バックオフリトライ
    """
    if not API_KEYS:
        print("ERROR: No API keys found in environment")
        return []

    # キーあたりの同時リクエストを制限 (1キー2並列まで)
    max_per_key = max(1, max_concurrent // len(API_KEYS) + 1)
    key_semaphores = {i: asyncio.Semaphore(max_per_key) for i in range(len(API_KEYS))}
    global_semaphore = asyncio.Semaphore(max_concurrent)
    # 順番にリクエストを発行するための排他ロック
    dispatch_lock = asyncio.Lock()
    dispatch_count = [0]  # mutable counter

    # PURPOSE: bounded_create の処理
    async def bounded_create(i: int, spec: Specialist):
        key_idx = i % len(API_KEYS)
        key = API_KEYS[key_idx]

        # dispatch_lock で順番にリクエスト発行 (burst 防止)
        async with dispatch_lock:
            dispatch_count[0] += 1
            if dispatch_count[0] > 1:
                await asyncio.sleep(REQUEST_DELAY)

        async with global_semaphore:
            async with key_semaphores[key_idx]:
                print(f"[{i+1}/{len(specialists)}] {spec.id} {spec.name[:20]}...")
                result = await create_session(key, spec, target_file)
                if "session_id" in result:
                    retries = result.get("retries", 0)
                    retry_info = f" (retried {retries}x)" if retries else ""
                    print(f"  ✓ Started ({spec.category}){retry_info}")
                else:
                    print(f"  ✗ Error: {result.get('error')}")
                return result

    tasks = [bounded_create(i, spec) for i, spec in enumerate(specialists)]
    results = await asyncio.gather(*tasks)
    return list(results)


# PURPOSE: セッション状態を確認
async def check_session_status(session_id: str, key: str) -> dict:
    """セッション状態を確認"""
    headers = {"X-Goog-Api-Key": key}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://jules.googleapis.com/v1alpha/sessions/{session_id}",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {"error": resp.status}


# PURPOSE: メイン実行
async def main():
    """メイン実行"""
    import argparse

    # 利用可能なカテゴリを動的に取得
    available_categories = ["all"] + get_all_categories()

    parser = argparse.ArgumentParser(description="Jules Specialist Batch Runner v4.0")
    parser.add_argument(
        "--target",
        "-t",
        default="mekhane/symploke/jules_client.py",
        help="Target file to review (used with --target-mode fixed)",
    )
    parser.add_argument(
        "--target-mode",
        choices=["fixed", "git-diff", "priority"],
        default="fixed",
        help="Target selection mode: fixed (single file), git-diff (changed files), priority (from file)",
    )
    parser.add_argument(
        "--priority-file",
        default="",
        help="Priority file path (one file per line, used with --target-mode priority)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=10,
        help="Maximum number of target files (used with git-diff/priority)",
    )
    parser.add_argument(
        "--category",
        "-c",
        choices=available_categories,
        default="all",
        help="Specialist category to run",
    )
    parser.add_argument(
        "--max-concurrent", "-m", type=int, default=3, help="Max concurrent sessions"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="",
        help="Output file for results (auto-generated if empty)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print prompts without executing"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="List available categories"
    )
    parser.add_argument(
        "--list-targets", action="store_true", help="List target files (for git-diff/priority mode)"
    )
    parser.add_argument(
        "--sample", "-s", type=int, help="Random sample N specialists per file"
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2],
        help="Run only Tier 1 (evolutionary) or Tier 2 (hygiene) specialists",
    )
    parser.add_argument(
        "--derive",
        nargs="?",
        const="all",
        metavar="SPEC",
        help="Generate derivatives: 'all' for all 8 variants, or 'SCOPE.INTENT' (e.g. M.F for Macro+Fix)",
    )
    parser.add_argument(
        "--scope",
        choices=["micro", "meso", "macro"],
        help="Derivative scope filter (use with --derive)",
    )
    parser.add_argument(
        "--intent",
        choices=["detect", "fix", "prevent"],
        help="Derivative intent filter (use with --derive)",
    )
    parser.add_argument(
        "--all-phases",
        action="store_true",
        help="Use ALL specialists (v2 + Phase 0-3, ~1000 specialists)",
    )

    args = parser.parse_args()

    # カテゴリ一覧
    if args.list_categories:
        print("=== Available Categories ===")
        for cat in get_all_categories():
            count = len(get_specialists_by_category(cat))
            print(f"  {cat}: {count}人")
        print(f"\n  all: {len(ALL_SPECIALISTS)}人")
        return

    # ターゲットファイル選択
    targets = select_targets(
        mode=args.target_mode,
        fixed_target=args.target,
        priority_file=args.priority_file,
        max_files=args.max_files,
    )

    if args.list_targets:
        print("=== Target Files ===")
        for i, t in enumerate(targets, 1):
            hints = suggest_categories(t)
            hint_str = f" → {', '.join(hints)}" if hints else ""
            print(f"  [{i}] {t}{hint_str}")
        print(f"\n  Total: {len(targets)} files")
        return

    if not targets:
        print("ERROR: No target files found. Use --target or --target-mode git-diff")
        return

    # 全ファイル分の結果を蓄積
    all_results = []
    total_started = 0
    total_failed = 0

    for file_idx, target_file in enumerate(targets, 1):
        print(f"\n{'='*60}")
        print(f"[{file_idx}/{len(targets)}] Target: {target_file}")
        print(f"{'='*60}")

        # 専門家フィルタリング
        file_hints = suggest_categories(target_file)

        if args.tier == 1:
            if args.category == "all":
                specialists = list(TIER1_SPECIALISTS)
            else:
                specialists = get_tier1_by_category(args.category)
        elif args.tier == 2:
            tier1_ids = {s.id for s in TIER1_SPECIALISTS}
            if args.category == "all":
                specialists = [s for s in ALL_SPECIALISTS if s.id not in tier1_ids]
            else:
                specialists = [s for s in get_specialists_by_category(args.category) if s.id not in tier1_ids]
        else:
            # 基本プール選択
            base_pool = get_unified_specialists() if args.all_phases else list(ALL_SPECIALISTS)

            if args.category == "all":
                # git-diff モードではカテゴリヒントで絞り込み
                if args.target_mode == "git-diff" and file_hints:
                    specialists = []
                    cat_pool = {s.category: [] for s in base_pool}
                    for s in base_pool:
                        cat_pool.setdefault(s.category, []).append(s)
                    for hint_cat in file_hints:
                        if hint_cat in cat_pool:
                            specialists.extend(cat_pool[hint_cat])
                    # 重複除去 (id ベース)
                    seen = set()
                    unique = []
                    for s in specialists:
                        if s.id not in seen:
                            seen.add(s.id)
                            unique.append(s)
                    specialists = unique
                else:
                    specialists = base_pool
            else:
                specialists = [s for s in base_pool if s.category == args.category]

        # ランダムサンプリング
        if args.sample:
            import random
            specialists = random.sample(specialists, min(args.sample, len(specialists)))

        # 派生適用
        if args.derive:
            scope_map = {"micro": Scope.MICRO, "meso": Scope.MESO, "macro": Scope.MACRO}
            intent_map = {"detect": Intent.DETECT, "fix": Intent.FIX, "prevent": Intent.PREVENT}

            if args.derive == "all" and not args.scope and not args.intent:
                derived = []
                for base in specialists:
                    derived.extend(get_all_derivatives(base))
                specialists = derived
            else:
                scope = scope_map.get(args.scope) if args.scope else None
                intent = intent_map.get(args.intent) if args.intent else None
                specialists = [derive_specialist(s, scope=scope, intent=intent) for s in specialists]

        print(f"Specialists: {len(specialists)}")
        if file_hints:
            print(f"Category hints: {', '.join(file_hints)}")
        print(f"API Keys: {len(API_KEYS)}")
        print()

        if args.dry_run:
            for spec in specialists[:3]:  # dry-run ではサンプル3つ
                print(f"--- {spec.id} {spec.name} ({spec.category}) ---")
                print(generate_prompt(spec, target_file))
                print()
            if len(specialists) > 3:
                print(f"  ... and {len(specialists) - 3} more specialists")
            continue

        # バッチ実行
        results = await run_batch(specialists, target_file, args.max_concurrent)

        # ファイル単位のサマリー
        started = sum(1 for r in results if "session_id" in r)
        failed = sum(1 for r in results if "error" in r)
        total_started += started
        total_failed += failed

        print(f"\n  → Started: {started}/{len(specialists)}, Failed: {failed}")

        all_results.append({
            "target_file": target_file,
            "specialists_count": len(specialists),
            "started": started,
            "failed": failed,
            "results": results,
        })

    if args.dry_run:
        return

    # 結果保存
    output_path = Path(
        args.output if args.output
        else f"logs/specialist_daily/run_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "version": "4.0",
        "timestamp": datetime.now().isoformat(),
        "target_mode": args.target_mode,
        "total_files": len(targets),
        "total_specialists": sum(r["specialists_count"] for r in all_results),
        "total_started": total_started,
        "total_failed": total_failed,
        "api_keys_used": len(API_KEYS),
        "files": all_results,
    }

    output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))

    # グローバルサマリー
    total_specs = sum(r["specialists_count"] for r in all_results)
    print(f"\n{'='*60}")
    print(f"=== Global Summary ===")
    print(f"Files: {len(targets)}")
    print(f"Started: {total_started}/{total_specs}")
    print(f"Failed: {total_failed}/{total_specs}")
    success_rate = (total_started / total_specs * 100) if total_specs else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Results: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
