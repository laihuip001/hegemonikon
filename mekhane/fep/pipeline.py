# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: UML Pre → CCL → Hermēneus → Attractor → PW → Cone → UML Post のE2Eパイプライン
"""
PROOF: [L2/FEP] このファイルは存在しなければならない

A0 → 個々のPJは単体テスト済みだが、パイプラインとして接続されていない
   → CCL式から最終Coneまで一気通貫で実行するオーケストレータが必要
   → UML Pre/Post チェックで MP 5段階を環境強制する
   → pipeline.py が担う

接続:
  UML Pre-check        → generate_pre_injection() (Stage 0)
  Hermēneus dispatch() → AST + workflows (Stage 1)
  Attractor diagnose() → SuggestResult (Stage 2)
  PW resolve_pw()      → Dict[str, float] (Stage 3)
  Cone converge()      → Cone dataclass (Stage 4)
  Advisor format_for_llm() → LLM注入文字列 (Stage 5)
  UML Post-check       → run_full_uml() (Stage 6)

Q.E.D.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# =============================================================================
# Stage Results
# =============================================================================


# PURPOSE: 1ステージの実行結果。
@dataclass
class StageResult:
    """1ステージの実行結果。"""
    name: str
    success: bool
    data: Any = None
    error: Optional[str] = None


# PURPOSE: E2E パイプラインの全体結果。
@dataclass
class PipelineResult:
    """E2E パイプラインの全体結果。"""
    ccl_expr: str
    stages: List[StageResult] = field(default_factory=list)
    # Derived
    workflows: List[str] = field(default_factory=list)
    series: List[str] = field(default_factory=list)
    pw: Dict[str, float] = field(default_factory=dict)
    llm_injection: str = ""
    # UML Phase 2
    uml_pre_prompt: str = ""
    uml_report: Any = None  # UMLReport from metacognitive_layer

    # PURPOSE: all_passed の処理
    @property
    def all_passed(self) -> bool:
        return all(s.success for s in self.stages)

    # PURPOSE: failed_at の処理
    @property
    def failed_at(self) -> Optional[str]:
        for s in self.stages:
            if not s.success:
                return s.name
        return None

    # PURPOSE: Human-readable summary
    def summary(self) -> str:
        """Human-readable summary."""
        lines = [f"Pipeline: {self.ccl_expr}"]
        for s in self.stages:
            mark = "✅" if s.success else "❌"
            err = f" — {s.error}" if s.error else ""
            lines.append(f"  {mark} {s.name}{err}")
        if self.uml_pre_prompt:
            lines.append(f"\nUML Pre-prompt ({len(self.uml_pre_prompt)} chars)")
        if self.llm_injection:
            lines.append(f"\nLLM injection:\n{self.llm_injection}")
        if self.uml_report:
            lines.append(f"\nUML Report: {self.uml_report.summary}")
        return "\n".join(lines)


# =============================================================================
# Pipeline Orchestrator
# =============================================================================


# PURPOSE: Execute the full UML Pre → CCL → Cone → UML Post pipeline
def run_pipeline(
    ccl_expr: str,
    *,
    context: Optional[str] = None,
    force_cpu: bool = True,
    use_gnosis: bool = False,
    use_uml: bool = True,
    mock_outputs: Optional[Dict[str, str]] = None,
) -> PipelineResult:
    """Execute the full UML Pre → CCL → Cone → UML Post pipeline.

    Args:
        ccl_expr: CCL expression string (e.g. "/dia+~*/noe")
        context: Optional context for PW inference
        force_cpu: Force CPU for embeddings (default True for tests)
        use_gnosis: Enable Gnōsis knowledge enrichment
        use_uml: Enable UML metacognitive pre/post checks
        mock_outputs: Mock theorem outputs for Cone converge
                      (in production, LLM generates these)

    Returns:
        PipelineResult with all stage results
    """
    result = PipelineResult(ccl_expr=ccl_expr)

    # ─── Stage 0: UML Pre-check ───
    if use_uml:
        stage0 = _stage_uml_pre(ccl_expr, context=context)
        result.stages.append(stage0)
        if stage0.success:
            result.uml_pre_prompt = stage0.data.get("prompt", "")
        # UML pre-check failure is non-blocking (advisory)

    # ─── Stage 1: Hermēneus Parse ───
    stage1 = _stage_hermeneus(ccl_expr)
    result.stages.append(stage1)
    if not stage1.success:
        return result
    result.workflows = stage1.data.get("workflows", [])

    # Derive WF name for UML (first workflow without /)
    wf_name = result.workflows[0].lstrip("/") if result.workflows else "unknown"

    # ─── Stage 2: Attractor Diagnose ───
    stage2 = _stage_attractor(ccl_expr, force_cpu=force_cpu)
    result.stages.append(stage2)
    if not stage2.success:
        return result
    result.series = stage2.data.get("series", [])

    # ─── Stage 3: PW Resolve ───
    primary_series = result.series[0] if result.series else None
    stage3 = _stage_pw(primary_series, context=context)
    result.stages.append(stage3)
    if not stage3.success:
        return result
    result.pw = stage3.data.get("pw", {})

    # ─── Stage 4: Cone Converge ───
    outputs = mock_outputs or _generate_stub_outputs(primary_series)
    stage4 = _stage_cone(primary_series, outputs, result.pw)
    result.stages.append(stage4)

    # ─── Stage 5: LLM Injection ───
    stage5 = _stage_llm_format(
        ccl_expr, force_cpu=force_cpu, use_gnosis=use_gnosis,
    )
    result.stages.append(stage5)
    if stage5.success:
        result.llm_injection = stage5.data.get("injection", "")

    # ─── Stage 6: UML Post-check ───
    if use_uml:
        # Use cone apex as "output" for UML post check
        cone_output = ""
        if stage4.success and stage4.data:
            cone_output = stage4.data.get("apex", "") or ""
        confidence = 0.0
        if stage4.success and stage4.data:
            confidence = stage4.data.get("confidence", 0.0)

        stage6 = _stage_uml_post(
            wf_name=wf_name,
            context=ccl_expr,
            output=cone_output,
            confidence=confidence,
        )
        result.stages.append(stage6)
        if stage6.success and stage6.data:
            result.uml_report = stage6.data.get("report")

    return result


# =============================================================================
# Individual Stages
# =============================================================================


def _stage_hermeneus(ccl_expr: str) -> StageResult:
    """Stage 1: CCL parse via Hermēneus dispatch()."""
    try:
        from hermeneus.src.dispatch import dispatch

        d = dispatch(ccl_expr)
        if not d["success"]:
            return StageResult(
                name="hermeneus",
                success=False,
                error=f"Parse error: {d.get('error', 'unknown')}",
            )
        return StageResult(
            name="hermeneus",
            success=True,
            data={
                "ast": d["ast"],
                "workflows": d["workflows"],
                "tree": d["tree"],
            },
        )
    except Exception as e:
        return StageResult(name="hermeneus", success=False, error=str(e))


def _stage_attractor(
    user_input: str, *, force_cpu: bool = True,
) -> StageResult:
    """Stage 2: Attractor diagnose() — series identification."""
    try:
        from mekhane.fep.attractor import SeriesAttractor

        attractor = SeriesAttractor(force_cpu=force_cpu)
        suggest = attractor.diagnose(user_input)

        series = [r.series for r in suggest.attractors]
        workflows = []
        for r in suggest.attractors:
            workflows.extend(r.workflows)

        return StageResult(
            name="attractor",
            success=True,
            data={
                "series": series,
                "workflows": workflows,
                "oscillation": suggest.oscillation.value,
                "top_similarity": suggest.top_similarity,
                "gap": suggest.gap,
            },
        )
    except Exception as e:
        return StageResult(name="attractor", success=False, error=str(e))


def _stage_pw(
    series: Optional[str], *, context: Optional[str] = None,
) -> StageResult:
    """Stage 3: PW resolve — precision weighting."""
    if not series:
        return StageResult(
            name="pw",
            success=False,
            error="No series identified for PW resolution",
        )
    try:
        from mekhane.fep.pw_adapter import resolve_pw

        pw = resolve_pw(series=series, context=context)
        return StageResult(
            name="pw",
            success=True,
            data={"pw": pw, "series": series},
        )
    except Exception as e:
        return StageResult(name="pw", success=False, error=str(e))


def _stage_cone(
    series: Optional[str],
    outputs: Dict[str, str],
    pw: Dict[str, float],
) -> StageResult:
    """Stage 4: Cone converge — build the final cone."""
    if not series:
        return StageResult(
            name="cone",
            success=False,
            error="No series for cone construction",
        )
    try:
        from mekhane.fep.category import Series
        from mekhane.fep.cone_builder import converge

        # Convert string series to Series enum
        series_enum = Series[series]

        cone = converge(
            series=series_enum,
            outputs=outputs,
            pw=pw if any(v != 0 for v in pw.values()) else None,
        )
        return StageResult(
            name="cone",
            success=True,
            data={
                "apex": cone.apex,
                "method": cone.resolution_method,
                "confidence": cone.confidence,
                "dispersion": cone.dispersion,
            },
        )
    except Exception as e:
        return StageResult(name="cone", success=False, error=str(e))


def _stage_llm_format(
    user_input: str,
    *,
    force_cpu: bool = True,
    use_gnosis: bool = False,
) -> StageResult:
    """Stage 5: AttractorAdvisor format_for_llm()."""
    try:
        from mekhane.fep.attractor_advisor import AttractorAdvisor

        advisor = AttractorAdvisor(
            force_cpu=force_cpu, use_gnosis=use_gnosis,
        )
        injection = advisor.format_for_llm(user_input)
        return StageResult(
            name="llm_format",
            success=True,
            data={"injection": injection},
        )
    except Exception as e:
        return StageResult(name="llm_format", success=False, error=str(e))


def _stage_uml_pre(
    ccl_expr: str,
    *,
    context: Optional[str] = None,
) -> StageResult:
    """Stage 0: UML Pre-check — generate metacognitive prompts.

    Generates the MP Stage 1-2 prompts that should be injected
    into the LLM's context before WF execution.
    """
    try:
        from mekhane.fep.metacognitive_layer import (
            generate_pre_injection,
            run_pre_checks,
        )

        # Derive WF name from CCL (best effort)
        wf_name = "unknown"
        if ccl_expr.startswith("/"):
            # Extract first workflow ID: "/dia+~*/noe" -> "dia"
            import re
            m = re.match(r"/([a-z]+)", ccl_expr)
            if m:
                wf_name = m.group(1)

        input_context = context or ccl_expr
        prompt = generate_pre_injection(wf_name, context=input_context)

        # Also run pre-checks to validate input quality
        pre_checks = run_pre_checks(input_context)
        checks_data = [
            {
                "stage": c.stage.value,
                "passed": c.passed,
                "result": c.result,
            }
            for c in pre_checks
        ]

        return StageResult(
            name="uml_pre",
            success=True,
            data={
                "prompt": prompt,
                "checks": checks_data,
                "wf_name": wf_name,
            },
        )
    except Exception as e:
        return StageResult(name="uml_pre", success=False, error=str(e))


def _stage_uml_post(
    wf_name: str,
    context: str,
    output: str,
    confidence: float = 0.0,
) -> StageResult:
    """Stage 6: UML Post-check — run full metacognitive evaluation.

    Runs MP Stage 3-5 checks on the pipeline output and generates
    a UMLReport with feedback loop status.
    """
    try:
        from mekhane.fep.metacognitive_layer import run_full_uml

        report = run_full_uml(
            context=context,
            output=output,
            wf_name=wf_name,
            confidence=confidence,
        )

        return StageResult(
            name="uml_post",
            success=True,
            data={
                "report": report,
                "overall_pass": report.overall_pass,
                "summary": report.summary,
                "pass_count": report.pass_count,
                "total_count": report.total_count,
            },
        )
    except Exception as e:
        return StageResult(name="uml_post", success=False, error=str(e))


# =============================================================================
# Helpers
# =============================================================================


# Series → 4 theorem IDs
_SERIES_THEOREMS = {
    "O": ["O1", "O2", "O3", "O4"],
    "S": ["S1", "S2", "S3", "S4"],
    "H": ["H1", "H2", "H3", "H4"],
    "P": ["P1", "P2", "P3", "P4"],
    "K": ["K1", "K2", "K3", "K4"],
    "A": ["A1", "A2", "A3", "A4"],
}


def _generate_stub_outputs(series: Optional[str]) -> Dict[str, str]:
    """Generate stub theorem outputs for testing.

    In production, these would be generated by the LLM executing
    each theorem's workflow.
    """
    if not series or series not in _SERIES_THEOREMS:
        return {}

    theorems = _SERIES_THEOREMS[series]
    return {
        t: f"[Stub output for {t}: This is a placeholder for "
           f"the LLM-generated theorem output in {series}-series]"
        for t in theorems
    }


# =============================================================================
# CLI
# =============================================================================


# PURPOSE: CLI: python -m mekhane.fep.pipeline '/dia+~*/noe'
def main() -> None:
    """CLI: python -m mekhane.fep.pipeline '/dia+~*/noe'"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.fep.pipeline '<CCL expression>'")
        sys.exit(1)

    ccl_expr = sys.argv[1]
    result = run_pipeline(ccl_expr, force_cpu=True)
    print(result.summary())


if __name__ == "__main__":
    main()
