# PROOF.md — 存在証明書

PURPOSE: routes モジュールの実装
REASON: routes の機能が必要だった

> **∃ routes/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón の実装コード (Mēkhanē) を格納し、認知ハイパーバイザーの全機能を提供する` の一部として存在が要請される
2. **機能公理**: `routes モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | PROOF: [L2/インフラ] <- mekhane/api/routes/ |
| `ccl.py` | CCL Routes — Hermēneus dispatch/executor と WorkflowRegistry  |
| `dendron.py` | Dendron Routes — dendron/checker モジュールのラッパー |
| `digestor.py` | Digestor API — digest_report の閲覧エンドポイント |
| `fep.py` | FEP Routes — fep_agent_v2 のラッパー |
| `gateway.py` | Gateway Router — MCP Gateway の REST API エンドポイント |
| `gnosis.py` | Gnōsis Routes — anamnesis GnosisIndex のラッパー |
| `gnosis_narrator.py` | Gnōsis Narrator Routes — 知識は問いとして走ってくる |
| `graph.py` | Graph Routes — Trígōnon/Taxis データを JSON API で提供 |
| `kalon.py` | Kalon Router — 概念の Kalon 判定を保存・取得する |
| `link_graph.py` | Link Graph Routes — LinkGraph データを 3D 可視化用 JSON API で提供 |
| `pks.py` | PKS Routes — 能動的知識表面化 API |
| `postcheck.py` | Postcheck Routes — wf_postcheck モジュールのラッパー |
| `sophia.py` | Sophia KI Routes — Knowledge Items の CRUD 管理 API |
| `status.py` | Status Routes — Peira hgk_health モジュールのラッパー |
| `sympatheia.py` | PROOF: [L2/Sympatheia] <- mekhane/api/routes/ |
| `symploke.py` | Symploke Routes — 知識統合層 REST API |
| `synteleia.py` | Synteleia Routes — 監査 REST API |
| `timeline.py` | Timeline Router — mneme/ の記録を統合タイムラインとして提供 |

---

*Generated: 2026-02-08 by generate_proofs.py*
