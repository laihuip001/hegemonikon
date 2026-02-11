#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→実行スクリプトが必要→run_remaining が担う
"""残りの専門家26人を実行"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from pathlib import Path

REPO_SOURCE = "sources/github/laihuip001/hegemonikon"
BRANCH = "master"

# 残りの専門家
SPECIALISTS = [
    ("CL-004", "チャンク化効率評価者", "関連処理のグループ化の効率性を評価"),
    ("CL-005", "事前知識査定者", "コード理解に必要な事前知識を列挙"),
    ("CL-006", "一時変数負荷評価者", "一時変数の認知負荷を評価"),
    ("CL-007", "ネスト深度評価者", "ネスト深度と論理的複雑性のバランスを評価"),
    (
        "AI-004",
        "Logic ハルシネーション検出者",
        "構文的に正しいが意味的欠陥のあるロジックを確認",
    ),
    ("AI-005", "不完全コード検出者", "未完成ブロックを確認"),
    ("AI-006", "DRY違反検出者", "重複コードを確認"),
    ("AS-002", "Orphaned Task 検出者", "awaitされていないcreate_task呼び出しを確認"),
    ("AS-003", "キャンセレーション処理評価者", "CancelledErrorハンドリングを評価"),
]


# PURPOSE: session を生成する
async def create_session(key, specialist_id, specialist_name, focus, file_path):
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    prompt = f"""# 専門家レビュー: {specialist_name}
## タスク
`{file_path}` を分析し、結果を `mekhane/symploke/reviews/{specialist_id.lower()}_review.md` に書き込んでください。
## 分析観点
{focus}
**必ずファイルを作成してコミットしてください。**
"""
    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": REPO_SOURCE,
            "githubRepoContext": {"startingBranch": BRANCH},
        },
        "automationMode": "AUTO_CREATE_PR",
        "requirePlanApproval": False,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://jules.googleapis.com/v1alpha/sessions",
            headers=headers,
            json=payload,
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "id": specialist_id,
                    "name": specialist_name,
                    "session_id": data.get("id"),
                    "status": "started",
                }
            return {"id": specialist_id, "name": specialist_name, "error": resp.status}


# PURPOSE: main の処理
async def main():
    keys = [os.environ.get(f"JULIUS_API_KEY_{i}") for i in [7, 8, 9]]
    print("=== 残りの専門家実行 ===")
    results = []
    for i, (spec_id, name, focus) in enumerate(SPECIALISTS):
        key = keys[i % len(keys)]
        print(f"[{i+1}/{len(SPECIALISTS)}] {spec_id}...")
        result = await create_session(
            key, spec_id, name, focus, "mekhane/symploke/jules_client.py"
        )
        results.append(result)
        if "session_id" in result:
            print(f"  Started")
        else:
            print(f'  Error: {result.get("error")}')
        await asyncio.sleep(0.3)
    Path(
        "/home/makaron8426/oikos/hegemonikon/mekhane/symploke/specialist_run_results_v3.json"
    ).write_text(
        json.dumps(
            {"timestamp": datetime.now().isoformat(), "results": results},
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f'Done: {sum(1 for r in results if "session_id" in r)}/{len(SPECIALISTS)}')


if __name__ == "__main__":
    asyncio.run(main())
