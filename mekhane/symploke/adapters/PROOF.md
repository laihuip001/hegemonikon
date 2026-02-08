# PROOF.md — 存在証明書

PURPOSE: 外部 API との接続アダプタ群
REASON: Jules/n8n 等の外部サービスとの統一的接続層が必要だった

> **∃ adapters/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `複数の認知モジュールを統合し、/boot シーケンスやオーケストレーション機能を提供する` の一部として存在が要請される
2. **機能公理**: `外部 API との接続アダプタ群` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Symplokē Adapters |
| `base.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダ |
| `embedding_adapter.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダ |
| `hnswlib_adapter.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダ |
| `mock_adapter.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダ |

---

*Generated: 2026-02-08 by generate_proofs.py*
