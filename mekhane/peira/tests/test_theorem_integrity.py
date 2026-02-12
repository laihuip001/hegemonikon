#!/usr/bin/env python3
# PROOF: [L2/検証] <- DX-008: THEOREM_WORKFLOWS バグ再発防止
"""
Theorem Integrity Tests — 定理テーブル整合性チェック

doctrine.md (正本) と theorem_activity.py のテーブルを照合し、
LLM 生成による定理名汚染を自動検出する。

BC-16 (参照先行義務) のプログラム的強制。
"""

import re
from pathlib import Path

import pytest

# --- Constants ---

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # hegemonikon/
DOCTRINE_PATH = PROJECT_ROOT / "kernel" / "doctrine.md"
WORKFLOWS_DIR = PROJECT_ROOT / ".agent" / "workflows"
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"

# Import the tables under test
import sys
sys.path.insert(0, str(PROJECT_ROOT))
from mekhane.peira.theorem_activity import (
    THEOREM_WORKFLOWS,
    HUB_EXPANSION,
    MACRO_EXPANSION,
    PERAS_WORKFLOWS,
)


# --- Doctrine Parser ---

def parse_adjunction_table(doctrine_path: Path) -> dict[str, str]:
    """
    doctrine.md の統一随伴表から正本マッピングを抽出。

    Returns:
        dict[wf_id, "SeriesNum Name"] e.g. {"noe": "O1 Noēsis", "bou": "O2 Boulēsis", ...}
    """
    content = doctrine_path.read_text(encoding="utf-8")

    # 統一随伴表のパターン:
    # | 1 | **noe ⊣ zet** (O1⊣O3) | ...
    # Each row has TWO theorems (F and G sides of adjunction)
    pattern = re.compile(
        r'\|\s*\d+\w?\s*\|'                     # | 1 | or | 0a |
        r'\s*\*\*(\w+)\s*⊣\s*(\w+)\*\*'         # **noe ⊣ zet**
        r'\s*\((\w\d)⊣(\w\d)\)',                 # (O1⊣O3)
        re.UNICODE
    )

    canonical: dict[str, str] = {}

    for match in pattern.finditer(content):
        wf_f, wf_g = match.group(1), match.group(2)
        series_f, series_g = match.group(3), match.group(4)

        # We need the full name. Extract from THEOREM_WORKFLOWS as cross-check,
        # but the series+number is the canonical identifier from doctrine.md
        canonical[wf_f] = series_f  # e.g. "noe" -> "O1"
        canonical[wf_g] = series_g  # e.g. "zet" -> "O3"

    return canonical


def parse_series_definitions(doctrine_path: Path) -> dict[str, str]:
    """
    doctrine.md の定理群テーブルから Series 名を抽出。

    Returns:
        dict[series_letter, series_name]  e.g. {"O": "Ousia", "S": "Schema", ...}
    """
    content = doctrine_path.read_text(encoding="utf-8")

    # | O | Ousia | 本質 |
    pattern = re.compile(
        r'\|\s*([OSHPKA])\s*\|\s*(\w+)\s*\|',
        re.UNICODE
    )

    series: dict[str, str] = {}
    for match in pattern.finditer(content):
        series[match.group(1)] = match.group(2)

    return series


# --- Fixtures ---

@pytest.fixture(scope="module")
def canonical_mapping():
    """doctrine.md から正本マッピングを取得"""
    assert DOCTRINE_PATH.exists(), f"doctrine.md not found: {DOCTRINE_PATH}"
    return parse_adjunction_table(DOCTRINE_PATH)


@pytest.fixture(scope="module")
def series_names():
    """doctrine.md から Series 名を取得"""
    return parse_series_definitions(DOCTRINE_PATH)


# --- Tests ---

class TestTheoremWorkflowsIntegrity:
    """THEOREM_WORKFLOWS テーブルの整合性検証"""

    def test_all_24_theorems_present(self):
        """24定理が全て定義されていること"""
        assert len(THEOREM_WORKFLOWS) == 24, (
            f"Expected 24 theorems, got {len(THEOREM_WORKFLOWS)}: "
            f"{sorted(THEOREM_WORKFLOWS.keys())}"
        )

    def test_wf_ids_match_doctrine(self, canonical_mapping):
        """WF ID が doctrine.md の統一随伴表と一致すること"""
        doctrine_ids = set(canonical_mapping.keys())
        table_ids = set(THEOREM_WORKFLOWS.keys())

        # doctrine.md にあるが THEOREM_WORKFLOWS にない
        missing_from_table = doctrine_ids - table_ids
        assert not missing_from_table, (
            f"doctrine.md に存在するが THEOREM_WORKFLOWS にない WF ID: {missing_from_table}"
        )

        # THEOREM_WORKFLOWS にあるが doctrine.md にない (= LLM 捏造の疑い)
        extra_in_table = table_ids - doctrine_ids
        assert not extra_in_table, (
            f"⚠️ THEOREM_WORKFLOWS に存在するが doctrine.md にない WF ID (BC-16 違反候補): "
            f"{extra_in_table}"
        )

    def test_series_numbers_match_doctrine(self, canonical_mapping):
        """定理の Series 番号 (O1, S2, ...) が doctrine.md と一致すること"""
        mismatches = []
        for wf_id, label in THEOREM_WORKFLOWS.items():
            if wf_id not in canonical_mapping:
                continue  # test_wf_ids_match_doctrine で検出済み

            # label format: "O1 Noēsis" -> series_num = "O1"
            series_num = label.split()[0]
            expected = canonical_mapping[wf_id]

            if series_num != expected:
                mismatches.append(
                    f"  /{wf_id}: table says '{series_num}', "
                    f"doctrine.md says '{expected}'"
                )

        assert not mismatches, (
            f"Series 番号の不一致 (定理名汚染の可能性):\n" +
            "\n".join(mismatches)
        )

    def test_series_coverage(self):
        """各 Series (O/S/H/P/K/A) に4つの定理が存在すること"""
        series_count: dict[str, int] = {}
        for label in THEOREM_WORKFLOWS.values():
            series_letter = label[0]
            series_count[series_letter] = series_count.get(series_letter, 0) + 1

        expected_series = {"O", "S", "H", "P", "K", "A"}
        assert set(series_count.keys()) == expected_series, (
            f"Series が不足: expected {expected_series}, got {set(series_count.keys())}"
        )

        for series, count in series_count.items():
            assert count == 4, (
                f"Series {series} has {count} theorems, expected 4"
            )

    def test_theorem_numbers_sequential(self):
        """各 Series 内で定理番号が 1-4 であること"""
        series_nums: dict[str, list[int]] = {}
        for label in THEOREM_WORKFLOWS.values():
            series_letter = label[0]
            num = int(label[1])
            series_nums.setdefault(series_letter, []).append(num)

        for series, nums in series_nums.items():
            assert sorted(nums) == [1, 2, 3, 4], (
                f"Series {series} has numbers {sorted(nums)}, expected [1, 2, 3, 4]"
            )


class TestWorkflowFilesExist:
    """WF ファイルの存在検証"""

    def test_all_theorem_wf_files_exist(self):
        """全24定理の WF ファイルが存在すること"""
        missing = []
        for wf_id in THEOREM_WORKFLOWS:
            wf_path = WORKFLOWS_DIR / f"{wf_id}.md"
            if not wf_path.exists():
                missing.append(f"/{wf_id} -> {wf_path}")

        assert not missing, (
            f"WF ファイルが存在しない定理:\n" +
            "\n".join(missing)
        )

    def test_all_peras_wf_files_exist(self):
        """全 Peras WF ファイルが存在すること"""
        missing = []
        for wf_id in PERAS_WORKFLOWS:
            wf_path = WORKFLOWS_DIR / f"{wf_id}.md"
            if not wf_path.exists():
                missing.append(f"/{wf_id} -> {wf_path}")

        assert not missing, (
            f"Peras WF ファイルが存在しない:\n" +
            "\n".join(missing)
        )


class TestHubExpansionIntegrity:
    """HUB_EXPANSION テーブルの整合性検証"""

    def test_hub_wf_ids_are_valid_theorems(self):
        """HUB_EXPANSION の展開先が全て THEOREM_WORKFLOWS に存在すること"""
        invalid = []
        for hub_id, sub_wfs in HUB_EXPANSION.items():
            for sub_wf in sub_wfs:
                if sub_wf not in THEOREM_WORKFLOWS:
                    invalid.append(
                        f"  HUB '{hub_id}' -> '{sub_wf}' "
                        f"(THEOREM_WORKFLOWS に存在しない)"
                    )

        assert not invalid, (
            f"HUB_EXPANSION に無効な WF ID:\n" +
            "\n".join(invalid)
        )

    def test_hub_covers_all_series(self):
        """各 Series Peras が対応する4定理を展開すること"""
        series_map = {"o": "O", "s": "S", "h": "H", "p": "P", "k": "K", "a": "A"}

        for hub_id, expected_series in series_map.items():
            assert hub_id in HUB_EXPANSION, f"HUB_EXPANSION に '{hub_id}' がない"
            expanded = HUB_EXPANSION[hub_id]

            # Check all expanded WFs belong to the expected series
            for wf_id in expanded:
                label = THEOREM_WORKFLOWS.get(wf_id, "")
                assert label.startswith(expected_series), (
                    f"HUB '{hub_id}' expanded to '{wf_id}' ({label}), "
                    f"but expected Series {expected_series}"
                )

            assert len(expanded) == 4, (
                f"HUB '{hub_id}' expands to {len(expanded)} theorems, expected 4"
            )

    def test_ax_covers_all_24(self):
        """/ax が全24定理を展開すること"""
        assert "ax" in HUB_EXPANSION
        ax_expanded = set(HUB_EXPANSION["ax"])
        all_theorems = set(THEOREM_WORKFLOWS.keys())

        missing = all_theorems - ax_expanded
        assert not missing, f"/ax が展開しない定理: {missing}"


class TestMacroExpansionIntegrity:
    """MACRO_EXPANSION テーブルの整合性検証"""

    def test_macro_wf_ids_are_valid_theorems(self):
        """MACRO_EXPANSION の展開先が全て THEOREM_WORKFLOWS に存在すること"""
        invalid = []
        for macro, sub_wfs in MACRO_EXPANSION.items():
            for sub_wf in sub_wfs:
                if sub_wf not in THEOREM_WORKFLOWS:
                    invalid.append(
                        f"  MACRO '@{macro}' -> '{sub_wf}' "
                        f"(THEOREM_WORKFLOWS に存在しない)"
                    )

        assert not invalid, (
            f"MACRO_EXPANSION に無効な WF ID (BC-16 違反候補):\n" +
            "\n".join(invalid)
        )

    def test_macro_definitions_not_empty(self):
        """全マクロが少なくとも1つの定理を展開すること"""
        empty = [m for m, wfs in MACRO_EXPANSION.items() if not wfs]
        assert not empty, f"空のマクロ定義: {empty}"


class TestSkillDirectoriesExist:
    """SKILL ディレクトリの存在検証"""

    SERIES_SKILL_DIRS = {
        "O": "ousia",
        "S": "schema",
        "H": "horme",
        "P": "perigraphe",
        "K": "kairos",
        "A": "akribeia",
    }

    def test_all_series_skill_dirs_exist(self):
        """全 Series の SKILL ディレクトリが存在すること"""
        missing = []
        for series, dirname in self.SERIES_SKILL_DIRS.items():
            skill_path = SKILLS_DIR / dirname
            if not skill_path.exists():
                missing.append(f"Series {series} -> {skill_path}")

        assert not missing, (
            f"SKILL ディレクトリが存在しない:\n" +
            "\n".join(missing)
        )


# --- Standalone runner ---

if __name__ == "__main__":
    print("=" * 60)
    print("定理テーブル整合性チェック")
    print("=" * 60)

    errors = []

    # 1. Parse doctrine.md
    if not DOCTRINE_PATH.exists():
        print(f"❌ doctrine.md not found: {DOCTRINE_PATH}")
        sys.exit(1)

    canonical = parse_adjunction_table(DOCTRINE_PATH)
    print(f"\n📖 doctrine.md から {len(canonical)} WF ID を抽出")

    # 2. Check THEOREM_WORKFLOWS
    print(f"\n--- THEOREM_WORKFLOWS ({len(THEOREM_WORKFLOWS)} entries) ---")

    table_ids = set(THEOREM_WORKFLOWS.keys())
    doctrine_ids = set(canonical.keys())

    missing = doctrine_ids - table_ids
    extra = table_ids - doctrine_ids

    if missing:
        msg = f"❌ doctrine.md にあるが THEOREM_WORKFLOWS にない: {missing}"
        print(msg)
        errors.append(msg)
    if extra:
        msg = f"⚠️ THEOREM_WORKFLOWS にあるが doctrine.md にない (LLM 捏造疑い): {extra}"
        print(msg)
        errors.append(msg)

    # Series number check
    for wf_id, label in THEOREM_WORKFLOWS.items():
        if wf_id in canonical:
            series_num = label.split()[0]
            expected = canonical[wf_id]
            if series_num != expected:
                msg = f"❌ /{wf_id}: '{series_num}' ≠ doctrine '{expected}'"
                print(msg)
                errors.append(msg)

    if not missing and not extra:
        print("✅ WF ID が doctrine.md と完全一致")

    # 3. Check WF files
    print(f"\n--- WF ファイル存在確認 ---")
    wf_missing = []
    for wf_id in THEOREM_WORKFLOWS:
        if not (WORKFLOWS_DIR / f"{wf_id}.md").exists():
            wf_missing.append(wf_id)

    if wf_missing:
        msg = f"❌ WF ファイルなし: {wf_missing}"
        print(msg)
        errors.append(msg)
    else:
        print("✅ 全24定理の WF ファイルが存在")

    # 4. Check HUB_EXPANSION
    print(f"\n--- HUB_EXPANSION ---")
    hub_invalid = []
    for hub_id, sub_wfs in HUB_EXPANSION.items():
        for sub_wf in sub_wfs:
            if sub_wf not in THEOREM_WORKFLOWS:
                hub_invalid.append(f"{hub_id} -> {sub_wf}")
    if hub_invalid:
        msg = f"❌ 無効な HUB 展開先: {hub_invalid}"
        print(msg)
        errors.append(msg)
    else:
        print("✅ HUB_EXPANSION の全展開先が THEOREM_WORKFLOWS に存在")

    # 5. Check MACRO_EXPANSION
    print(f"\n--- MACRO_EXPANSION ---")
    macro_invalid = []
    for macro, sub_wfs in MACRO_EXPANSION.items():
        for sub_wf in sub_wfs:
            if sub_wf not in THEOREM_WORKFLOWS:
                macro_invalid.append(f"@{macro} -> {sub_wf}")
    if macro_invalid:
        msg = f"❌ 無効なマクロ展開先: {macro_invalid}"
        print(msg)
        errors.append(msg)
    else:
        print("✅ MACRO_EXPANSION の全展開先が THEOREM_WORKFLOWS に存在")

    # Summary
    print(f"\n{'=' * 60}")
    if errors:
        print(f"❌ {len(errors)} 件のエラー")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("✅ 全チェック通過 — テーブル整合性に問題なし")
        sys.exit(0)
