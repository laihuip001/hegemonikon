# PROOF: [L1/定理] <- mekhane/basanos/ VISION.md 第3段階: 予兆を察知する免疫
# PURPOSE: GitMetrics — git 履歴からリスク予兆を検出する。
"""
GitMetrics — git 履歴からリスク予兆を検出する。

壊れてから直す → 壊れる前に気づく。

FEP 解釈:
- commit frequency = 環境の変動速度 (高 = 予測モデルの更新頻度を上げるべき)
- file churn = ファイル別の予測誤差蓄積 (高churn = 不安定 = 要監視)
- author switching = 生成モデルの一貫性リスク (多人数 = 暗黙知の断裂)
"""

import logging
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# PURPOSE: ファイルの変動(churn)情報。
@dataclass
class FileChurn:
    """ファイルの変動(churn)情報。"""

    path: str
    commits: int = 0          # total commits touching this file
    lines_added: int = 0
    lines_deleted: int = 0
    authors: int = 0          # unique author count
    last_modified: str = ""
    days_active: int = 0      # days with at least 1 commit

    # PURPOSE: 変動率: (added + deleted) / commits。高い = 不安定。
    @property
    def churn_rate(self) -> float:
        """変動率: (added + deleted) / commits。高い = 不安定。"""
        if self.commits == 0:
            return 0.0
        return (self.lines_added + self.lines_deleted) / self.commits

    # PURPOSE: リスクスコア: churn_rate × authors × recency。
    @property
    def risk_score(self) -> float:
        """リスクスコア: churn_rate × authors × recency。

        高い = 壊れやすい。
        """
        author_factor = 1.0 + (self.authors - 1) * 0.3  # multi-author penalty
        return self.churn_rate * author_factor


# PURPOSE: 日別のコミット統計。
@dataclass
class CommitStats:
    """日別のコミット統計。"""

    date: str
    count: int = 0
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


# PURPOSE: git 履歴からリスク予兆を検出する。
class GitMetrics:
    """git 履歴からリスク予兆を検出する。

    Usage:
        gm = GitMetrics(repo_root)
        churn = gm.file_churn(days=14)
        risky = gm.risky_files(top_n=10)
        daily = gm.daily_stats(days=14)
    """

    def __init__(self, repo_root: Optional[Path] = None, days: int = 14):
        self.repo_root = repo_root or Path.home() / "oikos/hegemonikon"
        self.days = days
        self._churn_cache: Optional[Dict[str, FileChurn]] = None

    def _git(self, *args: str) -> str:
        """git コマンドを実行して stdout を返す。"""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10,
            )
            if result.returncode != 0:
                logger.debug(f"git {' '.join(args)} failed: {result.stderr.strip()}")
                return ""
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"git command failed: {e}")
            return ""

    # PURPOSE: ファイル別の churn (変動) を算出。
    def file_churn(self) -> Dict[str, FileChurn]:
        """ファイル別の churn (変動) を算出。"""
        if self._churn_cache is not None:
            return self._churn_cache

        since = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")
        churns: Dict[str, FileChurn] = {}

        # git log: per-file commit count + numstat
        log_output = self._git(
            "log",
            f"--since={since}",
            "--format=%H|%ad|%an",
            "--date=short",
            "--numstat",
            "--diff-filter=ACDMR",
            "--",
            "*.py",
        )
        if not log_output:
            self._churn_cache = churns
            return churns

        current_commit = ""
        current_date = ""
        current_author = ""
        file_authors: Dict[str, set] = {}
        file_dates: Dict[str, set] = {}

        for line in log_output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            if "|" in line and line.count("|") >= 2:
                # Commit header: HASH|DATE|AUTHOR
                parts = line.split("|", 2)
                current_commit = parts[0]
                current_date = parts[1]
                current_author = parts[2]
            elif "\t" in line:
                # numstat: added\tdeleted\tfilename
                parts = line.split("\t", 2)
                if len(parts) == 3 and parts[0] != "-":
                    try:
                        added = int(parts[0])
                        deleted = int(parts[1])
                    except ValueError:
                        continue
                    filepath = parts[2]

                    if filepath not in churns:
                        churns[filepath] = FileChurn(path=filepath)
                        file_authors[filepath] = set()
                        file_dates[filepath] = set()

                    fc = churns[filepath]
                    fc.commits += 1
                    fc.lines_added += added
                    fc.lines_deleted += deleted
                    fc.last_modified = max(fc.last_modified, current_date) if fc.last_modified else current_date

                    file_authors[filepath].add(current_author)
                    file_dates[filepath].add(current_date)

        # Fill in author count and days_active
        for filepath, fc in churns.items():
            fc.authors = len(file_authors.get(filepath, set()))
            fc.days_active = len(file_dates.get(filepath, set()))

        self._churn_cache = churns
        return churns

    # PURPOSE: リスクスコア上位のファイルを返す。
    def risky_files(self, top_n: int = 10) -> List[FileChurn]:
        """リスクスコア上位のファイルを返す。"""
        churns = self.file_churn()
        ranked = sorted(churns.values(), key=lambda fc: fc.risk_score, reverse=True)
        return ranked[:top_n]

    # PURPOSE: 日別コミット統計。
    def daily_stats(self) -> List[CommitStats]:
        """日別コミット統計。"""
        since = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        log_output = self._git(
            "log",
            f"--since={since}",
            "--format=%ad",
            "--date=short",
        )
        if not log_output:
            return []

        date_counts = Counter(line.strip() for line in log_output.strip().split("\n") if line.strip())
        stats = []
        for date, count in sorted(date_counts.items()):
            stats.append(CommitStats(date=date, count=count))

        return stats

    # PURPOSE: TrendAnalyzer の hot files と git churn の交差点を検出。
    def hotspot_overlaps(self, trend_hot_files: List[str]) -> List[str]:
        """TrendAnalyzer の hot files と git churn の交差点を検出。

        両方で高スコア = 最優先で注意すべきファイル。
        """
        churns = self.file_churn()
        risky_set = {fc.path for fc in self.risky_files(top_n=20)}

        overlaps = []
        for file_path in trend_hot_files:
            # パスの正規化 (trend は相対パス)
            if file_path in risky_set:
                overlaps.append(file_path)
            else:
                # basename match
                for risky_path in risky_set:
                    if risky_path.endswith(file_path) or file_path.endswith(risky_path):
                        overlaps.append(file_path)
                        break

        return overlaps

    # PURPOSE: 直近のコミット速度 (commits/day)。
    def commit_velocity(self) -> float:
        """直近のコミット速度 (commits/day)。"""
        stats = self.daily_stats()
        if not stats:
            return 0.0
        total = sum(s.count for s in stats)
        return total / max(len(stats), 1)

    # PURPOSE: 分析結果の要約テキスト。
    def summary(self) -> str:
        """分析結果の要約テキスト。"""
        churns = self.file_churn()
        if not churns:
            return f"📊 Git Metrics: No commits in the past {self.days} days."

        risky = self.risky_files(top_n=3)
        velocity = self.commit_velocity()
        stats = self.daily_stats()

        lines = [
            f"📊 Git Metrics ({self.days} days, {len(churns)} files, {sum(s.count for s in stats)} commits)",
            f"   Velocity: {velocity:.1f} commits/day",
        ]

        if risky:
            lines.append("   ⚠️ High-churn files:")
            for fc in risky:
                lines.append(
                    f"      {fc.path} (churn={fc.churn_rate:.0f}, "
                    f"authors={fc.authors}, commits={fc.commits})"
                )

        return "\n".join(lines)
