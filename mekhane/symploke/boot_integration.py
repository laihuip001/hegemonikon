#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→継続する私が必要→boot_integration が担う
"""
Boot Integration - 13軸を統合した /boot 用 API

Axes:
  A. Handoff   B. Sophia/KI   C. Persona   D. PKS
  E. Safety    F. Attractor   G. GPU       H. EPT
  I. Projects  J. Skills      K. Doxa      L. Credit
  M. Explanation Stack

Theorem Coverage:
  全24定理 (O1-O4, S1-S4, H1-H4, P1-P4, K1-K4, A1-A4) を
  TheoremAttractor + THEOREM_REGISTRY 経由で Boot 時にアクセス可能。

Usage:
    python boot_integration.py                    # 標準起動
    python boot_integration.py --mode fast        # 高速起動
    python boot_integration.py --mode detailed    # 詳細起動
    python boot_integration.py --postcheck /tmp/boot_report.md --mode detailed  # ポストチェック
"""

import re
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ── 24 Theorem Registry ─────────────────────────────
# PURPOSE: 96要素体系の全24定理を Boot 時に明示的に参照可能にする
THEOREM_REGISTRY: dict[str, dict] = {
    # O-series (Ousia): Pure cognition — L1×L1
    "O1": {"name": "Noēsis", "series": "O", "wf": "/noe", "level": "L0"},
    "O2": {"name": "Boulēsis", "series": "O", "wf": "/bou", "level": "L0"},
    "O3": {"name": "Zētēsis", "series": "O", "wf": "/zet", "level": "L0"},
    "O4": {"name": "Energeia", "series": "O", "wf": "/ene", "level": "L0"},
    # S-series (Schema): Strategic design — L1×L1.5
    "S1": {"name": "Metron", "series": "S", "wf": "/met", "level": "L1"},
    "S2": {"name": "Mekhanē", "series": "S", "wf": "/mek", "level": "L1"},
    "S3": {"name": "Stathmos", "series": "S", "wf": "/sta", "level": "L1"},
    "S4": {"name": "Praxis", "series": "S", "wf": "/pra", "level": "L1"},
    # H-series (Hormē): Motivation — L1×L1.75
    "H1": {"name": "Propatheia", "series": "H", "wf": "/pro", "level": "L2a"},
    "H2": {"name": "Pistis", "series": "H", "wf": "/pis", "level": "L2a"},
    "H3": {"name": "Orexis", "series": "H", "wf": "/ore", "level": "L2a"},
    "H4": {"name": "Doxa", "series": "H", "wf": "/dox", "level": "L2a"},
    # P-series (Perigraphē): Context placement — L1.5×L1.5
    "P1": {"name": "Khōra", "series": "P", "wf": "/kho", "level": "L2b"},
    "P2": {"name": "Hodos", "series": "P", "wf": "/hod", "level": "L2b"},
    "P3": {"name": "Trokhia", "series": "P", "wf": "/tro", "level": "L2b"},
    "P4": {"name": "Tekhnē", "series": "P", "wf": "/tek", "level": "L2b"},
    # K-series (Kairos): Temporal judgment — L1.5×L1.75
    "K1": {"name": "Eukairia", "series": "K", "wf": "/euk", "level": "L3"},
    "K2": {"name": "Chronos", "series": "K", "wf": "/chr", "level": "L3"},
    "K3": {"name": "Telos", "series": "K", "wf": "/tel", "level": "L3"},
    "K4": {"name": "Sophia", "series": "K", "wf": "/sop", "level": "L3"},
    # A-series (Akribeia): Precision judgment — L1.75×L1.75
    "A1": {"name": "Pathos", "series": "A", "wf": "/pat", "level": "L4"},
    "A2": {"name": "Krisis", "series": "A", "wf": "/dia", "level": "L4"},
    "A3": {"name": "Gnōmē", "series": "A", "wf": "/gno", "level": "L4"},
    "A4": {"name": "Epistēmē", "series": "A", "wf": "/epi", "level": "L4"},
}

# Series metadata for boot summary
SERIES_INFO = {
    "O": "Ousia (認知)", "S": "Schema (戦略)", "H": "Hormē (動機)",
    "P": "Perigraphē (環境)", "K": "Kairos (時間)", "A": "Akribeia (精度)",
}



# PURPOSE: Extract Dispatcher dispatch plan from context
def extract_dispatch_info(context: str, gpu_ok: bool = True) -> dict:
    """Extract Dispatcher dispatch plan from context.

    Graceful degradation: returns empty-primary dict on any failure.
    Separated from _run_attractor() for testability (dia+ issue #1).
    """
    dispatch_info = {"primary": "", "alternatives": [], "dispatch_formatted": ""}
    try:
        from mekhane.fep.attractor_dispatcher import AttractorDispatcher
        dispatcher = AttractorDispatcher(force_cpu=not gpu_ok)
        plan = dispatcher.dispatch(context)
        if plan:
            dispatch_info = {
                "primary": plan.primary.workflow,
                "alternatives": [d.workflow for d in plan.alternatives[:3]],
                "dispatch_formatted": dispatcher.format_compact(plan),
            }
    except Exception:
        pass  # Dispatcher failure should not block boot
    return dispatch_info


def _load_projects(project_root: Path) -> dict:
    """Load project registry from .agent/projects/registry.yaml.

    Returns:
        dict: {
            "projects": [...],   # 全プロジェクト
            "active": int,
            "dormant": int,
            "total": int,
            "formatted": str     # フォーマット済み出力
        }
    """
    result = {"projects": [], "active": 0, "dormant": 0, "total": 0, "formatted": ""}
    registry_path = project_root / ".agent" / "projects" / "registry.yaml"
    if not registry_path.exists():
        return result

    try:
        import yaml
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        projects = data.get("projects", [])
        if not projects:
            return result

        active = [p for p in projects if p.get("status") == "active"]
        dormant = [p for p in projects if p.get("status") == "dormant"]
        archived = [p for p in projects if p.get("status") == "archived"]

        lines = ["📦 **Projects** (registry.yaml)"]
        # Group by category based on path patterns
        categories = {
            "コアランタイム": [],
            "Mekhane モジュール": [],
            "理論・言語基盤": [],
            "研究・概念": [],
            "補助": [],
        }
        for p in projects:
            path = p.get("path", "")
            status = p.get("status", "")
            if status == "archived":
                categories["補助"].append(p)
            elif path.startswith("mekhane/"):
                categories["Mekhane モジュール"].append(p)
            elif path.startswith(".") or p.get("id") in ("kalon", "aristos", "autophonos"):
                categories["研究・概念"].append(p)
            elif p.get("id") in ("ccl", "kernel", "pythosis"):
                categories["理論・言語基盤"].append(p)
            elif p.get("id") in ("hegemonikon-guide",):
                categories["補助"].append(p)
            else:
                categories["コアランタイム"].append(p)

        status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}
        for cat_name, cat_projects in categories.items():
            if not cat_projects:
                continue
            lines.append(f"  [{cat_name}]")
            for p in cat_projects:
                icon = status_icons.get(p.get("status", ""), "❓")
                name = p.get("name", p.get("id", "?"))
                phase = p.get("phase", "")
                summary = p.get("summary", "")
                if len(summary) > 50:
                    summary = summary[:50] + "..."
                line = f"    {icon} {name} [{phase}] — {summary}"
                # entry_point: CLI があれば表示
                ep = p.get("entry_point")
                if ep and isinstance(ep, dict):
                    cli = ep.get("cli", "")
                    if cli:
                        line += f"\n       📎 `{cli}`"
                lines.append(line)
                # usage_trigger: 利用条件を表示
                trigger = p.get("usage_trigger", "")
                if trigger and p.get("status") == "active":
                    lines.append(f"       ⚡ {trigger}")

        lines.append(f"  統計: {len(projects)}件 / Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)}")

        result = {
            "projects": projects,
            "active": len(active),
            "dormant": len(dormant),
            "total": len(projects),
            "formatted": "\n".join(lines),
        }
    except Exception:
        pass  # Registry loading failure should not block boot

    return result


# PURPOSE: /boot 起動時に全 Skill を発見し、Agent がコンテキストに取り込めるようにする
def _load_skills(project_root: Path) -> dict:
    """Load all Skills from .agent/skills/ for boot preloading.

    Returns:
        dict: {
            "skills": [{name, path, description}, ...],
            "count": int,
            "skill_paths": [str, ...],   # view_file 用の絶対パス一覧
            "formatted": str
        }
    """
    result = {"skills": [], "count": 0, "skill_paths": [], "formatted": ""}
    skills_dir = project_root / ".agent" / "skills"
    if not skills_dir.exists():
        return result

    try:
        skills = []
        skill_paths = []
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_dir.is_dir() or not skill_md.exists():
                continue

            # Parse YAML frontmatter
            content = skill_md.read_text(encoding="utf-8")
            name = skill_dir.name
            description = ""
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        meta = yaml.safe_load(parts[1])
                        name = meta.get("name", skill_dir.name)
                        description = meta.get("description", "")
                    except Exception:
                        pass

            abs_path = str(skill_md.resolve())
            # frontmatter 後の本文を抽出
            body = content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    body = parts[2].strip()

            skills.append({
                "name": name,
                "dir": skill_dir.name,
                "path": abs_path,
                "description": description,
                "body": body,
            })
            skill_paths.append(abs_path)

        if not skills:
            return result

        # 環境強制: SKILL.md の内容そのものを出力に含める
        # Agent は boot 出力を読むだけで全 Skill がコンテキストに入る
        # コスト: ~550行 = 200K コンテキストの 0.3%
        lines = [f"🧠 **Skills** ({len(skills)}件 — 全文プリロード済み)"]
        for s in skills:
            lines.append(f"\n{'='*60}")
            lines.append(f"📖 **{s['name']}** — {s['description']}")
            lines.append(f"   Path: `{s['path']}`")
            lines.append(f"{'='*60}")
            lines.append(s["body"])

        result = {
            "skills": skills,
            "count": len(skills),
            "skill_paths": skill_paths,
            "formatted": "\n".join(lines),
        }
    except Exception:
        pass  # Skill loading failure should not block boot

    return result


# PURPOSE: /boot 統合 API: 12軸を boot_axes.py に委譲して統合返却する
def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:
    """
    /boot 統合 API: 12軸を統合して返す (boot_axes.py に委譲)

    GPU プリフライトチェック付き: GPU 占有時は embedding 系を CPU フォールバックで実行

    Args:
        mode: "fast" (/boot-), "standard" (/boot), "detailed" (/boot+)
        context: 現在のコンテキスト（Handoff の主題など）

    Returns:
        dict: 各軸の結果 + "formatted" キーにフォーマット済み出力
    """
    from mekhane.symploke.boot_axes import (
        gpu_preflight as _gpu_pf,
        load_handoffs, load_sophia, load_persona, load_pks,
        load_safety, load_ept, load_digestor, load_attractor,
        load_projects, load_skills, load_doxa, load_feedback,
        load_proactive_push,
    )

    # GPU プリフライトチェック
    gpu_ok, gpu_reason = _gpu_pf()

    # ── 軸ロード (A-L) ──
    handoffs_result = load_handoffs(mode, context)

    # KI コンテキスト: Handoff 主題からフォールバック
    ki_context = context
    if not ki_context and handoffs_result.get("latest"):
        ki_context = handoffs_result["latest"].metadata.get("primary_task", "")
        if not ki_context:
            ki_context = handoffs_result["latest"].content[:200]

    ki_result = load_sophia(mode, context, ki_context=ki_context)
    persona_result = load_persona(mode, context)
    pks_result = load_pks(mode, context, ki_context=ki_context)
    safety_result = load_safety(mode, context)
    ept_result = load_ept(mode, context)
    digestor_result = load_digestor(mode, context)

    # Attractor: Handoff-derived context をフォールバック
    attractor_context = context or ki_context
    attractor_result = load_attractor(mode, attractor_context, gpu_ok=gpu_ok)

    projects_result = load_projects(mode, context)
    skills_result = load_skills(mode, context)
    doxa_result = load_doxa(mode, context)
    feedback_result = load_feedback(mode, context)
    proactive_push_result = load_proactive_push(mode, context)

    # ── 統合フォーマット ──
    lines: list[str] = []

    # 表示順: Persona → Handoff → KI → PKS → Safety → EPT
    #       → Digestor → Attractor → Projects → Skills → Doxa → Feedback
    if persona_result.get("formatted"):
        lines.append(persona_result["formatted"])
        lines.append("")

    if handoffs_result.get("latest"):
        from mekhane.symploke.handoff_search import format_boot_output
        lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))
        lines.append("")

    if ki_result.get("ki_items"):
        from mekhane.symploke.sophia_ingest import format_ki_output
        lines.append(format_ki_output(ki_result))

    for axis_result in [pks_result, safety_result, ept_result, digestor_result,
                        attractor_result, projects_result, skills_result,
                        doxa_result, feedback_result, proactive_push_result]:
        fmt = axis_result.get("formatted", "")
        if fmt:
            lines.append("")
            lines.append(fmt)

    # n8n WF-06: Session Start 通知
    try:
        import urllib.request
        n8n_payload = json.dumps({
            "mode": mode,
            "context": context or "",
            "agent": "Claude",
            "handoff_count": handoffs_result.get("count", 0),
            "ki_count": ki_result.get("count", 0),
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:5678/webhook/session-start",
            data=n8n_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
        print(" 📡 n8n: session started", file=sys.stderr)
    except Exception:
        pass  # n8n 未起動でもブートは継続

    return {
        "handoffs": handoffs_result,
        "ki": ki_result,
        "persona": persona_result,
        "pks": pks_result,
        "safety": safety_result,
        "ept": ept_result,
        "digestor": digestor_result,
        "attractor": attractor_result,
        "projects": projects_result,
        "skills": skills_result,
        "doxa": doxa_result,
        "feedback": feedback_result,
        "proactive_push": proactive_push_result,
        "formatted": "\n".join(lines),
    }




# PURPOSE: Print formatted boot summary
def print_boot_summary(mode: str = "standard", context: Optional[str] = None):
    """Print formatted boot summary."""
    result = get_boot_context(mode=mode, context=context)
    print(result["formatted"])

    # Summary line
    print()
    print("─" * 50)
    h_count = result["handoffs"]["count"]
    ki_count = result["ki"]["count"]
    sessions = result["persona"].get("sessions", 0)
    pks_count = result.get("pks", {}).get("count", 0)
    safety_errors = result.get("safety", {}).get("errors", 0)
    attractor_series = result.get("attractor", {}).get("series", [])
    attractor_str = "+".join(attractor_series) if attractor_series else "—"
    ept_pct = result.get("ept", {}).get("pct", 0)
    ept_str = f"{ept_pct:.0f}%" if ept_pct > 0 else "—"
    proj_total = result.get("projects", {}).get("total", 0)
    proj_active = result.get("projects", {}).get("active", 0)
    proj_str = f"{proj_active}/{proj_total}" if proj_total > 0 else "—"
    fb_total = result.get("feedback", {}).get("total", 0)
    fb_rate = result.get("feedback", {}).get("accept_rate", 0)
    fb_str = f"{fb_rate:.0%}({fb_total})" if fb_total > 0 else "—"
    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety: {'✅' if safety_errors == 0 else f'⚠️{safety_errors}'} | EPT: {ept_str} | PJ: {proj_str} | Attractor: {attractor_str} | FB: {fb_str}")

    # detailed モード: テンプレートファイル生成
    if mode == "detailed":
        template_path = generate_boot_template(result)
        print(f"\n📝 Boot Report Template: {template_path}", file=sys.stderr)
        print(f"TEMPLATE:{template_path}")


# ============================================================
# テンプレート生成 (A+C) — 環境強制: 穴埋め式テンプレート
# ============================================================

# モード別の最低要件定義
MODE_REQUIREMENTS = {
    "detailed": {
        "handoff_count": 10,
        "ki_count": 5,
        "min_chars": 3000,
        "required_sections": [
            "Handoff 個別要約",
            "KI 深読み",
            "Self-Profile 摩擦",
            "意味ある瞬間",
            "Phase 詳細",
            "開発中プロジェクト",
            "タスク提案",
        ],
    },
    "standard": {
        "handoff_count": 3,
        "ki_count": 3,
        "min_chars": 1000,
        "required_sections": [
            "Handoff サマリー",
            "タスク提案",
        ],
    },
    "fast": {
        "handoff_count": 0,
        "ki_count": 0,
        "min_chars": 0,
        "required_sections": [],
    },
}


# PURPOSE: 環境強制: モード別の穴埋めテンプレートを生成する。
def generate_boot_template(result: dict) -> Path:
    """
    環境強制: モード別の穴埋めテンプレートを生成する。

    <!-- REQUIRED --> マーカー付きセクションは必須。
    <!-- FILL --> マーカーは LLM が記入すべき箇所。
    postcheck で未記入の FILL が検出されると FAIL になる。
    """
    now = datetime.now()
    template_path = Path(f"/tmp/boot_report_{now.strftime('%Y%m%d_%H%M')}.md")

    lines = []
    lines.append(f"# Boot Report — {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 必須セクション チェックリスト")
    lines.append("")

    reqs = MODE_REQUIREMENTS.get("detailed", {})
    for section in reqs.get("required_sections", []):
        lines.append(f"- [ ] {section}")
    lines.append("")

    # --- Handoff 個別要約 ---
    lines.append("## Handoff 個別要約")
    lines.append("<!-- REQUIRED: 各 Handoff の S/A/R を1行以上 -->")
    lines.append("")

    handoffs = result.get("handoffs", {})
    related = handoffs.get("related", [])
    latest = handoffs.get("latest")

    all_handoffs = []
    if latest:
        all_handoffs.append(latest)
    if related:
        all_handoffs.extend(related)

    for i, h in enumerate(all_handoffs[:10], 1):
        title = "Unknown"
        if hasattr(h, "metadata"):
            title = h.metadata.get("primary_task", h.metadata.get("title", "Unknown"))
        elif isinstance(h, dict):
            title = h.get("primary_task", h.get("title", "Unknown"))
        lines.append(f"### Handoff {i}: {title}")
        lines.append("")
        lines.append("> 要約: <!-- FILL -->")
        lines.append("")

    # --- KI 深読み ---
    lines.append("## KI 深読み")
    lines.append("<!-- REQUIRED: サマリー引用 + 自分の解釈を記述 -->")
    lines.append("")

    ki_items = result.get("ki", {}).get("ki_items", [])
    for i, ki in enumerate(ki_items[:5], 1):
        name = "Unknown"
        summary = "N/A"
        if hasattr(ki, "metadata"):
            name = ki.metadata.get("ki_name", "Unknown")
            summary = ki.metadata.get("summary", "N/A")
        elif isinstance(ki, dict):
            name = ki.get("ki_name", "Unknown")
            summary = ki.get("summary", "N/A")
        lines.append(f"### KI {i}: {name}")
        lines.append("")
        lines.append(f"> サマリー: {summary[:100]}")
        lines.append("> 解釈: <!-- FILL -->")
        lines.append("")

    # 不足分はプレースホルダー
    for i in range(len(ki_items) + 1, 6):
        lines.append(f"### KI {i}: (session context から選択)")
        lines.append("")
        lines.append("> サマリー: <!-- FILL -->")
        lines.append("> 解釈: <!-- FILL -->")
        lines.append("")

    # --- Self-Profile 摩擦 ---
    lines.append("## Self-Profile 摩擦")
    lines.append("<!-- REQUIRED: ミスパターンとの摩擦を明示 -->")
    lines.append("")
    lines.append("今回のセッションで注意すべきミスパターン: <!-- FILL -->")
    lines.append("")

    # --- 意味ある瞬間 ---
    lines.append("## 意味ある瞬間")
    lines.append("<!-- REQUIRED: 各瞬間に対する自分の解釈を記述 -->")
    lines.append("")
    lines.append("解釈: <!-- FILL -->")
    lines.append("")

    # --- Phase 詳細 ---
    lines.append("## Phase 詳細")
    lines.append("<!-- REQUIRED: 各 Phase の展開された詳細を出力 -->")
    lines.append("")
    for phase in range(7):
        lines.append(f"### Phase {phase}")
        lines.append("")
        lines.append("<!-- FILL -->")
        lines.append("")

    # --- 開発中プロジェクト ---
    lines.append("## 開発中プロジェクト")
    lines.append("<!-- REQUIRED: registry.yaml から読み込んだ PJ 一覧 -->")
    lines.append("")

    projects = result.get("projects", {}).get("projects", [])
    if projects:
        status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}
        active = [p for p in projects if p.get("status") == "active"]
        dormant = [p for p in projects if p.get("status") == "dormant"]
        archived = [p for p in projects if p.get("status") == "archived"]
        # 全PJを表示（status で区別）— dormant/archived を省略しない
        for p in projects:
            icon = status_icons.get(p.get("status", ""), "❓")
            name = p.get("name", p.get("id", "?"))
            phase = p.get("phase", "")
            summary_text = p.get("summary", "")
            lines.append(f"- {icon} **{name}** [{phase}]: {summary_text}")
        lines.append("")
        lines.append(f"統計: Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)} / Total {len(projects)}")
    else:
        lines.append("<!-- FILL: registry.yaml が見つかりません -->")
    lines.append("")

    # --- タスク提案 ---
    lines.append("## タスク提案")
    lines.append("<!-- REQUIRED: Handoff から抽出したタスク提案 -->")
    lines.append("")
    lines.append("1. <!-- FILL -->")
    lines.append("")

    template_path.write_text("\n".join(lines), encoding="utf-8")
    return template_path


# ============================================================
# ポストチェック (B) — 環境強制: 記入済みレポートの検証
# ============================================================

# PURPOSE: 記入済み boot report を検証する。
def postcheck_boot_report(report_path: str, mode: str = "detailed") -> dict:
    """
    記入済み boot report を検証する。

    Returns:
        dict: {
            "passed": bool,
            "checks": [{"name": str, "passed": bool, "detail": str}],
            "formatted": str
        }
    """
    path = Path(report_path)
    if not path.exists():
        return {
            "passed": False,
            "checks": [{"name": "file_exists", "passed": False, "detail": f"File not found: {report_path}"}],
            "formatted": f"❌ Boot Report Validation: FAIL\n  ❌ File not found: {report_path}",
        }

    content = path.read_text(encoding="utf-8")
    reqs = MODE_REQUIREMENTS.get(mode, MODE_REQUIREMENTS["standard"])
    checks = []

    # Check 1: <!-- FILL --> の残存数
    fill_count = content.count("<!-- FILL -->")
    checks.append({
        "name": "unfilled_sections",
        "passed": fill_count == 0,
        "detail": f"{'No' if fill_count == 0 else fill_count} unfilled sections"
            + ("" if fill_count == 0 else f" remaining (<!-- FILL --> found {fill_count}x)"),
    })

    # Check 2: REQUIRED セクション数
    required_count = content.count("<!-- REQUIRED")
    expected = len(reqs.get("required_sections", []))
    checks.append({
        "name": "required_sections",
        "passed": required_count >= expected,
        "detail": f"Required sections: {required_count}/{expected}",
    })

    # Check 3: 総文字数
    min_chars = reqs.get("min_chars", 0)
    char_count = len(content)
    checks.append({
        "name": "content_length",
        "passed": char_count >= min_chars,
        "detail": f"Content length: {char_count} chars"
            + (f" (≥ {min_chars})" if char_count >= min_chars else f" (< {min_chars}, need {min_chars - char_count} more)"),
    })

    # Check 4: Handoff 引用数 (### Handoff N: の数)
    handoff_refs = len(re.findall(r"^### Handoff \d+:", content, re.MULTILINE))
    expected_h = reqs.get("handoff_count", 0)
    checks.append({
        "name": "handoff_references",
        "passed": handoff_refs >= expected_h,
        "detail": f"Handoff references: {handoff_refs}"
            + (f" (≥ {expected_h})" if handoff_refs >= expected_h else f" (< {expected_h})"),
    })

    # Check 5: チェックリスト完了率
    unchecked = content.count("- [ ]")
    checked = content.count("- [x]")
    total_checks = unchecked + checked
    all_checked = unchecked == 0 and total_checks > 0
    checks.append({
        "name": "checklist_completion",
        "passed": all_checked,
        "detail": f"Checklist: {checked}/{total_checks} completed"
            + ("" if all_checked else f" ({unchecked} remaining)"),
    })
    # Check 6: Intent-WAL 空チェック (Plan Object 案D — 環境強制)
    # /boot- (fast) では省略可、/boot, /boot+ では必須
    if mode != "fast":
        has_intent_wal = bool(re.search(
            r"intent_wal:|session_goal:", content, re.IGNORECASE
        ))
        # WAL が存在する場合、session_goal がプレースホルダーのままでないか確認
        wal_filled = has_intent_wal and not bool(re.search(
            r'session_goal:\s*["\']?\{', content
        ))
        checks.append({
            "name": "intent_wal",
            "passed": wal_filled,
            "detail": "Intent-WAL: "
                + ("✅ declared" if wal_filled else "❌ missing or unfilled")
                + (" (required for /boot and /boot+)" if not wal_filled else ""),
        })

    # Drift = 1 - ε (失われた文脈の量)
    # ε precision: Handoff への言及 + Self-Profile 参照 + 意味ある瞬間の記述
    # BS-3b fix: FILL 残存率で ε を割り引く
    #   テンプレート見出しに "Handoff" 等が含まれるため、
    #   記入前でもパターンマッチが成立してしまう問題を解消
    adjunction_indicators = {
        "handoff_context": bool(re.search(r"(?:引き継ぎ|handoff|Handoff|前回)", content, re.IGNORECASE)),
        "self_profile_ref": bool(re.search(r"(?:self.profile|ミスパターン|能力境界|Self-Profile)", content, re.IGNORECASE)),
        "meaningful_moment": bool(re.search(r"(?:意味ある瞬間|印象的|感動|発見)", content, re.IGNORECASE)),
        "task_continuity": bool(re.search(r"(?:前回の続き|継続|再開|残タスク)", content, re.IGNORECASE)),
    }
    epsilon_count = sum(adjunction_indicators.values())
    epsilon_raw = epsilon_count / len(adjunction_indicators)

    # BS-3b: FILL 残存ペナルティ (dia+ TH-005)
    # 未記入セクションが多い → テンプレート見出しのマッチは信頼できない
    fill_remaining = content.count("<!-- FILL -->")
    if fill_remaining > 0:
        # fill_ratio = 記入完了率 (0.0 = 全未記入, 1.0 = 全記入)
        # 推定: テンプレートは ~25 FILL マーカーを含む (detailed mode)
        estimated_total_fills = max(fill_remaining, 25)
        fill_ratio = 1.0 - (fill_remaining / estimated_total_fills)
        epsilon_precision = epsilon_raw * fill_ratio
    else:
        epsilon_precision = epsilon_raw

    drift = 1.0 - epsilon_precision
    checks.append({
        "name": "adjunction_metrics",
        "passed": True,  # Informational only, never blocks
        "detail": f"Adjunction L⊣R: ε={epsilon_precision:.0%}, Drift={drift:.0%}"
            + (f" (fill_penalty: {fill_remaining} FILL remaining)" if fill_remaining > 0 else "")
            + f" ({', '.join(k for k, v in adjunction_indicators.items() if v)})"
            if epsilon_count > 0
            else f"Adjunction L⊣R: ε=0%, Drift=100% (no context restoration detected)",
    })

    # 結果集計
    passed_count = sum(1 for c in checks if c["passed"])
    total = len(checks)
    all_passed = all(c["passed"] for c in checks)

    # フォーマット
    status = "PASS" if all_passed else "FAIL"
    icon = "✅" if all_passed else "❌"
    lines = [f"{icon} Boot Report Validation: {status} ({passed_count}/{total} checks)"]
    for c in checks:
        ci = "✅" if c["passed"] else "❌"
        lines.append(f"  {ci} {c['detail']}")

    return {
        "passed": all_passed,
        "checks": checks,
        "formatted": "\n".join(lines),
    }


# PURPOSE: main の処理
def main():
    parser = argparse.ArgumentParser(description="Boot integration API")
    parser.add_argument(
        "--mode",
        choices=["fast", "standard", "detailed"],
        default="standard",
        help="Boot mode",
    )
    parser.add_argument("--context", type=str, help="Context for search")
    parser.add_argument(
        "--postcheck",
        type=str,
        metavar="REPORT_PATH",
        help="Post-check a completed boot report file",
    )
    args = parser.parse_args()

    import warnings

    warnings.filterwarnings("ignore")

    # ポストチェックモード
    if args.postcheck:
        result = postcheck_boot_report(args.postcheck, mode=args.mode)
        print(result["formatted"])
        sys.exit(0 if result["passed"] else 1)

    # 通常ブートモード
    print(f"⏳ Boot Mode: {args.mode}", file=sys.stderr)

    try:
        print_boot_summary(mode=args.mode, context=args.context)
    except KeyboardInterrupt:
        print("\n⚠️ Boot sequence interrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Boot sequence failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

