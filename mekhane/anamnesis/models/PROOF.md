# PROOF.md — 存在証明書

PURPOSE: 知識構造のデータモデル定義
REASON: 論文・知識アイテムの型安全な表現が必要だった

> **∃ models/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `セッション間の記憶・知識の永続化と検索を提供し、認知の連続性を担保する` の一部として存在が要請される
2. **機能公理**: `知識構造のデータモデル定義` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | PROOF: [L2/インフラ] <- mekhane/anamnesis/models/ P3→知識の正規化が必要→m |
| `paper.py` | PROOF: [L2/インフラ] |
| `prompt_module.py` | Gnōsis Prompt Module Model - Library プロンプト統一スキーマ |

---

*Generated: 2026-02-08 by generate_proofs.py*
