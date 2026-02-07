#!/usr/bin/env python3
"""Dendron 自己診断テスト (軽量版) — mekhane/dendron のみ対象"""

import sys
sys.path.insert(0, '/home/makaron8426/oikos/hegemonikon')

from pathlib import Path
from mekhane.dendron.checker import DendronChecker, ProofStatus

TARGET = Path('/home/makaron8426/oikos/hegemonikon/mekhane/dendron')

checker = DendronChecker()

# dendron ディレクトリ内の .py ファイルのみ直接チェック
all_proofs = []
for py_file in sorted(TARGET.glob('*.py')):
    if py_file.name.startswith('__'):
        continue
    proofs = checker.check_functions_in_file(py_file)
    all_proofs.extend(proofs)

ok = [f for f in all_proofs if f.status == ProofStatus.OK]
weak = [f for f in all_proofs if f.status == ProofStatus.WEAK]
missing = [f for f in all_proofs if f.status == ProofStatus.MISSING]
exempt = [f for f in all_proofs if f.status == ProofStatus.EXEMPT]

print(f'=== Dendron Self-Diagnosis (v2.6) ===')
print(f'OK: {len(ok)} | WEAK: {len(weak)} | MISSING: {len(missing)} | EXEMPT: {len(exempt)}')

if weak:
    print()
    print('--- WEAK Purposes (Dendron detected) ---')
    for f in weak:
        print(f'  {f.path.name}:{f.line_number} {f.name}')
        print(f'    Current: {f.purpose_text}')
        print(f'    Issue:   {f.quality_issue}')
        print()

if missing:
    print()
    print('--- MISSING Purposes ---')
    for f in missing:
        print(f'  {f.path.name}:{f.line_number} {f.name}')

print()
if len(weak) == 0 and len(missing) == 0:
    print('✅ ALL CLEAR — Dendron is self-compliant!')
else:
    print(f'❌ {len(weak)} WEAK + {len(missing)} MISSING to fix')
