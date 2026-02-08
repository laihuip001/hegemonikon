# PROOF.md — 存在証明書

PURPOSE: プロジェクト全体のユーティリティスクリプト群
REASON: boot/bye/daily/export 等の運用スクリプトを一箇所に集約する必要があった

> **∃ scripts/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `プロジェクト全体のユーティリティスクリプト群` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `add_activation_triggers.py` | Library 111ファイルに activation_triggers と essence を追加 |
| `boot_gnosis.py` | Gnōsis Boot Integration — /boot Phase 3 expansion. |
| `cone_bridge.py` | PROOF: [L3/ユーティリティ] <- scripts/ |
| `e2e_demo.py` | FEP E2E Demo — 動く認知体のデモンストレーション |
| `generate_proofs.py` | Batch-generate PROOF.md for directories that have Python fil |
| `generate_reasons.py` | REASON Auto-Generator — LLM-based PROOF.md REASON field gene |
| `gnosis_index_update.py` | Gnōsis Knowledge Index — 自動更新スクリプト |
| `index_library.py` | Library 112ファイルを Gnōsis LanceDB にインデックス |
| `refactor_brain_dev_modules.py` | Brain 開発用 Module 01-25 → Hegemonikón Library 変換スクリプト |
| `refactor_brain_modules.py` | Brain モジュール → Hegemonikón Library 変換スクリプト |
| `refactor_brain_si_forge.py` | Brain Phase 3+4: System Instructions + Forge Prompt Structur |
| `refine_forge_triggers.py` | Forge モジュールの activation_triggers を精緻化 |
| `steering_poc.py` | steering_poc |
| `wf_postcheck.py` | wf_postcheck.py — 汎用 WF ポストチェック |

---

*Generated: 2026-02-08 by generate_proofs.py*
