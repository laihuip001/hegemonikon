#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: WF turbo ブロックから cone_builder を安全に呼び出すブリッジ
"""
Cone Bridge — WF turbo 環境変数ブリッジ

WF の turbo ブロック内で使用する。LLM が生成した定理出力を JSON 形式で
受け取り、cone_builder.converge() を呼び出して結果を表示する。

テンプレート変数 ${O1_OUT} のシェルクォーティング問題を回避する。

Usage (turbo block):
    cat <<'EOF' | PYTHONPATH=. .venv/bin/python scripts/cone_bridge.py --series O
    {"O1": "深い認識の出力", "O2": "意志の出力", "O3": "探求の出力", "O4": "行動の出力"}
    EOF

    # or with PW:
    cat <<'EOF' | PYTHONPATH=. .venv/bin/python scripts/cone_bridge.py --series O --pw "O1:0.5,O3:-0.5"
    {"O1": "output1", "O2": "output2", "O3": "output3", "O4": "output4"}
    EOF

    # or from file:
    PYTHONPATH=. .venv/bin/python scripts/cone_bridge.py --series O --file /tmp/outputs.json
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _parse_pw(pw_str: str) -> dict[str, float]:
    """Parse PW string: 'O1:0.5,O3:-0.5' → {'O1': 0.5, 'O3': -0.5}"""
    if not pw_str:
        return {}
    result = {}
    for pair in pw_str.split(","):
        pair = pair.strip()
        if ":" in pair:
            k, v = pair.split(":", 1)
            try:
                result[k.strip()] = float(v.strip())
            except ValueError:
                pass
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Cone Bridge — WF turbo env var bridge",
    )
    parser.add_argument(
        "--series", "-s",
        required=True,
        choices=["O", "S", "H", "P", "K", "A"],
        help="Series to build cone for",
    )
    parser.add_argument(
        "--pw",
        default="",
        help="Precision Weighting: 'O1:0.5,O3:-0.5'",
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="JSON file with theorem outputs (alternative to stdin)",
    )
    parser.add_argument(
        "--advise",
        action="store_true",
        help="Also run advise() and devil_attack() if needed",
    )
    args = parser.parse_args()

    # Read outputs from file or stdin
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            outputs = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("⚠️ No input. Pipe JSON to stdin or use --file.", file=sys.stderr)
            sys.exit(1)
        outputs = json.loads(raw)

    if not isinstance(outputs, dict) or not outputs:
        print("⚠️ Input must be a JSON dict: {\"O1\": \"...\", ...}", file=sys.stderr)
        sys.exit(1)

    # Build cone
    from mekhane.fep.category import Series
    from mekhane.fep.cone_builder import converge, describe_cone

    series = Series[args.series]
    pw = _parse_pw(args.pw) or None
    cone = converge(series, outputs, pw=pw)

    # Display
    print(describe_cone(cone))

    # Optional advise + devil_attack
    if args.advise:
        from mekhane.fep.cone_consumer import advise, devil_attack, format_advice_for_llm

        advice = advise(cone)
        print(f"\n### ConeAdvice")
        print(f"**Action**: {advice.action}")
        print(f"**Reason**: {advice.reason}")
        if advice.suggested_wf:
            print(f"**WF**: {advice.suggested_wf}")
        if advice.next_steps:
            for step in advice.next_steps:
                print(f"  - {step}")

        # Explanation Stack output
        print(f"\n### Explanation Stack")
        print(format_advice_for_llm(advice))

        if cone.needs_devil:
            attack = devil_attack(cone)
            print(f"\n### DevilAttack")
            print(f"**Summary**: {attack.attack_summary}")
            print(f"**Severity**: {attack.severity:.1f}")
            for i, ca in enumerate(attack.counterarguments, 1):
                print(f"  {i}. {ca}")
            print(f"\n**Resolution Paths**:")
            for rp in attack.resolution_paths:
                print(f"  - {rp}")


if __name__ == "__main__":
    main()
