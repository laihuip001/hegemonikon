#!/usr/bin/env python3
"""
bidirectional_linker.py — SE-6 Scalable Foundation実装

THEOREM_MAP (theorem_map.yaml) から全双方向リンクを生成。
新定理追加時はYAMLに1行追加 + このスクリプト実行で完了。
"""

import yaml
import re
from pathlib import Path

BASE_DIR = Path("/home/laihuip001/oikos/.agent")
WORKFLOWS_DIR = BASE_DIR / "workflows"
SKILLS_DIR = BASE_DIR / "skills"
MAP_FILE = BASE_DIR / "data/theorem_map.yaml"


def load_theorem_map() -> dict:
    """YAMLからマップ読込"""
    with open(MAP_FILE) as f:
        return yaml.safe_load(f)["theorems"]


def ensure_skill_ref_in_wf(wf_path: Path, skill_ref: str) -> bool:
    """WF frontmatter に skill_ref を追加/更新"""
    content = wf_path.read_text()
    
    # skill_ref が既にあるか確認
    if "skill_ref:" in content:
        # 既存の skill_ref を更新
        content = re.sub(
            r'skill_ref: .*',
            f'skill_ref: "{skill_ref}"',
            content
        )
    else:
        # frontmatter に追加 (version: の後に)
        content = re.sub(
            r'(version: "[^"]+"\n)',
            f'\\1skill_ref: "{skill_ref}"\n',
            content
        )
    
    wf_path.write_text(content)
    return True


def ensure_workflow_ref_in_skill(skill_path: Path, wf_ref: str) -> bool:
    """Skill frontmatter に workflow_ref を追加/更新"""
    content = skill_path.read_text()
    
    if "workflow_ref:" in content:
        content = re.sub(
            r'workflow_ref: .*',
            f'workflow_ref: "{wf_ref}"',
            content
        )
    else:
        # version: の後に追加
        content = re.sub(
            r'(version: "[^"]+"\n)',
            f'\\1workflow_ref: "{wf_ref}"\n',
            content
        )
    
    skill_path.write_text(content)
    return True


def verify_invariants(theorem_map: dict) -> list:
    """不変式検証"""
    errors = []
    
    for theorem_id, info in theorem_map.items():
        wf_path = WORKFLOWS_DIR / f"{info['wf']}.md"
        skill_path = SKILLS_DIR / info['skill'] / "SKILL.md"
        
        # WF存在確認
        if not wf_path.exists():
            errors.append(f"{theorem_id}: WF {wf_path} not found")
            continue
            
        # Skill存在確認
        if not skill_path.exists():
            errors.append(f"{theorem_id}: Skill {skill_path} not found")
            continue
        
        # 双方向リンク確認
        wf_content = wf_path.read_text()
        skill_content = skill_path.read_text()
        
        expected_skill_ref = f".agent/skills/{info['skill']}/SKILL.md"
        expected_wf_ref = f".agent/workflows/{info['wf']}.md"
        
        if expected_skill_ref not in wf_content and f"skills/{info['skill']}" not in wf_content:
            errors.append(f"{theorem_id}: WF missing skill_ref")
            
        if expected_wf_ref not in skill_content and f"/{info['wf']}" not in skill_content:
            errors.append(f"{theorem_id}: Skill missing workflow_ref")
    
    return errors


def generate_links():
    """メイン処理: 双方向リンク生成"""
    theorem_map = load_theorem_map()
    
    print("=== Bidirectional Link Generation ===")
    print(f"Theorems: {len(theorem_map)}")
    print()
    
    for theorem_id, info in theorem_map.items():
        wf_path = WORKFLOWS_DIR / f"{info['wf']}.md"
        skill_path = SKILLS_DIR / info['skill'] / "SKILL.md"
        
        skill_ref = f".agent/skills/{info['skill']}/SKILL.md"
        wf_ref = f".agent/workflows/{info['wf']}.md"
        
        if wf_path.exists():
            ensure_skill_ref_in_wf(wf_path, skill_ref)
            print(f"✅ {theorem_id}: WF → Skill")
        else:
            print(f"⚠️ {theorem_id}: WF not found")
            
        if skill_path.exists():
            ensure_workflow_ref_in_skill(skill_path, wf_ref)
            print(f"✅ {theorem_id}: Skill → WF")
        else:
            print(f"⚠️ {theorem_id}: Skill not found")
    
    print()
    print("=== Verification ===")
    errors = verify_invariants(theorem_map)
    
    if errors:
        print(f"⚠️ {len(errors)} issues found:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ All invariants satisfied!")
    
    return len(errors) == 0


if __name__ == "__main__":
    import sys
    success = generate_links()
    sys.exit(0 if success else 1)
