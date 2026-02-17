# PROOF: [L2/Periskopē] <- mekhane/periskope/searchers/ Package
"""
Searcher implementations for different sources.
"""

from .searxng import SearXNGSearcher
# from .exa_searcher import ExaSearcher
# from .internal_searcher import InternalSearcher

__all__ = [
    "SearXNGSearcher",
    # "ExaSearcher",
    # "InternalSearcher",
]
