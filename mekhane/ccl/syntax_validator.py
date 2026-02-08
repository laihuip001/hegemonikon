# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→syntax_validator が担う
"""
CCL Syntax Validator v2.0

Validates CCL expressions against the v2.0 specification.
"""

import re
from dataclasses import dataclass
from typing import List

# Valid workflows (commands)
VALID_WORKFLOWS = {
    # O-Series
    "noe",
    "bou",
    "zet",
    "ene",
    # S-Series
    "s",
    "mek",
    "met",
    "sta",
    "pra",
    # H-Series
    "h",
    "pro",
    "pis",
    "ore",
    "dox",
    # P-Series
    "p",
    "kho",
    "hod",
    "tro",
    "tek",
    # K-Series
    "k",
    "euk",
    "chr",
    "tel",
    "sop",
    # A-Series
    "a",
    "pat",
    "dia",
    "gno",
    "epi",
    # Meta
    "boot",
    "bye",
    "ax",
    "u",
    "syn",
    "pan",
    # Execution control
    "pre",
    "poc",
    "why",
    "flag",
    "vet",
    "fit",
    "epo",
}


@dataclass
# PURPOSE: Result of CCL validation.
class ValidationResult:
    """Result of CCL validation."""

    valid: bool
    errors: List[str]
    warnings: List[str]

    # PURPOSE: 内部処理: bool__
    def __bool__(self) -> bool:
        return self.valid

# PURPOSE: Validate CCL v2.0 expressions.

class CCLSyntaxValidator:
    """
    Validate CCL v2.0 expressions.

    Checks for:
    - Balanced braces
    - Valid workflow references
    - Valid operators
    - Control syntax correctness
    """

    WORKFLOW_PATTERN = r"/([a-z]+)"
    UNARY_OPS = set("+-^/")
    BINARY_OPS = set("_*~")

    # PURPOSE: Validate a CCL expression.
    def validate(self, ccl: str) -> ValidationResult:
        """
        Validate a CCL expression.

        Args:
            ccl: The CCL expression to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        if not ccl or not ccl.strip():
            errors.append("Empty CCL expression")
            return ValidationResult(False, errors, warnings)

        # Check balanced braces
        if ccl.count("{") != ccl.count("}"):
            errors.append("Unbalanced braces { }")

        if ccl.count("[") != ccl.count("]"):
            errors.append("Unbalanced brackets [ ]")

        if ccl.count("(") != ccl.count(")"):
            errors.append("Unbalanced parentheses ( )")

        # Extract and validate workflows
        workflows = re.findall(self.WORKFLOW_PATTERN, ccl)
        for wf in workflows:
            if wf not in VALID_WORKFLOWS:
                warnings.append(f"Unknown workflow: /{wf}")

        # Check for invalid operator sequences
        if re.search(r"[_*~]{2,}", ccl):
            errors.append("Consecutive binary operators")

        # Check control syntax
        control_matches = re.findall(r"([FI]):([^{]*)\{", ccl)
        for ctrl, condition in control_matches:
            if ctrl == "F" and not condition.strip():
                errors.append("For loop (F:) requires iteration specification")
            if ctrl == "I" and not condition.strip():
                errors.append("If statement (I:) requires condition")

        # Check for forbidden operator
        if "!" in ccl and not re.search(r"\[.*!\.*\]", ccl):
            warnings.append("Explosion operator (!) detected - use with caution")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            # NOTE: Removed self-assignment: warnings = warnings
        )
