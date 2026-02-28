# PROOF: [L2/インフラ] <- mekhane/exagoge/__main__
# PURPOSE: exagoge パッケージ CLI エントリーポイント
"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → CLIのエントリーポイントが必要
   → __main__ が担う

Q.E.D.

---
python -m mekhane.exagoge でCLIを実行可能にする。
"""
from .cli import main

main()
