"""
EV-002 Theorem Coverage Analysis for sophia_mcp_server.py
"""
import sys
from pathlib import Path

# Add project root to path if needed (though usually handled by execution context)
try:
    from mekhane.synedrion.ai_auditor import Issue, Severity
except ImportError:
    # Fallback if running directly without proper path setup
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from mekhane.synedrion.ai_auditor import Issue, Severity

def get_issues():
    """Returns the list of EV-002 issues for sophia_mcp_server.py."""
    return [
        Issue(
            code="EV-002",
            name="Theorem Coverage Skew",
            severity=Severity.LOW,
            line=1,
            message="PROOF distribution skewed: Only A0 (Archē) explicit. Missing O3, K4, A4, S2.",
            suggestion="Add explicit PROOF tags for implicit implementations.",
        ),
        Issue(
            code="EV-002",
            name="Implicit Theorem Implementation",
            severity=Severity.LOW,
            line=98,
            message="O3 (Zētēsis) implemented in search tool but not tagged.",
        ),
        Issue(
            code="EV-002",
            name="Implicit Theorem Implementation",
            severity=Severity.LOW,
            line=159,
            message="K4 (Anamnesis) implemented in index search but not tagged.",
        ),
        Issue(
            code="EV-002",
            name="Implicit Theorem Implementation",
            severity=Severity.LOW,
            line=237,
            message="A4 (Semainein) implemented in result formatting but not tagged.",
        ),
         Issue(
            code="EV-002",
            name="Implicit Theorem Implementation",
            severity=Severity.LOW,
            line=83,
            message="S2 (Mekhanē) implemented as MCP server but not tagged.",
        ),
        Issue(
            code="EV-002",
            name="Missing X-series Declaration",
            severity=Severity.LOW,
            line=1,
            message="Missing X-series declarations for EmbeddingAdapter and indices.",
        ),
    ]

if __name__ == "__main__":
    for issue in get_issues():
        print(f"{issue.code} [{issue.severity.value}]: {issue.message}")
