# PROOF.md — 存在証明書

PURPOSE: 外部知識源からデータを収集するコレクタモジュール群
REASON: Gnōsis に多様なデータソースを統合する必要があった

> **∃ collectors/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `セッション間の記憶・知識の永続化と検索を提供し、認知の連続性を担保する` の一部として存在が要請される
2. **機能公理**: `外部知識源からデータを収集するコレクタモジュール群` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | PROOF: [L2/インフラ] <- mekhane/anamnesis/collectors/ P3→知識収集が必要 |
| `arxiv.py` | PROOF: [L2/インフラ] |
| `base.py` | PROOF: [L2/インフラ] |
| `openalex.py` | PROOF: [L2/インフラ] |
| `semantic_scholar.py` | PROOF: [L2/インフラ] |

---

*Generated: 2026-02-08 by generate_proofs.py*
