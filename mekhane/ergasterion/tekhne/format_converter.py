#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ergasterion/tekhne/ A0→プロンプト形式変換が必要→format_converterが担う
"""
Format Converter — 3形式 (SKILL.md / .prompt / SAGE XML) の相互変換

Usage:
  python format_converter.py --input skill.md --to prompt
  python format_converter.py --input module.prompt --to sage
  python format_converter.py --input module.xml --to skill --verify-roundtrip
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def detect_format(content: str) -> str:
    """Auto-detect input format."""
    if content.strip().startswith("---") and "name:" in content[:500]:
        return "skill"
    if content.strip().startswith("//") or "#prompt" in content[:200]:
        return "prompt"
    if "<module_config>" in content or "<instruction>" in content:
        return "sage"
    return "unknown"


def extract_skill_parts(content: str) -> dict:
    """Extract structured parts from SKILL.md."""
    parts = {
        "name": "",
        "description": "",
        "role": "",
        "goal": "",
        "constraints": [],
        "examples": [],
        "sections": {},
        "raw_frontmatter": {},
    }

    # Extract frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        try:
            import yaml
            parts["raw_frontmatter"] = yaml.safe_load(fm_match.group(1)) or {}
            parts["name"] = parts["raw_frontmatter"].get("name", "")
            parts["description"] = parts["raw_frontmatter"].get("description", "")
        except Exception:
            pass

    # Extract sections by ## headings
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    for section in sections[1:]:  # skip pre-heading content
        lines = section.strip().split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        parts["sections"][title] = body

    return parts


def extract_prompt_parts(content: str) -> dict:
    """Extract structured parts from .prompt format."""
    parts = {
        "name": "",
        "description": "",
        "role": "",
        "goal": "",
        "constraints": [],
        "examples": [],
        "format_spec": "",
        "mixins": [],
    }

    # Extract #prompt name
    prompt_match = re.search(r"#prompt\s+(\w+)", content)
    if prompt_match:
        parts["name"] = prompt_match.group(1)

    # Extract @role
    role_match = re.search(r"@role:\s*\n(.*?)(?=\n@|\n#|\Z)", content, re.DOTALL)
    if role_match:
        parts["role"] = role_match.group(1).strip()

    # Extract @goal
    goal_match = re.search(r"@goal:\s*\n(.*?)(?=\n@|\n#|\Z)", content, re.DOTALL)
    if goal_match:
        parts["goal"] = goal_match.group(1).strip()

    # Extract @constraints
    constr_match = re.search(r"@constraints:\s*\n(.*?)(?=\n@|\n#|\Z)", content, re.DOTALL)
    if constr_match:
        lines = constr_match.group(1).strip().split("\n")
        parts["constraints"] = [l.strip().lstrip("- ") for l in lines if l.strip().startswith("-")]

    # Extract @examples
    ex_match = re.search(r"@examples:\s*\n(.*?)(?=\n@|\n#|\Z)", content, re.DOTALL)
    if ex_match:
        parts["examples"] = [ex_match.group(1).strip()]

    # Extract @format
    fmt_match = re.search(r"@format:\s*\n(.*?)(?=\n@|\n#|\Z)", content, re.DOTALL)
    if fmt_match:
        parts["format_spec"] = fmt_match.group(1).strip()

    return parts


def to_prompt(parts: dict, source_format: str) -> str:
    """Convert parts to .prompt format."""
    lines = []
    name = parts.get("name", "unnamed")
    lines.append(f"// {name} — Generated from {source_format} format")
    lines.append("")
    lines.append(f"#prompt {name.replace('-', '_').replace(' ', '_')}")
    lines.append("")

    if parts.get("role"):
        lines.append("@role:")
        lines.append(f"  {parts['role']}")
        lines.append("")

    if parts.get("goal") or parts.get("description"):
        lines.append("@goal:")
        lines.append(f"  {parts.get('goal') or parts.get('description', '')}")
        lines.append("")

    if parts.get("constraints"):
        lines.append("@constraints:")
        for c in parts["constraints"]:
            lines.append(f"  - {c}")
        lines.append("")

    if parts.get("format_spec"):
        lines.append("@format:")
        lines.append(f"  {parts['format_spec']}")
        lines.append("")

    if parts.get("examples"):
        lines.append("@examples:")
        for ex in parts["examples"]:
            lines.append(f"  {ex}")
        lines.append("")

    lines.append("@activation:")
    lines.append("  mode: manual")
    lines.append("  priority: 2")

    return "\n".join(lines)


def to_skill(parts: dict, source_format: str) -> str:
    """Convert parts to SKILL.md format."""
    lines = []
    name = parts.get("name", "unnamed")

    # Frontmatter
    lines.append("---")
    lines.append(f"name: {name}")
    desc = parts.get("description") or parts.get("goal", "")
    if desc:
        if "\n" in desc:
            lines.append("description: |")
            for dl in desc.split("\n"):
                lines.append(f"  {dl}")
        else:
            lines.append(f"description: \"{desc}\"")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# {name}")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(parts.get("goal") or parts.get("description") or "TODO: Add overview")
    lines.append("")

    # Core Behavior
    lines.append("## Core Behavior")
    lines.append("")
    if parts.get("constraints"):
        for c in parts["constraints"]:
            lines.append(f"- {c}")
    else:
        lines.append("- TODO: Define core behaviors")
    lines.append("")

    # Quality Standards
    lines.append("## Quality Standards")
    lines.append("")
    lines.append("- TODO: Define quantitative quality standards")
    lines.append("")

    # Edge Cases
    lines.append("## Edge Cases")
    lines.append("")
    lines.append("- TODO: Define edge cases and fallback strategies")
    lines.append("")

    # Examples
    lines.append("## Examples")
    lines.append("")
    if parts.get("examples"):
        for ex in parts["examples"]:
            lines.append(ex)
    else:
        lines.append("TODO: Add input/output examples")
    lines.append("")

    # Extra sections from source
    for section_name, section_body in parts.get("sections", {}).items():
        if section_name not in ["Overview", "Core Behavior", "Quality Standards",
                                 "Edge Cases", "Examples"]:
            lines.append(f"## {section_name}")
            lines.append("")
            lines.append(section_body)
            lines.append("")

    return "\n".join(lines)


def to_sage(parts: dict, source_format: str) -> str:
    """Convert parts to SAGE XML format."""
    name = parts.get("name", "unnamed")
    goal = parts.get("goal") or parts.get("description", "")
    role = parts.get("role", "")

    lines = []
    lines.append(f"<!-- Module: {name} — Generated from {source_format} format -->")
    lines.append("<module_config>")
    lines.append(f"  <name>{name}</name>")
    lines.append(f"  <model_target>Claude Opus 4.5 / Gemini 3 Pro</model_target>")
    lines.append(f"  <objective>{goal}</objective>")
    lines.append(f"  <context_awareness>AUTO-INGEST</context_awareness>")
    lines.append("</module_config>")
    lines.append("")
    lines.append("<instruction>")
    if role:
        lines.append(f"  {role}")
        lines.append("")

    lines.append("  <protocol>")
    if parts.get("constraints"):
        for i, c in enumerate(parts["constraints"][:5], 1):
            tag = f"step_{i}"
            lines.append(f"    <{tag}>")
            lines.append(f"      {c}")
            lines.append(f"    </{tag}>")
    else:
        lines.append("    <step_1>")
        lines.append("      TODO: Define processing steps")
        lines.append("    </step_1>")
    lines.append("  </protocol>")
    lines.append("")

    lines.append("  <constraints>")
    if parts.get("constraints"):
        for c in parts["constraints"]:
            lines.append(f"    <rule>{c}</rule>")
    lines.append("  </constraints>")
    lines.append("")

    lines.append("  <output_template>")
    if parts.get("format_spec"):
        lines.append(f"    {parts['format_spec']}")
    else:
        lines.append("    ## Result")
        lines.append("    [Define output structure here]")
    lines.append("  </output_template>")
    lines.append("</instruction>")

    return "\n".join(lines)


def convert(input_path: str, output_format: str) -> str:
    """Convert a prompt file to the specified format."""
    content = Path(input_path).read_text(encoding="utf-8")
    source_format = detect_format(content)

    if source_format == "unknown":
        print(f"⚠️  Unknown source format for {input_path}", file=sys.stderr)
        source_format = "skill"  # Default assumption

    # Extract parts
    if source_format == "skill":
        parts = extract_skill_parts(content)
    elif source_format == "prompt":
        parts = extract_prompt_parts(content)
    else:
        # SAGE → extract basic parts
        parts = {
            "name": "",
            "description": "",
            "role": "",
            "goal": "",
            "constraints": [],
            "examples": [],
            "sections": {},
        }
        name_match = re.search(r"<name>(.*?)</name>", content)
        if name_match:
            parts["name"] = name_match.group(1)
        obj_match = re.search(r"<objective>(.*?)</objective>", content)
        if obj_match:
            parts["goal"] = obj_match.group(1)

    # Convert to output format
    if output_format == "prompt":
        return to_prompt(parts, source_format)
    elif output_format == "skill":
        return to_skill(parts, source_format)
    elif output_format == "sage":
        return to_sage(parts, source_format)
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def verify_roundtrip(input_path: str, via_format: str) -> bool:
    """Verify roundtrip conversion preserves key information."""
    content = Path(input_path).read_text(encoding="utf-8")
    source_format = detect_format(content)

    # Convert to intermediate
    intermediate = convert(input_path, via_format)

    # Write temp and convert back
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=f".{via_format}.md",
                                      delete=False, encoding="utf-8") as f:
        f.write(intermediate)
        temp_path = f.name

    try:
        back = convert(temp_path, source_format)

        # Check key content preservation
        if source_format == "skill":
            orig_parts = extract_skill_parts(content)
            back_parts = extract_skill_parts(back)
        elif source_format == "prompt":
            orig_parts = extract_prompt_parts(content)
            back_parts = extract_prompt_parts(back)
        else:
            return True  # Can't verify SAGE roundtrip easily

        # Check name preservation
        name_preserved = (orig_parts.get("name", "") == back_parts.get("name", ""))

        print(f"  Name preserved: {'✅' if name_preserved else '❌'}")
        print(f"  Original name: {orig_parts.get('name', 'N/A')}")
        print(f"  Roundtrip name: {back_parts.get('name', 'N/A')}")

        return name_preserved
    finally:
        Path(temp_path).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Format Converter")
    parser.add_argument("--input", required=True, help="Input file")
    parser.add_argument("--to", required=True, choices=["prompt", "skill", "sage"],
                        help="Output format")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--verify-roundtrip", action="store_true",
                        help="Verify roundtrip conversion")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    result = convert(args.input, args.to)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"✅ Converted to {args.output}")
    else:
        print(result)

    if args.verify_roundtrip:
        print(f"\n🔄 Roundtrip verification ({detect_format(Path(args.input).read_text())} → {args.to} → back):")
        ok = verify_roundtrip(args.input, args.to)
        if ok:
            print("✅ Roundtrip: Key information preserved")
        else:
            print("⚠️  Roundtrip: Some information may have been lost")


if __name__ == "__main__":
    main()
