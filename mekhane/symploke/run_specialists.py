#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→実行スクリプトが必要→run_specialists が担う
"""
Jules 専門家バッチ実行スクリプト v3.0

Specialist v2（純化された知性）統合版。
140人の専門家、21カテゴリ対応。
"""

import asyncio
import aiohttp
import os
import json
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


# === 設定 ===
REPO_SOURCE = os.getenv("JULES_REPO_SOURCE", "sources/github/laihuip001/hegemonikon")
BRANCH = os.getenv("JULES_BRANCH", "master")
TASKS_PER_KEY = int(os.getenv("JULES_TASKS_PER_KEY", "80"))

# Rate limiting: burst 防止のためリクエスト間ディレイ (秒)
REQUEST_DELAY = float(os.getenv("JULES_REQUEST_DELAY", "1.0"))
# リトライ: FAILED_PRECONDITION (400) / RATE_LIMIT (429) 時の最大リトライ数
MAX_RETRIES = int(os.getenv("JULES_MAX_RETRIES", "3"))
# リトライ基底遅延 (秒) — 指数バックオフ: base * 2^retry
RETRY_BASE_DELAY = float(os.getenv("JULES_RETRY_BASE_DELAY", "2.0"))

# API キー（環境変数から取得）
API_KEYS = [
    os.getenv(f"JULIUS_API_KEY_{i}")
    for i in range(1, 19)
    if os.getenv(f"JULIUS_API_KEY_{i}")
]

# RETRYABLE エラーコード
_RETRYABLE_CODES = {400, 429, 500, 503}


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

    parser = argparse.ArgumentParser(description="Jules Specialist Batch Runner v3.0")
    parser.add_argument(
        "--target",
        "-t",
        default="mekhane/symploke/jules_client.py",
        help="Target file to review",
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
        default="docs/specialist_run_results.json",
        help="Output file for results",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print prompts without executing"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="List available categories"
    )
    parser.add_argument(
        "--sample", "-s", type=int, help="Random sample N specialists"
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

    args = parser.parse_args()

    # カテゴリ一覧
    if args.list_categories:
        print("=== Available Categories ===")
        for cat in get_all_categories():
            count = len(get_specialists_by_category(cat))
            print(f"  {cat}: {count}人")
        print(f"\n  all: {len(ALL_SPECIALISTS)}人")
        return

    # 専門家フィルタリング
    if args.tier == 1:
        # Tier 1: 進化専門家のみ
        if args.category == "all":
            specialists = list(TIER1_SPECIALISTS)
        else:
            specialists = get_tier1_by_category(args.category)
    elif args.tier == 2:
        # Tier 2: 衛生専門家のみ (Tier 1 を除外)
        tier1_ids = {s.id for s in TIER1_SPECIALISTS}
        if args.category == "all":
            specialists = [s for s in ALL_SPECIALISTS if s.id not in tier1_ids]
        else:
            specialists = [s for s in get_specialists_by_category(args.category) if s.id not in tier1_ids]
    else:
        # 全専門家
        if args.category == "all":
            specialists = list(ALL_SPECIALISTS)
        else:
            specialists = get_specialists_by_category(args.category)

    # ランダムサンプリング
    if args.sample:
        import random
        specialists = random.sample(specialists, min(args.sample, len(specialists)))

    # 派生適用
    if args.derive:
        scope_map = {"micro": Scope.MICRO, "meso": Scope.MESO, "macro": Scope.MACRO}
        intent_map = {"detect": Intent.DETECT, "fix": Intent.FIX, "prevent": Intent.PREVENT}
        
        if args.derive == "all" and not args.scope and not args.intent:
            # 全派生: 各基本専門家から8派生を生成
            derived = []
            for base in specialists:
                derived.extend(get_all_derivatives(base))
            specialists = derived
        else:
            # 特定派生: scope/intent を指定
            scope = scope_map.get(args.scope) if args.scope else None
            intent = intent_map.get(args.intent) if args.intent else None
            specialists = [derive_specialist(s, scope=scope, intent=intent) for s in specialists]

    print(f"=== Jules Specialist Batch Runner v3.0 ===")
    print(f"Target: {args.target}")
    print(f"Category: {args.category}")
    print(f"Specialists: {len(specialists)}")
    print(f"API Keys: {len(API_KEYS)}")
    print()

    if args.dry_run:
        for spec in specialists:
            print(f"--- {spec.id} {spec.name} ({spec.category}) ---")
            print(generate_prompt(spec, args.target))
            print()
        return

    # バッチ実行
    results = await run_batch(specialists, args.target, args.max_concurrent)

    # 結果保存
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "target_file": args.target,
        "category": args.category,
        "total_specialists": len(specialists),
        "api_keys_used": len(API_KEYS),
        "results": results,
    }

    output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))

    # サマリー
    started = sum(1 for r in results if "session_id" in r)
    failed = sum(1 for r in results if "error" in r)

    print()
    print(f"=== Summary ===")
    print(f"Started: {started}/{len(specialists)}")
    print(f"Failed: {failed}/{len(specialists)}")
    print(f"Results: {output_path}")

    # カテゴリ別サマリー
    categories_started = {}
    for r in results:
        cat = r.get("category", "unknown")
        if "session_id" in r:
            categories_started[cat] = categories_started.get(cat, 0) + 1
    
    if categories_started:
        print("\nBy Category:")
        for cat, count in sorted(categories_started.items()):
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
