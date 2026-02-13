#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/peira/ A0→システム可観測性が必要→hgk_healthが担う
"""
Hegemonikón Health Dashboard — 全サービスの死活と品質を一覧表示

Usage:
    python -m mekhane.peira.hgk_health          # ターミナル出力
    python -m mekhane.peira.hgk_health --json   # JSON出力 (監視連携用)
    python -m mekhane.peira.hgk_health --slack  # Slack通知
    python -m mekhane.peira.hgk_health --n8n   # n8n WF-05 webhook送信
"""

import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# PURPOSE: ヘルスチェック結果を統一的に扱い、レポート生成と判定分岐を可能にする
@dataclass
class HealthItem:
    name: str
    status: str  # "ok" | "warn" | "error" | "unknown"
    detail: str = ""
    metric: Optional[float] = None

    # PURPOSE: emoji の処理
    @property
    def emoji(self) -> str:
        return {"ok": "🟢", "warn": "🟡", "error": "🔴", "unknown": "⚪"}.get(self.status, "❓")

# PURPOSE: 全体のヘルスレポートを保持
@dataclass
class HealthReport:
    timestamp: str = ""
    items: list[HealthItem] = field(default_factory=list)

    # PURPOSE: 0.0-1.0 の総合スコア
    @property
    def score(self) -> float:
        """0.0-1.0 の総合スコア"""
        if not self.items:
            return 0.0
        weights = {"ok": 1.0, "warn": 0.6, "error": 0.0, "unknown": 0.3}
        return sum(weights.get(i.status, 0) for i in self.items) / len(self.items)


# PURPOSE: systemd サービスの死活チェック
def check_systemd_service(name: str, unit: str, is_user: bool = False) -> HealthItem:
    try:
        cmd = ["systemctl"]
        if is_user:
            cmd.append("--user")
        cmd.extend(["is-active", unit])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        active = result.stdout.strip() == "active"
        return HealthItem(name, "ok" if active else "error", result.stdout.strip())
    except Exception as e:
        return HealthItem(name, "unknown", str(e))


# PURPOSE: Docker コンテナの死活チェック
def check_docker(name: str, container_name: str = "n8n") -> HealthItem:
    try:
        result = subprocess.run(
            ["sudo", "docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        status = result.stdout.strip()
        if "Up" in status:
            return HealthItem(name, "ok", status)
        elif status:
            return HealthItem(name, "error", status)
        else:
            return HealthItem(name, "error", "container not running")
    except Exception as e:
        return HealthItem(name, "unknown", str(e))


# PURPOSE: crontab エントリの存在チェック
def check_cron(name: str, pattern: str) -> HealthItem:
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
        lines = [l for l in result.stdout.split("\n") if pattern in l and not l.strip().startswith("#")]
        if lines:
            return HealthItem(name, "ok", f"{len(lines)} entry(ies)")
        return HealthItem(name, "error", "not found in crontab")
    except Exception as e:
        return HealthItem(name, "unknown", str(e))


# PURPOSE: Handoff ディレクトリの状態チェック
def check_handoff() -> HealthItem:
    # Primary: sessions/ (current /bye output)
    handoff_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"
    # Fallback: handoffs/ (legacy)
    if not handoff_dir.exists():
        handoff_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "handoffs"
    if not handoff_dir.exists():
        return HealthItem("Handoff", "error", "directory does not exist")

    files = sorted(handoff_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return HealthItem("Handoff", "error", "0 files — /bye→handoff path broken?")

    latest = files[0]
    age_hours = (datetime.now().timestamp() - latest.stat().st_mtime) / 3600
    detail = f"{len(files)} files, latest: {latest.name} ({age_hours:.0f}h ago)"

    if age_hours < 24:
        return HealthItem("Handoff", "ok", detail, metric=age_hours)
    elif age_hours < 72:
        return HealthItem("Handoff", "warn", detail, metric=age_hours)
    else:
        return HealthItem("Handoff", "error", detail, metric=age_hours)


# PURPOSE: Digestor の最新実行状態チェック
def check_digestor_log() -> HealthItem:
    log_file = Path.home() / ".hegemonikon" / "digestor" / "scheduler.log"
    if not log_file.exists():
        return HealthItem("Digestor Log", "error", "log file not found")

    try:
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        last_lines = lines[-5:] if len(lines) >= 5 else lines
        last_text = "\n".join(last_lines)

        if "error" in last_text.lower() or "Error" in last_text:
            # エラーがあるが、その後 "Scheduler running" があれば warn
            if "Scheduler running" in last_text:
                return HealthItem("Digestor Log", "warn", "last run had errors but scheduler alive")
            return HealthItem("Digestor Log", "error", "errors in last run")

        if "Digestor complete" in last_text:
            return HealthItem("Digestor Log", "ok", "last run successful")

        if "Scheduler running" in last_text:
            return HealthItem("Digestor Log", "ok", "scheduler waiting for next run")

        return HealthItem("Digestor Log", "warn", "unknown state")
    except Exception as e:
        return HealthItem("Digestor Log", "unknown", str(e))


# PURPOSE: Dendron カバレッジチェック
def check_dendron() -> HealthItem:
    try:
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--format", "ci"],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        output = result.stdout + result.stderr
        if "✅" in output and "100.0%" in output:
            return HealthItem("Dendron L1", "ok", "100% PROOF coverage")
        elif "✅" in output:
            return HealthItem("Dendron L1", "ok", output.strip().split("\n")[-3] if output.strip() else "ok")
        elif "❌" in output:
            return HealthItem("Dendron L1", "error", output.strip().split("\n")[-3] if output.strip() else "failures")
        return HealthItem("Dendron L1", "unknown", "could not parse output")
    except Exception as e:
        return HealthItem("Dendron L1", "unknown", str(e))


# PURPOSE: 定理活性度チェック (Theorem Activity Report)
def check_theorem_activity() -> HealthItem:
    """24定理の活性度を集計し、体系の健全性を判定

    DX-008 R4: 直接発動と間接発動(ハブ経由)を分離し、
    「真の需要」と「ハブ依存生存」を区別する。
    """
    try:
        from mekhane.peira.theorem_activity import (
            scan_handoffs, classify_activity, THEOREM_WORKFLOWS
        )
        data = scan_handoffs(days=90)
        months = sorted(data["wf_by_month"].keys())
        months_span = max(len(months), 1)

        alive = dormant = dead = 0
        direct_alive = 0   # 直接発動で alive
        hub_only = 0        # ハブ経由のみで alive
        for wf_id in THEOREM_WORKFLOWS:
            direct = data["wf_counts"].get(wf_id, 0)
            via_hub = data["hub_counts"].get(wf_id, 0)
            total = direct + via_hub
            status = classify_activity(wf_id, total, months_span)
            if "alive" in status:
                alive += 1
                # 直接発動だけで alive 基準を満たすか判定
                direct_status = classify_activity(wf_id, direct, months_span)
                if "alive" in direct_status:
                    direct_alive += 1
                else:
                    hub_only += 1
            elif "death" in status:
                dead += 1
            else:
                dormant += 1

        total_theorems = len(THEOREM_WORKFLOWS)
        alive_rate = alive / total_theorems if total_theorems else 0
        detail = f"{alive}/{total_theorems} alive"
        if hub_only:
            detail += f" ({direct_alive} direct, {hub_only} hub-only)"
        if dormant:
            detail += f", {dormant} dormant"
        if dead:
            detail += f", {dead} dead"
        detail += f" ({alive_rate:.0%})"

        if alive >= 20:  # 83%+
            return HealthItem("Theorem Activity", "ok", detail, metric=alive_rate)
        elif alive >= 16:  # 66%+
            return HealthItem("Theorem Activity", "warn", detail, metric=alive_rate)
        else:
            return HealthItem("Theorem Activity", "error", detail, metric=alive_rate)
    except Exception as e:
        return HealthItem("Theorem Activity", "unknown", str(e))


# PURPOSE: Digest レポートの鮮度チェック
def check_digest_reports() -> HealthItem:
    report_dir = Path.home() / ".hegemonikon" / "digestor"
    reports = sorted(report_dir.glob("digest_report_*.json"), reverse=True)
    if not reports:
        return HealthItem("Digest Reports", "warn", "no reports yet (first run pending)")

    latest = reports[0]
    age_hours = (datetime.now().timestamp() - latest.stat().st_mtime) / 3600

    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
        candidates = data.get("candidates", [])
        detail = f"{len(reports)} reports, latest: {len(candidates)} candidates ({age_hours:.0f}h ago)"
    except Exception:
        detail = f"{len(reports)} reports ({age_hours:.0f}h ago)"

    if age_hours < 26:  # ~daily
        return HealthItem("Digest Reports", "ok", detail, metric=age_hours)
    elif age_hours < 72:
        return HealthItem("Digest Reports", "warn", detail, metric=age_hours)
    else:
        return HealthItem("Digest Reports", "error", detail, metric=age_hours)


# PURPOSE: Kalon (圏論的構造) 品質チェック
def check_kalon() -> HealthItem:
    """category.py の圏論的構造が Fix(G∘F) 品質基準を満たすか検証"""
    try:
        from mekhane.fep.kalon_checker import KalonChecker, KalonLevel

        checker = KalonChecker()
        report = checker.check_all()

        # KalonLevel → HealthItem status mapping
        level_map = {
            KalonLevel.KALON: "ok",
            KalonLevel.APPROACHING: "warn",
            KalonLevel.INCOMPLETE: "error",
            KalonLevel.ABSENT: "error",
        }
        status = level_map.get(report.overall_level, "unknown")

        kalon_count = sum(1 for r in report.results if r.level == KalonLevel.KALON)
        total = len(report.results)
        detail = f"{kalon_count}/{total} KALON ({report.overall_score:.2f})"

        if report.all_issues:
            detail += f", {len(report.all_issues)} issues"

        return HealthItem("Kalon Quality", status, detail, metric=report.overall_score)
    except Exception as e:
        return HealthItem("Kalon Quality", "unknown", str(e))


# PURPOSE: 全ヘルスチェックを実行してレポートを生成
def run_health_check() -> HealthReport:
    report = HealthReport(timestamp=datetime.now().isoformat())

    # Service checks
    report.items.append(check_systemd_service("Digestor Scheduler", "digestor-scheduler@makaron8426"))
    report.items.append(check_docker("n8n Container"))
    report.items.append(check_systemd_service("Gnosis Index Timer", "gnosis-index.timer", is_user=True))
    report.items.append(check_systemd_service("HGK Sync Timer", "hegemonikon-sync.timer", is_user=True))
    report.items.append(check_cron("Tier 1 Daily Cron", "tier1"))

    # Data checks
    report.items.append(check_handoff())
    report.items.append(check_digestor_log())
    report.items.append(check_digest_reports())

    # Quality checks (optional, slower)
    report.items.append(check_dendron())
    report.items.append(check_theorem_activity())
    report.items.append(check_kalon())

    return report


# PURPOSE: テキスト形式でレポートを表示
def format_terminal(report: HealthReport) -> str:
    lines = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║  Hegemonikón Health Dashboard            ║")
    lines.append(f"║  {report.timestamp[:19]:>38s}  ║")
    lines.append("╠══════════════════════════════════════════╣")

    for item in report.items:
        name = f"{item.name:.<25s}"
        lines.append(f"║  {item.emoji} {name} {item.detail[:30]:30s} ║")

    lines.append("╠══════════════════════════════════════════╣")
    score = report.score
    bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
    emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.5 else "🔴"
    lines.append(f"║  {emoji} Score: {score:.0%}  [{bar}]     ║")
    lines.append("╚══════════════════════════════════════════╝")
    return "\n".join(lines)


# PURPOSE: Slack webhook にレポートを送信
def send_slack(report: HealthReport):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        env_file = Path.home() / "oikos" / "hegemonikon" / ".env"
        if env_file.exists():
            for line in env_file.read_text().split("\n"):
                if line.startswith("SLACK_WEBHOOK_URL="):
                    webhook_url = line.split("=", 1)[1].strip().strip('"')

    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL not found", file=sys.stderr)
        return

    score = report.score
    emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.5 else "🔴"
    items_text = "\n".join(f"{i.emoji} {i.name}: {i.detail[:40]}" for i in report.items)
    text = f"{emoji} *HGK Health* — Score: {score:.0%}\n```\n{items_text}\n```"

    subprocess.run(
        ["curl", "-s", "-X", "POST", webhook_url,
         "-H", "Content-type: application/json",
         "-d", json.dumps({"text": text})],
        capture_output=True, timeout=10
    )


# PURPOSE: n8n WF-05 Health Alert webhook にレポートを送信
def send_n8n_alert(report: HealthReport) -> bool:
    """n8n の health-alert webhook にデータを送信。n8n 側で重大度分類と通知を行う。

    Returns:
        True if n8n accepted the alert, False otherwise.
    """
    url = "http://localhost:5678/webhook/health-alert"
    payload = json.dumps({
        "items": [asdict(i) for i in report.items],
        "score": report.score,
        "timestamp": report.timestamp,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            severity = result.get("severity", "?")
            print(f"📡 n8n WF-05: severity={severity}", file=sys.stderr)
            return True
    except Exception as e:
        print(f"⚠️ n8n WF-05 failed: {e}", file=sys.stderr)
        return False


# PURPOSE: CLI エントリポイント
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hegemonikón Health Dashboard")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--slack", action="store_true", help="Send directly to Slack (bypass n8n)")
    parser.add_argument("--n8n", action="store_true", help="Send to n8n WF-05")
    parser.add_argument("--auto", action="store_true", help="n8n first, Slack fallback (for cron)")
    parser.add_argument("--no-n8n", action="store_true", help="Suppress auto n8n send")
    args = parser.parse_args()

    report = run_health_check()

    if args.json:
        print(json.dumps([asdict(i) for i in report.items], indent=2, ensure_ascii=False))
    elif args.auto:
        # cron 用: n8n 優先 → 失敗時に Slack 直送フォールバック
        print(format_terminal(report))
        n8n_ok = send_n8n_alert(report)
        if not n8n_ok and report.score < 0.7:
            print("🔄 n8n unreachable, falling back to direct Slack", file=sys.stderr)
            send_slack(report)
    elif args.slack:
        # 直接 Slack送信 (n8n 未起動時のフォールバック)
        send_slack(report)
        print(format_terminal(report))
    else:
        print(format_terminal(report))

    # n8n 通知: n8n が Slack 通知の一元窓口
    # --n8n 明示指定 or スコア低下時は自動送信 (--slack/--auto との二重送信を回避)
    if not args.no_n8n and not args.slack and not args.auto:
        if args.n8n or report.score < 0.7:
            send_n8n_alert(report)

    # Exit code: 0 if score > 0.7, 1 otherwise
    sys.exit(0 if report.score >= 0.7 else 1)


if __name__ == "__main__":
    main()
