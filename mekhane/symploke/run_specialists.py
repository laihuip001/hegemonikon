#!/usr/bin/env python3
"""
Jules 専門家バッチ実行スクリプト v2.0

tekhne-maker v5.0 アーキタイプ駆動設計を統合。
GitHub Actions 定時実行対応。
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
    from specialist_prompts import ALL_SPECIALISTS, generate_prompt, SpecialistDefinition
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from specialist_prompts import ALL_SPECIALISTS, generate_prompt, SpecialistDefinition


# === 設定 ===
REPO_SOURCE = os.getenv("JULES_REPO_SOURCE", "sources/github/laihuip001/hegemonikon")
BRANCH = os.getenv("JULES_BRANCH", "master")
TASKS_PER_KEY = int(os.getenv("JULES_TASKS_PER_KEY", "80"))

# API キー（環境変数から取得）
API_KEYS = [
    os.getenv(f"JULIUS_API_KEY_{i}")
    for i in range(1, 19)
    if os.getenv(f"JULIUS_API_KEY_{i}")
]


async def create_session(
    key: str,
    spec: SpecialistDefinition,
    target_file: str,
) -> dict:
    """Jules セッションを作成"""
    headers = {
        "X-Goog-Api-Key": key,
        "Content-Type": "application/json"
    }
    
    prompt = generate_prompt(spec, target_file)
    
    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": REPO_SOURCE,
            "githubRepoContext": {"startingBranch": BRANCH}
        },
        "automationMode": "AUTO_CREATE_PR",
        "requirePlanApproval": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://jules.googleapis.com/v1alpha/sessions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "id": spec.id,
                        "name": spec.name,
                        "archetype": spec.archetype.value,
                        "session_id": data.get("id"),
                        "url": data.get("url"),
                        "status": "started"
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "id": spec.id,
                        "name": spec.name,
                        "error": resp.status,
                        "error_text": error_text[:200]
                    }
    except Exception as e:
        return {
            "id": spec.id,
            "name": spec.name,
            "error": str(e)
        }


async def run_batch(
    specialists: list[SpecialistDefinition],
    target_file: str,
    max_concurrent: int = 3,
) -> list[dict]:
    """専門家バッチ実行"""
    if not API_KEYS:
        print("ERROR: No API keys found in environment")
        return []
    
    results = []
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_create(i: int, spec: SpecialistDefinition):
        async with semaphore:
            key_idx = i % len(API_KEYS)
            key = API_KEYS[key_idx]
            print(f"[{i+1}/{len(specialists)}] {spec.id} {spec.name[:20]}...")
            result = await create_session(key, spec, target_file)
            if "session_id" in result:
                print(f"  ✓ Started")
            else:
                print(f"  ✗ Error: {result.get('error')}")
            return result
    
    tasks = [bounded_create(i, spec) for i, spec in enumerate(specialists)]
    results = await asyncio.gather(*tasks)
    return list(results)


async def check_session_status(session_id: str, key: str) -> dict:
    """セッション状態を確認"""
    headers = {"X-Goog-Api-Key": key}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://jules.googleapis.com/v1alpha/sessions/{session_id}",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {"error": resp.status}


async def main():
    """メイン実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jules Specialist Batch Runner")
    parser.add_argument(
        "--target", "-t",
        default="mekhane/symploke/jules_client.py",
        help="Target file to review"
    )
    parser.add_argument(
        "--category", "-c",
        choices=["all", "cognitive_load", "ai_risk", "async", "theory"],
        default="all",
        help="Specialist category to run"
    )
    parser.add_argument(
        "--max-concurrent", "-m",
        type=int,
        default=3,
        help="Max concurrent sessions"
    )
    parser.add_argument(
        "--output", "-o",
        default="docs/specialist_run_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without executing"
    )
    
    args = parser.parse_args()
    
    # 専門家フィルタリング
    if args.category == "all":
        specialists = ALL_SPECIALISTS
    else:
        specialists = [s for s in ALL_SPECIALISTS if s.category == args.category]
    
    print(f"=== Jules Specialist Batch Runner v2.0 ===")
    print(f"Target: {args.target}")
    print(f"Specialists: {len(specialists)}")
    print(f"API Keys: {len(API_KEYS)}")
    print()
    
    if args.dry_run:
        for spec in specialists:
            print(f"--- {spec.id} {spec.name} ---")
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
        "results": results
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


if __name__ == "__main__":
    asyncio.run(main())
