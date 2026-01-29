#!/usr/bin/env python3
"""
Workflow Inventory Generator

ワークフローの frontmatter から自動的に一覧表を生成する。
派生 (derivatives) の追加にも自動対応。

Usage:
    python workflow_inventory.py
    python workflow_inventory.py --output /path/to/output.md
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

WORKFLOWS_DIR = Path("/home/laihuip001/oikos/.agent/workflows")
DEFAULT_OUTPUT = Path("/home/laihuip001/oikos/hegemonikon/docs/workflow_inventory.md")


def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file."""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}
    return {}


def collect_workflows() -> list[dict]:
    """Collect all workflow metadata."""
    workflows = []
    for f in sorted(WORKFLOWS_DIR.glob("*.md")):
        fm = extract_frontmatter(f)
        workflows.append({
            "name": f.stem,
            "hegemonikon": fm.get("hegemonikon", ""),
            "modules": fm.get("modules", []),
            "derivatives": fm.get("derivatives", []),
            "version": fm.get("version", ""),
            "description": fm.get("description", ""),
            "children": fm.get("children", []),
        })
    return workflows


def categorize_workflows(workflows: list[dict]) -> dict[str, list]:
    """Categorize workflows by series."""
    categories = defaultdict(list)
    
    series_map = {
        "Ousia": "O-series",
        "Schema": "S-series",
        "Hormē": "H-series",
        "Perigraphē": "P-series",
        "Kairos": "K-series",
        "Akribeia": "A-series",
    }
    
    for wf in workflows:
        heg = wf["hegemonikon"]
        if not heg:
            categories["Utils"].append(wf)
        elif "," in heg:  # Multiple series
            categories["Utils"].append(wf)
        elif heg in series_map:
            categories[series_map[heg]].append(wf)
        else:
            categories["Other"].append(wf)
    
    # Special handling for X-series
    for wf in workflows:
        if wf["name"] in ["x", "ax"]:
            categories["X-series"].append(wf)
            # Remove from other categories
            for cat in list(categories.keys()):
                if cat != "X-series":
                    categories[cat] = [w for w in categories[cat] if w["name"] != wf["name"]]
    
    return dict(categories)


def count_derivatives(workflows: list[dict]) -> tuple[int, dict]:
    """Count total derivatives and by theorem."""
    total = 0
    by_theorem = {}
    
    for wf in workflows:
        derivs = wf["derivatives"]
        if isinstance(derivs, list) and derivs:
            total += len(derivs)
            modules = wf["modules"]
            if modules:
                key = modules[0] if isinstance(modules, list) else str(modules)
                by_theorem[key] = derivs
        elif isinstance(derivs, dict):
            # Hub format like /o.md
            for key, val in derivs.items():
                if isinstance(val, list):
                    total += len(val)
                    by_theorem[key] = val
    
    return total, by_theorem


def generate_markdown(workflows: list[dict], categories: dict, derivatives_info: tuple) -> str:
    """Generate markdown inventory."""
    total_derivs, by_theorem = derivatives_info
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        "# Hegemonikón ワークフロー一覧",
        "",
        f"> **自動生成**: {now}",
        f"> **総ワークフロー数**: {len(workflows)}",
        f"> **派生付きワークフロー**: {len([w for w in workflows if w['derivatives']])}",
        f"> **総派生数**: {total_derivs}",
        "",
        "---",
        "",
    ]
    
    # Series order
    series_order = ["O-series", "S-series", "H-series", "P-series", "K-series", "A-series", "X-series", "Utils"]
    
    for series in series_order:
        if series not in categories or not categories[series]:
            continue
        
        lines.append(f"## {series}")
        lines.append("")
        lines.append("| Workflow | Module | 派生 | Version |")
        lines.append("|:---------|:-------|:-----|:--------|")
        
        for wf in sorted(categories[series], key=lambda x: x["name"]):
            name = f"`/{wf['name']}`"
            modules = ", ".join(wf["modules"]) if wf["modules"] else "—"
            derivs = ", ".join(wf["derivatives"]) if isinstance(wf["derivatives"], list) and wf["derivatives"] else "—"
            version = wf["version"] or "—"
            lines.append(f"| {name} | {modules} | {derivs} | {version} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Derivatives matrix
    if by_theorem:
        lines.append("## 派生マトリクス")
        lines.append("")
        lines.append("| 定理 | 派生1 | 派生2 | 派生3 |")
        lines.append("|:-----|:------|:------|:------|")
        
        for theorem in sorted(by_theorem.keys()):
            derivs = by_theorem[theorem]
            row = [f"**{theorem}**"]
            for i in range(3):
                row.append(derivs[i] if i < len(derivs) else "—")
            lines.append("| " + " | ".join(row) + " |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Statistics
    lines.append("## 統計")
    lines.append("")
    lines.append("| カテゴリ | 数 |")
    lines.append("|:---------|:---|")
    
    for series in series_order:
        if series in categories:
            lines.append(f"| {series} | {len(categories[series])} |")
    
    lines.append(f"| **合計** | **{len(workflows)}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Auto-generated by workflow_inventory.py*")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate workflow inventory")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                        help="Output file path")
    args = parser.parse_args()
    
    print(f"📂 Scanning: {WORKFLOWS_DIR}")
    workflows = collect_workflows()
    print(f"   Found {len(workflows)} workflows")
    
    categories = categorize_workflows(workflows)
    derivatives_info = count_derivatives(workflows)
    
    markdown = generate_markdown(workflows, categories, derivatives_info)
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"✅ Generated: {args.output}")
    
    # Summary
    print(f"\n📊 Summary:")
    for cat, wfs in sorted(categories.items()):
        print(f"   {cat}: {len(wfs)}")
    print(f"   Derivatives: {derivatives_info[0]}")


if __name__ == "__main__":
    main()
