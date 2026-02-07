"""
morphism_proposer.py — X-series 射提案エンジン

PURPOSE: WF完了時に trigonon frontmatter を読み、
         射の提案ツリーを自動生成する。
         BC-8 (射出力義務) の計算的強制レイヤー。

Usage:
    python mekhane/taxis/morphism_proposer.py noe
    python mekhane/taxis/morphism_proposer.py met --confidence=low
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


# PURPOSE: WF名からシリーズ名へのマッピング
SERIES_NAMES = {
    "O": "Ousia (本質)",
    "S": "Schema (様態)",
    "H": "Hormē (衝動)",
    "P": "Perigraphē (環境)",
    "K": "Kairos (文脈)",
    "A": "Akribeia (精密)",
}


# PURPOSE: trigonon frontmatter をパースして射の提案を生成する
def parse_trigonon(wf_path: Path) -> Optional[dict]:
    """WF ファイルから trigonon セクションを抽出する"""
    try:
        content = wf_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    # YAML frontmatter を簡易パース (yaml ライブラリなしで動作)
    if not content.startswith("---"):
        return None

    end = content.index("---", 3)
    frontmatter = content[3:end]

    result = {}
    in_trigonon = False
    in_morphisms = False

    for line in frontmatter.split("\n"):
        stripped = line.strip()
        # YAML コメントを除去
        if "#" in stripped and not stripped.startswith('"'):
            stripped = stripped[: stripped.index("#")].strip()

        if stripped == "trigonon:":
            in_trigonon = True
            continue

        if in_trigonon:
            if stripped.startswith("series:"):
                result["series"] = stripped.split(":")[1].strip()
            elif stripped.startswith("type:"):
                result["type"] = stripped.split(":")[1].strip()
            elif stripped.startswith("theorem:"):
                result["theorem"] = stripped.split(":")[1].strip()
            elif stripped.startswith("bridge:"):
                val = stripped.split(":")[1].strip()
                result["bridge"] = [
                    s.strip() for s in val.strip("[]").split(",") if s.strip()
                ]
            elif stripped.startswith("anchor_via:"):
                val = stripped.split(":")[1].strip()
                result["anchor_via"] = [
                    s.strip() for s in val.strip("[]").split(",") if s.strip()
                ]
            elif stripped == "morphisms:":
                in_morphisms = True
                result["morphisms"] = {}
            elif in_morphisms and stripped.startswith('">>'):
                key, val = stripped.split(":", 1)
                key = key.strip().strip('"')
                wfs = [
                    w.strip() for w in val.strip().strip("[]").split(",") if w.strip()
                ]
                result["morphisms"][key] = wfs
            elif not stripped.startswith('">>') and ":" not in stripped and stripped:
                in_trigonon = False
                in_morphisms = False

    return result if result else None


# PURPOSE: 射の提案ツリーをフォーマットして出力する
def format_proposal(
    wf_name: str,
    trigonon: dict,
    confidence: Optional[str] = None,
) -> str:
    """射の提案ツリーを生成する"""
    series = trigonon.get("series", "?")
    theorem = trigonon.get("theorem", "?")
    stype = trigonon.get("type", "?")
    bridges = trigonon.get("bridge", [])
    anchors = trigonon.get("anchor_via", [])
    morphisms = trigonon.get("morphisms", {})

    # 確信度ラベル
    if confidence == "high":
        mode = "⚓ 収束モード: Anchor 優先"
    elif confidence == "low":
        mode = "🔍 探索モード: Bridge 優先"
    else:
        mode = "⚖️ 均衡モード"

    lines = [
        f"🔀 射の提案 (trigonon: {series}/{theorem}/{stype})",
        mode,
    ]

    # Bridge 射
    for b in bridges:
        key = f">>{b}"
        wfs = morphisms.get(key, [])
        wf_str = " ".join(wfs) if wfs else f"/{b.lower()} 系全般"
        series_name = SERIES_NAMES.get(b, b)
        lines.append(f"├─ Bridge >> {b}: {wf_str}  ({series_name})")

    # Anchor 射
    for a in anchors:
        series_name = SERIES_NAMES.get(a, a)
        lines.append(f"├─ Anchor >> {a}: via 中継  ({series_name})")

    lines.append("└─ (完了)")
    lines.append("")
    lines.append("→ 結果に確信がありますか？ (Y: Anchor優先 / N: Bridge優先 / 完了)")

    return "\n".join(lines)


# PURPOSE: CLI エントリーポイント
def main() -> None:
    parser = argparse.ArgumentParser(
        description="X-series 射提案エンジン (BC-8)",
    )
    parser.add_argument("wf", help="WF名 (例: noe, met, dia)")
    parser.add_argument(
        "--confidence",
        choices=["high", "low", "neutral"],
        default=None,
        help="確信度 (high=Anchor優先, low=Bridge優先)",
    )
    parser.add_argument(
        "--workflows-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent
        / ".agent"
        / "workflows",
        help="ワークフローディレクトリ",
    )

    args = parser.parse_args()

    wf_path = args.workflows_dir / f"{args.wf}.md"
    trigonon = parse_trigonon(wf_path)

    if trigonon is None:
        print(f"ERROR: {wf_path} に trigonon frontmatter が見つかりません",
              file=sys.stderr)
        sys.exit(1)

    proposal = format_proposal(args.wf, trigonon, args.confidence)
    print(proposal)


if __name__ == "__main__":
    main()
