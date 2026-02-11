#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/
# PURPOSE: Doxa 信念を Sophia 知識 (KI) に昇格させるパイプライン
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → 信念 (Doxa) は根拠と時間で知識 (Sophia) に昇格する
   → doxa_boot.py が候補を検出する
   → doxa_promoter.py が昇格を実行する:
     1. KI マークダウンを生成
     2. kernel/knowledge/doxa/ に KI 構造で配置
     3. Belief に promoted フラグを設定

Q.E.D.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from mekhane.fep.doxa_persistence import (
    Belief,
    DoxaStore,
)
from mekhane.symploke.doxa_boot import PromotionCandidate


# =============================================================================
# Constants
# =============================================================================

_PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_KI_BASE = _PROJECT_ROOT / "kernel" / "knowledge" / "doxa"


# =============================================================================
# Data Classes
# =============================================================================


# PURPOSE: PromotionResult の機能を提供する
@dataclass
class PromotionResult:
    """昇格実行結果。"""

    candidate: PromotionCandidate
    ki_id: str
    ki_dir: Path
    markdown_path: Path
    metadata_path: Path
    success: bool
    error: Optional[str] = None


# =============================================================================
# Core Functions
# =============================================================================


def _slugify(text: str, max_len: int = 40) -> str:
    """信念内容からファイル名用スラッグを生成。"""
    # 日本語はそのまま使う (ファイルシステムが対応)
    slug = text.strip()
    # 危険な文字を除去
    slug = re.sub(r'[/\\:*?"<>|]', "", slug)
    # 空白をアンダースコアに
    slug = re.sub(r"\s+", "_", slug)
    return slug[:max_len]


def _next_ki_number(ki_base: Path) -> int:
    """次の DX 番号を決定する。既存 DX-NNN を走査して max+1。"""
    if not ki_base.exists():
        return 1

    max_num = 0
    for d in ki_base.iterdir():
        if d.is_dir() and d.name.startswith("DX-"):
            try:
                num = int(d.name.split("-")[1].split("_")[0])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
    return max_num + 1


def _generate_ki_markdown(belief: Belief, ki_id: str) -> str:
    """Belief から KI マークダウンを生成。DX-007 フォーマットを踏襲。"""
    evidence_lines = "\n".join(f"- {e}" for e in belief.evidence) if belief.evidence else "- (なし)"

    return f"""# Doxa → Sophia: {belief.content}

> **昇格日時**: {datetime.now().strftime("%Y-%m-%dT%H:%M%z")}
> **元の記録日**: {belief.created_at.strftime("%Y-%m-%dT%H:%M%z")}
> **確信度**: {belief.confidence:.0%}
> **強さ**: {belief.strength.value}
> **ステータス**: PROMOTED
> **KI ID**: {ki_id}

---

## 信念の内容

{belief.content}

---

## 根拠 (Evidence)

{evidence_lines}

---

## 定着期間

{belief.age_days:.0f} 日間の実践を経て昇格。

---

*Doxa → Sophia promotion by Claude (Antigravity)*
*定着: {belief.age_days:.0f}d, 確信度: {belief.confidence:.0%}, 根拠: {len(belief.evidence)}件*
"""


def _generate_metadata(belief: Belief, ki_id: str) -> dict:
    """KI 構造用 metadata.json を生成。sophia_ingest.py が参照する。"""
    return {
        "name": f"Doxa: {belief.content[:60]}",
        "summary": (
            f"Doxa から Sophia に昇格した知識。"
            f"確信度 {belief.confidence:.0%}、"
            f"定着期間 {belief.age_days:.0f} 日、"
            f"根拠 {len(belief.evidence)} 件。"
        ),
        "source": "doxa_promotion",
        "ki_id": ki_id,
        "promoted_at": datetime.now().isoformat(),
        "original_created_at": belief.created_at.isoformat(),
        "strength": belief.strength.value,
        "confidence": belief.confidence,
        "evidence_count": len(belief.evidence),
    }


# PURPOSE: Doxa → Sophia 昇格を実行する
def promote_to_sophia(
    candidate: PromotionCandidate,
    store: DoxaStore,
    ki_base: Optional[Path] = None,
) -> PromotionResult:
    """Doxa 信念を Sophia KI に昇格する。

    1. kernel/knowledge/doxa/DX-{NNN}_{slug}/ に KI 構造を生成
    2. metadata.json + artifacts/{slug}.md を作成
    3. DoxaStore の Belief に promoted フラグを設定

    Args:
        candidate: 昇格候補 (doxa_boot.check_promotion_candidates から)
        store: DoxaStore インスタンス
        ki_base: KI 出力先ベースディレクトリ (省略時: kernel/knowledge/doxa/)

    Returns:
        PromotionResult
    """
    base = ki_base or DEFAULT_KI_BASE
    belief = candidate.belief

    # 二重昇格防止
    if belief.is_promoted:
        return PromotionResult(
            candidate=candidate,
            ki_id=belief.sophia_ki_id or "",
            ki_dir=base,
            markdown_path=base,
            metadata_path=base,
            success=False,
            error=f"既に昇格済み (ki_id={belief.sophia_ki_id})",
        )

    try:
        # KI ID と ディレクトリ
        num = _next_ki_number(base)
        slug = _slugify(belief.content)
        ki_id = f"DX-{num:03d}"
        ki_dir_name = f"{ki_id}_{slug}"
        ki_dir = base / ki_dir_name
        artifacts_dir = ki_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # metadata.json
        metadata = _generate_metadata(belief, ki_id)
        metadata_path = ki_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # artifacts/{slug}.md
        markdown = _generate_ki_markdown(belief, ki_id)
        md_path = artifacts_dir / f"{slug}.md"
        md_path.write_text(markdown, encoding="utf-8")

        # DoxaStore に promoted フラグ設定
        belief.promoted_at = datetime.now()
        belief.sophia_ki_id = ki_id

        return PromotionResult(
            candidate=candidate,
            ki_id=ki_id,
            ki_dir=ki_dir,
            markdown_path=md_path,
            metadata_path=metadata_path,
            success=True,
        )

    except Exception as e:
        return PromotionResult(
            candidate=candidate,
            ki_id="",
            ki_dir=base,
            markdown_path=base,
            metadata_path=base,
            success=False,
            error=str(e),
        )


# PURPOSE: 複数候補を一括昇格（Creator 承認後に呼ばれる）
def promote_approved(
    candidates: List[PromotionCandidate],
    store: DoxaStore,
    ki_base: Optional[Path] = None,
) -> List[PromotionResult]:
    """Creator が承認した候補を一括昇格する。

    Args:
        candidates: 承認済み候補リスト
        store: DoxaStore インスタンス
        ki_base: KI 出力先

    Returns:
        PromotionResult のリスト
    """
    results = []
    for candidate in candidates:
        result = promote_to_sophia(candidate, store, ki_base)
        results.append(result)
    return results


# PURPOSE: Creator 承認ゲート用の表示テキスト生成
def format_promotion_prompt(candidates: List[PromotionCandidate]) -> str:
    """Creator に昇格候補を提示するテキストを生成。

    /boot で表示して承認を求める。
    """
    if not candidates:
        return ""

    lines = [
        "### 📈 Sophia 昇格候補",
        "",
        "以下の信念が昇格条件を満たしています。昇格しますか？",
        "",
    ]

    for i, c in enumerate(candidates, 1):
        reasons_str = ", ".join(c.reasons)
        lines.append(
            f"{i}. **{c.belief.content[:60]}** "
            f"(確信度: {c.belief.confidence:.0%}, "
            f"定着: {c.belief.age_days:.0f}日, "
            f"根拠: {len(c.belief.evidence)}件)"
        )
        lines.append(f"   条件: {reasons_str}")

    lines.append("")
    lines.append("> 昇格すると `kernel/knowledge/doxa/` に KI として配置され、")
    lines.append("> 次回の Sophia インデックス更新で検索可能になります。")

    return "\n".join(lines)
