# PROOF: [L2/Infra] <- mekhane/synteleia/dokimasia/ Multi-Agent Semantics
"""Multi-Semantic Agent.

Coordinates multiple semantic agents for complex reasoning tasks.
"""

from typing import List
from mekhane.synteleia.dokimasia.ochema_backend import OchemaBackend

class MultiSemanticAgent:
    """Agent orchestrator."""

    def __init__(self, backends: List[OchemaBackend]):
        self.backends = backends

    def run_ensemble(self, query: str) -> List[str]:
        """Run an ensemble of agents on a query."""
        results = []
        for backend in self.backends:
            res = backend.execute_prompt(query)
            results.append(res.get("text", ""))
        return results
