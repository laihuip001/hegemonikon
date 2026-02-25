#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→bc_violation_logger
# PROOF: [L2/運用] <- scripts/
# PURPOSE: BC違反・Creator フィードバックのリアルタイムログ
"""
bc_violation_logger.py — BC違反ログ記録エンジン

Creator の叱責 / 承認 / AI の自己検出を JSONL に即時記録。
violations.md (重大違反の詳細分析) と併用し、日常的な違反頻度を追跡する。

構造:
  - violations.jsonl: 1行1レコード (JSONL)
  - フィードバック種別: reprimand (叱責), acknowledgment (承認), self_detected (自己検出)
  - セッション・期間ごとの統計を提供

Usage:
    # ログ記録
    python scripts/bc_violation_logger.py log \\
        --type reprimand \\
        --bc BC-1,BC-3 \\
        --pattern skip_bias \\
        --severity high \\
        --description "WF定義を読まずに実行" \\
        --creator-words "真剣にやれコラ"

    # セッション統計
    python scripts/bc_violation_logger.py stats

    # ダッシュボード
    python scripts/bc_violation_logger.py dashboard --period week
"""

import json
import sys
import argparse
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ============================================================
# Config
# ============================================================

LOG_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "bc_violations"
LOG_FILE = LOG_DIR / "violations.jsonl"

FEEDBACK_TYPES = {"reprimand", "acknowledgment", "self_detected"}

PATTERN_NAMES = {
    "skip_bias": "知っている→省略",
    "env_gap": "環境強制なし",
    "accuracy_vs_utility": "正確 ≠ 有用",
    "false_impossibility": "できない ≠ やっていない",
    "selective_omission": "勝手な省略",
    "stale_handoff": "古い情報を信じる",
    "preflight_waste": "確認が本番を消費",
    "shortcut": "短絡・手抜き",
    "overconfidence": "過信",
    "sycophancy": "迎合",
}

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
SEVERITY_ICONS = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "💀"}
TYPE_ICONS = {"reprimand": "⚡", "acknowledgment": "✨", "self_detected": "🔍"}


# ============================================================
# Data Model
# ============================================================

@dataclass
class FeedbackEntry:
    """1件のフィードバック記録"""
    timestamp: str                    # ISO 8601
    feedback_type: str                # reprimand / acknowledgment / self_detected
    bc_ids: list[str] = field(default_factory=list)  # ["BC-1", "BC-3"]
    pattern: str = ""                 # skip_bias, selective_omission etc.
    severity: str = "medium"          # low, medium, high, critical
    description: str = ""             # 何が起きたか
    context: str = ""                 # そのとき何をしていたか
    creator_words: str = ""           # Creator の原文 (叱責/承認の言葉)
    corrective: str = ""              # 取った是正行動
    session_id: str = ""              # セッション識別 (Handoff ID など)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "FeedbackEntry":
        # Ignore unknown fields gracefully
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


# ============================================================
# Logger
# ============================================================

def log_entry(entry: FeedbackEntry) -> Path:
    """JSONL ファイルにアペンド。ディレクトリがなければ作成。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
    return LOG_FILE


def read_all_entries(path: Optional[Path] = None) -> list[FeedbackEntry]:
    """全エントリを読み込む。"""
    path = path or LOG_FILE
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            try:
                entries.append(FeedbackEntry.from_dict(json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                continue
    return entries


def filter_entries(
    entries: list[FeedbackEntry],
    *,
    feedback_type: Optional[str] = None,
    since_days: Optional[int] = None,
    pattern: Optional[str] = None,
    session_id: Optional[str] = None,
) -> list[FeedbackEntry]:
    """エントリをフィルタリング。"""
    result = entries

    if feedback_type:
        result = [e for e in result if e.feedback_type == feedback_type]

    if pattern:
        result = [e for e in result if e.pattern == pattern]

    if session_id:
        result = [e for e in result if e.session_id == session_id]

    if since_days is not None:
        cutoff = datetime.now() - timedelta(days=since_days)
        result = [
            e for e in result
            if _parse_ts(e.timestamp) >= cutoff
        ]

    return result


def _parse_ts(ts: str) -> datetime:
    """ISO 8601 timestamp をパース。"""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return datetime.min


# ============================================================
# Statistics
# ============================================================

def compute_stats(entries: list[FeedbackEntry]) -> dict:
    """エントリ群から統計を計算。"""
    if not entries:
        return {
            "total": 0,
            "by_type": {},
            "by_pattern": {},
            "by_bc": {},
            "by_severity": {},
            "reprimand_rate": 0.0,
            "self_detection_rate": 0.0,
            "creator_words_samples": [],
        }

    type_counts = Counter(e.feedback_type for e in entries)
    pattern_counts = Counter(e.pattern for e in entries if e.pattern)
    bc_counts: Counter = Counter()
    for e in entries:
        bc_counts.update(e.bc_ids)
    severity_counts = Counter(e.severity for e in entries if e.feedback_type != "acknowledgment")

    total = len(entries)
    reprimands = type_counts.get("reprimand", 0)
    acknowledgments = type_counts.get("acknowledgment", 0)
    self_detected = type_counts.get("self_detected", 0)

    # 違反系 (reprimand + self_detected) のうち自己検出の率
    violation_total = reprimands + self_detected
    self_detection_rate = (self_detected / violation_total * 100) if violation_total > 0 else 0

    # 叱責率 = reprimand / (reprimand + acknowledgment)
    feedback_total = reprimands + acknowledgments
    reprimand_rate = (reprimands / feedback_total * 100) if feedback_total > 0 else 0

    # Creator の言葉サンプル (直近5件)
    creator_samples = [
        {"type": e.feedback_type, "words": e.creator_words, "date": e.timestamp[:10]}
        for e in reversed(entries)
        if e.creator_words
    ][:5]

    return {
        "total": total,
        "by_type": dict(type_counts.most_common()),
        "by_pattern": dict(pattern_counts.most_common()),
        "by_bc": dict(bc_counts.most_common()),
        "by_severity": dict(severity_counts),
        "reprimand_rate": round(reprimand_rate, 1),
        "self_detection_rate": round(self_detection_rate, 1),
        "creator_words_samples": creator_samples,
    }


def compute_trend(entries: list[FeedbackEntry], weeks: int = 4) -> list[dict]:
    """週次トレンドを計算。"""
    now = datetime.now()
    trend = []
    for w in range(weeks - 1, -1, -1):
        start = now - timedelta(weeks=w + 1)
        end = now - timedelta(weeks=w)
        week_entries = [
            e for e in entries
            if start <= _parse_ts(e.timestamp) < end
        ]
        reprimands = sum(1 for e in week_entries if e.feedback_type == "reprimand")
        acks = sum(1 for e in week_entries if e.feedback_type == "acknowledgment")
        self_det = sum(1 for e in week_entries if e.feedback_type == "self_detected")
        trend.append({
            "week": f"W{weeks - w}",
            "start": start.strftime("%m/%d"),
            "end": end.strftime("%m/%d"),
            "reprimands": reprimands,
            "acknowledgments": acks,
            "self_detected": self_det,
            "total": len(week_entries),
        })
    return trend


# ============================================================
# Dashboard Formatter
# ============================================================

def format_dashboard(
    entries: list[FeedbackEntry],
    period: str = "all",
) -> str:
    """CLIダッシュボードを生成。"""
    # Period filter
    if period == "today":
        entries = filter_entries(entries, since_days=0)
    elif period == "week":
        entries = filter_entries(entries, since_days=7)
    elif period == "month":
        entries = filter_entries(entries, since_days=30)

    stats = compute_stats(entries)
    trend = compute_trend(entries)

    lines = [
        "📊 BC違反・フィードバック ダッシュボード",
        f"   期間: {period} | 総件数: {stats['total']}",
        "━" * 50,
        "",
    ]

    # Type breakdown
    lines.append("📋 フィードバック種別")
    for t, icon in TYPE_ICONS.items():
        count = stats["by_type"].get(t, 0)
        bar = "█" * count
        label = {"reprimand": "叱責", "acknowledgment": "承認", "self_detected": "自己検出"}[t]
        lines.append(f"  {icon} {label:8s}: {bar} {count}")
    lines.append("")

    # Reprimand rate vs self-detection rate
    lines.append("📈 指標")
    lines.append(f"  叱責率: {stats['reprimand_rate']}% (叱責 / (叱責+承認))")
    lines.append(f"  自己検出率: {stats['self_detection_rate']}% (自己検出 / (叱責+自己検出))")
    lines.append("")

    # Severity
    if stats["by_severity"]:
        lines.append("🔴 深刻度分布")
        for sev in ["critical", "high", "medium", "low"]:
            count = stats["by_severity"].get(sev, 0)
            if count > 0:
                icon = SEVERITY_ICONS.get(sev, "⚪")
                bar = "█" * count
                lines.append(f"  {icon} {sev:10s}: {bar} {count}")
        lines.append("")

    # Pattern frequency
    if stats["by_pattern"]:
        lines.append("🔁 パターン頻度")
        for pattern, count in stats["by_pattern"].items():
            name = PATTERN_NAMES.get(pattern, pattern)
            bar = "█" * count
            lines.append(f"  {name:20s}: {bar} {count}")
        lines.append("")

    # Most violated BCs
    if stats["by_bc"]:
        lines.append("⚠️ 違反 BC ランキング")
        for bc, count in stats["by_bc"].items():
            bar = "█" * count
            lines.append(f"  {bc:8s}: {bar} {count}")
        lines.append("")

    # Weekly trend
    lines.append("📊 週次トレンド")
    for w in trend:
        rep_bar = "⚡" * w["reprimands"]
        ack_bar = "✨" * w["acknowledgments"]
        self_bar = "🔍" * w["self_detected"]
        lines.append(f"  {w['week']} ({w['start']}-{w['end']}): {rep_bar}{ack_bar}{self_bar} ({w['total']})")
    lines.append("")

    # Creator's words
    if stats["creator_words_samples"]:
        lines.append("💬 Creator の言葉 (直近)")
        for s in stats["creator_words_samples"]:
            icon = TYPE_ICONS.get(s["type"], "")
            lines.append(f"  {icon} [{s['date']}] \"{s['words']}\"")
        lines.append("")

    return "\n".join(lines)


def format_session_summary(entries: list[FeedbackEntry], session_id: str = "") -> str:
    """セッション内サマリー (簡潔)。"""
    if session_id:
        entries = filter_entries(entries, session_id=session_id)

    stats = compute_stats(entries)
    if stats["total"] == 0:
        return "✅ このセッションでの違反記録なし"

    rep = stats["by_type"].get("reprimand", 0)
    ack = stats["by_type"].get("acknowledgment", 0)
    sd = stats["by_type"].get("self_detected", 0)

    parts = []
    if rep > 0:
        parts.append(f"⚡叱責 {rep}")
    if ack > 0:
        parts.append(f"✨承認 {ack}")
    if sd > 0:
        parts.append(f"🔍自己検出 {sd}")

    return f"📊 セッション: {' | '.join(parts)} | 自己検出率: {stats['self_detection_rate']}%"


def format_bye_section(entries: list[FeedbackEntry]) -> str:
    """
    /bye Handoff に含める BC違反セクション。

    Step 2 (セッション情報収集) と Step 3.7 (Self-Profile) で使う。
    """
    stats = compute_stats(entries)
    if stats["total"] == 0:
        return "## ⚡ BC フィードバック\n\n✅ このセッションでのフィードバック記録なし\n"

    lines = [
        "## ⚡ BC フィードバック",
        "",
        "| 指標 | 値 |",
        "|:-----|:---|",
        f"| 総件数 | {stats['total']} |",
        f"| 叱責率 | {stats['reprimand_rate']}% |",
        f"| 自己検出率 | {stats['self_detection_rate']}% |",
    ]

    # 種別内訳
    rep = stats["by_type"].get("reprimand", 0)
    ack = stats["by_type"].get("acknowledgment", 0)
    sd = stats["by_type"].get("self_detected", 0)
    lines.append(f"| 内訳 | ⚡叱責 {rep} / ✨承認 {ack} / 🔍自己検出 {sd} |")

    # パターン
    if stats["by_pattern"]:
        top_patterns = ", ".join(
            f"{PATTERN_NAMES.get(p, p)}({c})"
            for p, c in list(stats["by_pattern"].items())[:3]
        )
        lines.append(f"| 頻出パターン | {top_patterns} |")

    # 最多 BC
    if stats["by_bc"]:
        top_bcs = ", ".join(
            f"{bc}({c})" for bc, c in list(stats["by_bc"].items())[:3]
        )
        lines.append(f"| 最多 BC | {top_bcs} |")

    lines.append("")

    # Creator の言葉
    if stats["creator_words_samples"]:
        lines.append("### Creator の言葉")
        lines.append("")
        for s in stats["creator_words_samples"]:
            icon = TYPE_ICONS.get(s["type"], "")
            lines.append(f"- {icon} [{s['date']}] \"{s['words']}\"")
        lines.append("")

    return "\n".join(lines)


def format_boot_summary(entries: list[FeedbackEntry]) -> str:
    """
    /boot 時に突きつける前セッションまでの傾向サマリー。

    コンパクトに叱責率・自己検出率・直近トレンドを返す。
    """
    if not entries:
        return "⚡ BC: 記録なし"

    stats = compute_stats(entries)
    trend = compute_trend(entries, weeks=2)

    # 直近週のデータ
    latest = trend[-1] if trend else {}
    latest_rep = latest.get("reprimands", 0)
    latest_total = latest.get("total", 0)

    parts = [
        f"⚡ BC: 累計{stats['total']}件",
        f"叱責率{stats['reprimand_rate']}%",
        f"自己検出率{stats['self_detection_rate']}%",
        f"直近週: {latest_rep}叱責/{latest_total}件",
    ]

    # 最多パターン警告
    if stats["by_pattern"]:
        top_pattern = list(stats["by_pattern"].keys())[0]
        top_name = PATTERN_NAMES.get(top_pattern, top_pattern)
        parts.append(f"⚠️{top_name}")

    return " | ".join(parts)


# ============================================================
# Escalation — violations.md への昇格提案
# ============================================================

VIOLATIONS_MD = (
    Path.home()
    / "oikos"
    / "hegemonikon"
    / ".agent"
    / "rules"
    / "behavioral_constraints"
    / "violations.md"
)


def _next_violation_id(violations_path: Optional[Path] = None) -> str:
    """violations.md の既存最大 V-NNN ID を検出し、次の ID を返す。

    YAML ブロック内の `id: V-NNN` 行のみを対象にする。
    本文中の言及 (例: 'V-006 の再発') は無視する。
    """
    path = violations_path or VIOLATIONS_MD
    if not path.exists():
        return "V-001"
    import re

    content = path.read_text(encoding="utf-8")
    # YAML ブロック内の id: V-NNN のみを対象
    ids = re.findall(r'^id:\s*V-(\d{3})', content, re.MULTILINE)
    if not ids:
        return "V-001"
    max_id = max(int(i) for i in ids)
    return f"V-{max_id + 1:03d}"


def _existing_patterns_in_violations(violations_path: Optional[Path] = None) -> set[str]:
    """violations.md に既に記録されているパターン名を返す。"""
    path = violations_path or VIOLATIONS_MD
    if not path.exists():
        return set()
    import re

    content = path.read_text(encoding="utf-8")
    return set(re.findall(r'^pattern:\s*(\S+)', content, re.MULTILINE))


def suggest_escalation(
    entries: list[FeedbackEntry],
    *,
    min_severity: str = "high",
    min_occurrences: int = 2,
) -> list[dict]:
    """
    violations.md への昇格候補を検出する。

    昇格条件 (OR):
      1. severity が min_severity 以上
      2. 同じ pattern が min_occurrences 回以上出現

    Returns:
        list[dict]: 昇格候補のリスト。各要素は:
          - pattern: str
          - severity: str (最高深刻度)
          - count: int
          - reason: str ("severity" or "recurrence" or "both")
          - entries: list[FeedbackEntry] (該当エントリ)
          - template: str (violations.md 用 YAML テンプレート)
    """
    if not entries:
        return []

    # パターンごとに集計
    pattern_groups: dict[str, list[FeedbackEntry]] = {}
    for e in entries:
        if e.pattern:
            pattern_groups.setdefault(e.pattern, []).append(e)

    # 二重提案防止: violations.md に既に記録されているパターンを除外
    existing_patterns = _existing_patterns_in_violations()
    for p in existing_patterns:
        pattern_groups.pop(p, None)

    sev_threshold = SEVERITY_ORDER.get(min_severity, 2)
    next_id = _next_violation_id()
    candidates = []

    for pattern, group in pattern_groups.items():
        max_sev = max(SEVERITY_ORDER.get(e.severity, 0) for e in group)
        max_sev_name = next(k for k, v in SEVERITY_ORDER.items() if v == max_sev)
        count = len(group)

        is_severe = max_sev >= sev_threshold
        is_recurrent = count >= min_occurrences
        if not (is_severe or is_recurrent):
            continue

        reason = "both" if (is_severe and is_recurrent) else (
            "severity" if is_severe else "recurrence"
        )

        # YAML テンプレート生成
        template = _format_escalation_entry(
            vid=next_id,
            pattern=pattern,
            severity=max_sev_name,
            recurrent=is_recurrent,
            group=group,
        )

        candidates.append({
            "pattern": pattern,
            "severity": max_sev_name,
            "count": count,
            "reason": reason,
            "entries": group,
            "template": template,
        })

        # 次の ID をインクリメント
        num = int(next_id.split("-")[1])
        next_id = f"V-{num + 1:03d}"

    # 深刻度降順 → 件数降順
    candidates.sort(
        key=lambda c: (-SEVERITY_ORDER.get(c["severity"], 0), -c["count"])
    )
    return candidates


def _format_escalation_entry(
    vid: str,
    pattern: str,
    severity: str,
    recurrent: bool,
    group: list[FeedbackEntry],
) -> str:
    """violations.md 用の YAML テンプレートを生成。"""
    from datetime import date

    # BC の集約
    all_bcs: set[str] = set()
    for e in group:
        all_bcs.update(e.bc_ids)
    bc_list = sorted(all_bcs) if all_bcs else ["BC-?"]

    # サマリー: 代表的な description を使用
    descriptions = [e.description for e in group if e.description]
    summary = descriptions[0] if descriptions else "JSONL から昇格"
    if len(descriptions) > 1:
        summary += f" (他 {len(descriptions) - 1} 件)"

    # Creator の言葉
    creator_words = [e.creator_words for e in group if e.creator_words]
    creator_section = ""
    if creator_words:
        creator_section = "\n  Creator の言葉:\n" + "\n".join(
            f"    - \"{w}\"" for w in creator_words[:3]
        )

    # 是正行動
    correctives = [e.corrective for e in group if e.corrective]
    corrective_section = correctives[0] if correctives else "<!-- FILL: 是正行動 -->"

    pattern_name = PATTERN_NAMES.get(pattern, pattern)

    return f"""### {vid}: {pattern_name}（JSONL 昇格）

```yaml
id: {vid}
date: "{date.today().isoformat()}"
bc: [{', '.join(bc_list)}]
pattern: {pattern}
severity: {severity}
recurrence: {str(recurrent).lower()}
summary: |
  {summary}
  JSONL 記録 {len(group)} 件から昇格。{creator_section}
root_cause: |
  <!-- FILL: 根本原因を記述 -->
corrective: |
  {corrective_section}
lesson: |
  <!-- FILL: 教訓を記述 -->
```

---"""


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="BC違反ログ記録エンジン — Creator フィードバック追跡"
    )
    sub = parser.add_subparsers(dest="command")

    # log コマンド
    log_parser = sub.add_parser("log", help="フィードバックを記録")
    log_parser.add_argument("--type", required=True, choices=sorted(FEEDBACK_TYPES),
                           help="フィードバック種別")
    log_parser.add_argument("--bc", type=str, default="",
                           help="BC ID (カンマ区切り: BC-1,BC-3)")
    log_parser.add_argument("--pattern", type=str, default="",
                           help="パターンID")
    log_parser.add_argument("--severity", type=str, default="medium",
                           choices=sorted(SEVERITY_ORDER.keys()),
                           help="深刻度")
    log_parser.add_argument("--description", type=str, default="",
                           help="何が起きたか")
    log_parser.add_argument("--context", type=str, default="",
                           help="文脈")
    log_parser.add_argument("--creator-words", type=str, default="",
                           help="Creator の原文")
    log_parser.add_argument("--corrective", type=str, default="",
                           help="是正行動")
    log_parser.add_argument("--session-id", type=str, default="",
                           help="セッションID")

    # stats コマンド
    sub.add_parser("stats", help="統計を表示")

    # dashboard コマンド
    dash_parser = sub.add_parser("dashboard", help="ダッシュボードを表示")
    dash_parser.add_argument("--period", type=str, default="all",
                            choices=["today", "week", "month", "all"],
                            help="期間")
    dash_parser.add_argument("--json", action="store_true", help="JSON出力")

    # escalate コマンド
    esc_parser = sub.add_parser("escalate", help="violations.md への昇格候補を表示")
    esc_parser.add_argument("--min-severity", type=str, default="high",
                           choices=sorted(SEVERITY_ORDER.keys()),
                           help="最低深刻度 (default: high)")
    esc_parser.add_argument("--min-occurrences", type=int, default=2,
                           help="最低出現回数 (default: 2)")

    args = parser.parse_args()

    if args.command == "log":
        bc_ids = [b.strip() for b in args.bc.split(",") if b.strip()]
        entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            feedback_type=args.type,
            bc_ids=bc_ids,
            pattern=args.pattern,
            severity=args.severity,
            description=args.description,
            context=args.context,
            creator_words=args.creator_words,
            corrective=args.corrective,
            session_id=args.session_id,
        )
        path = log_entry(entry)
        icon = TYPE_ICONS.get(args.type, "")
        print(f"{icon} 記録完了: {path}")
        print(f"   種別: {args.type} | BC: {bc_ids} | パターン: {args.pattern}")

        # 記録後にセッションサマリーを表示
        all_entries = read_all_entries()
        print()
        print(format_session_summary(all_entries))

    elif args.command == "stats":
        entries = read_all_entries()
        stats = compute_stats(entries)
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.command == "dashboard":
        entries = read_all_entries()
        if args.json:
            stats = compute_stats(entries)
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print(format_dashboard(entries, period=args.period))

    elif args.command == "escalate":
        entries = read_all_entries()
        candidates = suggest_escalation(
            entries,
            min_severity=args.min_severity,
            min_occurrences=args.min_occurrences,
        )
        if not candidates:
            print("✅ 昇格候補なし — 現在の記録に重大/反復パターンは検出されませんでした")
        else:
            print(f"⬆️ 昇格候補: {len(candidates)} 件")
            print(f"   次の ID: {_next_violation_id()}")
            print("━" * 50)
            for c in candidates:
                name = PATTERN_NAMES.get(c["pattern"], c["pattern"])
                icon = SEVERITY_ICONS.get(c["severity"], "⚪")
                print(f"\n{icon} {name} — {c['count']}件 ({c['reason']})")
                print(c["template"])

    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
