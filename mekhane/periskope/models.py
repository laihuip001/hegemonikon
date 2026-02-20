# PROOF: [P4/Periskopē] <- mekhane/periskope/ S5->Models
"""Periskopē Models.

Data models for Periskopē.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SearchResult:
    """Search Result."""
    url: str
    title: str
    snippet: str
    metadata: Dict[str, Any]
