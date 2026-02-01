#!/usr/bin/env python3
# PROOF: [L2/インフラ]
#
# P3 → セッション終了時に Walkthrough を保存する必要がある
#    → Antigravity brain から walkthrough.md を mneme にコピー
#    → このスクリプトが担う
# Q.E.D.
#
# walkthrough_export.py - セッション終了時に Walkthrough を mneme に保存
# 使用方法: python walkthrough_export.py [conversation_id]
# /bye から呼び出される

import shutil
import sys
from datetime import datetime
from pathlib import Path

# 設定
OIKOS_ROOT = Path("/home/laihuip001/oikos")
BRAIN_DIR = OIKOS_ROOT / ".gemini/antigravity/brain"
MNEME_DIR = OIKOS_ROOT / "mneme/.hegemonikon/sessions"


def export_walkthrough(conversation_id: str | None = None) -> Path | None:
    """Walkthrough を mneme にエクスポート

    Args:
        conversation_id: 会話ID。None の場合は最新の walkthrough を取得

    Returns:
        エクスポートされたファイルのパス、またはNone
    """
    MNEME_DIR.mkdir(parents=True, exist_ok=True)

    if conversation_id:
        # 指定されたセッションの walkthrough
        walkthrough_path = BRAIN_DIR / conversation_id / "walkthrough.md"
    else:
        # 最新の walkthrough を検索
        walkthroughs = list(BRAIN_DIR.glob("*/walkthrough.md"))
        if not walkthroughs:
            print("[!] No walkthrough.md found")
            return None
        # 更新日時が最新のものを選択
        walkthrough_path = max(walkthroughs, key=lambda p: p.stat().st_mtime)
        conversation_id = walkthrough_path.parent.name

    if not walkthrough_path.exists():
        print(f"[!] Walkthrough not found: {walkthrough_path}")
        return None

    # 出力ファイル名
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_name = f"walkthrough_{date_str}_{conversation_id[:8]}.md"
    output_path = MNEME_DIR / output_name

    # コピー
    shutil.copy2(walkthrough_path, output_path)
    print(f"[✓] Walkthrough exported: {output_path}")

    # 関連ファイルもコピー (task.md, implementation_plan.md)
    for related in ["task.md", "implementation_plan.md"]:
        related_path = walkthrough_path.parent / related
        if related_path.exists():
            related_output = (
                MNEME_DIR / f"{related.replace('.md', '')}_{date_str}_{conversation_id[:8]}.md"
            )
            shutil.copy2(related_path, related_output)
            print(f"[✓] Related: {related_output.name}")

    return output_path


def main():
    conv_id = sys.argv[1] if len(sys.argv) > 1 else None
    result = export_walkthrough(conv_id)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
