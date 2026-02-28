# PROOF: [L2/テスト] <- mekhane/basanos/ L2レベルのセマンティック/構造的品質検証が必要
# PURPOSE: kernel/ MD ファイルから HGK 概念を機械的に抽出する構造パーサー
# REASON: F⊣G 随伴の G_struct 部分 — YAML frontmatter, 定理テーブル, 定義を抽出
"""G_struct: Mechanical parser for kernel/ markdown files.

Extracts HGKConcept and ExternalForm from kernel/ documents
by parsing YAML frontmatter, theorem tables, and structural elements.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from mekhane.basanos.l2.models import ExternalForm, HGKConcept


class GStruct:
    """Structural parser for kernel/ markdown files.

    G_struct is the mechanical component of G = G_struct ∘ G_semantic.
    It extracts structured data from kernel/ docs without interpretation.
    """

    # Series identification from doc_id or path
    SERIES_PATTERNS = {
        "O": re.compile(r"(?:OUSIA|ousia|O[1-4])", re.IGNORECASE),
        "S": re.compile(r"(?:SCHEMA|schema|S[1-4])", re.IGNORECASE),
        "H": re.compile(r"(?:HORME|horme|H[1-4])", re.IGNORECASE),
        "P": re.compile(r"(?:PERIGRAPHE|perigraphe|P[1-4])", re.IGNORECASE),
        "K": re.compile(r"(?:KAIROS|kairos|K[1-4])", re.IGNORECASE),
        "A": re.compile(r"(?:AKRIBEIA|akribeia|A[1-4])", re.IGNORECASE),
    }

    # Theorem ID pattern: O1, S2, H3, P4, K1, A2 etc.
    THEOREM_ID_RE = re.compile(r"\b([OSHPKA][1-4])\b")

    # Claim patterns: blockquotes starting with **
    CLAIM_RE = re.compile(r"^>\s*\*\*[「「](.+?)[」」]\*\*", re.MULTILINE)

    def __init__(self, kernel_root: Path | str) -> None:
        self.kernel_root = Path(kernel_root)

    def parse_file(self, path: Path | str) -> Optional[HGKConcept]:
        """Parse a single kernel/ markdown file into HGKConcept."""
        path = Path(path)
        if not path.exists():
            return None

        text = path.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(text)
        body = self._strip_frontmatter(text)

        doc_id = frontmatter.get("doc_id", path.stem.upper())
        title = self._extract_title(body) or path.stem
        series = self._detect_series(doc_id, str(path))
        theorem_ids = self.THEOREM_ID_RE.findall(body)
        extends_raw = frontmatter.get("extends", {})
        extends = []
        if isinstance(extends_raw, dict):
            for v in extends_raw.values():
                if isinstance(v, list):
                    extends.extend(v)
                elif isinstance(v, str):
                    extends.append(v)
        elif isinstance(extends_raw, list):
            extends = extends_raw

        rel_path = str(path.relative_to(self.kernel_root.parent))

        return HGKConcept(
            doc_id=doc_id,
            path=rel_path,
            title=title,
            series=series or "?",
            theorem_ids=list(set(theorem_ids)),
            status=frontmatter.get("status", "UNKNOWN"),
            extends=extends,
        )

    def extract_external_form(self, path: Path | str) -> Optional[ExternalForm]:
        """Extract ExternalForm (G_struct output) from a kernel/ file.

        This is the mechanical part of G. Keywords, claims, dependencies
        are extracted structurally. G_semantic (LLM) would further translate
        HGK-specific terms to general academic terms.
        """
        path = Path(path)
        if not path.exists():
            return None

        text = path.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(text)
        body = self._strip_frontmatter(text)

        keywords = self._extract_keywords(body, frontmatter)
        claims = self.CLAIM_RE.findall(body)
        theorem_ids = list(set(self.THEOREM_ID_RE.findall(body)))
        mechanisms = self._extract_mechanisms(body)

        extends_raw = frontmatter.get("extends", {})
        dependencies = []
        if isinstance(extends_raw, dict):
            axioms = extends_raw.get("axioms", [])
            if isinstance(axioms, list):
                dependencies = axioms
        elif isinstance(extends_raw, list):
            dependencies = extends_raw

        rel_path = str(path.relative_to(self.kernel_root.parent))

        return ExternalForm(
            source_path=rel_path,
            keywords=keywords,
            mechanisms=mechanisms,
            claims=claims,
            dependencies=dependencies,
            theorem_ids=theorem_ids,
        )

    def scan_all(self) -> list[HGKConcept]:
        """Scan all kernel/ markdown files and return HGKConcepts."""
        concepts = []
        for md in sorted(self.kernel_root.glob("*.md")):
            concept = self.parse_file(md)
            if concept:
                concepts.append(concept)
        return concepts

    # --- Private helpers ---

    def _extract_frontmatter(self, text: str) -> dict:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            return {}
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _strip_frontmatter(self, text: str) -> str:
        """Remove YAML frontmatter from markdown."""
        return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)

    def _extract_title(self, body: str) -> Optional[str]:
        """Extract first H1 heading."""
        match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _detect_series(self, doc_id: str, path: str) -> Optional[str]:
        """Detect which series (O/S/H/P/K/A) a document belongs to."""
        combined = f"{doc_id} {path}"
        for series, pattern in self.SERIES_PATTERNS.items():
            if pattern.search(combined):
                return series
        return None

    def _extract_keywords(self, body: str, frontmatter: dict) -> list[str]:
        """Extract keywords from headings and bold terms."""
        keywords = []
        # H2/H3 headings
        for match in re.finditer(r"^#{2,3}\s+(.+)$", body, re.MULTILINE):
            heading = match.group(1).strip()
            # Remove markdown formatting
            heading = re.sub(r"[*_`]", "", heading)
            if heading and len(heading) < 60:
                keywords.append(heading)
        # Bold terms in definitions
        for match in re.finditer(r"\*\*(\w[\w\s]{2,30})\*\*", body):
            keywords.append(match.group(1).strip())
        return list(set(keywords))

    def _extract_mechanisms(self, body: str) -> list[str]:
        """Extract mechanism descriptions (implementation details)."""
        mechanisms = []
        # Look for implementation/realization sections
        in_impl = False
        for line in body.split("\n"):
            if re.match(r"^#{2,3}\s+.*(?:実装|実現|Implementation)", line, re.IGNORECASE):
                in_impl = True
                continue
            if in_impl and re.match(r"^#{1,3}\s+", line):
                in_impl = False
            if in_impl and line.strip().startswith("|") and "—" not in line:
                # Table row in implementation section
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2:
                    mechanisms.append(f"{cells[0]}: {cells[1]}")
        return mechanisms
