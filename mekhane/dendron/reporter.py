# PROOF: [L2/インフラ] <- mekhane/dendron/
"""
Dendron Reporter — レポート生成 v3

チェック結果をさまざまな形式で出力する。
v2: ORPHAN (親参照なし) の警告表示をサポート。
v3: L2 Purpose 統計を全形式に統合。
"""

from enum import Enum
from pathlib import Path
from typing import TextIO
import sys

from .checker import CheckResult, FileProof, DirProof, ProofStatus, ProofLevel, FunctionProof, VariableProof


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

    # PURPOSE: DendronReporter の初期化 — レポートを出力
    def __init__(self, output: TextIO = None):
        self.output = output or sys.stdout

    # PURPOSE: 指定形式に応じたレポート出力メソッドを振り分ける
    def report(self, result: CheckResult, format: ReportFormat = ReportFormat.TEXT) -> None:
        """レポートを出力"""
        if format == ReportFormat.TEXT:
            self._report_text(result)
        elif format == ReportFormat.MARKDOWN:
            self._report_markdown(result)
        elif format == ReportFormat.CI:
            self._report_ci(result)
        elif format == ReportFormat.JSON:
            self._report_json(result)

    # PURPOSE: テキスト形式
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

        # L2 Purpose (v3)
        if result.total_functions > 0:
            self._print("-" * 40)
            self._print("L2 Purpose:")
            self._print(f"  OK:      {result.functions_with_purpose}")
            self._print(f"  Weak:    {result.functions_weak_purpose}")
            self._print(f"  Missing: {result.functions_missing_purpose}")
            purpose_total = result.functions_with_purpose + result.functions_missing_purpose
            if purpose_total > 0:
                pcov = result.functions_with_purpose / purpose_total * 100
                self._print(f"  Coverage: {pcov:.1f}%")
            self._print()

        # L3 Variable (v3.0)
        if result.total_checked_signatures > 0:
            self._print("-" * 40)
            self._print("L3 Variable:")
            self._print(f"  Type hints: {result.signatures_with_hints}/{result.total_checked_signatures}")
            if result.short_name_violations > 0:
                self._print(f"  Short names: {result.short_name_violations} violations")
            self._print()

        # EPT Matrix (v3.3)
        total_ept = result.total_structure_checks + result.total_function_nf_checks + result.total_verification_checks
        if total_ept > 0:
            ok_ept = result.structure_ok + result.function_nf_ok + result.verification_ok
            pct = (ok_ept / total_ept * 100)
            self._print("-" * 40)
            self._print("EPT Matrix:")
            self._print(f"  NF2 Structure:     {result.structure_ok}/{result.total_structure_checks}")
            self._print(f"  NF3 Function:      {result.function_nf_ok}/{result.total_function_nf_checks}")
            self._print(f"  BCNF Verification: {result.verification_ok}/{result.total_verification_checks}")
            self._print(f"  EPT Score:         {ok_ept}/{total_ept} ({pct:.0f}%)")
            self._print()

        if result.is_passing:
            self._print("✅ PASS")
        else:
            self._print("❌ FAIL")

    # PURPOSE: Markdown 形式
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

        # L2 Purpose (v3)
        if result.total_functions > 0:
            self._print()
            self._print("## L2 Purpose Quality\n")
            self._print("| Metric | Value |")
            self._print("|--------|-------|")
            self._print(f"| OK | {result.functions_with_purpose} |")
            self._print(f"| Weak | {result.functions_weak_purpose} |")
            self._print(f"| Missing | {result.functions_missing_purpose} |")
            purpose_total = result.functions_with_purpose + result.functions_missing_purpose
            if purpose_total > 0:
                pcov = result.functions_with_purpose / purpose_total * 100
                self._print(f"| Coverage | {pcov:.1f}% |")

        # L3 Variable (v3.0)
        if result.total_checked_signatures > 0:
            self._print()
            self._print("## L3 Variable Quality\n")
            self._print("| Metric | Value |")
            self._print("|--------|-------|")
            self._print(f"| Type hints | {result.signatures_with_hints}/{result.total_checked_signatures} |")
            if result.short_name_violations > 0:
                self._print(f"| Short names | {result.short_name_violations} violations |")

        # EPT Matrix (v3.3)
        total_ept = result.total_structure_checks + result.total_function_nf_checks + result.total_verification_checks
        if total_ept > 0:
            ok_ept = result.structure_ok + result.function_nf_ok + result.verification_ok
            pct = (ok_ept / total_ept * 100)
            self._print()
            self._print("## EPT Matrix\n")
            self._print("| Layer | OK | Total | Score |")
            self._print("|-------|---:|------:|------:|")
            nf2_pct = (result.structure_ok / result.total_structure_checks * 100) if result.total_structure_checks else 0
            nf3_pct = (result.function_nf_ok / result.total_function_nf_checks * 100) if result.total_function_nf_checks else 0
            bcnf_pct = (result.verification_ok / result.total_verification_checks * 100) if result.total_verification_checks else 0
            self._print(f"| NF2 Structure | {result.structure_ok} | {result.total_structure_checks} | {nf2_pct:.0f}% |")
            self._print(f"| NF3 Function | {result.function_nf_ok} | {result.total_function_nf_checks} | {nf3_pct:.0f}% |")
            self._print(f"| BCNF Verify | {result.verification_ok} | {result.total_verification_checks} | {bcnf_pct:.0f}% |")
            self._print(f"| **Total** | **{ok_ept}** | **{total_ept}** | **{pct:.0f}%** |")

    # PURPOSE: CI 向け最小出力 (v3: L2 Purpose 対応)
    def _report_ci(self, result: CheckResult):
        """CI 向け最小出力 (v3: L2 Purpose 対応)"""
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
        # L2 Purpose summary (v3)
        if result.total_functions > 0:
            self._print(f"   Purpose: {result.functions_with_purpose} ok, {result.functions_weak_purpose} weak, {result.functions_missing_purpose} missing")
        # L3 Variable summary (v3.0)
        if result.total_checked_signatures > 0:
            hint_cov = (result.signatures_with_hints / result.total_checked_signatures * 100) if result.total_checked_signatures > 0 else 100.0
            short_str = f", {result.short_name_violations} short" if result.short_name_violations > 0 else ""
            self._print(f"   TypeHints: {result.signatures_with_hints}/{result.total_checked_signatures} ({hint_cov:.0f}%){short_str}")
        # EPT Matrix summary (v3.3)
        total_ept = result.total_structure_checks + result.total_function_nf_checks + result.total_verification_checks
        if total_ept > 0:
            ok_ept = result.structure_ok + result.function_nf_ok + result.verification_ok
            pct = (ok_ept / total_ept * 100)
            nf2_str = f"NF2:{result.structure_ok}/{result.total_structure_checks}"
            nf3_str = f"NF3:{result.function_nf_ok}/{result.total_function_nf_checks}"
            bcnf_str = f"BCNF:{result.verification_ok}/{result.total_verification_checks}"
            self._print(f"   EPT: {ok_ept}/{total_ept} ({pct:.0f}%) [{nf2_str} {nf3_str} {bcnf_str}]")

    # PURPOSE: JSON 形式
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
            # v3: L2 Purpose
            "purpose": {
                "total": result.total_functions,
                "ok": result.functions_with_purpose,
                "weak": result.functions_weak_purpose,
                "missing": result.functions_missing_purpose,
            },
            # v3.0: L3 Variable
            "type_hints": {
                "total": result.total_checked_signatures,
                "ok": result.signatures_with_hints,
                "missing": result.signatures_missing_hints,
            },
            "short_name_violations": result.short_name_violations,
            # v3.3: EPT Matrix
            "ept": {
                "nf2": {"ok": result.structure_ok, "total": result.total_structure_checks},
                "nf3": {"ok": result.function_nf_ok, "total": result.total_function_nf_checks},
                "bcnf": {"ok": result.verification_ok, "total": result.total_verification_checks},
                "score": result.structure_ok + result.function_nf_ok + result.verification_ok,
                "total": result.total_structure_checks + result.total_function_nf_checks + result.total_verification_checks,
            },
        }

        self._print(json.dumps(data, indent=2, ensure_ascii=False))

    # PURPOSE: 出力
    def _print(self, text: str = ""):
        """出力"""
        print(text, file=self.output)
