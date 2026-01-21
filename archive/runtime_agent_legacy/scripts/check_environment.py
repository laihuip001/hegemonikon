#!/usr/bin/env python3
"""
check_environment.py - 環境設定チェックスクリプト
Hegemonikón M1 Aisthēsis 連携用
"""

import os
import sys

def check_env():
    """環境設定をチェック"""
    gemini_dir = os.path.expanduser("~/.gemini")
    
    required_files = [
        "GEMINI.md",
        ".env.local",
        ".agent/workflows/boot.md",
        ".agent/workflows/do.md",
        ".agent/skills/m1-aisthesis/SKILL.md",
    ]
    
    print("[Hegemonikón Environment Check]")
    print("-" * 40)
    
    all_ok = True
    for file in required_files:
        path = os.path.join(gemini_dir, file)
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        if not exists:
            all_ok = False
    
    print("-" * 40)
    if all_ok:
        print("✅ All checks passed!")
    else:
        print("❌ Some files missing. Run /boot to initialize.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(check_env())
