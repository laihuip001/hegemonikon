# PROOF: [L2/インフラ] <- mekhane/dendron/
"""
Skill & Workflow Frontmatter Checker — Safety Contract 検証

SKILL.md の risk_tier/risks/fallbacks と WF の lcm_state を検証する。
/dia+ で指摘された F1-F4 を実装:
  F1: risk_tier 未記載 SKILL.md を WARNING で検出
  F2: lcm_state: deprecated の WF を警告
"""

import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict

try:
    import yaml
except ImportError:
    yaml = None


# PURPOSE: SKILL/WF フロントマター検証結果の分類を可能にする
class AuditSeverity(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


# PURPOSE: 1件のフロントマター検証結果を統一的に保持し、レポート生成に渡す
@dataclass
class AuditFinding:
    path: Path
    severity: AuditSeverity
    field: str
    message: str
    file_type: str  # "skill" or "workflow"


# PURPOSE: 全検証結果を集計し、CI 判定・サマリ表示に渡す
@dataclass
class AuditResult:
    findings: List[AuditFinding] = field(default_factory=list)
    skills_checked: int = 0
    workflows_checked: int = 0

    # PURPOSE: ERROR 件数を集計し CI ゲート判定に使用する
    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f.severity == AuditSeverity.ERROR)

    # PURPOSE: WARNING 件数を集計しレポートに表示する
    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == AuditSeverity.WARNING)

    # PURPOSE: CI パイプラインでの合否を判定する
    @property
    def is_passing(self) -> bool:
        return self.errors == 0

    # PURPOSE: risk_tier の分布を集計し、/boot サマリに表示するデータを生成する
    def risk_distribution(self) -> Dict[str, int]:
        dist: Dict[str, int] = {"L0": 0, "L1": 0, "L2": 0, "L3": 0, "missing": 0}
        for f in self.findings:
            if f.field == "risk_tier" and f.severity == AuditSeverity.OK:
                tier = f.message.split("=")[-1].strip() if "=" in f.message else "missing"
                if tier in dist:
                    dist[tier] += 1
            elif f.field == "risk_tier" and f.severity in (AuditSeverity.ERROR, AuditSeverity.WARNING):
                dist["missing"] += 1
        return dist

    # PURPOSE: lcm_state の分布を集計し、/boot サマリに表示するデータを生成する
    def lcm_distribution(self) -> Dict[str, int]:
        dist: Dict[str, int] = {"draft": 0, "beta": 0, "stable": 0, "deprecated": 0, "missing": 0}
        for f in self.findings:
            if f.field == "lcm_state" and f.severity == AuditSeverity.OK:
                state = f.message.split("=")[-1].strip() if "=" in f.message else "missing"
                if state in dist:
                    dist[state] += 1
            elif f.field == "lcm_state" and f.severity in (AuditSeverity.ERROR, AuditSeverity.WARNING):
                dist["missing"] += 1
        return dist


# ─────────────────────────────────────────────────────
# Safety Contract required fields
# ─────────────────────────────────────────────────────

SKILL_REQUIRED_FIELDS = ["risk_tier", "risks"]
SKILL_RECOMMENDED_FIELDS = ["reversible", "requires_approval", "fallbacks"]
VALID_RISK_TIERS = {"L0", "L1", "L2", "L3"}
VALID_LCM_STATES = {"draft", "beta", "stable", "deprecated"}


# ─────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


# PURPOSE: Markdown ファイルの YAML フロントマターを抽出・パースする
def parse_frontmatter(path: Path) -> Optional[dict]:
    """Markdown ファイルから YAML フロントマターをパースする"""
    if yaml is None:
        print("WARNING: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
        return None

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


# PURPOSE: SKILL.md フロントマターの Safety Contract フィールドを検証する (F1)
def check_skill(path: Path) -> List[AuditFinding]:
    """SKILL.md の Safety Contract フィールドを検証する"""
    findings: List[AuditFinding] = []
    fm = parse_frontmatter(path)

    if fm is None:
        findings.append(AuditFinding(
            path=path, severity=AuditSeverity.ERROR,
            field="frontmatter", message="フロントマターなし or パース失敗",
            file_type="skill"
        ))
        return findings

    # Required fields
    for req_field in SKILL_REQUIRED_FIELDS:
        if req_field not in fm:
            findings.append(AuditFinding(
                path=path, severity=AuditSeverity.ERROR,
                field=req_field, message=f"{req_field} が未記載",
                file_type="skill"
            ))
        elif req_field == "risk_tier":
            tier = str(fm[req_field])
            if tier not in VALID_RISK_TIERS:
                findings.append(AuditFinding(
                    path=path, severity=AuditSeverity.ERROR,
                    field=req_field, message=f"無効な risk_tier: {tier} (有効: {VALID_RISK_TIERS})",
                    file_type="skill"
                ))
            else:
                findings.append(AuditFinding(
                    path=path, severity=AuditSeverity.OK,
                    field=req_field, message=f"risk_tier={tier}",
                    file_type="skill"
                ))
        elif req_field == "risks":
            risks = fm[req_field]
            if not risks or (isinstance(risks, list) and len(risks) == 0):
                findings.append(AuditFinding(
                    path=path, severity=AuditSeverity.WARNING,
                    field=req_field, message="risks が空 (Anti-Confidence: 最低1つ記載推奨)",
                    file_type="skill"
                ))
            else:
                findings.append(AuditFinding(
                    path=path, severity=AuditSeverity.OK,
                    field=req_field, message=f"risks={len(risks)}件",
                    file_type="skill"
                ))

    # Recommended fields
    for rec_field in SKILL_RECOMMENDED_FIELDS:
        if rec_field not in fm:
            findings.append(AuditFinding(
                path=path, severity=AuditSeverity.WARNING,
                field=rec_field, message=f"{rec_field} が未記載 (推奨)",
                file_type="skill"
            ))

    return findings


# PURPOSE: WF フロントマターの lcm_state を検証し、deprecated を警告する (F2)
def check_workflow(path: Path) -> List[AuditFinding]:
    """WF フロントマターの lcm_state を検証する"""
    findings: List[AuditFinding] = []
    fm = parse_frontmatter(path)

    if fm is None:
        # WF にフロントマターがないのは現状多いので WARNING
        findings.append(AuditFinding(
            path=path, severity=AuditSeverity.WARNING,
            field="frontmatter", message="フロントマターなし or パース失敗",
            file_type="workflow"
        ))
        return findings

    # lcm_state
    if "lcm_state" not in fm:
        findings.append(AuditFinding(
            path=path, severity=AuditSeverity.WARNING,
            field="lcm_state", message="lcm_state が未記載",
            file_type="workflow"
        ))
    else:
        state = str(fm["lcm_state"])
        if state not in VALID_LCM_STATES:
            findings.append(AuditFinding(
                path=path, severity=AuditSeverity.ERROR,
                field="lcm_state", message=f"無効な lcm_state: {state}",
                file_type="workflow"
            ))
        elif state == "deprecated":
            findings.append(AuditFinding(
                path=path, severity=AuditSeverity.WARNING,
                field="lcm_state", message=f"⚠️ lcm_state=deprecated — この WF は非推奨です",
                file_type="workflow"
            ))
        else:
            findings.append(AuditFinding(
                path=path, severity=AuditSeverity.OK,
                field="lcm_state", message=f"lcm_state={state}",
                file_type="workflow"
            ))

    # version (WF は version 推奨)
    if "version" not in fm:
        findings.append(AuditFinding(
            path=path, severity=AuditSeverity.WARNING,
            field="version", message="version が未記載",
            file_type="workflow"
        ))

    return findings


# ─────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────

# PURPOSE: .agent/ ディレクトリ以下の SKILL.md と WF を一括検証する
def run_audit(agent_dir: Path) -> AuditResult:
    """
    .agent/ ディレクトリ以下の SKILL.md と WF を一括検証する

    Args:
        agent_dir: .agent/ ディレクトリへのパス
    """
    result = AuditResult()

    # Skills
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        for skill_md in skills_dir.rglob("SKILL.md"):
            # SKILL_TEMPLATE.md と _archive/ は除外
            if "TEMPLATE" in skill_md.name.upper():
                continue
            if "_archive" in skill_md.parts:
                continue
            result.skills_checked += 1
            result.findings.extend(check_skill(skill_md))

    # Workflows
    wf_dir = agent_dir / "workflows"
    if wf_dir.exists():
        for wf_md in wf_dir.glob("*.md"):
            result.workflows_checked += 1
            result.findings.extend(check_workflow(wf_md))

    return result


# PURPOSE: 検証結果を人間が読めるレポートに整形する
def format_report(result: AuditResult, verbose: bool = False) -> str:
    """検証結果をレポートに整形する"""
    lines = []
    lines.append("# 🛡️ Safety Contract Audit Report")
    lines.append("")
    lines.append(f"Skills checked: {result.skills_checked}")
    lines.append(f"Workflows checked: {result.workflows_checked}")
    lines.append(f"Errors: {result.errors} | Warnings: {result.warnings}")
    lines.append(f"Verdict: {'✅ PASS' if result.is_passing else '❌ FAIL'}")
    lines.append("")

    # Risk distribution
    dist = result.risk_distribution()
    if any(v > 0 for v in dist.values()):
        lines.append("## Risk Tier Distribution")
        for tier in ["L0", "L1", "L2", "L3", "missing"]:
            count = dist.get(tier, 0)
            if count > 0:
                bar = "█" * count
                lines.append(f"  {tier:>7}: {bar} {count}")
        lines.append("")

    # LCM distribution
    lcm = result.lcm_distribution()
    if any(v > 0 for v in lcm.values()):
        lines.append("## WF Lifecycle Distribution")
        for state in ["stable", "beta", "draft", "deprecated", "missing"]:
            count = lcm.get(state, 0)
            if count > 0:
                emoji = {"stable": "🟢", "beta": "🟡", "draft": "⚪", "deprecated": "🔴", "missing": "❓"}.get(state, "")
                lines.append(f"  {emoji} {state:>10}: {count}")
        lines.append("")

    # Findings
    errors = [f for f in result.findings if f.severity == AuditSeverity.ERROR]
    warnings = [f for f in result.findings if f.severity == AuditSeverity.WARNING]

    if errors:
        lines.append("## ❌ Errors")
        for f in errors:
            lines.append(f"  - [{f.file_type}] {f.path.name}: {f.field} — {f.message}")
        lines.append("")

    if warnings:
        lines.append("## ⚠️ Warnings")
        for f in warnings:
            lines.append(f"  - [{f.file_type}] {f.path.name}: {f.field} — {f.message}")
        lines.append("")

    if verbose:
        oks = [f for f in result.findings if f.severity == AuditSeverity.OK]
        if oks:
            lines.append("## ✅ OK")
            for f in oks:
                lines.append(f"  - [{f.file_type}] {f.path.name}: {f.field} — {f.message}")
            lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────

# PURPOSE: コマンドラインからの直接実行を可能にし、CI ゲートの判定結果を返す
def main() -> None:
    """CLI entrypoint for skill-audit"""
    import argparse

    parser = argparse.ArgumentParser(description="Safety Contract Audit")
    parser.add_argument("agent_dir", type=Path, nargs="?",
                        default=Path(".agent"),
                        help="Path to .agent/ directory")
    parser.add_argument("--ci", action="store_true", help="CI mode (exit 1 on errors)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show OK findings too")
    parser.add_argument("--boot-summary", action="store_true",
                        help="Output compact summary for /boot")
    args = parser.parse_args()

    result = run_audit(args.agent_dir)

    if args.boot_summary:
        # /boot 用のコンパクトサマリ
        dist = result.risk_distribution()
        lcm = result.lcm_distribution()
        print(f"\n🛡️ Safety Contract:")
        print(f"  Skills: {result.skills_checked} | WF: {result.workflows_checked}")
        risk_parts = [f"{k}:{v}" for k, v in dist.items() if v > 0]
        if risk_parts:
            print(f"  Risk: {' '.join(risk_parts)}")
        lcm_parts = [f"{k}:{v}" for k, v in lcm.items() if v > 0]
        if lcm_parts:
            print(f"  LCM:  {' '.join(lcm_parts)}")
        if result.errors > 0:
            print(f"  ⚠️ {result.errors} errors found")
    else:
        print(format_report(result, verbose=args.verbose))

    if args.ci and not result.is_passing:
        sys.exit(1)


if __name__ == "__main__":
    main()
