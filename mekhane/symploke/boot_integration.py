#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→継続する私が必要→boot_integration が担う
"""
Boot Integration - 8軸を統合した /boot 用 API

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


def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:
    """
    /boot 統合 API: 8軸（Handoff, Sophia, Persona, PKS, Safety, EPT, Digestor, Attractor）を統合して返す

    GPU プリフライトチェック付き: GPU 占有時は embedding 系を CPU フォールバックで実行

    Args:
        mode: "fast" (/boot-), "standard" (/boot), "detailed" (/boot+)
        context: 現在のコンテキスト（Handoff の主題など）

    Returns:
        dict: {
            "handoffs": {...},    # 軸 A
            "ki": {...},          # 軸 B
            "persona": {...},     # 軸 C
            "pks": {...},         # 軸 D
            "safety": {...},      # 軸 E
            "ept": {...},          # 軸 H
            "attractor": {...},   # 軸 F
            "formatted": str      # フォーマット済み出力
        }
    """
    # GPU プリフライトチェック (G)
    gpu_ok = True
    gpu_reason = ""
    try:
        from mekhane.symploke.gpu_guard import gpu_preflight, force_cpu_env
        gpu_status = gpu_preflight()
        gpu_ok = gpu_status.gpu_available
        gpu_reason = gpu_status.reason
        if not gpu_ok:
            print(f" ⚠️ GPU busy ({gpu_reason}), embedding 系は CPU フォールバック", file=sys.stderr)
            force_cpu_env()  # CUDA_VISIBLE_DEVICES="" を設定
        else:
            print(f" 🟢 GPU available ({gpu_status.utilization}%, {gpu_status.memory_used_mb}MiB)", file=sys.stderr)
    except Exception:
        pass  # GPU チェック失敗時は無視して続行

    # 軸 A: Handoff 活用
    print(" [1/8] 📋 Searching Handoffs...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.handoff_search import get_boot_handoffs, format_boot_output

    handoffs_result = get_boot_handoffs(mode=mode, context=context)
    print(" Done.", file=sys.stderr)

    # 軸 B: Sophia アクティベーション (タイムアウト付き)
    print(" [2/8] 📚 Ingesting Knowledge (Sophia)...", file=sys.stderr, end="", flush=True)
    # コンテキストを Handoff から取得
    ki_context = context
    if not ki_context and handoffs_result["latest"]:
        ki_context = handoffs_result["latest"].metadata.get("primary_task", "")
        if not ki_context:
            ki_context = handoffs_result["latest"].content[:200]

    ki_result = {"ki_items": [], "count": 0}
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

        def _run_sophia():
            from mekhane.symploke.sophia_ingest import get_boot_ki, format_ki_output
            return get_boot_ki(context=ki_context, mode=mode)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_sophia)
            ki_result = future.result(timeout=15.0)
        print(" Done.", file=sys.stderr)
    except (FutureTimeout, TimeoutError):
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)
    print(" [3/8] 👤 Loading Persona...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.persona import get_boot_persona

    persona_result = get_boot_persona(mode=mode)
    print(" Done.", file=sys.stderr)

    # 軸 D: PKS (能動的知識プッシュ)
    # 重い処理なのでタイムアウトを設定
    pks_result = {"nuggets": [], "count": 0, "formatted": ""}
    
    if mode != "fast":  # fastモードではPKSをスキップ
        print(" [4/8] 🧠 Activating PKS Engine...", file=sys.stderr, end="", flush=True)
        try:
            from concurrent.futures import ThreadPoolExecutor
            
            def _run_pks():
                from mekhane.pks.pks_engine import PKSEngine
                pks_engine = PKSEngine(threshold=0.5, max_push=3)
                
                # コンテキスト設定
                pks_topics = []
                if context:
                    pks_topics = [t.strip() for t in context.split(",")]
                elif ki_context:
                    # KI コンテキストからトピック抽出
                    words = ki_context.split()[:5]
                    pks_topics = [w for w in words if len(w) > 2]
                
                if pks_topics:
                    pks_engine.set_context(topics=pks_topics)
                    return pks_engine.proactive_push(k=10)
                return []

            # 10秒タイムアウト (detailedでも待たせすぎない)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_pks)
                nuggets = future.result(timeout=10.0)
                
            if nuggets:
                from mekhane.pks.pks_engine import PKSEngine  # 型ヒント用
                # インスタンス化せずにフォーマットメソッドだけ借用したいが、インスタンスメソッドなので
                # 簡易フォーマッターを使用するか、再インスタンス化する（軽量）
                pks_engine_dummy = PKSEngine()
                pks_result = {
                    "nuggets": nuggets,
                    "count": len(nuggets),
                    "formatted": pks_engine_dummy.format_push_report(nuggets),
                }
            print(" Done.", file=sys.stderr)
            
        except TimeoutError:
            print(" Timeout (skipped).", file=sys.stderr)
        except Exception as e:
            print(f" Failed ({str(e)}).", file=sys.stderr)
    else:
         print(" [4/8] 🧠 PKS Engine skipped (fast mode).", file=sys.stderr)

    # 軸 E: Safety Contract Audit (v3.1)
    safety_result = {"skills": 0, "workflows": 0, "errors": 0, "warnings": 0, "formatted": ""}
    print(" [5/8] 🛡️ Running Safety Contract Audit...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.dendron.skill_checker import run_audit, AuditResult
        agent_dir = Path(__file__).parent.parent.parent / ".agent"
        if agent_dir.exists():
            audit = run_audit(agent_dir)
            dist = audit.risk_distribution()
            lcm = audit.lcm_distribution()
            safety_lines = []
            safety_lines.append("🛡️ **Safety Contract**")
            safety_lines.append(f"  Skills: {audit.skills_checked} | WF: {audit.workflows_checked}")
            risk_parts = [f"{k}:{v}" for k, v in dist.items() if v > 0]
            if risk_parts:
                safety_lines.append(f"  Risk: {' '.join(risk_parts)}")
            lcm_parts = [f"{k}:{v}" for k, v in lcm.items() if v > 0]
            if lcm_parts:
                safety_lines.append(f"  LCM:  {' '.join(lcm_parts)}")
            if audit.errors > 0:
                safety_lines.append(f"  ⚠️ {audit.errors} error(s), {audit.warnings} warning(s)")
            safety_result = {
                "skills": audit.skills_checked,
                "workflows": audit.workflows_checked,
                "errors": audit.errors,
                "warnings": audit.warnings,
                "formatted": "\n".join(safety_lines),
            }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)

    # 軸 H: EPT (Existence Purpose Tensor)
    ept_result = {"score": 0, "total": 0, "pct": 0, "formatted": ""}
    print(" [6/8] 📐 Running EPT Matrix...", file=sys.stderr, end="", flush=True)
    try:
        from concurrent.futures import ThreadPoolExecutor
        def _run_ept():
            from mekhane.dendron.checker import DendronChecker
            c = DendronChecker(
                check_structure=True,
                check_function_nf=True,
                check_verification=True,
            )
            r = c.check(Path(__file__).parent.parent)  # mekhane/
            total = r.total_structure_checks + r.total_function_nf_checks + r.total_verification_checks
            ok = r.structure_ok + r.function_nf_ok + r.verification_ok
            pct = (ok / total * 100) if total > 0 else 0
            return {
                "score": ok, "total": total, "pct": pct,
                "nf2": f"{r.structure_ok}/{r.total_structure_checks}",
                "nf3": f"{r.function_nf_ok}/{r.total_function_nf_checks}",
                "bcnf": f"{r.verification_ok}/{r.total_verification_checks}",
                "formatted": f"📐 **EPT**: {ok}/{total} ({pct:.0f}%) [NF2:{r.structure_ok}/{r.total_structure_checks} NF3:{r.function_nf_ok}/{r.total_function_nf_checks} BCNF:{r.verification_ok}/{r.total_verification_checks}]",
            }
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_ept)
            ept_result = future.result(timeout=10.0)
        print(" Done.", file=sys.stderr)
    except TimeoutError:
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)

    # 軸 G: Digestor 候補 (論文レコメンド)
    digestor_result = {"candidates": [], "count": 0, "formatted": ""}
    print(" [7/8] 📄 Loading Digest Candidates...", file=sys.stderr, end="", flush=True)
    try:
        import glob
        digest_dir = Path.home() / ".hegemonikon" / "digestor"
        reports = sorted(glob.glob(str(digest_dir / "digest_report_*.json")), reverse=True)
        if reports:
            with open(reports[0], "r", encoding="utf-8") as f:
                report = json.load(f)
            candidates = report.get("candidates", [])[:3]
            if candidates:
                digest_lines = ["📄 **Digest Candidates** (今日の論文推薦)"]
                for i, c in enumerate(candidates, 1):
                    title = c.get("title", "Unknown")[:60]
                    score = c.get("score", 0)
                    topics = ", ".join(c.get("matched_topics", [])[:2])
                    digest_lines.append(f"  {i}. [{score:.2f}] {title}... ({topics})")
                digestor_result = {
                    "candidates": candidates,
                    "count": len(candidates),
                    "formatted": "\n".join(digest_lines),
                }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)

    # 軸 F: Attractor Dispatch Engine
    attractor_result = {"series": [], "workflows": [], "llm_format": "", "formatted": ""}
    if context:
        print(" [8/8] 🎯 Attractor Dispatch...", file=sys.stderr, end="", flush=True)
        try:
            from concurrent.futures import ThreadPoolExecutor

            def _run_attractor():
                from mekhane.fep.attractor_advisor import AttractorAdvisor
                advisor = AttractorAdvisor(force_cpu=not gpu_ok)

                # Problem C: 過去の basin bias を適用
                try:
                    from mekhane.fep.basin_logger import BasinLogger
                    basin_logger = BasinLogger()
                    log_files = sorted(basin_logger.log_dir.glob("attractor_log_*.jsonl"))
                    if log_files:
                        for lf in log_files[-3:]:  # 直近3日分
                            basin_logger.load_biases(lf)
                        advisor._attractor.apply_bias(basin_logger._biases)
                except Exception:
                    pass  # Bias loading failure should not block boot

                rec = advisor.recommend(context)
                llm_fmt = advisor.format_for_llm(context)

                # Dispatcher integration (Problem A)
                dispatch_info = extract_dispatch_info(context, gpu_ok=gpu_ok)

                formatted_parts = []
                if llm_fmt:
                    formatted_parts.append(f"🎯 **Attractor**: {llm_fmt}")
                if dispatch_info["primary"]:
                    formatted_parts.append(f"   📎 Dispatch: {dispatch_info['dispatch_formatted']}")

                return {
                    "series": rec.series,
                    "workflows": rec.workflows,
                    "llm_format": llm_fmt,
                    "confidence": rec.confidence,
                    "oscillation": rec.oscillation.value,
                    "advice": rec.advice,
                    "dispatch_primary": dispatch_info["primary"],
                    "dispatch_alternatives": dispatch_info["alternatives"],
                    "formatted": "\n".join(formatted_parts) if formatted_parts else "",
                }

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_attractor)
                attractor_result = future.result(timeout=30.0)
            print(" Done.", file=sys.stderr)
        except TimeoutError:
            print(" Timeout (skipped).", file=sys.stderr)
        except Exception as e:
            print(f" Failed ({str(e)}).", file=sys.stderr)
    else:
        print(" [8/8] 🎯 Attractor skipped (no context).", file=sys.stderr)

    # 統合フォーマット
    lines = []

    # Persona (最初に)
    if persona_result.get("formatted"):
        lines.append(persona_result["formatted"])
        lines.append("")

    # Handoff
    if handoffs_result["latest"]:
        lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))
        lines.append("")

    # KI
    if ki_result["ki_items"]:
        from mekhane.symploke.sophia_ingest import format_ki_output
        lines.append(format_ki_output(ki_result))

    # PKS
    if pks_result["formatted"]:
        lines.append("")
        lines.append(pks_result["formatted"])

    # Safety Contract
    if safety_result["formatted"]:
        lines.append("")
        lines.append(safety_result["formatted"])

    # EPT
    if ept_result["formatted"]:
        lines.append("")
        lines.append(ept_result["formatted"])

    # Digestor
    if digestor_result["formatted"]:
        lines.append("")
        lines.append(digestor_result["formatted"])

    # Attractor
    if attractor_result["formatted"]:
        lines.append("")
        lines.append(attractor_result["formatted"])

    # n8n WF-06: Session Start 通知
    try:
        import urllib.request
        n8n_payload = json.dumps({
            "mode": mode,
            "context": context or "",
            "agent": "Claude",
            "handoff_count": handoffs_result["count"],
            "ki_count": ki_result["count"],
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
        "formatted": "\n".join(lines),
    }


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
    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety: {'✅' if safety_errors == 0 else f'⚠️{safety_errors}'} | EPT: {ept_str} | Attractor: {attractor_str}")

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

    # Check 6: 随伴メトリクス (Adjunction L⊣R)
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

