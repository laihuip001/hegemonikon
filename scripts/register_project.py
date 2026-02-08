#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- projects.yaml A0→新規PJの可視化が必要→register_project が担う
"""
Project Registration Script

新規プロジェクトを作成し、以下を自動実行する:
1. registry.yaml にエントリを追加
2. ディレクトリ作成 + PROOF.md + __init__.py
3. SKILL.md テンプレート生成 (オプション)

Usage:
    python scripts/register_project.py <id> <path> --name "表示名" --summary "説明" [--skill]
    python scripts/register_project.py dendron-v2 mekhane/dendron_v2/ --name "Dendron v2" --summary "EPT v2" --skill
"""

import argparse
import sys
from pathlib import Path
from datetime import date


PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / ".agent" / "projects" / "registry.yaml"
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"


def register_project(
    project_id: str,
    path: str,
    name: str,
    summary: str,
    status: str = "active",
    phase: str = "design",
    etymology: str = "",
    create_skill: bool = False,
    create_dir: bool = True,
) -> dict:
    """Register a new project in registry.yaml.

    Returns:
        dict: {"success": bool, "message": str, "actions": [str]}
    """
    actions = []

    # 1. Check registry exists
    if not REGISTRY_PATH.exists():
        return {"success": False, "message": f"Registry not found: {REGISTRY_PATH}", "actions": []}

    # 2. Check for duplicate ID
    import yaml
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    projects = data.get("projects", [])
    existing_ids = {p.get("id") for p in projects}
    if project_id in existing_ids:
        return {"success": False, "message": f"Project '{project_id}' already exists in registry", "actions": []}

    # 3. Create directory structure
    project_dir = PROJECT_ROOT / path.rstrip("/")
    if create_dir and not project_dir.exists():
        project_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Created directory: {project_dir}")

        # __init__.py
        init_file = project_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'# {name}\n"""{summary}"""\n', encoding="utf-8")
            actions.append(f"Created: {init_file}")

        # PROOF.md
        proof_file = project_dir / "PROOF.md"
        if not proof_file.exists():
            proof_content = f"""# PROOF: {project_dir.relative_to(PROJECT_ROOT)}

PURPOSE: {summary}
REASON: 新規 PJ として発足 ({date.today().isoformat()})

## 存在証明

このモジュールは [{name}] として registry.yaml に登録済み。
"""
            proof_file.write_text(proof_content, encoding="utf-8")
            actions.append(f"Created: {proof_file}")

    # 4. Add to registry.yaml
    new_entry = {
        "id": project_id,
        "name": name,
        "path": path,
        "summary": summary,
        "status": status,
        "phase": phase,
    }
    if etymology:
        new_entry["etymology"] = etymology
    new_entry["entry_point"] = None
    new_entry["usage_trigger"] = None

    # Append YAML entry (preserve formatting)
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")
    entry_yaml = f"""
  - id: {project_id}
    name: "{name}"
    path: "{path}"
    summary: "{summary}"
    status: "{status}"
    phase: "{phase}"
    entry_point: null
    usage_trigger: null
"""
    if etymology:
        entry_yaml = entry_yaml.replace(
            "    entry_point:",
            f'    etymology: "{etymology}"\n    entry_point:',
        )

    # Insert before the statistics comment
    if "# ─── 統計" in registry_text:
        registry_text = registry_text.replace("# ─── 統計", entry_yaml + "\n# ─── 統計")
    else:
        registry_text += entry_yaml

    REGISTRY_PATH.write_text(registry_text, encoding="utf-8")
    actions.append(f"Added to registry.yaml: {project_id}")

    # 5. Create SKILL.md template (optional)
    if create_skill:
        skill_dir = SKILLS_DIR / project_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            skill_content = f"""---
name: {name}
description: {summary}
triggers:
  - "{project_id}"
  - "{name.lower()}"
---

# {name}

> **目的**: {summary}

> [!CAUTION]
> このテンプレートは自動生成です。
> **以下の import パスを実際のコードと照合して検証してください。**
> 存在しないクラス名・関数名を書くと、Skill が機能しません。
> 検証コマンド: `PYTHONPATH=. .venv/bin/python -c "from {path.replace('/', '.').rstrip('.')} import YOUR_CLASS"`

## 発動条件

- TODO: トリガー条件を定義

## 手順

### Step 1: TODO — import パスを検証して書き換えること

// turbo

```bash
# FIXME: 以下は仮のコマンド。実際のモジュールに合わせて書き換えること
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
# TODO: import パスを実際のコードと照合
# from {path.replace('/', '.').rstrip('.')} import MAIN_CLASS
print('TODO: {project_id} の実行コマンドを定義')
"
```

---

*v1.0 — 自動生成 ({date.today().isoformat()})*
"""
            skill_md.write_text(skill_content, encoding="utf-8")
            actions.append(f"Created SKILL.md: {skill_md}")

    return {
        "success": True,
        "message": f"Project '{project_id}' registered successfully",
        "actions": actions,
    }


def main():
    parser = argparse.ArgumentParser(description="Register a new Hegemonikón project")
    parser.add_argument("id", help="Project ID (e.g., dendron-v2)")
    parser.add_argument("path", help="Relative path from project root (e.g., mekhane/dendron_v2/)")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--summary", required=True, help="One-line summary")
    parser.add_argument("--status", default="active", choices=["active", "dormant", "planned", "archived"])
    parser.add_argument("--phase", default="design", choices=["theory", "design", "implementation", "operational", "maintenance"])
    parser.add_argument("--etymology", default="", help="Greek etymology")
    parser.add_argument("--skill", action="store_true", help="Create SKILL.md template")
    parser.add_argument("--no-dir", action="store_true", help="Skip directory creation")

    args = parser.parse_args()

    result = register_project(
        project_id=args.id,
        path=args.path,
        name=args.name,
        summary=args.summary,
        status=args.status,
        phase=args.phase,
        etymology=args.etymology,
        create_skill=args.skill,
        create_dir=not args.no_dir,
    )

    if result["success"]:
        print(f"✅ {result['message']}")
        for action in result["actions"]:
            print(f"  → {action}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
