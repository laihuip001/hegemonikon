import sys
import re
from pathlib import Path

# Mocking the function from boot_integration.py
def postcheck_boot_report_mock(content, mode="detailed"):
    MODE_REQUIREMENTS = {
        "detailed": {"required_sections": ["A"], "min_chars": 10},
        "fast": {"required_sections": [], "min_chars": 0},
    }

    reqs = MODE_REQUIREMENTS.get(mode, MODE_REQUIREMENTS["detailed"])
    checks = []

    # Check 5 logic
    unchecked = content.count("- [ ]")
    checked = content.count("- [x]")
    total_checks = unchecked + checked
    all_checked = unchecked == 0 and total_checks > 0
    checks.append({
        "name": "checklist_completion",
        "passed": all_checked,
        "detail": f"Checklist: {checked}/{total_checks}"
    })

    return checks

print("--- Test 1: Fast mode, no checklist ---")
checks = postcheck_boot_report_mock("Just some content", mode="fast")
print(checks[0])

print("\n--- Test 2: Detailed mode, checklist ---")
checks = postcheck_boot_report_mock("- [x] Done", mode="detailed")
print(checks[0])
