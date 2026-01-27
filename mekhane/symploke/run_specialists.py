#!/usr/bin/env python3
"""
866人専門家 バッチ実行スクリプト

1 API キー = 最大 80 タスク
1 アカウント (3キー) = 240 タスク
3 アカウント (9キー) = 720 タスク

残り 146 タスクは次回バッチ
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# プロジェクトルートを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from mekhane.symploke.jules_client import JulesClient

# APIキー設定
API_KEYS = [
    os.getenv("JULIUS_API_KEY_1"),
    os.getenv("JULIUS_API_KEY_2"),
    os.getenv("JULIUS_API_KEY_3"),
    os.getenv("JULIUS_API_KEY_4"),
    os.getenv("JULIUS_API_KEY_5"),
    os.getenv("JULIUS_API_KEY_6"),
    os.getenv("JULIUS_API_KEY_7"),
    os.getenv("JULIUS_API_KEY_8"),
    os.getenv("JULIUS_API_KEY_9"),
]

# リポジトリソース形式: sources/github/{owner}/{repo}
REPO_SOURCE = "sources/github/laihuip001/hegemonikon"
BRANCH = "master"
TASKS_PER_KEY = 80


@dataclass
class Specialist:
    """専門家定義"""
    id: str
    name: str
    layer: str
    prompt_template: str


# Phase 1: 見落とし層（76人）
PHASE_1_SPECIALISTS = [
    # 認知負荷層（15人）
    Specialist("CL-001", "変数スコープ認知負荷評価者", "認知負荷", 
        "以下のコードの変数スコープを分析し、認知負荷の観点から問題点を指摘してください:\n{code}"),
    Specialist("CL-002", "抽象度層状評価者", "認知負荷",
        "以下のコードの抽象度の階層構造を分析し、レイヤー間の概念的ギャップを評価してください:\n{code}"),
    Specialist("CL-003", "メンタルモデル穴検出者", "認知負荷",
        "以下のコードで暗黙的に仮定されている前提条件を洗い出してください:\n{code}"),
    Specialist("CL-004", "チャンク化効率評価者", "認知負荷",
        "以下のコードのチャンク化（関連処理のグループ化）の効率性を評価してください:\n{code}"),
    Specialist("CL-005", "事前知識査定者", "認知負荷",
        "以下のコードを理解するために必要な事前知識を列挙してください:\n{code}"),
    Specialist("CL-006", "一時変数負荷評価者", "認知負荷",
        "以下のコードの一時変数（i, temp等）の使用が認知負荷に与える影響を評価してください:\n{code}"),
    Specialist("CL-007", "ネスト深度評価者", "認知負荷",
        "以下のコードのネスト深度と論理的複雑性のバランスを評価してください:\n{code}"),
    Specialist("CL-008", "コード密度測定者", "認知負荷",
        "以下のコードの論理密度（行あたりの意思決定点）を測定してください:\n{code}"),
    Specialist("CL-009", "パターン認識評価者", "認知負荷",
        "以下のコードで認識可能なパターンとその視認性を評価してください:\n{code}"),
    Specialist("CL-010", "ドメイン概念評価者", "認知負荷",
        "以下のコードのドメイン固有概念（造語、メタファー）の統一性を評価してください:\n{code}"),
    Specialist("CL-011", "契約明示度評価者", "認知負荷",
        "以下のコードの事前条件・事後条件の明示度を評価してください:\n{code}"),
    Specialist("CL-012", "リソース管理評価者", "認知負荷",
        "以下のコードのリソース管理（メモリ、接続等）の心的負荷を評価してください:\n{code}"),
    Specialist("CL-013", "エラー経路評価者", "認知負荷",
        "以下のコードのエラーハンドリング経路の複雑さを評価してください:\n{code}"),
    Specialist("CL-014", "非局所影響評価者", "認知負荷",
        "以下のコードのグローバル状態や副作用の追跡可能性を評価してください:\n{code}"),
    Specialist("CL-015", "順序依存評価者", "認知負荷",
        "以下のコードの関数呼び出し順序への依存性を評価してください:\n{code}"),

    # AI固有リスク層（22人）- 抜粋
    Specialist("AI-001", "命名ハルシネーション検出者", "AI固有",
        "以下のコードで実在しないライブラリや関数への参照がないか確認してください:\n{code}"),
    Specialist("AI-002", "Mapping ハルシネーション検出者", "AI固有",
        "以下のコードで存在しないAPIメソッド呼び出しがないか確認してください:\n{code}"),
    Specialist("AI-003", "Resource ハルシネーション検出者", "AI固有",
        "以下のコードで非実在のリソース（ファイルパス、環境変数）参照がないか確認してください:\n{code}"),
    Specialist("AI-004", "Logic ハルシネーション検出者", "AI固有",
        "以下のコードで構文的には正しいが意味的に欠陥のあるロジックがないか確認してください:\n{code}"),
    Specialist("AI-005", "不完全コード検出者", "AI固有",
        "以下のコードで未完成のブロック（try/except未完成、return欠落等）がないか確認してください:\n{code}"),
    Specialist("AI-006", "DRY違反検出者", "AI固有",
        "以下のコードで重複コード（同機能の3箇所以上）がないか確認してください:\n{code}"),
    Specialist("AI-007", "パターン一貫性検出者", "AI固有",
        "以下のコードで同じライブラリを異なる命名規則で使用していないか確認してください:\n{code}"),
    Specialist("AI-008", "自己矛盾検出者", "AI固有",
        "以下のコードで前後の前提条件が矛盾していないか確認してください:\n{code}"),
    Specialist("AI-009", "既知脆弱性パターン検出者", "AI固有",
        "以下のコードで既知のセキュリティ脆弱性パターン（CWE）がないか確認してください:\n{code}"),
    Specialist("AI-010", "入力検証欠落検出者", "AI固有",
        "以下のコードで入力バリデーションが省略されていないか確認してください:\n{code}"),

    # 非同期層（12人）- 抜粋
    Specialist("AS-001", "イベントループブロッキング検出者", "非同期",
        "以下のコードでイベントループをブロックする同期呼び出し（time.sleep等）がないか確認してください:\n{code}"),
    Specialist("AS-002", "Orphaned Task 検出者", "非同期",
        "以下のコードでawaitされていないcreate_task呼び出しがないか確認してください:\n{code}"),
    Specialist("AS-003", "キャンセレーション処理評価者", "非同期",
        "以下のコードのCancelledErrorハンドリングが適切か評価してください:\n{code}"),
    Specialist("AS-004", "非同期リソース管理評価者", "非同期",
        "以下のコードでasync withコンテキストマネージャの使用が適切か評価してください:\n{code}"),
    Specialist("AS-005", "gather制限評価者", "非同期",
        "以下のコードでgather()に適切なタスク数制限（Semaphore）があるか評価してください:\n{code}"),

    # 理論的整合性層（16人）- 抜粋
    Specialist("TH-001", "予測誤差バグ検出者", "理論",
        "以下のコードで実装と仕様の不一致（FEP観点での予測誤差）がないか確認してください:\n{code}"),
    Specialist("TH-002", "信念状態一貫性評価者", "理論",
        "以下のコードの暗黙的前提の統一性を評価してください:\n{code}"),
    Specialist("TH-003", "Markov blanket 検出者", "理論",
        "以下のコードの依存関係における条件付き独立性を分析してください:\n{code}"),
    Specialist("TH-004", "支配二分法評価者", "理論",
        "以下のコードで変更可能な側面とシステム制約が明確に区別されているか評価してください:\n{code}"),
    Specialist("TH-005", "因果構造透明性評価者", "理論",
        "以下のコードの実装における因果関係の明確さを評価してください:\n{code}"),
]


def generate_task_prompts(specialists: list[Specialist], target_file: str, code: str) -> list[dict]:
    """各専門家のタスクプロンプトを生成"""
    tasks = []
    for spec in specialists:
        prompt = f"""# 専門家レビュー: {spec.name}

## レイヤー: {spec.layer}

## 対象ファイル
{target_file}

## レビュー観点
{spec.prompt_template.format(code=code)}

## 出力形式
以下の形式で回答してください:

### 発見事項
- （問題があれば列挙、なければ「問題なし」）

### 重大度
- 高/中/低/なし

### 推奨事項
- （改善提案があれば記載）

### 沈黙判定
- 沈黙（問題なし）/ 発言（要改善）
"""
        tasks.append({
            "specialist_id": spec.id,
            "specialist_name": spec.name,
            "layer": spec.layer,
            "prompt": prompt,
        })
    return tasks


async def run_specialist_batch(
    api_key: str,
    tasks: list[dict],
    source: str,
    branch: str,
    key_index: int,
) -> list[dict]:
    """1つのAPIキーで複数タスクを実行"""
    client = JulesClient(api_key=api_key)
    results = []
    
    print(f"\n[Key {key_index}] Starting {len(tasks)} tasks...")
    
    for i, task in enumerate(tasks):
        try:
            session = await client.create_session(
                prompt=task["prompt"],
                source=source,
                branch=branch,
            )
            results.append({
                "specialist_id": task["specialist_id"],
                "specialist_name": task["specialist_name"],
                "layer": task["layer"],
                "session_id": session.get("sessionId"),
                "status": "started",
            })
            print(f"  [{key_index}] {i+1}/{len(tasks)}: {task['specialist_name']} - Started")
        except Exception as e:
            results.append({
                "specialist_id": task["specialist_id"],
                "specialist_name": task["specialist_name"],
                "layer": task["layer"],
                "session_id": None,
                "status": f"error: {e}",
            })
            print(f"  [{key_index}] {i+1}/{len(tasks)}: {task['specialist_name']} - Error: {e}")
        
        # レートリミット対策
        await asyncio.sleep(0.5)
    
    await client.close()
    return results


async def main():
    """メイン実行"""
    print("=" * 70)
    print("866人専門家 バッチ実行")
    print("=" * 70)
    
    # 環境変数読み込み
    from dotenv import load_dotenv
    load_dotenv("/home/laihuip001/oikos/hegemonikon/.env.jules")
    
    # 利用可能なキーを確認
    available_keys = [k for k in [os.getenv(f"JULIUS_API_KEY_{i}") for i in range(1, 10)] if k]
    print(f"\n利用可能なAPIキー: {len(available_keys)}個")
    
    if not available_keys:
        print("Error: No API keys found")
        return
    
    # 対象ファイル（例）
    target_file = "mekhane/symploke/jules_client.py"
    target_path = Path("/home/laihuip001/oikos/hegemonikon") / target_file
    
    if not target_path.exists():
        print(f"Error: Target file not found: {target_path}")
        return
    
    code = target_path.read_text()
    
    # タスク生成
    all_tasks = generate_task_prompts(PHASE_1_SPECIALISTS, target_file, code)
    print(f"\n生成されたタスク数: {len(all_tasks)}")
    
    # キーごとにタスクを分散
    tasks_per_key = len(all_tasks) // len(available_keys) + 1
    key_tasks = []
    for i, key in enumerate(available_keys):
        start = i * tasks_per_key
        end = min(start + tasks_per_key, len(all_tasks))
        key_tasks.append((key, all_tasks[start:end], i + 1))
    
    # 並列実行
    print("\n並列実行開始...")
    tasks = [
        run_specialist_batch(key, tasks, REPO_SOURCE, BRANCH, idx)
        for key, tasks, idx in key_tasks
        if tasks  # 空でないタスクのみ
    ]
    
    all_results = await asyncio.gather(*tasks)
    
    # 結果集計
    results = [r for batch in all_results for r in batch]
    
    started = sum(1 for r in results if r["status"] == "started")
    errors = sum(1 for r in results if r["status"].startswith("error"))
    
    print("\n" + "=" * 70)
    print("実行結果")
    print("=" * 70)
    print(f"合計タスク: {len(results)}")
    print(f"開始成功: {started}")
    print(f"エラー: {errors}")
    
    # 結果をファイルに保存
    result_file = Path("/home/laihuip001/oikos/hegemonikon/docs/specialist_results.json")
    import json
    with open(result_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(results),
            "started": started,
            "errors": errors,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果保存: {result_file}")


if __name__ == "__main__":
    asyncio.run(main())
