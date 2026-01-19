�#!/usr/bin/env python3
"""
diagnose_error.py - Antigravity/Perplexity エラー診断スクリプト
Hegemonikón M5 Peira 連携用
"""

import os
import sys
from datetime import datetime

def diagnose():
    """エラー診断を実行"""
    print("=" * 50)
    print("Hegemonikón Error Diagnosis")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    checks = {
        "PERPLEXITY_API_KEY": os.environ.get("PERPLEXITY_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "ENV_FILE": os.path.exists(os.path.expanduser("~/.gemini/.env.local")),
    }
    
    print("\n[Environment Check]")
    for key, value in checks.items():
        if key.endswith("_KEY"):
            status = "✅ Set" if value else "❌ Not set"
        else:
            status = "✅ Exists" if value else "❌ Missing"
        print(f"  {key}: {status}")
    
    print("\n[Recommendations]")
    if not checks["PERPLEXITY_API_KEY"]:
        print("  - Set PERPLEXITY_API_KEY in ~/.gemini/.env.local")
    if not checks["ENV_FILE"]:
        print("  - Create ~/.gemini/.env.local with API keys")
    
    print("\n[Common Errors]")
    print("  - 429: Rate limit exceeded → Wait or use browser mode")
    print("  - Timeout: Increase read_timeout to 120s for deep research")
    print("  - Agent terminated: Check Output panel for details")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    diagnose()
�*cascade082?file:///C:/Users/raikh/.gemini/.agent/scripts/diagnose_error.py