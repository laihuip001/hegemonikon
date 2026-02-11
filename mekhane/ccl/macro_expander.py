# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→macro_expander が担う
"""
CCL Macro Expander

Expands @macro references in CCL expressions.
Part of CCL v2.1 macro system.
"""

import re
from typing import Tuple, Optional
from .macro_registry import MacroRegistry


# PURPOSE: Expands @macro references in CCL expressions.
class MacroExpander:
    """Expands @macro references in CCL expressions."""

    # Pattern to match @macro_name
    MACRO_PATTERN = re.compile(r"@(\w+)")

    # Pattern to match old @N level syntax (for migration)
    OLD_LEVEL_PATTERN = re.compile(r"(@)(\d+)(?!\w)")

    # PURPOSE: Initialize the expander.
    def __init__(self, registry: Optional[MacroRegistry] = None):
        """
        Initialize the expander.

        Args:
            registry: Macro registry to use
        """
        self.registry = registry or MacroRegistry()

    # PURPOSE: Expand all @macro references in a CCL expression.
    def expand(self, ccl: str) -> Tuple[str, bool]:
        """
        Expand all @macro references in a CCL expression.

        Args:
            ccl: CCL expression possibly containing @macros

        Returns:
            Tuple of (expanded CCL, whether any expansion occurred)
        """
        expanded = False
        result = ccl

        # Find all @name patterns
        # PURPOSE: マクロを展開するヘルパー関数
        def replace(match):
            nonlocal expanded
            name = match.group(1)

            # Skip if it's a number (that's a level, not a macro)
            if name.isdigit():
                return match.group(0)

            macro = self.registry.get(name)
            if macro:
                expanded = True
                self.registry.record_usage(name)
                return macro.ccl
            return match.group(0)

        result = self.MACRO_PATTERN.sub(replace, ccl)

        return result, expanded

    # PURPOSE: Migrate old @N level syntax to new :N syntax.
    def migrate_level_syntax(self, ccl: str) -> str:
        """
        Migrate old @N level syntax to new :N syntax.

        Args:
            ccl: CCL expression with old @N syntax

        Returns:
            CCL with :N syntax
        """
        # Replace @N with :N where N is a digit
        # But only when @ is followed by just digits (not a macro name)
        return self.OLD_LEVEL_PATTERN.sub(r":\2", ccl)

    # PURPOSE: Check if expression contains macro references.
    def has_macros(self, ccl: str) -> bool:
        """Check if expression contains macro references."""
        for match in self.MACRO_PATTERN.finditer(ccl):
            name = match.group(1)
            if not name.isdigit() and self.registry.get(name):
                return True
        return False

    # PURPOSE: List all macros used in an expression.
    def list_macros_in_expr(self, ccl: str) -> list:
        """List all macros used in an expression."""
        macros = []
        for match in self.MACRO_PATTERN.finditer(ccl):
            name = match.group(1)
            if not name.isdigit():
                macro = self.registry.get(name)
                if macro:
                    macros.append(macro)
        return macros
