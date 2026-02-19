#!/usr/bin/env python3
"""F0 CCL Processing Experiment.

ask_with_tools で Gemini にローカルファイルを読ませ、
CCL 式を処理させる実験。

Usage:
    cd ~/oikos/hegemonikon
    PYTHONPATH=. .venv/bin/python experiments/f0_ccl_test.py
"""
import sys
sys.path.insert(0, ".")

from mekhane.ochema.service import OchemaService


SYSTEM_INSTRUCTION = """あなたは Hegemonikón 認知ハイパーバイザーの CCL エンジンです。

## 実行手順
1. まず以下のファイルを read_file ツールで読んでください:
   - /home/makaron8426/oikos/hegemonikon/.agent/skills/ousia/o1-noesis/SKILL.md
   - /home/makaron8426/oikos/hegemonikon/.agent/rules/behavioral_constraints.md
   - /home/makaron8426/oikos/hegemonikon/.agent/rules/hegemonikon.md
2. 読み込んだ SKILL.md の PHASE 0-6 の出力テンプレートと Anti-Skip Protocol を内在化してください
3. 読み込んだ BC (Behavioral Constraints) を遵守してください
4. その上で、与えられた CCL 式を対象に対して実行してください

## 重要な制約
- 全出力は日本語
- 各 PHASE の出力テンプレートを省略しない
- 各セルは最低3行以上。1行で済ますのは禁止
- [CHECKPOINT PHASE X/6] を各フェーズ末尾に出力
- 省略禁止: 「詳細は省略」「要約すると」は使用禁止
"""

PROMPT = """以下の CCL 式を実行してください:

```
(/noe+)*%(/noe+^)
```

## CCL 演算子
- `/noe+` = O1 Noēsis 深層認識 (PHASE 0-6 全実行)
- `^` = メタ化 — 前の処理の前提自体を問う
- `*%` = FuseOuter — 収束(*) と展開(%) の同時実行

## 対象
「LLM が認知アーキテクチャのワークフローを実行するとき、
テンプレートの存在は出力品質を保証するか？
具体的には、PHASE 0-6 の出力テンプレートが存在しても、
各セルを1行で埋めて終わりにする省略行動が観察された。
テンプレートは「何を書くか」を制御するが
「どれだけ深く書くか」は制御しない。
この問題の本質と解決策は何か？」

まず上記のファイルを read_file で読んでから実行してください。
"""


def main():
    print("=" * 60)
    print("F0 CCL Processing Experiment")
    print("=" * 60)

    svc = OchemaService.get()

    print("\n[1] Sending CCL task with tool use...")
    print("    Model: gemini-2.5-pro")
    print("    Tools: read_file, list_directory, search_text")
    print("    Waiting for response (may take 60-120s)...\n")

    result = svc.ask_with_tools(
        message=PROMPT,
        model="gemini-2.5-pro",
        system_instruction=SYSTEM_INSTRUCTION,
        max_iterations=10,
        max_tokens=8192,
        timeout=120,
    )

    print(f"\n{'=' * 60}")
    print(f"Model: {result.model}")
    print(f"Tokens: {result.token_usage}")
    print(f"Response length: {len(result.text)} chars")
    print(f"{'=' * 60}\n")

    # Save result
    output_path = "/home/makaron8426/oikos/mneme/.hegemonikon/workflows/f0_ccl_result_20260218.md"
    with open(output_path, "w") as f:
        f.write(f"# F0 CCL Processing Result\n\n")
        f.write(f"> Model: {result.model}\n")
        f.write(f"> Tokens: {result.token_usage}\n")
        f.write(f"> CCL: `(/noe+)*%(/noe+^)`\n\n")
        f.write(result.text)

    print(f"Result saved to: {output_path}")
    print(f"\n--- Response Preview (first 2000 chars) ---\n")
    print(result.text[:2000])
    if len(result.text) > 2000:
        print(f"\n... ({len(result.text) - 2000} more chars)")


if __name__ == "__main__":
    main()
