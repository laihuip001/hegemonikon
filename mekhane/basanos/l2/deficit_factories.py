# PROOF: [L2/Mekhane] <- mekhane/basanos/l2/deficit_factories.py Axiom->Reason->Module
# PURPOSE: 3種の deficit (η, ε, Δε/Δt) を検出するファクトリ群
# REASON: F⊣G 随伴構造の「破れ」を自動検出し、問いに変換するため
"""Deficit factories for Basanos L2.

Three factories detect structural discrepancies:
- EtaDeficitFactory: External knowledge not absorbed (η deficit)
- EpsilonDeficitFactory: HGK claims lacking impl/justification (ε deficit)
- DeltaDeficitFactory: Change-introduced discrepancies (Δε/Δt)
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mekhane.basanos.l2.g_struct import GStruct
from mekhane.basanos.l2.models import Deficit, DeficitType, ExternalForm, HGKConcept


# ---------------------------------------------------------------------------
# η deficit: What external knowledge has NOT been absorbed?
# ---------------------------------------------------------------------------


class EtaDeficitFactory:
    # PURPOSE: 外部知識の未吸収を検出する η deficit ファクトリ
    """Detect η deficit: external knowledge not absorbed into HGK.

    Compares Gnōsis papers against kernel/ concepts.
    If a paper's core concepts have no corresponding kernel/ definition,
    that's an η deficit — knowledge lost during /eat.
    """

    def __init__(self, g_struct: GStruct, project_root: Path | str) -> None:
        self.g_struct = g_struct
        self.project_root = Path(project_root)
        self._hgk_keywords: Optional[set[str]] = None

    def detect(self, paper_keywords: list[str], paper_title: str) -> list[Deficit]:
        # PURPOSE: 論文キーワードと HGK kernel/ を照合し、未吸収概念を deficit として返す
        """Detect η deficits by comparing paper keywords against HGK.

        Args:
            paper_keywords: Keywords from an external paper (via Gnōsis)
            paper_title: Title of the source paper

        Returns:
            List of Deficit objects for unabsorbed concepts
        """
        hgk_kw = self._get_hgk_keywords()
        deficits = []

        for kw in paper_keywords:
            kw_lower = kw.lower()
            # Check if any HGK keyword overlaps
            if not any(kw_lower in hk or hk in kw_lower for hk in hgk_kw):
                deficits.append(
                    Deficit(
                        type=DeficitType.ETA,
                        severity=0.5,  # Default; could be weighted by paper citation count
                        source=paper_title,
                        target=kw,
                        description=f"概念「{kw}」が HGK に未取り込み",
                        evidence=[f"論文: {paper_title}", f"キーワード: {kw}"],
                        suggested_action=f"/eat で「{kw}」を消化検討",
                    )
                )

        return deficits

    def _get_hgk_keywords(self) -> set[str]:
        """Cache and return all HGK keywords from kernel/."""
        if self._hgk_keywords is not None:
            return self._hgk_keywords

        keywords = set()
        kernel_root = self.project_root / "kernel"
        for md in kernel_root.glob("*.md"):
            ext_form = self.g_struct.extract_external_form(md)
            if ext_form:
                keywords.update(kw.lower() for kw in ext_form.keywords)
                keywords.update(tid.lower() for tid in ext_form.theorem_ids)

        self._hgk_keywords = keywords
        return keywords


# ---------------------------------------------------------------------------
# ε deficit: What HGK claims lack implementation or justification?
# ---------------------------------------------------------------------------


class EpsilonDeficitFactory:
    # PURPOSE: HGK の主張に実装/根拠がない ε deficit を検出するファクトリ
    """Detect ε deficit: HGK claims lacking implementation or justification.

    Two sub-types:
    - ε-impl: kernel/ definition exists but no PROOF.md / mekhane/ implementation
    - ε-just: kernel/ claim exists but no supporting paper in Gnōsis
    """

    # Map series to expected implementation directories
    IMPL_DIRS: dict[str, list[str]] = {
        "O": [".agent/workflows", ".agent/skills"],
        "S": [".agent/workflows", ".agent/skills", "mekhane/ergasterion", "mekhane/symploke"],
        "H": [".agent/workflows", ".agent/skills"],
        "P": ["mekhane/fep", ".agent/workflows"],
        "K": ["mekhane/anamnesis", "mekhane/basanos", ".agent/workflows"],
        "A": ["mekhane/basanos", "mekhane/fep", ".agent/workflows"],
    }

    # Fallback static mapping (used only if auto-detection fails)
    _FALLBACK_THEOREM_TO_WF: dict[str, list[str]] = {
        "O1": ["noe"], "O2": ["bou"], "O3": ["zet"], "O4": ["ene"],
        "S1": ["met"], "S2": ["mek"], "S3": ["sta"], "S4": ["pra"],
        "H1": ["pro"], "H2": ["pis"], "H3": ["ore"], "H4": ["dox"],
        "P1": ["kho"], "P2": ["hod"], "P3": ["tro"], "P4": ["tek"],
        "K1": ["euk"], "K2": ["chr"], "K3": ["tel"], "K4": ["sop"],
        "A1": ["pat"], "A2": ["dia"], "A3": ["gno"], "A4": ["epi"],
    }

    def __init__(self, g_struct: GStruct, project_root: Path | str) -> None:
        self.g_struct = g_struct
        self.project_root = Path(project_root)
        self.THEOREM_TO_WF = self._build_theorem_to_wf()

    def _build_theorem_to_wf(self) -> dict[str, list[str]]:
        """Auto-generate THEOREM_TO_WF from .agent/workflows/ frontmatter.

        Parses YAML frontmatter `modules: [X1, X2]` from each WF file
        and builds the theorem→WF basename mapping dynamically.
        Falls back to static dict if directory doesn't exist or parsing fails.
        """
        wf_dir = self.project_root / ".agent" / "workflows"
        if not wf_dir.is_dir():
            return dict(self._FALLBACK_THEOREM_TO_WF)

        mapping: dict[str, list[str]] = {}
        theorem_re = re.compile(r"^[OSHPKA][1-4]$")
        theorem_search_re = re.compile(r"\b([OSHPKA][1-4])\b")

        for wf_path in sorted(wf_dir.glob("*.md")):
            basename = wf_path.stem
            # Skip CCL macros and non-theorem WFs
            if basename.startswith("ccl-"):
                continue

            try:
                text = wf_path.read_text(encoding="utf-8")
                fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
                if not fm_match:
                    continue

                import yaml
                fm = yaml.safe_load(fm_match.group(1)) or {}

                # Source 1: modules: [X1, X2]
                modules = fm.get("modules", [])
                if isinstance(modules, list):
                    for mod in modules:
                        mod_str = str(mod).strip()
                        if theorem_re.match(mod_str):
                            if mod_str not in mapping:
                                mapping[mod_str] = []
                            if basename not in mapping[mod_str]:
                                mapping[mod_str].append(basename)

                # Source 2: hegemonikon: "K4 Sophia" → extract "K4"
                hgk_field = fm.get("hegemonikon", "")
                if isinstance(hgk_field, str):
                    hgk_match = theorem_search_re.search(hgk_field)
                    if hgk_match:
                        tid = hgk_match.group(1)
                        if tid not in mapping:
                            mapping[tid] = []
                        if basename not in mapping[tid]:
                            mapping[tid].append(basename)
            except Exception:
                continue

        # Merge with fallback for any missing theorems
        result = dict(self._FALLBACK_THEOREM_TO_WF)
        result.update(mapping)
        return result

    def detect_impl_deficits(self) -> list[Deficit]:
        # PURPOSE: kernel/ 定義に対応する WF/mekhane 実装の有無を検査
        """Detect ε-impl: kernel definitions without implementations."""
        deficits = []
        concepts = self.g_struct.scan_all()

        for concept in concepts:
            if concept.status != "CANONICAL":
                continue

            # Check each theorem individually
            unimplemented = []
            for tid in concept.theorem_ids:
                if self._has_implementation(tid, concept.series):
                    continue
                unimplemented.append(tid)

            if unimplemented:
                deficits.append(
                    Deficit(
                        type=DeficitType.EPSILON_IMPL,
                        severity=0.6,
                        source=concept.path,
                        target=", ".join(unimplemented),
                        description=(
                            f"{concept.title} の定理 {unimplemented} に"
                            f"実装/WF が見つからない"
                        ),
                        evidence=[
                            f"kernel path: {concept.path}",
                            f"series: {concept.series}",
                            f"実装済: {[t for t in concept.theorem_ids if t not in unimplemented]}",
                        ],
                        suggested_action=".agent/workflows/ か mekhane/ に実装が必要",
                    )
                )

        return deficits

    def _has_implementation(self, theorem_id: str, series: str) -> bool:
        """Check if a theorem has any implementation (WF, skill, or code)."""
        # 1. Check known WF mapping (fast, deterministic)
        wf_names = self.THEOREM_TO_WF.get(theorem_id, [])
        for wf_name in wf_names:
            wf_path = self.project_root / ".agent" / "workflows" / f"{wf_name}.md"
            if wf_path.exists():
                return True

        # 2. Check implementation directories via grep
        impl_dirs = self.IMPL_DIRS.get(series, [])
        for impl_dir in impl_dirs:
            impl_path = self.project_root / impl_dir
            if impl_path.exists() and self._find_reference(impl_path, theorem_id):
                return True

        return False

    def detect_justification_deficits(
        self, gnosis_keywords: set[str]
    ) -> list[Deficit]:
        # PURPOSE: kernel/ の主張に Gnōsis 論文による学術的根拠があるかを検査
        """Detect ε-justification: HGK claims without external support.

        Args:
            gnosis_keywords: Set of keywords from Gnōsis paper database

        Returns:
            List of justification deficits (flagged, not resolved)
        """
        deficits = []
        kernel_root = self.project_root / "kernel"

        for md in sorted(kernel_root.glob("*.md")):
            ext_form = self.g_struct.extract_external_form(md)
            if not ext_form:
                continue

            for claim in ext_form.claims:
                # Check if any gnosis keyword relates to this claim
                claim_words = set(claim.lower().split())
                overlap = claim_words & gnosis_keywords
                if not overlap:
                    deficits.append(
                        Deficit(
                            type=DeficitType.EPSILON_JUST,
                            severity=0.4,  # Flag only; resolution via /sop
                            source=ext_form.source_path,
                            target=claim,
                            description=f"主張「{claim[:50]}...」に Gnōsis の根拠なし",
                            evidence=[f"source: {ext_form.source_path}"],
                            suggested_action="/sop で学術的根拠を調査",
                        )
                    )

        return deficits

    def _find_reference(self, directory: Path, theorem_id: str) -> bool:
        """Check if a theorem ID is referenced in any file under directory."""
        try:
            result = subprocess.run(
                ["grep", "-rl", theorem_id, str(directory)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, OSError):
            return False


# ---------------------------------------------------------------------------
# Δε/Δt: What changes introduced new discrepancies?
# ---------------------------------------------------------------------------


class DeltaDeficitFactory:
    # PURPOSE: git 変更差分から構造的不整合を検出する Δε/Δt ファクトリ
    """Detect Δε/Δt: changes that introduce structural discrepancies.

    Uses git diff to find recent changes to kernel/ or mekhane/ files,
    then checks if those changes break consistency.
    """

    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root)

    def detect(self, since: str = "HEAD~5") -> list[Deficit]:
        # PURPOSE: 直近の git コミットから kernel/mekhane 間の不整合を検出
        """Detect change-induced deficits from recent git history.

        Args:
            since: Git revision range (default: last 5 commits)

        Returns:
            List of Δε/Δt deficits
        """
        deficits = []

        # Get changed kernel/ files
        kernel_changes = self._get_changed_files(since, "kernel/")
        mekhane_changes = self._get_changed_files(since, "mekhane/")

        # If kernel changed but mekhane didn't (or vice versa), flag it
        for kf in kernel_changes:
            series = self._detect_series_from_path(kf)
            if series:
                related_mekhane = [
                    mf for mf in mekhane_changes if self._is_related(series, mf)
                ]
                if not related_mekhane:
                    deficits.append(
                        Deficit(
                            type=DeficitType.DELTA,
                            severity=0.5,
                            source=kf,
                            target="mekhane/",
                            description=f"kernel/{kf} が変更されたが、対応する mekhane/ の更新がない",
                            evidence=[f"変更ファイル: kernel/{kf}", f"series: {series}"],
                            suggested_action="kernel の変更に合わせて実装を更新するか確認",
                        )
                    )

        return deficits

    def _get_changed_files(self, since: str, prefix: str) -> list[str]:
        """Get list of files changed since given revision under prefix."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    since,
                    "--",
                    prefix,
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=10,
            )
            return [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
        except (subprocess.TimeoutExpired, OSError):
            return []

    def _detect_series_from_path(self, path: str) -> Optional[str]:
        """Detect series from file path."""
        basename = Path(path).stem.lower()
        mapping = {
            "ousia": "O",
            "schema": "S",
            "horme": "H",
            "perigraphe": "P",
            "kairos": "K",
            "akribeia": "A",
        }
        for name, series in mapping.items():
            if name in basename:
                return series
        return None

    def _is_related(self, series: str, mekhane_path: str) -> bool:
        """Check if a mekhane path is related to a series."""
        related_dirs = EpsilonDeficitFactory.IMPL_DIRS.get(series, [])
        return any(mekhane_path.startswith(d) for d in related_dirs)
