#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/scripts/ O4→ブランチからPRを作成する必要→create_prs_from_branches が担う
"""
Jules Branch → Pull Request Creator

Jules が作成したブランチから Pull Request を一括作成するスクリプト。
GitHub API を使用して未 PR のブランチを検出し、PR を作成する。

Usage:
    # ドライラン (実際には作成しない)
    python create_prs_from_branches.py --dry-run

    # 実行 (最大10件)
    python create_prs_from_branches.py --limit 10

    # 全件実行
    python create_prs_from_branches.py --all

Requires:
    - GITHUB_TOKEN environment variable
"""

import os
import sys
import re
import argparse
import subprocess
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

try:
    import requests
except ImportError:
    print("❌ requests ライブラリが必要です: pip install requests")
    sys.exit(1)


@dataclass
# PURPOSE: ブランチ情報
class BranchInfo:
    """ブランチ情報"""

    name: str
    review_type: str  # e.g., "ae-008", "th-012"
    description: str  # e.g., "simplicity-review"
    session_id: str  # Jules session ID
    has_pr: bool = False


# PURPOSE: GitHub トークンを取得
def get_github_token() -> str:
    """GitHub トークンを取得"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # gcloud から取得を試みる
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "secrets",
                    "versions",
                    "access",
                    "latest",
                    "--secret=github-token",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            token = result.stdout.strip()
        except subprocess.CalledProcessError:
            pass  # TODO: Add proper error handling

    if not token:
        raise ValueError(
            "GITHUB_TOKEN が設定されていません。\n"
            "export GITHUB_TOKEN=ghp_xxx または gcloud secrets を設定してください。"
        )
    return token


# PURPOSE: ブランチ名をパースして情報を抽出
def parse_branch_name(branch: str) -> Optional[BranchInfo]:
    """
    ブランチ名をパースして情報を抽出

    Examples:
        ae-008-simplicity-review-13575771094057254873
        th-012-review-jules-client-17873865984729236088
        active-inference-review-jules-client-15268335583687300539
        comment-quality-review-cl-015-9012620130133128825
        specialist-review-ai-015-17345855063383740926
    """
    # パターン1: {type}-{num}-{description}-{session_id}
    pattern1 = r"^([a-z]+-\d+)-(.+?)-(\d{15,})$"
    # パターン2: {description}-review-{type}-{num}-{session_id}
    pattern2 = r"^(.+?)-review-([a-z]+-\d+)-(\d{15,})$"
    # パターン3: {description}-review-jules-client-{session_id}
    pattern3 = r"^(.+?)-review-jules-client-(\d{15,})$"
    # パターン4: {description}-review-{session_id}
    pattern4 = r"^(.+?)-review-(\d{15,})$"
    # パターン5: jules-client-review-{type}-{session_id}
    pattern5 = r"^jules-client-review-([a-z]+-?\d*)-(\d{15,})$"
    # パターン6: {type}/...review...-{session_id}
    pattern6 = r"^(?:[a-z]+/)?([a-z]+-\d+)-review-?.*?-?(\d{15,})$"
    # パターン7: specialist-review-{type}-{session_id}
    pattern7 = r"^specialist-review-([a-z]+-\d+)-(\d{15,})$"
    # パターン8: {description}-review/{type}-{session_id}
    pattern8 = r"^specialist-review/([a-z]+-\d+)-(\d{15,})$"
    # パターン9: security/...-review-...-{session_id}
    pattern9 = r"^([a-z]+)/(.+?)-review-.*?(\d{15,})$"
    # パターン10: docs/...-review-...-{session_id}
    pattern10 = r"^docs/([a-z]+-\d+)-review-.+?-(\d{15,})$"

    # パターンを順番に試す
    match = re.match(pattern1, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description=match.group(2),
            session_id=match.group(3),
        )

    match = re.match(pattern2, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(2),
            description=match.group(1),
            session_id=match.group(3),
        )

    match = re.match(pattern3, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type="jules-client",
            description=match.group(1),
            session_id=match.group(2),
        )

    match = re.match(pattern5, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description="jules-client-review",
            session_id=match.group(2),
        )

    match = re.match(pattern7, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description="specialist-review",
            session_id=match.group(2),
        )

    match = re.match(pattern8, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description="specialist-review",
            session_id=match.group(2),
        )

    match = re.match(pattern9, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description=match.group(2),
            session_id=match.group(3),
        )

    match = re.match(pattern10, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type=match.group(1),
            description="docs-review",
            session_id=match.group(2),
        )

    match = re.match(pattern4, branch)
    if match:
        return BranchInfo(
            name=branch,
            review_type="review",
            description=match.group(1),
            session_id=match.group(2),
        )

    return None


# PURPOSE: リモートの Jules レビューブランチを取得
def get_remote_branches() -> list[str]:
    """リモートの Jules レビューブランチを取得"""
    result = subprocess.run(
        ["git", "branch", "-a"], capture_output=True, text=True, check=True
    )

    branches = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if line.startswith("remotes/origin/") and "-review" in line:
            branch_name = line.replace("remotes/origin/", "")
            branches.append(branch_name)

    return branches


# PURPOSE: 既存の PR のブランチ名を取得
def get_existing_prs(token: str, owner: str, repo: str) -> set[str]:
    """既存の PR のブランチ名を取得"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    existing_branches = set()
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {"state": "all", "per_page": per_page, "page": page}

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()

        prs = resp.json()
        if not prs:
            break

        for pr in prs:
            existing_branches.add(pr["head"]["ref"])

        page += 1
        if len(prs) < per_page:
            break

    return existing_branches


# PURPOSE: Pull Request を作成
def create_pr(
    token: str, owner: str, repo: str, branch: BranchInfo, base: str = "master"
) -> dict:
    """Pull Request を作成"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    # PR タイトルを生成
    title = f"[Jules Review] {branch.review_type}: {branch.description}"

    # PR 本文を生成
    body = f"""## 🤖 Jules Synedrion Review

**Review Type**: `{branch.review_type}`
**Description**: {branch.description}
**Session ID**: `{branch.session_id}`

---

This PR was automatically created from a Jules review branch.

### Review Focus
{branch.description.replace("-", " ").title()}

---

*Auto-generated by `create_prs_from_branches.py`*
"""

    payload = {
        "title": title,
        "head": branch.name,
        "base": base,
        "body": body,
        "draft": False,
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code == 422:
        # Unprocessable Entity - likely no commits or already exists
        error = resp.json()
        return {"error": error.get("message", str(error))}

    resp.raise_for_status()
    return resp.json()


# PURPOSE: 関数: main
def main():
    parser = argparse.ArgumentParser(description="Jules ブランチから PR を一括作成")
    parser.add_argument(
        "--dry-run", action="store_true", help="実際には作成せずプレビュー"
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="作成する PR の最大数 (default: 10)"
    )
    parser.add_argument("--all", action="store_true", help="全件処理 (--limit を無視)")
    parser.add_argument("--owner", default="laihuip001", help="GitHub オーナー")
    parser.add_argument("--repo", default="hegemonikon", help="GitHub リポジトリ")
    parser.add_argument(
        "--base", default="master", help="ベースブランチ (default: master)"
    )
    args = parser.parse_args()

    print("🔍 Jules Branch → PR Creator")
    print("=" * 50)

    # Git リポジトリに移動
    repo_path = Path("/home/makaron8426/oikos/hegemonikon")
    os.chdir(repo_path)

    # 最新を取得
    print("📡 Fetching remote branches...")
    subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)

    # リモートブランチを取得
    branches = get_remote_branches()
    print(f"📂 Found {len(branches)} review branches")

    # ブランチ情報をパース
    parsed_branches = []
    for b in branches:
        info = parse_branch_name(b)
        if info:
            parsed_branches.append(info)
        else:
            print(f"  ⚠️ Could not parse: {b}")

    print(f"✅ Parsed {len(parsed_branches)} branches")

    if args.dry_run:
        print("\n📋 Dry Run - Preview only")
        for i, b in enumerate(
            parsed_branches[: args.limit if not args.all else len(parsed_branches)], 1
        ):
            print(f"  {i}. [{b.review_type}] {b.description}")
        print(
            f"\n→ Would create {min(len(parsed_branches), args.limit if not args.all else len(parsed_branches))} PRs"
        )
        return

    # トークン取得
    try:
        token = get_github_token()
        print("🔑 GitHub Token: OK")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 既存 PR を取得
    print("📊 Checking existing PRs...")
    existing_prs = get_existing_prs(token, args.owner, args.repo)
    print(f"  Found {len(existing_prs)} existing PRs")

    # 未 PR ブランチをフィルタ
    new_branches = [b for b in parsed_branches if b.name not in existing_prs]
    print(f"🆕 {len(new_branches)} branches without PR")

    if not new_branches:
        print("✅ All branches already have PRs!")
        return

    # 制限を適用
    to_create = new_branches if args.all else new_branches[: args.limit]

    print(f"\n🚀 Creating {len(to_create)} PRs...")

    created = 0
    failed = 0
    for i, branch in enumerate(to_create, 1):
        print(f"  [{i}/{len(to_create)}] {branch.name[:50]}...", end=" ")

        result = create_pr(token, args.owner, args.repo, branch, args.base)

        if "error" in result:
            print(f"❌ {result['error'][:50]}")
            failed += 1
        else:
            print(f"✅ #{result['number']}")
            created += 1

    print("\n" + "=" * 50)
    print(
        f"📊 Summary: {created} created, {failed} failed, {len(new_branches) - len(to_create)} remaining"
    )


if __name__ == "__main__":
    main()
