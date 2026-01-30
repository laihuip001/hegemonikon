# PROOF: [L2/インフラ] S2→プロンプト言語が必要→prompt_lang_integrate が担う
#!/usr/bin/env python3
"""
prompt-lang Auto-Fire Integration
==================================

Integrates prompt-lang parser with AI workflow.
Called when AI generates a new prompt.

Usage:
    python prompt_lang_integrate.py generate <slug> <role> <goal> [--constraints <c1> <c2>...]
    python prompt_lang_integrate.py load <file>
    python prompt_lang_integrate.py list

Requirements:
    Python 3.10+
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import the parser
sys.path.insert(0, str(Path(__file__).parent))
from prompt_lang import Prompt, PromptLangParser, parse_file, validate_file


# Configuration
STAGING_DIR = Path(__file__).parent / "staging"
LIBRARY_DIR = Path(__file__).parent.parent / "library"


def generate_prompt(
    slug: str,
    role: str,
    goal: str,
    constraints: Optional[list[str]] = None,
    tools: Optional[dict[str, str]] = None,
    resources: Optional[dict[str, str]] = None,
    format_spec: Optional[str] = None,
    examples: Optional[list[dict]] = None
) -> tuple[Path, Prompt]:
    """
    Generate a new prompt-lang file and save to staging.
    
    Returns:
        Tuple of (file_path, parsed_prompt)
    """
    # Ensure staging directory exists
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{timestamp}_{slug}.prompt"
    filepath = STAGING_DIR / filename
    
    # Build prompt-lang content
    lines = [f"#prompt {slug}", ""]
    
    lines.append("@role:")
    lines.append(f"  {role}")
    lines.append("")
    
    lines.append("@goal:")
    lines.append(f"  {goal}")
    lines.append("")
    
    if constraints:
        lines.append("@constraints:")
        for c in constraints:
            lines.append(f"  - {c}")
        lines.append("")
    
    if tools:
        lines.append("@tools:")
        for name, desc in tools.items():
            lines.append(f"  - {name}: {desc}")
        lines.append("")
    
    if resources:
        lines.append("@resources:")
        for name, uri in resources.items():
            lines.append(f"  - {name}: {uri}")
        lines.append("")
    
    if format_spec:
        lines.append("@format:")
        for line in format_spec.split("\n"):
            lines.append(f"  {line}")
        lines.append("")
    
    if examples:
        lines.append("@examples:")
        for ex in examples:
            lines.append(f"  - input: {ex.get('input', '')}")
            lines.append(f"    output: {ex.get('output', '')}")
        lines.append("")
    
    # Write file
    content = "\n".join(lines)
    filepath.write_text(content, encoding="utf-8")
    
    # Parse and validate
    parser = PromptLangParser(content)
    prompt = parser.parse()
    
    return filepath, prompt


def load_prompt(filepath: str) -> dict:
    """
    Load and expand a prompt file.
    
    Returns:
        Dictionary with parsed data and expanded prompt.
    """
    prompt = parse_file(filepath)
    return {
        "parsed": prompt.to_dict(),
        "expanded": prompt.expand(),
        "valid": True
    }


def list_prompts() -> list[dict]:
    """
    List all prompts in staging and library.
    """
    prompts = []
    
    for dir_path, label in [(STAGING_DIR, "staging"), (LIBRARY_DIR, "library")]:
        if dir_path.exists():
            for f in dir_path.glob("*.prompt"):
                valid, msg = validate_file(str(f))
                prompts.append({
                    "name": f.stem,
                    "path": str(f),
                    "location": label,
                    "valid": valid,
                    "error": None if valid else msg
                })
    
    return prompts


class SkillAdapter:
    """Interface for Hegemonikon Skills (M-Series)."""
    
    @staticmethod
    def find_prompt(query: str, threshold: float = 0.5) -> list[dict]:
        """Find best matching prompts for a user query."""
        query = query.lower()
        terms = query.split()
        
        prompts = list_prompts()
        matched = []
        
        for p in prompts:
            if not p["valid"]:
                continue
            try:
                data = load_prompt(p["path"])
                content = json.dumps(data["parsed"]).lower()
                
                # Logic: Coverage of search terms
                hits = sum(1 for term in terms if term in content)
                score = hits / len(terms) if terms else 0.0
                
                if score >= threshold:
                    p["score"] = score
                    p["expanded"] = data["expanded"] # Include full prompt for skill
                    matched.append(p)
            except Exception:
                continue
        
        # Sort by score desc
        matched.sort(key=lambda x: x["score"], reverse=True)
        return matched

    @staticmethod
    def create_draft(slug: str, role: str, goal: str, **kwargs) -> str:
        """Create a new draft prompt from skill output."""
        filepath, _ = generate_prompt(slug, role, goal, **kwargs)
        return str(filepath)


def auto_fire_header(trigger: str, filename: str, purpose: str) -> str:
    """
    Generate auto-fire header for AI output.
    """
    return f"""[prompt-lang] Auto-generated
  Trigger: {trigger}
  File: {filename}
  Purpose: {purpose}"""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "generate":
        if len(sys.argv) < 5:
            print("Usage: prompt_lang_integrate.py generate <slug> <role> <goal>")
            sys.exit(1)
        
        slug = sys.argv[2]
        role = sys.argv[3]
        goal = sys.argv[4]
        
        # Parse optional constraints
        constraints = []
        if "--constraints" in sys.argv:
            idx = sys.argv.index("--constraints")
            constraints = sys.argv[idx + 1:]
        
        filepath, prompt = generate_prompt(slug, role, goal, constraints)
        
        print(auto_fire_header("explicit_request", filepath.name, goal[:50]))
        print(f"\nSaved to: {filepath}")
        print(f"\nExpanded prompt:\n{prompt.expand()}")
    
    elif command == "load":
        if len(sys.argv) < 3:
            print("Usage: prompt_lang_integrate.py load <file>")
            sys.exit(1)
        
        result = load_prompt(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "list":
        prompts = list_prompts()
        print(json.dumps(prompts, indent=2, ensure_ascii=False))

    elif command == "match":
        if len(sys.argv) < 3:
            print("Usage: prompt_lang_integrate.py match <query>")
            sys.exit(1)
        
        query = sys.argv[2].lower()
        terms = query.split()
        
        prompts = list_prompts()
        matched = []
        
        for p in prompts:
            if not p["valid"]:
                continue
            
            # Load prompt content for searching
            try:
                data = load_prompt(p["path"])
                content = json.dumps(data["parsed"]).lower()
                
                # Simple boolean AND search
                if all(term in content for term in terms):
                    # specific matched data
                    p["score"] = 1.0 # Placeholder
                    p["preview"] = data["parsed"].get("goal", "")[:100]
                    matched.append(p)
            except Exception:
                continue
        
        print(json.dumps(matched, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
