# PROOF.md — 存在証明書

PURPOSE: プロンプト言語の解析・実行エンジン
REASON: 構造化されたプロンプト記法の機械的処理が必要だった

> **∃ typos/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `開発支援ツール群 (テスト、品質保証、生産性向上) を提供する` の一部として存在が要請される
2. **機能公理**: `プロンプト言語の解析・実行エンジン` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `typos.py` | typos Parser |
| `typos_integrate.py` | PROOF: [L2/インフラ] <- mekhane/ergasterion/typos/ S2→プロンプ |
| `test_integration.py` | PROOF: [L2/インフラ] <- mekhane/ergasterion/typos/ S2→プロンプ |
| `test_typos.py` | typos Unit Tests |

---

*Generated: 2026-02-08 by generate_proofs.py*
