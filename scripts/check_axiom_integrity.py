#!/usr/bin/env python3
"""
Axiom Coordinate Integrity Check

This script scans Python files in the `mekhane/` directory for `coordinates: [...]` metadata
(typically in docstrings or comments) and validates that the listed coordinates correspond to
valid theorem series (O, S, H, P, K, A, E, X).

Usage:
    python3 scripts/check_axiom_integrity.py
"""

import os
import re
import sys
from pathlib import Path

# Valid series based on 24 Theorems + X-series + E (Energeia/Expansion?)
# O: Ousia (Essence)
# S: Stasis (State)
# H: Hyle (Matter)
# P: Poiesis (Creation)
# K: Kinesis (Motion)
# A: Aisthesis (Perception/Axiom)
# E: Energeia (Activity - O4) / Expansion?
# X: Unknown/Experimental
VALID_COORDINATES = {'O', 'S', 'H', 'P', 'K', 'A', 'E', 'X'}

def check_file(filepath: Path) -> list[str]:
    """Checks a single file for invalid coordinates."""
    errors = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"Could not read file: {e}"]

    # Look for patterns like: coordinates: [A, E]
    # Case-insensitive "coordinates:", followed by optional whitespace, then brackets
    matches = re.finditer(r'coordinates:\s*\[([a-zA-Z,\s]+)\]', content, re.IGNORECASE)

    for match in matches:
        coord_str = match.group(1)
        # Split by comma and strip whitespace
        coords = [c.strip() for c in coord_str.split(',') if c.strip()]

        for coord in coords:
            if coord not in VALID_COORDINATES:
                errors.append(f"Invalid coordinate '{coord}' found in {filepath}. Valid: {VALID_COORDINATES}")

    return errors

def main():
    root_dir = Path("mekhane")
    if not root_dir.exists():
        print("Directory 'mekhane' not found.")
        sys.exit(1)

    all_errors = []

    # Walk through all python files
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                errors = check_file(filepath)
                all_errors.extend(errors)

    if all_errors:
        print("Axiom Coordinate Integrity Violations Found:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Axiom Coordinate Integrity Check Passed (Silent).")
        sys.exit(0)

if __name__ == "__main__":
    main()
