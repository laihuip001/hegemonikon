# PROOF: [L2/インフラ] <- mekhane/dendron/
"""
Dendron Reporter — レポート生成 v2

チェック結果をさまざまな形式で出力する。
v2: ORPHAN (親参照なし) の警告表示をサポート。
"""

from enum import Enum
from pathlib import Path
from typing import TextIO
import sys

from .checker import CheckResult, FileProof, DirProof, ProofStatus, ProofLevel


# PURPOSE: レポートの出力形式を定義する列挙型
class ReportFormat(Enum):
    """レポート形式"""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    CI = "ci"  # CI 向け最小出力


# PURPOSE: チェック結果を様々な形式で出力するメインクラス
class DendronReporter:  # noqa: AI-007
    """Dendron レポート生成器"""

    def __init__(self, output: TextIO = None):
        self.output = output or sys.stdout

    # PURPOSE: 指定形式に応じたレポート出力メソッドを振り分ける
    def report(self, result: CheckResult, format: ReportFormat = ReportFormat.TEXT):
        """レポートを出力"""
        if format == ReportFormat.TEXT:
            self._report_text(result)
        elif format == ReportFormat.MARKDOWN:
            self._report_markdown(result)
        elif format == ReportFormat.CI:
            self._report_ci(result)
        elif format == ReportFormat.JSON:
            self._report_json(result)

    def _report_text(self, result: CheckResult):  # noqa: AI-007
        """テキスト形式"""
        self._print("=" * 60)
        self._print("Dendron PROOF Check Report")
        self._print("=" * 60)
        self._print()

        # サマリー
        self._print(f"Total files: {result.total_files}")
        self._print(f"With proof:  {result.files_with_proof}")
        self._print(f"Orphan:      {result.files_orphan}")  # v2
        self._print(f"Missing:     {result.files_missing_proof}")
        self._print(f"Invalid:     {result.files_invalid_proof}")
        self._print(f"Exempt:      {result.files_exempt}")
        self._print(f"Coverage:    {result.coverage:.1f}%")

        # レベル統計
        if result.level_stats:
            stats = result.level_stats
            self._print(f"Levels:      L1:{stats.get('L1', 0)} | L2:{stats.get('L2', 0)} | L3:{stats.get('L3', 0)}")
        self._print()

        # ディレクトリ統計
        if result.dir_proofs:
            dirs_ok = sum(1 for d in result.dir_proofs if d.status == ProofStatus.OK)
            dirs_missing = sum(1 for d in result.dir_proofs if d.status == ProofStatus.MISSING)
            self._print(
                f"Directories: {len(result.dir_proofs)} total, {dirs_ok} with PROOF.md, {dirs_missing} missing"
            )
            self._print()

        # 問題のあるファイル
        if result.files_missing_proof > 0:
            self._print("-" * 40)
            self._print("Missing PROOF:")
            for f in result.file_proofs:
                if f.status == ProofStatus.MISSING:
                    self._print(f"  ❌ {f.path}")

        # 結果
        self._print()
        if result.is_passing:
            self._print("✅ PASS")
        else:
            self._print("❌ FAIL")

    def _report_markdown(self, result: CheckResult):
        """Markdown 形式"""
        self._print("# Dendron PROOF Check Report\n")

        # サマリーテーブル
        self._print("| Metric | Value |")
        self._print("|--------|-------|")
        self._print(f"| Total files | {result.total_files} |")
        self._print(f"| With proof | {result.files_with_proof} |")
        self._print(f"| Missing | {result.files_missing_proof} |")
        self._print(f"| Coverage | {result.coverage:.1f}% |")
        if result.level_stats:
            stats = result.level_stats
            self._print(f"| Levels | L1:{stats.get('L1', 0)} / L2:{stats.get('L2', 0)} / L3:{stats.get('L3', 0)} |")
        self._print()

        # 問題のあるファイル
        if result.files_missing_proof > 0:
            self._print("## Missing PROOF\n")
            for f in result.file_proofs:
                if f.status == ProofStatus.MISSING:
                    self._print(f"- `{f.path}`")
            self._print()

        # 結果
        if result.is_passing:
            self._print("**Result**: ✅ PASS")
        else:
            self._print("**Result**: ❌ FAIL")

    def _report_ci(self, result: CheckResult):
        """CI 向け最小出力 (v2: ORPHAN 警告対応)"""
        if result.is_passing:
            stats = result.level_stats
            level_str = f" (L1:{stats.get('L1', 0)}/L2:{stats.get('L2', 0)}/L3:{stats.get('L3', 0)})" if stats else ""
            orphan_str = f" ⚠️{result.files_orphan} orphan" if result.files_orphan > 0 else ""
            self._print(f"✅ Dendron: {result.coverage:.1f}% coverage{level_str}{orphan_str}")
        else:
            self._print(f"❌ Dendron: {result.files_missing_proof} files missing PROOF")
            for f in result.file_proofs:
                if f.status == ProofStatus.MISSING:
                    self._print(f"  {f.path}")

    def _report_json(self, result: CheckResult):
        """JSON 形式"""
        import json

        data = {
            "total_files": result.total_files,
            "files_with_proof": result.files_with_proof,
            "files_missing_proof": result.files_missing_proof,
            "files_invalid_proof": result.files_invalid_proof,
            "coverage": result.coverage,
            "is_passing": result.is_passing,
            "level_stats": result.level_stats,
            "missing_files": [
                str(f.path) for f in result.file_proofs if f.status == ProofStatus.MISSING
            ],
        }

        self._print(json.dumps(data, indent=2, ensure_ascii=False))

    def _print(self, text: str = ""):
        """出力"""
        print(text, file=self.output)
