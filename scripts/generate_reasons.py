#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/ O4→REASON自動生成が必要→generate_reasons が担う
"""
REASON Auto-Generator — LLM-based PROOF.md REASON field generation

PROOF.md に REASON フィールドが存在しない場合、
ディレクトリの内容・git 履歴・PURPOSE を参考に LLM で REASON を生成する。

Usage:
    # Dry-run (生成結果を表示のみ)
    python scripts/generate_reasons.py --dry-run

    # 実行 (PROOF.md に書き込み)
    python scripts/generate_reasons.py

    # 特定ファイル
    python scripts/generate_reasons.py --target kernel/PROOF.md
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ── Constants ──

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REASON_PATTERN = re.compile(r"(?:#\s*)?REASON:\s*(.+)")
PURPOSE_PATTERN = re.compile(r"(?:#\s*)?PURPOSE:\s*(.+)")


def find_proofs_without_reason(root: Path) -> list[Path]:
    """REASON が存在しない PROOF.md を検索する"""
    missing = []
    for proof_path in sorted(root.rglob("PROOF.md")):
        # .venv, __pycache__, .git を除外
        if any(part.startswith(".") or part == "__pycache__" or part == ".venv"
               for part in proof_path.parts):
            continue
        content = proof_path.read_text(encoding="utf-8")
        if not REASON_PATTERN.search(content):
            missing.append(proof_path)
    return missing


def gather_context(proof_path: Path) -> dict:
    """REASON 生成のためのコンテキストを収集する"""
    dir_path = proof_path.parent
    rel_dir = dir_path.relative_to(PROJECT_ROOT)

    # 1. PROOF.md の内容
    proof_content = proof_path.read_text(encoding="utf-8")

    # 2. PURPOSE 抽出
    purpose_match = PURPOSE_PATTERN.search(proof_content)
    purpose = purpose_match.group(1).strip() if purpose_match else ""

    # 3. ディレクトリ内のファイル一覧
    files = []
    for f in sorted(dir_path.iterdir()):
        if f.name.startswith(".") or f.name == "__pycache__":
            continue
        ftype = "dir" if f.is_dir() else "file"
        files.append(f"{ftype}: {f.name}")

    # 4. Git 初回コミット情報
    try:
        git_result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H %ai %s",
             "--", str(rel_dir)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=5,
        )
        git_lines = git_result.stdout.strip().split("\n")
        first_commit = git_lines[-1] if git_lines and git_lines[-1] else ""
    except Exception:
        first_commit = ""

    # 5. README.md があれば要約
    readme_path = dir_path / "README.md"
    readme_excerpt = ""
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        # 最初の200文字
        readme_excerpt = readme_text[:300].strip()

    return {
        "dir": str(rel_dir),
        "proof_content": proof_content[:500],
        "purpose": purpose,
        "files": "\n".join(files[:15]),
        "first_commit": first_commit,
        "readme": readme_excerpt,
    }


def build_prompt(ctx: dict) -> str:
    """LLM に送るプロンプトを構築する"""
    return f"""あなたは Hegemonikón プロジェクトの所属ディレクトリの「経緯」を記述するアシスタントです。

以下の情報から、このディレクトリがなぜ存在するのかの「経緯 (REASON)」を1行で生成してください。

## ルール
- 「〜する必要があった」「〜が不在だった」などの過去形で書く
- 技術的に正確に、だが簡潔に（60文字以内目標）
- PURPOSE（目的）とは異なる視点: WHYの背景を書く
- 日本語で書く

## ディレクトリ情報
- パス: {ctx['dir']}/
- PURPOSE: {ctx['purpose'] or '(未定義)'}
- ファイル一覧:
{ctx['files']}

## PROOF.md 冒頭:
{ctx['proof_content'][:300]}

## README 抜粋:
{ctx['readme'][:200] or '(なし)'}

## Git 初回コミット:
{ctx['first_commit'] or '(不明)'}

## 出力形式
REASON: (ここに1行で記述)"""


def generate_reason_llm(prompt: str, model_name: str = "Qwen/Qwen2.5-7B-Instruct") -> str:
    """ローカル LLM で REASON を生成する"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError:
        print("ERROR: transformers not installed")
        sys.exit(1)

    # グローバルキャッシュでモデル再利用
    if not hasattr(generate_reason_llm, "_model"):
        print(f"Loading model: {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        generate_reason_llm._model = model
        generate_reason_llm._tokenizer = tokenizer
        print("Model loaded.")

    model = generate_reason_llm._model
    tokenizer = generate_reason_llm._tokenizer

    messages = [
        {"role": "system", "content": "あなたはコードベースの経緯を記述する専門家です。簡潔に日本語で回答してください。"},
        {"role": "user", "content": prompt},
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
        )

    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    # REASON: 行を抽出
    for line in response.strip().split("\n"):
        line = line.strip()
        if line.startswith("REASON:"):
            return line
    # フォールバック: 最初の非空行
    for line in response.strip().split("\n"):
        if line.strip():
            return f"REASON: {line.strip()}"
    return "REASON: (生成失敗)"


def insert_reason(proof_path: Path, reason_line: str, dry_run: bool = True) -> bool:
    """PROOF.md に REASON 行を挿入する"""
    content = proof_path.read_text(encoding="utf-8")

    # 既に REASON がある場合はスキップ
    if REASON_PATTERN.search(content):
        return False

    # AUTO-REASON タグ付きで挿入
    reason_with_tag = f"{reason_line}  <!-- AUTO-REASON -->"

    # PURPOSE 行の直後に挿入を試みる
    purpose_match = PURPOSE_PATTERN.search(content)
    if purpose_match:
        insert_pos = purpose_match.end()
        new_content = content[:insert_pos] + "\n" + reason_with_tag + content[insert_pos:]
    else:
        # PURPOSE がない場合: 最初の空行またはヘッダーの後に挿入
        lines = content.split("\n")
        insert_idx = 1  # デフォルト: 2行目
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_idx = i + 1
                # 次の空行を探す
                while insert_idx < len(lines) and lines[insert_idx].strip():
                    insert_idx += 1
                break
        lines.insert(insert_idx, "")
        lines.insert(insert_idx + 1, reason_with_tag)
        new_content = "\n".join(lines)

    if dry_run:
        print(f"  [DRY-RUN] Would insert: {reason_with_tag}")
        return True
    else:
        proof_path.write_text(new_content, encoding="utf-8")
        print(f"  [WRITTEN] {reason_with_tag}")
        return True


def main():
    parser = argparse.ArgumentParser(description="REASON Auto-Generator")
    parser.add_argument("--dry-run", action="store_true", help="生成結果を表示のみ")
    parser.add_argument("--target", type=str, help="特定の PROOF.md パス")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct",
                        help="使用する LLM モデル")
    args = parser.parse_args()

    if args.target:
        targets = [PROJECT_ROOT / args.target]
        # 存在確認
        for t in targets:
            if not t.exists():
                print(f"ERROR: {t} not found")
                sys.exit(1)
    else:
        targets = find_proofs_without_reason(PROJECT_ROOT)

    if not targets:
        print("✅ All PROOF.md files already have REASON fields!")
        return

    print(f"Found {len(targets)} PROOF.md without REASON:\n")
    for t in targets:
        print(f"  - {t.relative_to(PROJECT_ROOT)}")
    print()

    for proof_path in targets:
        rel = proof_path.relative_to(PROJECT_ROOT)
        print(f"{'=' * 60}")
        print(f"Processing: {rel}")
        print(f"{'=' * 60}")

        ctx = gather_context(proof_path)
        prompt = build_prompt(ctx)

        print(f"  Context: purpose='{ctx['purpose'][:50]}', files={len(ctx['files'].split(chr(10)))}")

        reason_line = generate_reason_llm(prompt, model_name=args.model)
        print(f"  Generated: {reason_line}")

        insert_reason(proof_path, reason_line, dry_run=args.dry_run)
        print()

    print(f"\n{'=' * 60}")
    print(f"Done! Processed {len(targets)} files.")
    if args.dry_run:
        print("(Dry-run mode — no files modified. Remove --dry-run to write.)")


if __name__ == "__main__":
    main()
