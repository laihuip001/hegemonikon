"""CCL マクロの定理含有テスト。

各 CCL マクロが期待されるワークフロー (定理) を含んでいるかを検証する。
theorem_activation_map の実行可能なソースオブトゥルースとして機能する。
"""

from __future__ import annotations

import re
from pathlib import Path
import pytest

# ── 基本設定 ──

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".agent" / "workflows"

# ── 期待テーブル: CCL マクロ → 含まれるべき定理スラグ ──

EXPECTED_THEOREMS: dict[str, list[str]] = {
    "ccl-plan.md": ["bou", "chr", "hod", "pis", "dox", "dia"],
    "ccl-build.md": ["bou", "met", "tek", "ene", "dia", "dox"],
    "ccl-fix.md": ["kho", "tel", "tek", "dia", "ene", "pis", "dox"],
    "ccl-dig.md": ["pro", "met", "ana", "dia", "pis", "dox"],
    "ccl-rpr.md": ["tro"],
    "ccl-chew.md": ["pro", "pis", "dox"],
    "ccl-helm.md": ["pro", "kho", "bou", "zet", "pis", "dox"],
    "ccl-ready.md": ["bou", "pat", "pro", "kho", "chr", "euk", "pis", "dox"],
    "ccl-vet.md": ["kho", "sta", "dia", "ene", "pra", "tek", "pis", "dox"],
    "ccl-syn.md": ["kho", "pro", "dia", "noe", "pis", "dox"],
    "ccl-kyc.md": ["pro", "sop", "noe", "ene", "dia", "pis", "dox"],
    "ccl-nous.md": ["pro", "noe", "dia", "pis", "dox"],
    "ccl-learn.md": ["pro", "dox", "noe", "dia", "pis"],
    "ccl-read.md": ["pro", "noe", "dia", "ore", "pis", "dox"],
    "ccl-tak.md": ["sta", "chr", "kho", "zet", "sop", "euk", "bou"],
    "ccl-proof.md": ["noe", "dia", "ene"],
}


def _file_contains_slug(content: str, slug: str) -> bool:
    """Check if content references a workflow slug (e.g. /noe, /noe+, /noe-)."""
    # Match /slug in various CCL contexts:
    #   /slug, /slug+, /slug-, /slug_, /slug}, /slug), /slug*
    #   standalone slug as word
    patterns = [
        rf"/{slug}[+\-*_}}\)]",   # /noe_, /noe+, /noe}, /noe)
        rf"/{slug}\b",             # /noe at word boundary
        rf"/{slug}$",              # /noe at end of line
        rf"\b{slug}\b",            # standalone slug
    ]
    for pat in patterns:
        if re.search(pat, content, re.IGNORECASE | re.MULTILINE):
            return True
    return False


# PURPOSE: CCL マクロファイルの定理含有検証。
class TestCCLTheorems:
    """CCL マクロファイルの定理含有検証。"""

    # PURPOSE: Ensure workflow directory exists
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure workflow directory exists."""
        assert WORKFLOWS_DIR.exists(), f"Workflows dir not found: {WORKFLOWS_DIR}"

    # PURPOSE: 各 CCL マクロが期待する定理を含んでいるか。
    @pytest.mark.parametrize("macro_file,expected_slugs", list(EXPECTED_THEOREMS.items()))
    def test_ccl_contains_expected_theorems(self, macro_file: str, expected_slugs: list[str]):
        """各 CCL マクロが期待する定理を含んでいるか。"""
        fpath = WORKFLOWS_DIR / macro_file
        if not fpath.exists():
            pytest.skip(f"File not found: {macro_file}")

        content = fpath.read_text(encoding="utf-8")
        missing = []
        for slug in expected_slugs:
            if not _file_contains_slug(content, slug):
                missing.append(slug)

        assert not missing, (
            f"{macro_file} is missing expected theorems: {missing}"
        )

    # PURPOSE: 期待テーブルの全ファイルが存在するか。
    def test_all_macro_files_exist(self):
        """期待テーブルの全ファイルが存在するか。"""
        missing_files = []
        for fname in EXPECTED_THEOREMS:
            if not (WORKFLOWS_DIR / fname).exists():
                missing_files.append(fname)
        assert not missing_files, f"Missing CCL macro files: {missing_files}"

    # PURPOSE: 期待テーブルに空リストがないか。
    def test_no_empty_macro_expectations(self):
        """期待テーブルに空リストがないか。"""
        for fname, slugs in EXPECTED_THEOREMS.items():
            assert len(slugs) > 0, f"{fname} has empty expected theorems"


# ── 逆方向テスト: 定理 → CCL マクロ ──

# 全24定理のスラグ (6 Series × 4)
ALL_24_THEOREMS: dict[str, str] = {
    # O-series
    "noe": "O1 Noēsis",
    "bou": "O2 Boulēsis",
    "zet": "O3 Zētēsis",
    "ene": "O4 Energeia",
    # S-series
    "met": "S1 Metron",
    "mek": "S2 Mekhanē",
    "sta": "S3 Stathmos",
    "pra": "S4 Praxis",
    # H-series
    "pro": "H1 Propatheia",
    "pis": "H2 Pistis",
    "ore": "H3 Orexis",
    "dox": "H4 Doxa",
    # P-series
    "kho": "P1 Khōra",
    "hod": "P2 Hodos",
    "tro": "P3 Trokhia",
    "tek": "P4 Tekhnē",
    # K-series
    "euk": "K1 Eukairia",
    "chr": "K2 Chronos",
    "tel": "K3 Telos",
    "sop": "K4 Sophia",
    # A-series
    "pat": "A1 Pathos",
    "dia": "A2 Krisis",
    "gno": "A3 Gnōmē",
    "epi": "A4 Epistēmē",
}


# PURPOSE: 逆方向: 各定理が少なくとも1つのワークフローで使われているか。
class TestTheoremCoverage:
    """逆方向: 各定理が少なくとも1つのワークフローで使われているか。"""

    # PURPOSE: Ensure workflow directory exists and load all workflow contents
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure workflow directory exists and load all workflow contents."""
        assert WORKFLOWS_DIR.exists()
        self._all_wf_contents: dict[str, str] = {}
        for fpath in WORKFLOWS_DIR.glob("*.md"):
            self._all_wf_contents[fpath.name] = fpath.read_text(encoding="utf-8")

    # PURPOSE: 各定理が少なくとも1つのワークフローで参照されているか。
    @pytest.mark.parametrize("slug,theorem_name", list(ALL_24_THEOREMS.items()))
    def test_theorem_used_in_at_least_one_workflow(self, slug: str, theorem_name: str):
        """各定理が少なくとも1つのワークフローで参照されているか。"""
        found_in = []
        for fname, content in self._all_wf_contents.items():
            if _file_contains_slug(content, slug):
                found_in.append(fname)

        assert found_in, (
            f"{theorem_name} ({slug}) is not referenced in any workflow. "
            f"Checked {len(self._all_wf_contents)} files."
        )

    # PURPOSE: 24定理が全て定義されているか。
    def test_all_24_theorems_defined(self):
        """24定理が全て定義されているか。"""
        assert len(ALL_24_THEOREMS) == 24, (
            f"Expected 24 theorems, got {len(ALL_24_THEOREMS)}"
        )


# ── 注釈整合性テスト: WF 内の (XX Name) が kernel 定義と一致するか ──

# slug → theorem_id マッピング (category.py THEOREMS 準拠)
SLUG_TO_ID: dict[str, str] = {slug: name.split()[0] for slug, name in ALL_24_THEOREMS.items()}
# theorem_id → theorem_name マッピング
ID_TO_NAME: dict[str, str] = {name.split()[0]: " ".join(name.split()[1:]) for name in ALL_24_THEOREMS.values()}

# 注釈パターン: `/slug` ... (XX Name) の形式を検出
# 例: `/met` (S1 Metron), `/kho` (P1 Khōra)
_ANNOTATION_RE = re.compile(
    r"/(\w+)[`\s]*\(([A-Z]\d)\s+(\S+?)\)",
)


# PURPOSE: WF ファイル内の定理注釈 (XX Name) が kernel 定義と一致するか。
class TestAnnotationConsistency:
    """WF ファイル内の定理注釈 (XX Name) が kernel 定義と一致するか。"""

    # PURPOSE: Load all workflow files
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load all workflow files."""
        assert WORKFLOWS_DIR.exists()
        self._wf_annotations: list[tuple[str, int, str, str, str]] = []
        for fpath in sorted(WORKFLOWS_DIR.glob("*.md")):
            for i, line in enumerate(fpath.read_text(encoding="utf-8").splitlines(), 1):
                for m in _ANNOTATION_RE.finditer(line):
                    slug, tid, tname = m.group(1), m.group(2), m.group(3)
                    self._wf_annotations.append((fpath.name, i, slug, tid, tname))

    # PURPOSE: 注釈の定理ID (e.g. S1) がスラグ (e.g. met) と一致するか。
    def test_annotation_id_matches_slug(self):
        """注釈の定理ID (e.g. S1) がスラグ (e.g. met) と一致するか。"""
        mismatches = []
        for fname, line, slug, tid, tname in self._wf_annotations:
            if slug not in SLUG_TO_ID:
                continue  # 24定理外のスラグはスキップ
            expected_id = SLUG_TO_ID[slug]
            if tid != expected_id:
                mismatches.append(
                    f"{fname}:{line} — /{slug} annotated as ({tid} {tname}), "
                    f"expected ({expected_id} ...)"
                )
        assert not mismatches, (
            f"Theorem ID mismatches in annotations:\n" + "\n".join(mismatches)
        )

    # PURPOSE: 注釈の定理名 (e.g. Metron) が ID (e.g. S1) と一致するか。
    def test_annotation_name_matches_id(self):
        """注釈の定理名 (e.g. Metron) が ID (e.g. S1) と一致するか。"""
        mismatches = []
        for fname, line, slug, tid, tname in self._wf_annotations:
            if tid not in ID_TO_NAME:
                continue  # 24定理外の ID はスキップ
            expected_name = ID_TO_NAME[tid]
            if tname != expected_name:
                mismatches.append(
                    f"{fname}:{line} — ({tid} {tname}), "
                    f"expected ({tid} {expected_name})"
                )
        assert not mismatches, (
            f"Theorem name mismatches in annotations:\n" + "\n".join(mismatches)
        )

    # PURPOSE: 注釈が少なくとも1つ存在するか (テスト自体の健全性確認)。
    def test_annotations_found(self):
        """注釈が少なくとも1つ存在するか (テスト自体の健全性確認)。"""
        assert len(self._wf_annotations) > 0, (
            "No (XX Name) annotations found in workflow files"
        )

