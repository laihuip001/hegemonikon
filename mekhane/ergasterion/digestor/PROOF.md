# PROOF.md — 存在証明書

PURPOSE: 外部コンテンツを Hegemonikón に消化する変換エンジン
REASON: 外部知識を内部形式に変換する統一インターフェースが必要だった

> **∃ digestor/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `開発支援ツール群 (テスト、品質保証、生産性向上) を提供する` の一部として存在が要請される
2. **機能公理**: `外部コンテンツを Hegemonikón に消化する変換エンジン` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | PROOF: [L2/インフラ] <- mekhane/ergasterion/digestor/ A0→消化処理が必要 |
| `pipeline.py` | Digestor Pipeline - Gnosis → /eat 連携パイプライン |
| `scheduler.py` | Digestor Scheduler - OS 非依存の定時収集デーモン |
| `selector.py` | Digestor Selector - 消化候補選定ロジック |

---

*Generated: 2026-02-08 by generate_proofs.py*
