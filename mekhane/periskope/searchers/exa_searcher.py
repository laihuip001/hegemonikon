# PROOF: [L2/Infra] <- mekhane/periskope/searchers/
# PURPOSE: Search provider using Exa API
"""Exa searcher implementation."""
from typing import Any, List, Dict, Optional

class ExaSearcher:
    """Searcher implementation using Exa API."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Mock search for now, as it's missing."""
        return []
