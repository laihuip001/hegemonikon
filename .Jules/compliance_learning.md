## 2024-05-22 - [Compliance Checks]
**Learning:** The project enforces strict compliance checks via .
1. Code in  must have  comments for all classes and functions.
2. Skill definitions () must have  and  in frontmatter.
3. Workflow definitions () must have  and  in frontmatter.
**Action:** When adding new code or documentation, always run ============================================================
Dendron PROOF Check Report
============================================================

Total files: 554
With proof:  377
Orphan:      0
Missing:     3
Invalid:     0
Exempt:      174
Coverage:    99.2%
Levels:      L1:45 | L2:256 | L3:76

Directories: 1065 total, 104 with PROOF.md, 961 missing

----------------------------------------
Missing PROOF:
  ❌ scripts/adjunction_status.py
  ❌ scripts/ingest_peira_raw.py
  ❌ scripts/verify_typos_v3.py

----------------------------------------
L2 Purpose:
  OK:      2570
  Weak:    0
  Missing: 300
  Coverage: 89.5%

----------------------------------------
L3 Variable:
  Type hints: 3601/4121
  Short names: 5 violations

❌ FAIL locally to catch these issues before CI.
