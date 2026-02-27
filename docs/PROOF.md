# PROOF.md — 存在証明書

PURPOSE: docs モジュールの実装
REASON: docs の機能が必要だった

> **∃ docs/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `docs モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `enrich_o_series.py` | Enrich O-series WFs with BC-15 compliant detailed data. |
| `enrich_pka_series.py` | Enrich P/K/A series WFs with BC-15 compliant detailed data. |
| `enrich_sh_series.py` | Enrich S-series + H-series WFs with BC-15 compliant detailed |
| `generate_wf_data.py` | Generate wf-data.js from workflow markdown sources. |
| `patch_wf_data.py` | Patch wf-data.js with enriched phases and usecases extracted |

---

*Generated: 2026-02-08 by generate_proofs.py*
