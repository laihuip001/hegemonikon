# PROOF: [L2/Hodos] <- mekhane/ochema/
# PURPOSE: Ochēma Package Initialization
# REASON: Exports the public interface for the Antigravity Language Server client.
"""
Ochēma (ὄχημα): The Vehicle/Chariot.

Provides the infrastructure client for connecting to the local Antigravity Language Server.
This module aligns with Theorem P2 (Hodos) as the path/way to external intelligence.
"""

from .antigravity_client import AntigravityClient, LLMResponse

__all__ = ["AntigravityClient", "LLMResponse"]
