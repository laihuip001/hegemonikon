# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Attractor 推薦を実際の WF dispatch 指示に変換する
"""
Attractor Dispatcher — Problem A 解決

AttractorAdvisor の Recommendation を消費し、
WF ファイル読み込み → SKILL.md 参照 → dispatch 指示を生成する。

Usage:
    dispatcher = AttractorDispatcher()
    plan = dispatcher.dispatch("なぜこのプロジェクトが必要か")
    print(plan.primary.workflow)   # "/noe"
    print(plan.primary.reason)     # "O-series に明確収束..."
    print(dispatcher.format_dispatch(plan))
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mekhane.fep.attractor import OscillationType
from mekhane.fep.attractor_advisor import AttractorAdvisor, Recommendation


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# PURPOSE: プロジェクトルートから .agent/ を解決する基準パス
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # mekhane/fep/ → project root
_AGENT_DIR = _PROJECT_ROOT / ".agent"
_WF_DIR = _AGENT_DIR / "workflows"
_SKILLS_DIR = _AGENT_DIR / "skills"

# YAML frontmatter パーサ
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

# PURPOSE: 単一 WF の dispatch 指示
@dataclass
class DispatchResult:
    """単一 WF の dispatch 指示"""
    workflow: str              # e.g. "/noe"
    wf_path: Path              # .agent/workflows/noe.md
    skill_path: Optional[Path] # .agent/skills/ousia/o1-noesis/SKILL.md
    series: str                # "O"
    confidence: float
    reason: str                # 推薦理由
    when_to_use: str           # SKILL.md から抽出
    description: str           # WF description

    # PURPOSE: 内部処理: repr__
    def __repr__(self) -> str:
        return f"⟨Dispatch: {self.workflow} ({self.series}) conf={self.confidence:.3f}⟩"


# PURPOSE: 完全な dispatch 計画（primary + alternatives）
@dataclass
class DispatchPlan:
    """完全な dispatch 計画"""
    primary: DispatchResult
    alternatives: list[DispatchResult] = field(default_factory=list)
    oscillation: OscillationType = OscillationType.CLEAR
    raw_recommendation: Optional[Recommendation] = None

    @property
    # PURPOSE: 全 dispatch 対象を返す
    def all_dispatches(self) -> list[DispatchResult]:
        """primary + alternatives"""
        return [self.primary] + self.alternatives

    # PURPOSE: 内部処理: repr__
    def __repr__(self) -> str:
        alt_count = len(self.alternatives)
        return (
            f"⟨DispatchPlan: {self.primary.workflow} "
            f"[+{alt_count} alt] | {self.oscillation.value}⟩"
        )


# ---------------------------------------------------------------------------
# Frontmatter Parser (lightweight, no pyyaml dependency)
# ---------------------------------------------------------------------------

# PURPOSE: YAMLフロントマターから特定のキーの値を抽出する（軽量版）
def _extract_field(content: str, field_name: str) -> str:
    """frontmatter from markdown content, extract a specific field value."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return ""

    fm_text = match.group(1)
    # Simple key: "value" or key: value extraction
    pattern = re.compile(rf'^{field_name}:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
    m = pattern.search(fm_text)
    return m.group(1).strip() if m else ""


# PURPOSE: Markdown の特定セクションの内容を抽出する
def _extract_section(content: str, heading: str, max_lines: int = 10) -> str:
    """Extract content under a specific markdown heading."""
    pattern = re.compile(
        rf"^#+\s+.*{re.escape(heading)}.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(content)
    if not m:
        return ""

    # Collect lines until next heading or max_lines
    start = m.end()
    lines = content[start:].split("\n")
    result_lines: list[str] = []
    for line in lines[1:]:  # skip the heading itself
        if line.startswith("#"):
            break
        if len(result_lines) >= max_lines:
            break
        stripped = line.strip()
        if stripped:
            result_lines.append(stripped)

    return " ".join(result_lines)


# PURPOSE: YAMLフロントマターの multiline field (| or >) を抽出する
def _extract_multiline_field(content: str, field_name: str) -> str:
    """Extract a YAML multiline field (block scalar) from frontmatter."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return ""

    fm_text = match.group(1)
    # Find the field
    pattern = re.compile(rf'^{field_name}:\s*[|>]?\s*$', re.MULTILINE)
    m = pattern.search(fm_text)
    if not m:
        # Try inline value
        inline = re.compile(rf'^{field_name}:\s*(.+)$', re.MULTILINE)
        mi = inline.search(fm_text)
        return mi.group(1).strip().strip('"') if mi else ""

    # Collect indented continuation lines (skip leading blank lines)
    lines = fm_text[m.end():].split("\n")
    result: list[str] = []
    indent_level = 0
    found_content = False
    for line in lines:
        if not found_content:
            # Skip blank lines before content
            if not line.strip():
                continue
            # First non-blank line determines indent level
            if line[0].isspace():
                indent_level = len(line) - len(line.lstrip())
                found_content = True
                result.append(line.strip())
            else:
                break  # Non-indented line = end of block
        else:
            # Blank lines within block are OK
            if not line.strip():
                continue
            # Check indentation
            if line[0].isspace() and (len(line) - len(line.lstrip())) >= indent_level:
                result.append(line.strip())
            else:
                break
    return " ".join(result)


# ---------------------------------------------------------------------------
# AttractorDispatcher
# ---------------------------------------------------------------------------

# PURPOSE: Attractor 推薦を WF dispatch 指示に変換するエンジン
class AttractorDispatcher:
    """
    Attractor 推薦を WF dispatch 指示に変換する。

    AttractorAdvisor の出力を消費し、
    WF frontmatter と SKILL.md を読み込んで
    実行可能な dispatch plan を生成する。

    Usage:
        dispatcher = AttractorDispatcher()
        plan = dispatcher.dispatch("なぜこのプロジェクトが必要か")
        print(dispatcher.format_dispatch(plan))
    """

    # PURPOSE: 内部処理: init__
    def __init__(self, force_cpu: bool = False):
        self._advisor = AttractorAdvisor(force_cpu=force_cpu)

    # PURPOSE: ユーザー入力から WF dispatch plan を生成する
    def dispatch(self, user_input: str) -> Optional[DispatchPlan]:
        """
        ユーザー入力から WF dispatch plan を生成する。

        Returns:
            DispatchPlan or None (引力圏外の場合)
        """
        rec = self._advisor.recommend(user_input)

        if not rec.workflows:
            return None

        # Build dispatch results for each workflow
        dispatches: list[DispatchResult] = []
        for wf_name in rec.workflows:
            dr = self._resolve_workflow(wf_name, rec)
            if dr is not None:
                dispatches.append(dr)

        if not dispatches:
            return None

        return DispatchPlan(
            primary=dispatches[0],
            alternatives=dispatches[1:],
            oscillation=rec.oscillation,
            raw_recommendation=rec,
        )

    # PURPOSE: WF 名から DispatchResult を構築する
    def _resolve_workflow(
        self, wf_name: str, rec: Recommendation
    ) -> Optional[DispatchResult]:
        """WF 名 (e.g. '/noe') から DispatchResult を構築する。"""
        # wf_name: "/noe" → "noe.md"
        basename = wf_name.lstrip("/")
        wf_path = _WF_DIR / f"{basename}.md"

        if not wf_path.exists():
            return None

        wf_content = wf_path.read_text(encoding="utf-8")
        description = _extract_field(wf_content, "description")
        skill_ref = _extract_field(wf_content, "skill_ref")

        # Resolve skill path
        skill_path: Optional[Path] = None
        when_to_use = ""
        if skill_ref:
            skill_path = _PROJECT_ROOT / skill_ref
            if skill_path.exists():
                skill_content = skill_path.read_text(encoding="utf-8")
                when_to_use = _extract_multiline_field(skill_content, "when_to_use")
                if not when_to_use:
                    when_to_use = _extract_section(skill_content, "When to Use")

        # Determine series from recommendation
        series = rec.series[0] if rec.series else "?"

        # Build reason
        reason = self._build_reason(rec, wf_name, description)

        return DispatchResult(
            workflow=wf_name,
            wf_path=wf_path,
            skill_path=skill_path,
            series=series,
            confidence=rec.confidence,
            reason=reason,
            when_to_use=when_to_use,
            description=description,
        )

    # PURPOSE: 推薦理由テキストを構築する
    @staticmethod
    def _build_reason(rec: Recommendation, wf_name: str, description: str) -> str:
        """推薦理由テキストを構築する。"""
        series_str = "+".join(rec.series) if rec.series else "?"

        if rec.oscillation == OscillationType.CLEAR:
            return (
                f"{series_str}-series に明確に収束 (conf={rec.confidence:.2f})。"
                f"{description}"
            )
        elif rec.oscillation == OscillationType.POSITIVE:
            return (
                f"多面的入力: {series_str} が共鳴。"
                f"{wf_name} は {description}"
            )
        elif rec.oscillation == OscillationType.NEGATIVE:
            return (
                f"Basin 未分化。{series_str} が最近接だが引力弱。"
                f"入力を具体化すると精度向上。"
            )
        else:
            return f"引力弱。{wf_name} を暫定提案。"

    # PURPOSE: dispatch plan を人間/LLM 向けの指示文に整形する
    def format_dispatch(self, plan: DispatchPlan) -> str:
        """dispatch plan を人間/LLM 向けの指示文に整形する。"""
        lines: list[str] = []

        lines.append("┌─[Attractor Dispatch]──────────────────────┐")
        lines.append(f"│ 推薦: {plan.primary.workflow}")
        lines.append(f"│ Series: {plan.primary.series}")
        lines.append(f"│ 確信度: {plan.primary.confidence:.2f}")
        lines.append(f"│ 収束: {plan.oscillation.value}")
        lines.append(f"│ 理由: {plan.primary.reason}")

        if plan.primary.when_to_use:
            wtu = plan.primary.when_to_use[:80]
            lines.append(f"│ 使用条件: {wtu}")

        if plan.alternatives:
            alt_str = ", ".join(d.workflow for d in plan.alternatives)
            lines.append(f"│ 代替: {alt_str}")

        lines.append("└────────────────────────────────────────────┘")
        return "\n".join(lines)

    # PURPOSE: boot_integration 互換の compact 表示を生成する
    def format_compact(self, plan: DispatchPlan) -> str:
        """boot_integration 互換の compact 表示"""
        primary = plan.primary
        alt = ", ".join(d.workflow for d in plan.alternatives[:2])
        parts = [f"→ {primary.workflow} ({primary.series}, {plan.oscillation.value})"]
        if alt:
            parts.append(f"alt: {alt}")
        return " | ".join(parts)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

# PURPOSE: CLI: python -m mekhane.fep.attractor_dispatcher "入力テキスト"
def main() -> None:
    """CLI: python -m mekhane.fep.attractor_dispatcher "入力テキスト" """
    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.fep.attractor_dispatcher <input_text>")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    dispatcher = AttractorDispatcher()

    print(f"\n入力: {user_input}")
    print("=" * 60)

    plan = dispatcher.dispatch(user_input)

    if plan is None:
        print("\n⚠️ 引力圏外 — 特定の WF に収束しません。")
        sys.exit(0)

    print(f"\n{dispatcher.format_dispatch(plan)}")

    print(f"\n── 詳細 ──")
    for d in plan.all_dispatches:
        print(f"  {d.workflow}:")
        print(f"    WF: {d.wf_path}")
        print(f"    Skill: {d.skill_path or '(なし)'}")
        print(f"    When: {d.when_to_use[:100] or '(未記載)'}")

    print(f"\nCompact: {dispatcher.format_compact(plan)}")


if __name__ == "__main__":
    main()
