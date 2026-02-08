# PROOF.md — 存在証明書

PURPOSE: ワークフロー実行のフロー制御エンジン
REASON: 複雑なワークフロー手順の逐次・並列実行管理が必要だった

> **∃ flow/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `創造・生成機能 (コード生成、テンプレート展開等) を実装する` の一部として存在が要請される
2. **機能公理**: `ワークフロー実行のフロー制御エンジン` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | PROOF: [L2/インフラ] <- mekhane/poiema/flow/ O4→創造機能が必要 |
| `doxa_cache.py` | Doxa Cache — H4 Doxa Instantiation |
| `energeia_core.py` | Energeia Core — O4 Energeia Instantiation |
| `epoche_shield.py` | Epochē Shield — A2 Krisis (Epochē) Instantiation |
| `metron_resolver.py` | Metron Resolver — S1 Metron Instantiation |
| `noesis_client.py` | Noēsis Client — O1 Noēsis Instantiation (API Layer) |

---

*Generated: 2026-02-08 by generate_proofs.py*
