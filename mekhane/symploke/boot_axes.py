# PROOF: [L2/インフラ] <- mekhane/symploke/
# PURPOSE: Boot 軸ローダー群 — boot_integration.py から抽出された個別軸ロード関数
"""
Boot Axes — get_boot_context() から抽出された 16 軸ローダー.

各関数は同じパターン:
    1. デフォルト結果を定義
    2. ステータス出力 (stderr)
    3. try/except でグレースフルロード
    4. {"key": ..., "formatted": str} を返却

Design: boot_integration.py のゴッド関数 (600行) を構造化するためのリファクタリング。
API 互換は完全維持 — 戻り値の型と key は一切変えない。
"""

from __future__ import annotations

import copy
import json
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────
# GPU Preflight
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: boot_axes の gpu preflight 処理を実行する
def gpu_preflight() -> tuple[bool, str]:
    """GPU プリフライトチェック。

    Returns:
        (gpu_ok, reason)
    """
    try:
        from mekhane.symploke.gpu_guard import gpu_preflight as _gp, force_cpu_env
        status = _gp()
        if not status.gpu_available:
            print(f" ⚠️ GPU busy ({status.reason}), embedding 系は CPU フォールバック", file=sys.stderr)
            force_cpu_env()
            return False, status.reason
        print(f" 🟢 GPU available ({status.utilization}%, {status.memory_used_mb}MiB)", file=sys.stderr)
        return True, ""
    except Exception:
        return True, ""  # GPU チェック失敗時は楽観的に続行


# ─────────────────────────────────────────────────────────────────────
# 軸 A: Handoff
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: handoffs を読み込む
def load_handoffs(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"latest": None, "related": [], "conversations": [], "count": 0}
    print(" [1/13] 📋 Searching Handoffs...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.symploke.handoff_search import get_boot_handoffs
        result = get_boot_handoffs(mode=mode, context=context)
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 B: Sophia (KI)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: sophia を読み込む
def load_sophia(mode: str, context: Optional[str] = None, **kw) -> dict:
    print(" [2/13] 📚 Ingesting Knowledge (Sophia)...", file=sys.stderr, end="", flush=True)
    ki_context = context or kw.get("ki_context")
    ki_result: dict = {"ki_items": [], "count": 0}
    try:
        def _run():
            from mekhane.symploke.sophia_ingest import get_boot_ki
            return get_boot_ki(context=ki_context, mode=mode)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run)
            ki_result = future.result(timeout=15.0)
        print(" Done.", file=sys.stderr)
    except (FutureTimeout, TimeoutError):
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return ki_result


# ─────────────────────────────────────────────────────────────────────
# 軸 C: Persona
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: persona を読み込む
def load_persona(mode: str, context: Optional[str] = None, **kw) -> dict:
    print(" [3/13] 👤 Loading Persona...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.persona import get_boot_persona
    result = get_boot_persona(mode=mode)
    print(" Done.", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 D: PKS (能動的知識プッシュ)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: pks を読み込む
def load_pks(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"nuggets": [], "count": 0, "formatted": ""}
    if mode == "fast":
        print(" [4/13] 🧠 PKS Engine skipped (fast mode).", file=sys.stderr)
        return result

    print(" [4/13] 🧠 Activating PKS Engine...", file=sys.stderr, end="", flush=True)
    ki_context = kw.get("ki_context")
    try:
        def _run():
            from mekhane.pks.pks_engine import PKSEngine
            engine = PKSEngine(threshold=0.5, max_push=3)
            topics: list = []
            if context:
                topics = [t.strip() for t in context.split(",")]
            elif ki_context:
                words = ki_context.split()[:5]
                topics = [w for w in words if len(w) > 2]
            if topics:
                engine.set_context(topics=topics)
                return engine.proactive_push(k=10)
            return []

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run)
            nuggets = future.result(timeout=10.0)

        if nuggets:
            from mekhane.pks.pks_engine import PKSEngine
            dummy = PKSEngine()
            result = {
                "nuggets": nuggets,
                "count": len(nuggets),
                "formatted": dummy.format_push_report(nuggets),
            }
        print(" Done.", file=sys.stderr)
    except TimeoutError:
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 E: Safety Contract Audit
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: safety を読み込む
def load_safety(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"skills": 0, "workflows": 0, "errors": 0, "warnings": 0, "formatted": ""}
    print(" [5/13] 🛡️ Running Safety Contract Audit...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.dendron.skill_checker import run_audit
        agent_dir = Path(__file__).parent.parent.parent / ".agent"
        if agent_dir.exists():
            audit = run_audit(agent_dir)
            dist = audit.risk_distribution()
            lcm = audit.lcm_distribution()
            lines = ["🛡️ **Safety Contract**"]
            lines.append(f"  Skills: {audit.skills_checked} | WF: {audit.workflows_checked}")
            risk_parts = [f"{k}:{v}" for k, v in dist.items() if v > 0]
            if risk_parts:
                lines.append(f"  Risk: {' '.join(risk_parts)}")
            lcm_parts = [f"{k}:{v}" for k, v in lcm.items() if v > 0]
            if lcm_parts:
                lines.append(f"  LCM:  {' '.join(lcm_parts)}")
            if audit.errors > 0:
                lines.append(f"  ⚠️ {audit.errors} error(s), {audit.warnings} warning(s)")
            result = {
                "skills": audit.skills_checked,
                "workflows": audit.workflows_checked,
                "errors": audit.errors,
                "warnings": audit.warnings,
                "formatted": "\n".join(lines),
            }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 H: EPT (Existence Purpose Tensor)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: ept を読み込む
def load_ept(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"score": 0, "total": 0, "pct": 0, "formatted": ""}
    print(" [6/13] 📐 Running EPT Matrix...", file=sys.stderr, end="", flush=True)
    try:
        def _run():
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
                "formatted": (
                    f"📐 **EPT**: {ok}/{total} ({pct:.0f}%) "
                    f"[NF2:{r.structure_ok}/{r.total_structure_checks} "
                    f"NF3:{r.function_nf_ok}/{r.total_function_nf_checks} "
                    f"BCNF:{r.verification_ok}/{r.total_verification_checks}]"
                ),
            }
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run)
            result = future.result(timeout=10.0)
        print(" Done.", file=sys.stderr)
    except TimeoutError:
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 G: Digestor 候補 (論文レコメンド)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: digestor を読み込む
def load_digestor(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"candidates": [], "count": 0, "formatted": ""}
    print(" [7/13] 📄 Loading Digest Candidates...", file=sys.stderr, end="", flush=True)
    try:
        import glob
        digest_dir = Path.home() / ".hegemonikon" / "digestor"
        reports = sorted(glob.glob(str(digest_dir / "digest_report_*.json")), reverse=True)
        if reports:
            with open(reports[0], "r", encoding="utf-8") as f:
                report = json.load(f)
            candidates = report.get("candidates", [])[:3]
            if candidates:
                lines = ["📄 **Digest Candidates** (今日の論文推薦)"]
                for i, c in enumerate(candidates, 1):
                    title = c.get("title", "Unknown")[:60]
                    score = c.get("score", 0)
                    topics = ", ".join(c.get("matched_topics", [])[:2])
                    lines.append(f"  {i}. [{score:.2f}] {title}... ({topics})")
                result = {
                    "candidates": candidates,
                    "count": len(candidates),
                    "formatted": "\n".join(lines),
                }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 F: Attractor Dispatch Engine (最大: FEP v2 + TheoremAttractor 統合)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: attractor を読み込む
def load_attractor(mode: str, context: Optional[str] = None, **kw) -> dict:
    """Attractor 軸: Series 推薦 + Theorem 粒度 + FEP v2 統合推論."""
    result: dict = {"series": [], "workflows": [], "llm_format": "", "formatted": ""}
    gpu_ok = kw.get("gpu_ok", True)
    attractor_context = context

    if not attractor_context:
        print(" [8/13] 🎯 Attractor skipped (no context & no Handoff).", file=sys.stderr)
        return result

    print(" [8/13] 🎯 Attractor Dispatch...", file=sys.stderr, end="", flush=True)
    try:
        def _run():
            from mekhane.fep.attractor_advisor import AttractorAdvisor
            advisor = AttractorAdvisor(force_cpu=not gpu_ok)

            # Basin bias 復元
            _apply_basin_bias(advisor)
            _apply_basin_learner(advisor)

            rec = advisor.recommend(attractor_context)
            llm_fmt = advisor.format_for_llm(attractor_context)

            # 統合情報収集
            from mekhane.symploke.boot_integration import extract_dispatch_info
            dispatch_info = extract_dispatch_info(attractor_context, gpu_ok=gpu_ok)
            theorem_detail = _build_theorem_detail(attractor_context, gpu_ok)
            fep_v2_result, learning_diff_fmt = _run_fep_v2(
                rec, attractor_context, gpu_ok,
            )

            # フォーマット
            formatted = _format_attractor(
                llm_fmt, theorem_detail, dispatch_info,
                fep_v2_result, learning_diff_fmt,
            )

            return {
                "series": rec.series,
                "workflows": rec.workflows,
                "llm_format": llm_fmt,
                "confidence": rec.confidence,
                "oscillation": rec.oscillation.value,
                "advice": rec.advice,
                "dispatch_primary": dispatch_info["primary"],
                "dispatch_alternatives": dispatch_info["alternatives"],
                "theorem_detail": theorem_detail,
                "fep_v2": fep_v2_result,
                "formatted": formatted,
            }

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run)
            result = future.result(timeout=30.0)
        print(" Done.", file=sys.stderr)
    except TimeoutError:
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


def _apply_basin_bias(advisor: Any) -> None:
    """Basin Logger bias 復元."""
    try:
        from mekhane.fep.basin_logger import BasinLogger
        bl = BasinLogger()
        log_files = sorted(bl.log_dir.glob("attractor_log_*.jsonl"))
        if log_files:
            for lf in log_files[-3:]:
                bl.load_biases(lf)
            advisor._attractor.apply_bias(bl._biases)
    except Exception:
        pass


def _apply_basin_learner(advisor: Any) -> None:
    """BasinLearner 学習済み重み適用."""
    try:
        from mekhane.fep.basin_learner import BasinLearner
        learner = BasinLearner()
        if learner.load_history() > 0:
            overrides = learner.get_weight_overrides()
            if overrides:
                for series, weight in overrides.items():
                    adjustment = (weight - 1.0) * 0.1
                    advisor._attractor._bias_adjustments[series] = adjustment
    except Exception:
        pass


def _build_theorem_detail(context: str, gpu_ok: bool) -> dict:
    """TheoremAttractor による 24 定理粒度の詳細."""
    try:
        from mekhane.fep.theorem_attractor import TheoremAttractor
        ta = TheoremAttractor(force_cpu=not gpu_ok)
        top_theorems = ta.suggest(context, top_k=5)
        flow = ta.simulate_flow(context, steps=10)
        mixture = ta.diagnose_mixture(context)
        return {
            "top_theorems": [
                {"theorem": r.theorem, "name": r.name,
                 "series": r.series, "sim": round(r.similarity, 3),
                 "command": r.command}
                for r in top_theorems
            ],
            "flow_converged": flow.converged_at,
            "flow_final": [t for t, _ in flow.final_theorems[:3]],
            "mixture": {
                "entropy": mixture.entropy,
                "dominant_series": mixture.dominant_series,
                "series_distribution": mixture.series_distribution,
            },
        }
    except Exception:
        return {}


def _run_fep_v2(rec: Any, context: str, gpu_ok: bool) -> tuple[dict, str]:
    """FEP v2 Agent: 統合認知判断 (48-state)."""
    import numpy as np
    fep_v2_result: dict = {}
    learning_diff_fmt = ""
    try:
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        from mekhane.fep.state_spaces_v2 import SERIES_STATES
        from mekhane.fep.persistence import (
            save_snapshot, diff_A, format_learning_diff,
        )

        agent = HegemonikónFEPAgentV2()
        agent.load_learned_A()
        agent.load_learned_B()
        agent.load_epsilon()

        A_before = copy.deepcopy(agent.agent.A)

        _s2obs = {s: 8 + i for i, s in enumerate(SERIES_STATES)}
        att_series = rec.series
        if isinstance(att_series, list):
            att_series = att_series[0]
        topic_obs = _s2obs.get(att_series, 8)

        r1 = agent.step(topic_obs)
        r2 = agent.step(topic_obs)
        final = r2

        agent.update_A_dirichlet(topic_obs)
        agent.update_B_dirichlet(final["action"])

        predicted_obs = int(np.argmax(agent._get_predicted_observation()))
        agent.track_prediction(topic_obs, predicted_obs)
        agent.update_epsilon()

        agent.save_learned_A()
        agent.save_learned_B()
        agent.save_epsilon()

        save_snapshot(agent, label="boot")
        learning_diff = diff_A(A_before, agent.agent.A)
        learning_diff_fmt = format_learning_diff(learning_diff)

        conf_pct = int(100.0 * max(final["beliefs"]))
        explanation = agent.explain(final)
        fep_v2_result = {
            "action": final["action_name"],
            "selected_series": final.get("selected_series"),
            "entropy": round(final["entropy"], 3),
            "confidence_pct": conf_pct,
            "attractor_series": att_series,
            "agreement": final.get("selected_series") == att_series,
            "map_state": final["map_state_names"],
            "explanation": explanation,
            "learning_diff": learning_diff,
            "epsilon": agent.epsilon_summary(),
        }

        # Convergence tracking (pushout)
        try:
            from mekhane.fep.convergence_tracker import record_agreement
            conv_summary = record_agreement(
                agent_series=final.get("selected_series"),
                attractor_series=att_series,
                agent_action=final["action_name"],
                epsilon=dict(agent.epsilon),
                agent_confidence=max(final["beliefs"]),
                attractor_similarity=rec.confidence if hasattr(rec, 'confidence') else 0.0,
            )
            fep_v2_result["convergence"] = conv_summary
        except Exception:
            pass

    except Exception:
        pass
    return fep_v2_result, learning_diff_fmt


def _format_attractor(
    llm_fmt: str,
    theorem_detail: dict,
    dispatch_info: dict,
    fep_v2_result: dict,
    learning_diff_fmt: str,
) -> str:
    """Attractor 軸のフォーマット済み出力."""
    parts: list[str] = []
    if llm_fmt:
        parts.append(f"🎯 **Attractor**: {llm_fmt}")
    if theorem_detail.get("top_theorems"):
        tops = ", ".join(
            f"{t['theorem']}({t['sim']:.2f})"
            for t in theorem_detail["top_theorems"][:3]
        )
        mix = theorem_detail.get("mixture", {})
        h_str = f" | H={mix['entropy']:.2f}" if mix.get("entropy") is not None else ""
        dom = f" dom={mix['dominant_series']}" if mix.get("dominant_series") else ""
        parts.append(f"   🔬 Theorems: {tops}{h_str}{dom}")
    if dispatch_info.get("primary"):
        parts.append(f"   📎 Dispatch: {dispatch_info['dispatch_formatted']}")
    if fep_v2_result:
        act = fep_v2_result["action"]
        sel = fep_v2_result.get("selected_series") or "-"
        ent = fep_v2_result["entropy"]
        conf = fep_v2_result["confidence_pct"]
        att_s = fep_v2_result.get("attractor_series", "?")
        agree = "✓一致" if fep_v2_result.get("agreement") else "✗不一致"
        parts.append(
            f"   🧠 FEP v2: {act} [Series={sel}] "
            f"(entropy={ent}, conf={conf}%) ↔ ATT={att_s} [{agree}]"
        )
        expl = fep_v2_result.get("explanation", "")
        if expl:
            for line in expl.split("\n"):
                parts.append(f"      {line}")
        conv = fep_v2_result.get("convergence")
        if conv:
            from mekhane.fep.convergence_tracker import format_convergence
            parts.append(f"   {format_convergence(conv)}")
        eps_info = fep_v2_result.get("epsilon", {})
        eps_vals = eps_info.get("epsilon", {})
        if eps_vals:
            eps_str = " ".join(f"{k}={v:.3f}" for k, v in eps_vals.items())
            parts.append(f"   ε: {eps_str}")
    if learning_diff_fmt:
        for line in learning_diff_fmt.split("\n"):
            parts.append(f"   {line}")
    return "\n".join(parts) if parts else ""


# ─────────────────────────────────────────────────────────────────────
# 軸 I: Projects
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: projects を読み込む
def load_projects(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"projects": [], "active": 0, "dormant": 0, "total": 0, "formatted": ""}
    print(" [9/13] 📦 Loading Projects Registry...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.symploke.boot_integration import _load_projects
        project_root = Path(__file__).parent.parent.parent
        result = _load_projects(project_root)
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 J: Skills
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: skills を読み込む
def load_skills(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"skills": [], "count": 0, "skill_paths": [], "formatted": ""}
    print(" [10/13] 🧠 Loading Skills...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.symploke.boot_integration import _load_skills
        project_root = Path(__file__).parent.parent.parent
        result = _load_skills(project_root)
        print(f" Done ({result['count']} skills).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 K: Doxa (信念ストア)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: doxa を読み込む
def load_doxa(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"beliefs_loaded": 0, "active_count": 0, "promotion_candidates": [], "formatted": ""}
    print(" [11/13] 🧿 Loading Doxa Beliefs...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.symploke.doxa_boot import load_doxa_for_boot
        doxa_boot = load_doxa_for_boot()
        result = {
            "beliefs_loaded": doxa_boot.beliefs_loaded,
            "active_count": doxa_boot.active_count,
            "archived_count": doxa_boot.archived_count,
            "promotion_candidates": [
                {"content": c.belief.content[:50], "score": c.score, "reasons": c.reasons}
                for c in doxa_boot.promotion_candidates
            ],
            "formatted": doxa_boot.summary,
        }
        print(f" Done ({doxa_boot.beliefs_loaded} beliefs).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 L: Credit Assignment (フィードバック学習)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: feedback を読み込む
def load_feedback(mode: str, context: Optional[str] = None, **kw) -> dict:
    result: dict = {"total": 0, "accept_rate": 0.0, "formatted": ""}
    print(" [12/13] 🎓 Loading Feedback History...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.fep.credit_assignment import (
            load_feedback_history,
            feedback_summary,
        )
        records = load_feedback_history(months=3)
        if records:
            summary = feedback_summary(records)
            lines = [f"### 🎓 軸 L: Credit Assignment ({summary['total']}件)"]
            lines.append(f"Accept Rate: {summary['accept_rate']:.0%}")
            if summary["common_corrections"]:
                corrections = ", ".join(
                    f"{f}→{t}({c})" for f, t, c in summary["common_corrections"][:3]
                )
                lines.append(f"Common Corrections: {corrections}")
            result = {
                "total": summary["total"],
                "accept_rate": summary["accept_rate"],
                "per_series": summary.get("per_series", {}),
                "formatted": "\n".join(lines),
            }
            print(f" Done ({summary['total']} records, {summary['accept_rate']:.0%} accept).", file=sys.stderr)
        else:
            print(" No feedback yet.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 M: Proactive Push (知識推薦)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: proactive push を読み込む
def load_proactive_push(mode: str, context: Optional[str] = None, **kw) -> dict:
    """Proactive Push 軸: 知識が自ら語りかけてくる推薦."""
    result: dict = {"recommendations": [], "count": 0, "formatted": ""}
    if mode == "fast":
        print(" [13/15] 💡 Proactive Push skipped (fast mode).", file=sys.stderr)
        return result

    print(" [13/15] 💡 Proactive Push...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.anamnesis.proactive_push import ProactivePush
        push = ProactivePush(max_recommendations=3)
        push_result = push.boot_recommendations(context)

        if push_result.recommendations:
            result = {
                "recommendations": [
                    {
                        "title": r.title,
                        "source_type": r.source_type,
                        "relevance": r.relevance,
                        "benefit": r.benefit,
                        "actions": r.actions,
                    }
                    for r in push_result.recommendations
                ],
                "count": len(push_result.recommendations),
                "retrieval_time": push_result.retrieval_time,
                "formatted": ProactivePush.format_recommendations(push_result),
            }
        print(f" Done ({len(push_result.recommendations)} recs).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 N: Violation Trends (違反傾向)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: violations を読み込む
def load_violations(mode: str, context: Optional[str] = None, **kw) -> dict:
    """Violation Trends 軸: 直近の違反パターン傾向を /boot に表示."""
    result: dict = {"total": 0, "patterns": {}, "recurrence": 0, "formatted": ""}
    print(" [14/15] ⚠️ Analyzing Violation Trends...", file=sys.stderr, end="", flush=True)
    try:
        from scripts.violation_analyzer import parse_violations, analyze, format_boot_summary
        entries = parse_violations()
        stats = analyze(entries, since_days=7)
        result = {
            "total": stats["total"],
            "patterns": stats["patterns"],
            "recurrence": stats["recurrence"],
            "formatted": format_boot_summary(stats),
        }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 O: Gnōsis Advice (知識アドバイス)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: gnosis advice を読み込む
def load_gnosis_advice(mode: str, context: Optional[str] = None, **kw) -> dict:
    """Gnōsis Advice 軸: WF に関連する学術知識のハイライト."""
    result: dict = {"advice": "", "formatted": ""}
    if mode == "fast":
        print(" [15/15] 📖 Gnōsis Advice skipped (fast mode).", file=sys.stderr)
        return result
    print(" [15/15] 📖 Loading Gnōsis Advice...", file=sys.stderr, end="", flush=True)
    try:
        from scripts.gnosis_advisor import daily_topics
        advice = daily_topics()
        result = {"advice": advice, "formatted": advice}
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# 軸 P: Ideas (HGK Gateway アイデア)
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: HGK Gateway で捕捉されたアイデアメモを読み込む
def load_ideas(mode: str, context: Optional[str] = None, **kw) -> dict:
    """Ideas 軸: HGK Gateway で捕捉された未処理アイデアを /boot に表示."""
    result: dict = {"ideas": [], "count": 0, "formatted": ""}
    print(" [16/16] 💡 Loading Gateway Ideas...", file=sys.stderr, end="", flush=True)
    try:
        idea_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "ideas"
        if not idea_dir.exists():
            print(" No ideas dir.", file=sys.stderr)
            return result

        idea_files = sorted(idea_dir.glob("idea_*.md"), reverse=True)
        if not idea_files:
            print(" No ideas.", file=sys.stderr)
            return result

        ideas = []
        for fp in idea_files:
            content = fp.read_text(encoding="utf-8")
            # Parse metadata from markdown
            tags = ""
            date_str = ""
            body_lines = []
            in_body = False
            for line in content.split("\n"):
                if line.startswith("> **タグ**:"):
                    tags = line.split(":", 1)[1].strip()
                elif line.startswith("> **日時**:"):
                    date_str = line.split(":", 1)[1].strip()
                elif line.strip() == "---":
                    if in_body:
                        break  # End of body
                    in_body = True
                elif in_body and line.strip():
                    body_lines.append(line.strip())

            # First non-empty body line as title (truncated)
            title = body_lines[0][:80] if body_lines else fp.stem
            ideas.append({
                "file": fp.name,
                "title": title,
                "tags": tags,
                "date": date_str,
            })

        lines = [f"💡 **Gateway Ideas** ({len(ideas)}件 — 未処理アイデア)"]
        for i, idea in enumerate(ideas, 1):
            tag_str = f" [{idea['tags']}]" if idea["tags"] and idea["tags"] != "未分類" else ""
            lines.append(f"  {i}. {idea['title']}{tag_str}")
        lines.append(f"  📂 `~/oikos/mneme/.hegemonikon/ideas/`")

        result = {
            "ideas": ideas,
            "count": len(ideas),
            "formatted": "\n".join(lines),
        }
        print(f" Done ({len(ideas)} ideas).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({e}).", file=sys.stderr)
    return result


# ─────────────────────────────────────────────────────────────────────
# Axis Registry — 統合フォーマット用の順序定義
# ─────────────────────────────────────────────────────────────────────

# (key, loader, format_order) — format_order は統合フォーマットでの表示順
AXIS_REGISTRY: list[tuple[str, Any, int]] = [
    ("handoffs",        load_handoffs,        2),
    ("ki",              load_sophia,          3),
    ("persona",         load_persona,         1),    # 最初に表示
    ("pks",             load_pks,             4),
    ("safety",          load_safety,          5),
    ("ept",             load_ept,             6),
    ("digestor",        load_digestor,        7),
    ("attractor",       load_attractor,       8),
    ("projects",        load_projects,        9),
    ("skills",          load_skills,          10),
    ("doxa",            load_doxa,            11),
    ("feedback",        load_feedback,        12),
    ("proactive_push",  load_proactive_push,  13),
    ("violations",      load_violations,      14),
    ("gnosis_advice",   load_gnosis_advice,   15),
    ("ideas",           load_ideas,            16),
]
