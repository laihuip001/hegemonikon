#!/usr/bin/env python3
# PURPOSE: Generate domain-specific context files for Jules specialist reviews
"""
Generate Jules Context Files

Queries Sophia/Gnosis knowledge bases and generates markdown context files
in mekhane/symploke/context/ for automatic injection into specialist review prompts.

Usage:
    .venv/bin/python scripts/generate_jules_context.py [--themes THEME1,THEME2]
    .venv/bin/python scripts/generate_jules_context.py --list-themes
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = REPO_ROOT / "mekhane" / "symploke" / "context"

# Predefined themes with search queries
THEMES: dict[str, dict[str, str | list[str]]] = {
    "fep_foundation": {
        "title": "FEP Theoretical Foundation",
        "queries": [
            "free energy principle prediction error",
            "active inference variational",
            "precision weighting attention",
        ],
        "description": "Core FEP concepts that underpin the entire framework",
    },
    "design_patterns": {
        "title": "Design Patterns & Architecture",
        "queries": [
            "cognitive architecture design patterns",
            "domain specific language cognitive",
            "category theory software design",
        ],
        "description": "Architectural patterns used across the codebase",
    },
    "ccl_language": {
        "title": "CCL (Cognitive Control Language)",
        "queries": [
            "CCL cognitive control language",
            "workflow orchestration language",
            "domain specific language parser",
        ],
        "description": "The custom DSL for cognitive workflow orchestration",
    },
    "quality_assurance": {
        "title": "Quality Assurance & Testing",
        "queries": [
            "code quality assurance automated",
            "proof verification software",
            "testing cognitive systems",
        ],
        "description": "Quality assurance patterns including PROOF.md and Dendron",
    },
}


def search_sophia(query: str, limit: int = 3) -> list[dict]:
    """Search Sophia knowledge base via CLI."""
    try:
        result = subprocess.run(
            [
                str(REPO_ROOT / ".venv" / "bin" / "python"),
                "-m", "mekhane.anamnesis.cli",
                "search", query,
                "--limit", str(limit),
                "--format", "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def search_gnosis(query: str, limit: int = 3) -> list[dict]:
    """Search Gnosis paper database."""
    try:
        result = subprocess.run(
            [
                str(REPO_ROOT / ".venv" / "bin" / "python"),
                "-m", "mekhane.anamnesis.cli",
                "search", query,
                "--source", "gnosis",
                "--limit", str(limit),
                "--format", "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def generate_context_file(
    theme_id: str,
    theme: dict,
    output_dir: Path,
) -> Optional[Path]:
    """Generate a context markdown file for a given theme."""
    title = theme["title"]
    queries = theme["queries"]
    description = theme["description"]

    sections: list[str] = []
    sections.append(f"# {title}\n")
    sections.append(f"> {description}\n")
    sections.append(f"> Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Search knowledge bases
    all_results: list[dict] = []
    for query in queries:
        results = search_sophia(query, limit=2)
        all_results.extend(results)
        gnosis_results = search_gnosis(query, limit=2)
        all_results.extend(gnosis_results)

    if all_results:
        sections.append("## Key Knowledge Items\n")
        seen_titles: set[str] = set()
        for item in all_results:
            item_title = str(item.get("title") or item.get("name") or "Unknown")
            if item_title in seen_titles:
                continue
            seen_titles.add(item_title)
            score = item.get("score", 0)
            source = item.get("source", "unknown")
            raw_snippet = str(item.get("snippet") or item.get("abstract") or "")
            snippet = raw_snippet[:200]
            sections.append(f"- **{item_title}** (source: {source}, relevance: {score:.2f})")
            if snippet:
                sections.append(f"  > {snippet}")
            sections.append("")
    else:
        sections.append("## Notes\n")
        sections.append("No knowledge items found for this theme. Context is based on static definitions.\n")

    # Add theme-specific static content
    sections.append(f"## Relevance to Specialist Review\n")
    sections.append(f"When reviewing code related to {title.lower()}, consider:")
    sections.append(f"- Does the implementation align with the project's {description.lower()}?")
    sections.append(f"- Are there design principle violations (Reduced Complexity, Form Follows Function)?")
    sections.append(f"- Is the naming consistent with established patterns?")

    content = "\n".join(sections)
    output_path = output_dir / f"{theme_id}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def list_themes() -> None:
    """List available themes."""
    print("Available themes:")
    print()
    for theme_id, theme in THEMES.items():
        print(f"  {theme_id:20s} — {theme['title']}")
        print(f"  {'':20s}   {theme['description']}")
        print()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Jules context files")
    parser.add_argument(
        "--themes",
        type=str,
        default=None,
        help="Comma-separated theme IDs (default: all)",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(CONTEXT_DIR),
        help="Output directory (default: mekhane/symploke/context/)",
    )
    args = parser.parse_args()

    if args.list_themes:
        list_themes()
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    themes_to_generate = THEMES
    if args.themes:
        requested = [t.strip() for t in args.themes.split(",")]
        themes_to_generate = {k: v for k, v in THEMES.items() if k in requested}
        if not themes_to_generate:
            print(f"Error: No matching themes. Available: {', '.join(THEMES.keys())}")
            sys.exit(1)

    print(f"Generating context files in {output_dir}/")
    print(f"Themes: {', '.join(themes_to_generate.keys())}")
    print()

    generated: list[Path] = []
    for theme_id, theme in themes_to_generate.items():
        print(f"  [{theme_id}] {theme['title']}...", end=" ", flush=True)
        path = generate_context_file(theme_id, theme, output_dir)
        if path:
            generated.append(path)
            print(f"✅ {path.name}")
        else:
            print("❌ Failed")

    print(f"\nGenerated {len(generated)}/{len(themes_to_generate)} context files.")
    # Don't overwrite the manually curated hgk_knowledge.md
    print("Note: hgk_knowledge.md is manually maintained and not overwritten.")


if __name__ == "__main__":
    main()
