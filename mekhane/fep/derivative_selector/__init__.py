"""
Derivative Selector Package

This package provides derivative selection logic for all 6 theorem series.

The original implementation is in the parent directory for backward compatibility.
This package provides a structured API with re-exports.

Usage:
    from mekhane.fep.derivative_selector import select_derivative, DerivativeStateSpace

Structure:
    - base.py: DerivativeStateSpace class and shared utilities
    - The original derivative_selector.py remains in parent for compatibility
"""

# Re-export from original file for backward compatibility
import sys
from pathlib import Path

# Import from parent module
_parent = Path(__file__).parent.parent / "derivative_selector.py"
if _parent.exists():
    # Use relative import since we're a subpackage
    from ..derivative_selector import (
        DerivativeStateSpace,
        O1_PATTERNS, O2_PATTERNS, O3_PATTERNS, O4_PATTERNS,
        S1_PATTERNS, S2_PATTERNS, S3_PATTERNS, S4_PATTERNS,
        H1_PATTERNS, H2_PATTERNS, H3_PATTERNS, H4_PATTERNS,
        P1_PATTERNS, P2_PATTERNS, P3_PATTERNS, P4_PATTERNS,
        K1_PATTERNS, K2_PATTERNS, K3_PATTERNS, K4_PATTERNS,
        A1_PATTERNS, A2_PATTERNS, A3_PATTERNS, A4_PATTERNS,
    )

    # Try to import selection functions
    try:
        from ..derivative_selector import (
            select_derivative,
            select_o1_derivative,
            select_o2_derivative,
            select_o3_derivative,
            select_o4_derivative,
            select_s1_derivative,
            select_s2_derivative,
            select_s3_derivative,
            select_s4_derivative,
        )
    except ImportError:
        pass  # Some functions may not exist

__all__ = [
    "DerivativeStateSpace",
    # O-series
    "O1_PATTERNS", "O2_PATTERNS", "O3_PATTERNS", "O4_PATTERNS",
    # S-series
    "S1_PATTERNS", "S2_PATTERNS", "S3_PATTERNS", "S4_PATTERNS",
    # H-series
    "H1_PATTERNS", "H2_PATTERNS", "H3_PATTERNS", "H4_PATTERNS",
    # P-series
    "P1_PATTERNS", "P2_PATTERNS", "P3_PATTERNS", "P4_PATTERNS",
    # K-series
    "K1_PATTERNS", "K2_PATTERNS", "K3_PATTERNS", "K4_PATTERNS",
    # A-series
    "A1_PATTERNS", "A2_PATTERNS", "A3_PATTERNS", "A4_PATTERNS",
]
