# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: CCL → Hermēneus → Attractor → PW → Cone のE2Eパイプライン
"""
PROOF: [L2/FEP] このファイルは存在しなければならない

A0 → 個々のPJは単体テスト済みだが、パイプラインとして接続されていない
   → CCL式から最終Coneまで一気通貫で実行するオーケストレータが必要
   → pipeline.py が担う

接続:
  Hermēneus dispatch() → AST + workflows
  Attractor diagnose() → SuggestResult (series, oscillation)
  PW resolve_pw()      → Dict[str, float] (theorem weights)
  Cone converge()      → Cone dataclass
  Advisor format_for_llm() → LLM注入文字列

Q.E.D.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# =============================================================================
# Stage Results
# =============================================================================


@dataclass
class StageResult:
    """1ステージの実行結果。"""
    name: str
    success: bool
    data: Any = None
    error: Optional[str] = None


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

    @property
    def all_passed(self) -> bool:
        return all(s.success for s in self.stages)

    @property
    def failed_at(self) -> Optional[str]:
        for s in self.stages:
            if not s.success:
                return s.name
        return None

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [f"Pipeline: {self.ccl_expr}"]
        for s in self.stages:
            mark = "✅" if s.success else "❌"
            err = f" — {s.error}" if s.error else ""
            lines.append(f"  {mark} {s.name}{err}")
        if self.llm_injection:
            lines.append(f"\nLLM injection:\n{self.llm_injection}")
        return "\n".join(lines)


# =============================================================================
# Pipeline Orchestrator
# =============================================================================


def run_pipeline(
    ccl_expr: str,
    *,
    context: Optional[str] = None,
    force_cpu: bool = True,
    use_gnosis: bool = False,
    mock_outputs: Optional[Dict[str, str]] = None,
) -> PipelineResult:
    """Execute the full CCL → Cone pipeline.

    Args:
        ccl_expr: CCL expression string (e.g. "/dia+~*/noe")
        context: Optional context for PW inference
        force_cpu: Force CPU for embeddings (default True for tests)
        use_gnosis: Enable Gnōsis knowledge enrichment
        mock_outputs: Mock theorem outputs for Cone converge
                      (in production, LLM generates these)

    Returns:
        PipelineResult with all stage results
    """
    result = PipelineResult(ccl_expr=ccl_expr)

    # ─── Stage 1: Hermēneus Parse ───
    stage1 = _stage_hermeneus(ccl_expr)
    result.stages.append(stage1)
    if not stage1.success:
        return result
    result.workflows = stage1.data.get("workflows", [])

    # ─── Stage 2: Attractor Diagnose ───
    # Use the CCL expression itself as semantic input to the attractor
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
        from mekhane.fep.cone_builder import converge

        cone = converge(
            series=series,
            outputs=outputs,
            pw=pw if any(v != 0 for v in pw.values()) else None,
        )
        return StageResult(
            name="cone",
            success=True,
            data={
                "apex": cone.apex,
                "method": cone.method,
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
