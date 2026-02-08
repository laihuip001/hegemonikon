#!/usr/bin/env python3
"""
wf_postcheck.py — 汎用 WF ポストチェック

環境強制: WF 出力の品質を機械的に検証する。
sel_enforcement の minimum_requirements を YAML から読み込み、
出力内容と照合する。

Usage:
    python scripts/wf_postcheck.py --wf boot --mode detailed --output /tmp/boot_report.md
    python scripts/wf_postcheck.py --wf dia --mode "+" --text "判定結果テキスト..."
    python scripts/wf_postcheck.py --list  # sel_enforcement 一覧表示
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Optional

import yaml


# ============================================================
# YAML から sel_enforcement を読み込む
# ============================================================

WF_DIR = Path(__file__).parent.parent / ".agent" / "workflows"


def load_sel_enforcement(wf_name: str) -> dict:
    """WF の sel_enforcement を YAML frontmatter から読み込む。"""
    wf_path = WF_DIR / f"{wf_name}.md"
    if not wf_path.exists():
        return {}

    content = wf_path.read_text(encoding="utf-8")

    # YAML frontmatter を抽出 (--- で囲まれた部分)
    match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not match:
        return {}

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}

    return fm.get("sel_enforcement", {})


def list_all_sel_enforcement() -> dict[str, dict]:
    """全WFの sel_enforcement を読み込んで返す。"""
    result = {}
    for wf_path in sorted(WF_DIR.glob("*.md")):
        wf_name = wf_path.stem
        sel = load_sel_enforcement(wf_name)
        if sel:
            result[wf_name] = sel
    return result


# ============================================================
# 汎用チェッカー
# ============================================================

# モード名の正規化: "+" → "+", "detailed" → "+"
MODE_MAP = {
    "detailed": "+",
    "standard": "",
    "fast": "-",
    "+": "+",
    "-": "-",
    "*": "*",
    "": "",
}


def check_requirements(
    content: str,
    requirements: list[str],
) -> list[dict]:
    """
    requirements リストの各項目を content に対してチェックする。

    チェック方法:
    - 要件からキーワードを抽出（コロン前をプライマリキーワードとして優先）
    - content にキーワードが含まれるかヒューリスティック検査
    - 数値要件（N件以上、N行以内等）は正規表現で抽出・検証
    """
    checks = []
    content_lower = content.lower()

    for req in requirements:
        # 数値パターンの検出: "3つ以上", "5行以内", "N件"
        num_match = re.search(r"(\d+)[つ件個箇所]+以上", req)
        limit_match = re.search(r"(\d+)行以内", req)

        # コロン前をプライマリキーワードとして抽出
        primary_keywords = []
        if ":" in req or "：" in req:
            label = re.split(r"[:：]", req)[0].strip()
            primary_keywords = re.findall(r"[A-Za-z_-]{2,}|[ぁ-んァ-ヶ一-龠]{2,}", label)

        # 全体からキーワード抽出
        all_keywords = re.findall(r"[A-Za-z_-]{2,}|[ぁ-んァ-ヶ一-龠]{2,}", req)
        # ノイズ除去
        noise = {"必須", "明示", "以上", "以内", "のみ", "する", "こと", "出力",
                 "記載", "minimum", "requirements", "を", "で", "に", "は", "の", "が"}
        all_keywords = [k for k in all_keywords if k not in noise]

        # キーワードマッチ判定
        if primary_keywords:
            # プライマリキーワードの完全一致 OR 部分一致（2文字以上の部分文字列）
            primary_hit = False
            for k in primary_keywords:
                k_lower = k.lower()
                if k_lower in content_lower:
                    primary_hit = True
                    break
                # 長い日本語キーワードを分解して部分一致（例: 証拠セクション → 証拠, セクション）
                if len(k) >= 4:
                    for i in range(len(k) - 1):
                        sub = k[i:i+2]
                        if sub in content_lower:
                            primary_hit = True
                            break
                if primary_hit:
                    break
        else:
            primary_hit = False

        if all_keywords:
            match_count = sum(1 for k in all_keywords if k.lower() in content_lower)
            match_ratio = match_count / len(all_keywords)
        else:
            match_count = 0
            match_ratio = 0.0

        # 判定: プライマリキーワードマッチ OR 全体30%以上
        passed = primary_hit or match_ratio >= 0.3

        # 数値チェック: "3つ以上" → 該当パターンが3つ以上あるか
        if num_match and passed:
            expected = int(num_match.group(1))
            # ヒューリスティック: セクションヘッダ数で近似
            section_count = len(re.findall(r"^#{1,4}\s", content, re.MULTILINE))
            if section_count < expected:
                passed = False

        # 行数制限チェック
        if limit_match:
            max_lines = int(limit_match.group(1))
            actual_lines = len(content.strip().split("\n"))
            passed = actual_lines <= max_lines

        checks.append({
            "name": req[:60],
            "passed": passed,
            "detail": f"{'✅' if passed else '❌'} {req}" + (
                f" (keywords: {match_count}/{len(all_keywords)})" if all_keywords else ""
            ),
        })

    return checks


def postcheck(
    wf_name: str,
    mode: str,
    content: str,
) -> dict:
    """
    汎用ポストチェック。

    Returns:
        dict: {"passed": bool, "checks": [...], "formatted": str}
    """
    sel = load_sel_enforcement(wf_name)
    if not sel:
        return {
            "passed": True,
            "checks": [],
            "formatted": f"⚠️ {wf_name}: sel_enforcement 未定義（チェックスキップ）",
        }

    normalized_mode = MODE_MAP.get(mode, mode)
    mode_sel = sel.get(normalized_mode, {})
    if not mode_sel:
        return {
            "passed": True,
            "checks": [],
            "formatted": f"⚠️ {wf_name}: モード '{mode}' の sel_enforcement 未定義",
        }

    requirements = mode_sel.get("minimum_requirements", [])
    if not requirements:
        return {
            "passed": True,
            "checks": [],
            "formatted": f"✅ {wf_name}: 要件なし（チェックスキップ）",
        }

    checks = check_requirements(content, requirements)

    passed_count = sum(1 for c in checks if c["passed"])
    total = len(checks)
    all_passed = all(c["passed"] for c in checks)

    status = "PASS" if all_passed else "FAIL"
    icon = "✅" if all_passed else "❌"
    lines = [f"{icon} /{wf_name}{normalized_mode} Postcheck: {status} ({passed_count}/{total})"]
    for c in checks:
        lines.append(f"  {c['detail']}")

    return {
        "passed": all_passed,
        "checks": checks,
        "formatted": "\n".join(lines),
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="汎用 WF ポストチェック — sel_enforcement ベースの品質検証"
    )
    parser.add_argument("--wf", type=str, help="ワークフロー名 (例: boot, dia, noe)")
    parser.add_argument("--mode", type=str, default="+", help='モード (+, -, *, detailed, fast)')
    parser.add_argument("--output", type=str, help="チェック対象ファイルパス")
    parser.add_argument("--text", type=str, help="チェック対象テキスト（直接指定）")
    parser.add_argument("--list", action="store_true", help="全WFの sel_enforcement 一覧")
    args = parser.parse_args()

    if args.list:
        all_sel = list_all_sel_enforcement()
        print(f"📋 sel_enforcement 定義済み WF: {len(all_sel)}")
        print()
        for wf_name, sel in all_sel.items():
            modes = ", ".join(sel.keys())
            print(f"  /{wf_name}: [{modes}]")
            for mode_key, mode_val in sel.items():
                reqs = mode_val.get("minimum_requirements", [])
                print(f"    {mode_key}: {len(reqs)} requirements")
        sys.exit(0)

    if not args.wf:
        parser.error("--wf is required (or use --list)")

    # コンテンツ取得
    content = ""
    if args.output:
        path = Path(args.output)
        if not path.exists():
            print(f"❌ File not found: {args.output}")
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        # stdin から読み込み
        content = sys.stdin.read()

    result = postcheck(args.wf, args.mode, content)
    print(result["formatted"])
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
