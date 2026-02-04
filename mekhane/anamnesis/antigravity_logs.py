# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → Antigravity IDE のセッションログ収集が必要
   → antigravity_logs.py が担う

Q.E.D.

---

Antigravity Output Panel Log Collector

Antigravity IDE の Output パネルに表示されるログを収集・分析するモジュール。

ログの場所:
    %APPDATA%/Antigravity/logs/<timestamp>/window1/exthost/google.antigravity/Antigravity.log

Usage:
    from mekhane.anamnesis.antigravity_logs import AntigravityLogCollector

    collector = AntigravityLogCollector()
    summary = collector.summary()
    print(summary)
"""

import os
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogEntry:
    """ログエントリ"""

    timestamp: datetime
    level: str  # info, warning, error
    message: str
    raw: str


@dataclass
class LogSummary:
    """ログの要約"""

    session_id: str
    session_start: Optional[datetime] = None
    model: Optional[str] = None
    total_requests: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    token_usage: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_start": (
                self.session_start.isoformat() if self.session_start else None
            ),
            "model": self.model,
            "total_requests": self.total_requests,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "token_usage": self.token_usage,
        }


class AntigravityLogCollector:
    """Antigravity Output パネルログの収集・分析"""

    # ログ解析用の正規表現
    RE_LOG_LINE = re.compile(
        r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \[(\w+)\] (.+)$"
    )
    RE_MODEL = re.compile(r"model[:\s]+([a-zA-Z0-9\-_.]+)")
    RE_TOKEN = re.compile(r"current tokens: (\d+),?\s*token limit: (\d+)")
    RE_PLANNER = re.compile(r"Requesting planner with (\d+) chat messages")
    RE_UNAVAILABLE = re.compile(r"UNAVAILABLE.*No capacity available for model (\S+)")

    def __init__(self):
        self._log_base = self._get_log_directory()

    @staticmethod
    def _get_log_directory() -> Path:
        """Antigravity ログディレクトリのパスを取得"""
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            # Fallback for non-Windows
            appdata = Path.home() / "AppData" / "Roaming"
        return Path(appdata) / "Antigravity" / "logs"

    def get_sessions(self, limit: int = 10) -> list[Path]:
        """利用可能なセッションディレクトリを取得（新しい順）"""
        if not self._log_base.exists():
            return []

        sessions = sorted(
            [d for d in self._log_base.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )
        return sessions[:limit]

    def get_latest_session(self) -> Optional[Path]:
        """最新セッションのログディレクトリを取得"""
        sessions = self.get_sessions(limit=1)
        return sessions[0] if sessions else None

    def get_antigravity_log(self, session: Optional[Path] = None) -> Optional[Path]:
        """Antigravity.log ファイルのパスを取得"""
        if session is None:
            session = self.get_latest_session()

        if session is None:
            return None

        log_path = (
            session / "window1" / "exthost" / "google.antigravity" / "Antigravity.log"
        )
        return log_path if log_path.exists() else None

    def read_log(self, session: Optional[Path] = None, tail: int = 0) -> list[str]:
        """ログファイルを読み込む

        Args:
            session: セッションディレクトリ（None で最新）
            tail: 末尾から取得する行数（0 で全行）
        """
        log_path = self.get_antigravity_log(session)
        if log_path is None:
            return []

        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return lines[-tail:] if tail > 0 else lines

    def parse_log(self, lines: list[str]) -> list[LogEntry]:
        """ログ行をパースして LogEntry のリストを返す"""
        entries = []
        for line in lines:
            match = self.RE_LOG_LINE.match(line)
            if match:
                ts_str, level, message = match.groups()
                try:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    ts = datetime.now()
                entries.append(
                    LogEntry(
                        timestamp=ts, level=level.lower(), message=message, raw=line
                    )
                )
        return entries

    def extract_model_info(self, lines: list[str]) -> list[str]:
        """モデル選択情報を抽出"""
        models = set()
        for line in lines:
            # claude-opus-4-5-thinking や gemini-3-pro などを検出
            if "model" in line.lower():
                match = self.RE_MODEL.search(line)
                if match:
                    model = match.group(1)
                    # フィルタ: 明らかなモデル名のみ
                    if any(
                        m in model.lower()
                        for m in ["claude", "gemini", "opus", "sonnet"]
                    ):
                        models.add(model)
        return sorted(models)

    def extract_errors(self, lines: list[str]) -> list[dict]:
        """エラー・警告を抽出"""
        errors = []
        for line in lines:
            if "[error]" in line.lower() or "Error" in line:
                match = self.RE_LOG_LINE.match(line)
                if match:
                    ts_str, level, message = match.groups()
                    errors.append(
                        {
                            "timestamp": ts_str,
                            "level": level,
                            "message": message[:200],  # 長すぎるメッセージを切り詰め
                        }
                    )
        return errors

    def extract_capacity_errors(self, lines: list[str]) -> list[dict]:
        """503 No capacity エラーを抽出"""
        errors = []
        for line in lines:
            match = self.RE_UNAVAILABLE.search(line)
            if match:
                model = match.group(1)
                ts_match = self.RE_LOG_LINE.match(line)
                ts_str = ts_match.group(1) if ts_match else "unknown"
                errors.append(
                    {"timestamp": ts_str, "model": model, "type": "503_no_capacity"}
                )
        return errors

    def extract_token_usage(self, lines: list[str]) -> Optional[dict]:
        """最新のトークン使用量を抽出"""
        for line in reversed(lines):
            match = self.RE_TOKEN.search(line)
            if match:
                current, limit = match.groups()
                return {
                    "current": int(current),
                    "limit": int(limit),
                    "percentage": round(int(current) / int(limit) * 100, 1),
                }
        return None

    def extract_request_count(self, lines: list[str]) -> int:
        """プランナーリクエスト数をカウント"""
        return sum(1 for line in lines if self.RE_PLANNER.search(line))

    def summary(self, session: Optional[Path] = None) -> dict:
        """ログの要約を生成

        Returns:
            dict: 要約情報
                - session_id: セッションID（タイムスタンプ）
                - model: 検出されたモデル
                - total_requests: プランナーリクエスト数
                - error_count: エラー数
                - capacity_errors: 503エラー数
                - token_usage: トークン使用量
        """
        if session is None:
            session = self.get_latest_session()

        if session is None:
            return {"error": "No session found"}

        lines = self.read_log(session)
        if not lines:
            return {"error": "Empty log file"}

        models = self.extract_model_info(lines)
        errors = self.extract_errors(lines)
        capacity_errors = self.extract_capacity_errors(lines)
        token_usage = self.extract_token_usage(lines)
        request_count = self.extract_request_count(lines)

        return {
            "session_id": session.name,
            "model": models[0] if models else "unknown",
            "all_models": models,
            "total_requests": request_count,
            "error_count": len(errors),
            "capacity_errors": len(capacity_errors),
            "token_usage": token_usage,
            "log_lines": len(lines),
        }

    def format_summary(self, summary: dict) -> str:
        """要約を人間が読みやすい形式でフォーマット"""
        if "error" in summary:
            return f"[Error] {summary['error']}"

        lines = [
            f"[Antigravity] Session: {summary['session_id']}",
            f"  Model: {summary['model']}",
            f"  Requests: {summary['total_requests']}",
            f"  Errors: {summary['error_count']} (503: {summary['capacity_errors']})",
        ]

        if summary.get("token_usage"):
            tu = summary["token_usage"]
            lines.append(
                f"  Tokens: {tu['current']:,} / {tu['limit']:,} ({tu['percentage']}%)"
            )

        return "\n".join(lines)


# CLI 用のエントリポイント関数
def cmd_logs(args) -> int:
    """logs サブコマンドのハンドラ"""
    from mekhane.anamnesis.ux_utils import (
        print_error,
        print_header,
        print_info,
        print_warning,
        colorize_usage,
    )

    collector = AntigravityLogCollector()

    # セッション一覧
    if args.list:
        sessions = collector.get_sessions(limit=args.limit)
        if not sessions:
            print_warning("No sessions found")
            return 1
        print_header(f"Antigravity Sessions ({len(sessions)} shown)")
        for s in sessions:
            print(f"  {s.name}")
        return 0

    # 特定セッションまたは最新
    session = None
    if args.session:
        session = collector._log_base / args.session
        if not session.exists():
            print_error(f"Session not found: {args.session}")
            return 1

    # エラーのみ
    if args.errors:
        lines = collector.read_log(session)
        errors = collector.extract_errors(lines)
        capacity = collector.extract_capacity_errors(lines)
        print_header(f"Errors: {len(errors)} total, {len(capacity)} capacity (503)")
        for e in errors[:20]:  # 最大20件
            print(f"  {e['timestamp']} [{e['level']}] {e['message'][:80]}...")
        return 0

    # モデル情報のみ
    if args.models:
        lines = collector.read_log(session)
        models = collector.extract_model_info(lines)
        print_info(f"Detected: {', '.join(models) if models else 'none'}", label="Models")
        return 0

    # トークン情報のみ
    if args.tokens:
        lines = collector.read_log(session)
        usage = collector.extract_token_usage(lines)
        if usage:
            colored_usage = colorize_usage(usage['current'], usage['limit'])
            print_info(colored_usage, label="Tokens")
        else:
            print_warning("Tokens not found")
        return 0

    # デフォルト: 要約
    summary = collector.summary(session)
    print(collector.format_summary(summary))
    return 0


if __name__ == "__main__":
    # スタンドアロン実行用
    collector = AntigravityLogCollector()
    summary = collector.summary()
    print(collector.format_summary(summary))
