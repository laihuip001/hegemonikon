#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→theorem_usage_scan
"""Theorem Usage Scanner — CCL マクロ/ワークフロー中の定理参照を計測する。

Usage:
    python scripts/theorem_usage_scan.py [--update-map]

定理活性化マップ (theorem_activation_map.md) のソースオブトゥルースとして、
.agent/workflows/ を横断スキャンし、各定理の CCL 参照数を集計する。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional

# ── 定理定義 ──

THEOREMS: dict[str, dict[str, str]] = {
    # O-series (Ousia)
    "O1": {"name": "Noēsis", "slug": "noe"},
    "O2": {"name": "Boulēsis", "slug": "bou"},
    "O3": {"name": "Zētēsis", "slug": "zet"},
    "O4": {"name": "Energeia", "slug": "ene"},
    # S-series (Schema)
    "S1": {"name": "Metron", "slug": "met"},
    "S2": {"name": "Mekhanē", "slug": "mek"},
    "S3": {"name": "Hodos", "slug": "hod"},  # Note: P2 is also Hodos
    "S4": {"name": "Praxis", "slug": "pra"},
    # H-series (Hormē)
    "H1": {"name": "Propatheia", "slug": "pro"},
    "H2": {"name": "Pistis", "slug": "pis"},
    "H3": {"name": "Orexis", "slug": "ore"},
    "H4": {"name": "Doxa", "slug": "dox"},
    # P-series (Perigraphē)
    "P1": {"name": "Stasis", "slug": "sta"},
    "P2": {"name": "Hodos", "slug": "hod"},
    "P3": {"name": "Trokhia", "slug": "tro"},
    "P4": {"name": "Tekhnē", "slug": "tek"},
    # K-series (Kairos)
    "K1": {"name": "Chronos", "slug": "chr"},
    "K2": {"name": "Khōra", "slug": "kho"},
    "K3": {"name": "Eukairia", "slug": "euk"},
    "K4": {"name": "Sophia", "slug": "sop"},
    # A-series (Akribeia)
    "A1": {"name": "Analogia", "slug": "ana"},
    "A2": {"name": "Krisis", "slug": "dia"},
    "A3": {"name": "Teleologia", "slug": "tel"},
    "A4": {"name": "Epistēmē", "slug": "epi"},
}


def scan_workflows(base_dir: Path) -> dict[str, list[str]]:
    """Scan workflow files for theorem references.

    Returns:
        dict mapping theorem_id -> list of referencing files
    """
    wf_dir = base_dir / ".agent" / "workflows"
    if not wf_dir.exists():
        print(f"⚠️ Workflow directory not found: {wf_dir}", file=sys.stderr)
        return {}

    refs: dict[str, list[str]] = defaultdict(list)

    for md_file in sorted(wf_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        for tid, info in THEOREMS.items():
            slug = info["slug"]
            name = info["name"]
            # Match patterns: /slug, /slug+, /slug-, slug in CCL expressions
            patterns = [
                rf"/{slug}[+\-]?\b",           # /noe, /noe+, /noe-
                rf"\b{tid}\b",                  # O1, S2, etc.
                rf"\b{name}\b",                 # Noēsis, Mekhanē, etc.
                rf"\b{name.lower()}\b",         # noēsis, mekhanē, etc.
                # Also match ASCII approximations
                rf"\b{_ascii_name(name)}\b",    # Noesis, Mekhane, etc.
            ]
            for pat in patterns:
                if re.search(pat, content, re.IGNORECASE):
                    if md_file.name not in refs[tid]:
                        refs[tid].append(md_file.name)
                    break

    return dict(refs)


def _ascii_name(name: str) -> str:
    """Convert Greek-accented name to ASCII approximation."""
    return (name
            .replace("ē", "e")
            .replace("ō", "o")
            .replace("ā", "a")
            .replace("ī", "i")
            .replace("ū", "u"))


def classify_activation(ref_count: int) -> str:
    """Classify theorem activation state."""
    if ref_count >= 3:
        return "active"
    elif ref_count >= 1:
        return "latent"
    else:
        return "dormant"


def print_report(refs: dict[str, list[str]]) -> None:
    """Print formatted activation report."""
    series_order = ["O", "S", "H", "P", "K", "A"]

    counts = {"active": 0, "latent": 0, "dormant": 0}

    print("# 定理活性化スキャン結果\n")
    print(f"| ID | Name | Status | Refs | Files |")
    print(f"|:---|:-----|:-------|-----:|:------|")

    for series in series_order:
        for i in range(1, 5):
            tid = f"{series}{i}"
            info = THEOREMS[tid]
            file_list = refs.get(tid, [])
            ref_count = len(file_list)
            status = classify_activation(ref_count)
            counts[status] += 1

            emoji = {"active": "🟢", "latent": "🟡", "dormant": "🔴"}[status]
            files_str = ", ".join(file_list[:3])
            if len(file_list) > 3:
                files_str += f" +{len(file_list) - 3}"

            print(f"| {tid} | {info['name']} | {emoji} {status} | {ref_count} | {files_str} |")

    print(f"\n## Summary")
    print(f"- 🟢 Active: {counts['active']}/24")
    print(f"- 🟡 Latent: {counts['latent']}/24")
    print(f"- 🔴 Dormant: {counts['dormant']}/24")


def update_map(refs: dict[str, list[str]], base_dir: Path) -> Optional[Path]:
    """Update theorem_activation_map.md with scan results."""
    map_path = base_dir / "mekhane" / "designs" / "theorem_activation_map.md"
    if not map_path.exists():
        print(f"⚠️ Activation map not found: {map_path}", file=sys.stderr)
        return None

    content = map_path.read_text(encoding="utf-8")

    # Add scan timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    scan_section = f"\n\n## 自動スキャン結果 ({timestamp})\n\n"
    scan_section += "| ID | Status | Refs |\n"
    scan_section += "|:---|:-------|-----:|\n"

    for series in ["O", "S", "H", "P", "K", "A"]:
        for i in range(1, 5):
            tid = f"{series}{i}"
            ref_count = len(refs.get(tid, []))
            status = classify_activation(ref_count)
            emoji = {"active": "🟢", "latent": "🟡", "dormant": "🔴"}[status]
            scan_section += f"| {tid} | {emoji} {status} | {ref_count} |\n"

    # Replace or append scan section
    marker = "## 自動スキャン結果"
    if marker in content:
        idx = content.index(marker)
        # Find next ## or end
        next_section = content.find("\n## ", idx + len(marker))
        if next_section == -1:
            content = content[:idx] + scan_section.strip() + "\n"
        else:
            content = content[:idx] + scan_section.strip() + "\n" + content[next_section:]
    else:
        content += scan_section

    map_path.write_text(content, encoding="utf-8")
    print(f"\n✅ Updated: {map_path}")
    return map_path


def main():
    base_dir = Path(__file__).resolve().parent.parent
    update = "--update-map" in sys.argv

    refs = scan_workflows(base_dir)
    print_report(refs)

    if update:
        update_map(refs, base_dir)


if __name__ == "__main__":
    main()
