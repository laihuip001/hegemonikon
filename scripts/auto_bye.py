#!/usr/bin/env python3
"""Auto-Bye — セッション安全ネット

WF-06 から呼ばれ、/bye を忘れたセッションの簡易 Handoff を自動生成する。
第零原則「意志より環境」の具体実装。

Usage:
    # n8n WF-06 から呼ばれる (自動モード)
    python scripts/auto_bye.py --auto

    # ドライラン (判定結果のみ)
    python scripts/auto_bye.py --dry-run

    # 手動実行 (強制生成)
    python scripts/auto_bye.py --force
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──
MNEME_ROOT = Path.home() / "oikos" / "mneme" / ".hegemonikon"
HANDOFF_DIR = MNEME_ROOT / "handoffs"
SESSION_DIR = MNEME_ROOT / "sessions"
SESSION_HISTORY = MNEME_ROOT / "session_history.jsonl"
HEGEMONIKON_ROOT = Path.home() / "oikos" / "hegemonikon"


def get_latest_handoff() -> tuple[Path | None, datetime | None]:
    """最新の Handoff ファイルと日時を取得."""
    if not HANDOFF_DIR.exists():
        return None, None

    handoffs = sorted(HANDOFF_DIR.glob("handoff_*.md"), reverse=True)
    if not handoffs:
        # SESSION_DIR も確認 (旧形式)
        handoffs = sorted(SESSION_DIR.glob("handoff_*.md"), reverse=True)
    if not handoffs:
        return None, None

    latest = handoffs[0]
    mtime = datetime.fromtimestamp(latest.stat().st_mtime)
    return latest, mtime


def get_latest_session_log() -> tuple[Path | None, datetime | None]:
    """最新のセッションログと日時を取得."""
    if not SESSION_DIR.exists():
        return None, None

    # チャットエクスポートファイルを検索
    logs = sorted(SESSION_DIR.glob("2026-*_*.md"), reverse=True)
    if not logs:
        return None, None

    latest = logs[0]
    mtime = datetime.fromtimestamp(latest.stat().st_mtime)
    return latest, mtime


def get_active_session() -> dict | None:
    """WF-06 の session_history.jsonl から最新のアクティブセッションを取得."""
    if not SESSION_HISTORY.exists():
        return None

    # 最新行を読む
    lines = SESSION_HISTORY.read_text(encoding="utf-8").strip().split("\n")
    if not lines:
        return None

    for line in reversed(lines):
        try:
            session = json.loads(line)
            if session.get("status") == "active":
                return session
        except json.JSONDecodeError:
            continue

    return None


def get_recent_git_summary() -> str:
    """直近のGitコミットサマリーを取得."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--no-decorate"],
            cwd=str(HEGEMONIKON_ROOT),
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "(Git 情報取得失敗)"


def generate_auto_handoff(reason: str = "timeout") -> Path:
    """簡易 Handoff を自動生成."""
    now = datetime.now()
    filename = f"handoff_{now.strftime('%Y%m%d_%H%M')}_auto.md"
    filepath = HANDOFF_DIR / filename

    # 最新セッションログの情報を取得
    log_path, log_time = get_latest_session_log()
    git_summary = get_recent_git_summary()
    active = get_active_session()

    # セッション情報
    if active:
        start_time = active.get("startTime", "?")
        mode = active.get("mode", "?")
        context = active.get("context", "?")
    else:
        start_time = "不明"
        mode = "不明"
        context = "不明"

    content = f"""# [AUTO-BYE] 自動生成 Handoff

> ⚠️ このHandoffは `/bye` が実行されなかったため、WF-06 により自動生成されました。
> 詳細は最新のチャットログ (ker(R)) を参照してください。

**Date**: {now.strftime('%Y-%m-%d %H:%M')} (Auto-Generated)
**Reason**: {reason}

---

## S (Situation)

セッション開始: {start_time}
モード: {mode}
コンテキスト: {context}

## B (Background)

最新チャットログ: {log_path.name if log_path else '未検出'}
ログ更新時刻: {log_time.strftime('%Y-%m-%d %H:%M') if log_time else '不明'}

## A (Assessment)

⚠️ `/bye` が実行されなかったため、以下は **自動推測** です。
詳細はチャットログを確認してください。

### 直近のGitコミット

```
{git_summary}
```

## R (Recommendation)

1. 次回 `/boot` 時にチャットログ (ker(R)) を確認
2. `/bye` の実行を忘れないよう注意
3. 未コミット変更がないか `git status` で確認

---

**V[session]**: 0.8 (自動生成のため不確実性高)
**⚠️ Auto-Bye**: 人間の /bye による圧縮ではないため、ε 精度は低い。
"""

    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    return filepath


def check_gap() -> dict:
    """Handoff gap を検出."""
    handoff_path, handoff_time = get_latest_handoff()
    log_path, log_time = get_latest_session_log()

    result = {
        "latest_handoff": str(handoff_path) if handoff_path else None,
        "handoff_time": handoff_time.isoformat() if handoff_time else None,
        "latest_log": str(log_path) if log_path else None,
        "log_time": log_time.isoformat() if log_time else None,
        "gap_detected": False,
        "reason": "",
    }

    if not log_time:
        result["reason"] = "チャットログなし"
        return result

    if not handoff_time:
        result["gap_detected"] = True
        result["reason"] = "Handoff が一度も生成されていない"
        return result

    # チャットログが Handoff より新しい = /bye なしでセッション終了
    if log_time > handoff_time + timedelta(hours=1):
        result["gap_detected"] = True
        result["reason"] = (
            f"チャット ({log_time.strftime('%m/%d %H:%M')}) が "
            f"Handoff ({handoff_time.strftime('%m/%d %H:%M')}) より新しい"
        )

    return result


def main():
    parser = argparse.ArgumentParser(description="Auto-Bye: セッション安全ネット")
    parser.add_argument("--auto", action="store_true",
                        help="n8n WF-06 から呼ばれる自動モード")
    parser.add_argument("--dry-run", action="store_true",
                        help="判定結果のみ出力 (Handoff 生成しない)")
    parser.add_argument("--force", action="store_true",
                        help="gap 検出に関係なく Handoff を強制生成")
    args = parser.parse_args()

    print(f"=== Auto-Bye ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===")

    gap = check_gap()
    print(f"  Latest Handoff: {gap['handoff_time'] or 'なし'}")
    print(f"  Latest Log:     {gap['log_time'] or 'なし'}")
    print(f"  Gap detected:   {gap['gap_detected']}")
    if gap['reason']:
        print(f"  Reason:         {gap['reason']}")

    should_generate = gap["gap_detected"] or args.force

    if args.dry_run:
        print(f"\n  [DRY-RUN] Would generate: {should_generate}")
        return 0

    if should_generate:
        reason = "force" if args.force else gap["reason"]
        path = generate_auto_handoff(reason=reason)
        print(f"\n  ✅ Auto Handoff generated: {path.name}")

        # JSON 出力 (n8n が読む)
        if args.auto:
            output = {
                "status": "generated",
                "file": str(path),
                "reason": reason,
            }
            print(json.dumps(output))
        return 0
    else:
        print("\n  🟢 No gap detected. Nothing to do.")
        if args.auto:
            print(json.dumps({"status": "no_gap"}))
        return 0


if __name__ == "__main__":
    sys.exit(main())
