#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→レビュー結果からIssue生成が必要→create_issues が担う
"""
Jules Specialist レビュー結果 → GitHub Issue 自動作成 v1.0

完了したセッションの結果を取得し、重要な発見を GitHub Issue として起票する。

Usage:
  python create_issues.py --results /tmp/jules_test_*.json
  python create_issues.py --dir logs/specialist_daily --days 1
  python create_issues.py --results result.json --dry-run  # Issue 作成せず内容を表示

Requires:
  - gh CLI (GitHub CLI) がインストール・認証済み
  - JULES_API_KEY_01 環境変数（セッション結果取得用）
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)


# === 定数 ===
JULES_API_BASE = "https://jules.googleapis.com/v1alpha/sessions"
MAX_ISSUES_PER_RUN = 3  # 1回の実行で作る Issue の上限
REPO = os.getenv("JULES_REPO_SOURCE", "laihuip001/hegemonikon")


# PURPOSE: API キーを1つ取得
def get_api_key() -> str:
    """セッション確認用の API キーを取得"""
    for i in range(1, 20):
        key = os.getenv(f"JULES_API_KEY_{i:02d}")
        if key:
            return key
    raise RuntimeError("No API key found (JULES_API_KEY_01~19)")


# PURPOSE: セッション状態を取得
async def get_session(session_id: str, api_key: str) -> dict:
    """Jules セッションの状態と結果を取得"""
    headers = {"X-Goog-Api-Key": api_key}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{JULES_API_BASE}/{session_id}",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {"error": resp.status, "session_id": session_id}


# PURPOSE: 複数セッションをバッチ取得
async def fetch_sessions(session_ids: list[str], api_key: str) -> list[dict]:
    """複数セッションを並列で取得（rate limit 考慮）"""
    results = []
    for sid in session_ids:
        result = await get_session(sid, api_key)
        results.append(result)
        await asyncio.sleep(0.5)  # rate limit 対策
    return results


# PURPOSE: 結果ファイルからセッション情報を抽出
def extract_sessions(result_file: Path) -> list[dict]:
    """結果 JSON からセッション情報を抽出"""
    data = json.loads(result_file.read_text())
    sessions = []

    if "files" in data:
        for file_entry in data["files"]:
            target = file_entry.get("target_file", "unknown")
            for result in file_entry.get("results", []):
                if "session_id" in result:
                    sessions.append({
                        "session_id": result["session_id"],
                        "specialist_id": result.get("id", ""),
                        "specialist_name": result.get("name", ""),
                        "category": result.get("category", ""),
                        "archetype": result.get("archetype", ""),
                        "target_file": target,
                        "url": result.get("url", ""),
                    })
    elif "results" in data:
        target = data.get("target_file", "unknown")
        for result in data.get("results", []):
            if "session_id" in result:
                sessions.append({
                    "session_id": result["session_id"],
                    "specialist_id": result.get("id", ""),
                    "specialist_name": result.get("name", ""),
                    "category": result.get("category", ""),
                    "target_file": target,
                    "url": result.get("url", ""),
                })

    return sessions


# PURPOSE: セッション結果から Issue 本文を生成
def format_issue(session_info: dict, session_data: dict) -> dict | None:
    """セッション結果を GitHub Issue の title/body に変換

    Returns:
        {"title": ..., "body": ..., "labels": [...]} or None (Issue 不要)
    """
    state = session_data.get("state", "UNKNOWN")

    # 完了していないセッションはスキップ
    if state not in ("COMPLETED", "COMPLETED_WITH_CHANGES"):
        return None

    # PR/変更情報があるか
    changes = session_data.get("codeChanges", [])
    pr_url = session_data.get("pullRequestUrl", "")
    summary = session_data.get("summary", "")

    if not summary and not changes and not pr_url:
        return None

    specialist = session_info.get("specialist_name", "Unknown")
    specialist_id = session_info.get("specialist_id", "")
    target = session_info.get("target_file", "unknown")
    category = session_info.get("category", "specialist-review")
    session_url = session_info.get("url", "")

    title = f"[Jules/{specialist_id}] {specialist}: {target}"

    body_lines = [
        f"## 🔍 Specialist Review Result",
        f"",
        f"| Item | Value |",
        f"|:-----|:------|",
        f"| **Specialist** | {specialist} (`{specialist_id}`) |",
        f"| **Category** | `{category}` |",
        f"| **Target** | `{target}` |",
        f"| **Session** | [{session_info.get('session_id', '')}]({session_url}) |",
    ]

    if pr_url:
        body_lines.append(f"| **PR** | {pr_url} |")

    body_lines.extend(["", "## Summary", "", summary or "_No summary available_"])

    if changes:
        body_lines.extend(["", "## Changes", ""])
        for change in changes[:10]:  # 最大10件
            path = change.get("path", "unknown")
            action = change.get("action", "modified")
            body_lines.append(f"- `{path}` ({action})")

    body_lines.extend([
        "",
        "---",
        f"*Auto-generated by Jules Specialist Reviews at {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])

    labels = ["jules-review", category]
    if pr_url:
        labels.append("has-pr")

    return {
        "title": title,
        "body": "\n".join(body_lines),
        "labels": labels,
    }


# PURPOSE: gh CLI で Issue を作成
def create_github_issue(title: str, body: str, labels: list[str], repo: str, dry_run: bool = False) -> str | None:
    """gh CLI で GitHub Issue を作成"""
    if dry_run:
        print(f"\n{'='*60}")
        print(f"[DRY RUN] Issue: {title}")
        print(f"Labels: {', '.join(labels)}")
        print(f"{'='*60}")
        print(body)
        print(f"{'='*60}\n")
        return None

    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
    ]
    for label in labels:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"  ✓ Issue created: {url}")
            return url
        else:
            print(f"  ✗ Failed: {result.stderr.strip()}")
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  ✗ Error: {e}")
        return None


# PURPOSE: メインエントリポイント
async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Jules → GitHub Issue Creator v1.0")
    parser.add_argument("--results", "-r", nargs="+", help="Result JSON file(s)")
    parser.add_argument("--dir", "-d", default="", help="Results directory")
    parser.add_argument("--days", type=int, default=1, help="Days back to scan")
    parser.add_argument("--repo", default=REPO, help=f"GitHub repo (default: {REPO})")
    parser.add_argument("--max-issues", type=int, default=MAX_ISSUES_PER_RUN, help="Max issues per run")
    parser.add_argument("--dry-run", action="store_true", help="Print issues without creating")
    parser.add_argument("--status-only", action="store_true", help="Only check session statuses")

    args = parser.parse_args()

    # 結果ファイル収集
    result_files = []
    if args.results:
        result_files = [Path(f) for f in args.results if Path(f).exists()]
    elif args.dir:
        from collect_results import find_result_files
        result_files = find_result_files(base_dir=args.dir, days_back=args.days)
    else:
        # デフォルト: logs/specialist_daily
        from collect_results import find_result_files
        result_files = find_result_files(days_back=args.days)

    if not result_files:
        print("No result files found.")
        return

    print(f"📁 Result files: {len(result_files)}")

    # セッション情報抽出
    all_sessions = []
    for rf in result_files:
        sessions = extract_sessions(rf)
        all_sessions.extend(sessions)

    if not all_sessions:
        print("No sessions found in result files.")
        return

    print(f"📋 Sessions found: {len(all_sessions)}")

    # API キー取得
    api_key = get_api_key()

    # セッション状態確認
    session_ids = [s["session_id"] for s in all_sessions]
    print(f"🔍 Checking {len(session_ids)} session(s)...")

    session_results = await fetch_sessions(session_ids, api_key)

    # 状態集計
    states = {}
    for sr in session_results:
        state = sr.get("state", sr.get("error", "UNKNOWN"))
        states[state] = states.get(state, 0) + 1

    print(f"\n📊 Session states:")
    for state, count in sorted(states.items(), key=lambda x: -x[1]):
        print(f"  {state}: {count}")

    if args.status_only:
        return

    # Issue 作成
    issues_created = 0
    for session_info, session_data in zip(all_sessions, session_results):
        if issues_created >= args.max_issues:
            remaining = len(all_sessions) - issues_created
            print(f"\n⚠️ Max issues reached ({args.max_issues}). {remaining} sessions remaining.")
            break

        issue = format_issue(session_info, session_data)
        if not issue:
            continue

        url = create_github_issue(
            title=issue["title"],
            body=issue["body"],
            labels=issue["labels"],
            repo=args.repo,
            dry_run=args.dry_run,
        )
        if url or args.dry_run:
            issues_created += 1

    print(f"\n{'='*40}")
    print(f"Issues {'previewed' if args.dry_run else 'created'}: {issues_created}")
    print(f"{'='*40}")


if __name__ == "__main__":
    asyncio.run(main())
