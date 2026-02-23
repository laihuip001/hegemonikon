# tests/

> テスト群 — このサブパッケージのユニットテストを集約

## 構成

- **__init__.py**
- **test_consensus_and_stats.py**
- **test_cortex_backend.py** — CortexBackend の接続テスト + フォールバック動作検証
- **test_l2_live.py** — L2 SemanticAgent 実弾テスト (OpenAI Backend)
- **test_language_checks.py** — audit helper
- **test_multi_semantic.py** — MultiSemanticAgent のテスト (Layer B: Nous)
- **test_multilang_strip.py**
- **test_pattern_consistency.py** — YAML パターンと _FALLBACK ハードコード値のドリフトを検出
- **test_semantic_agent.py** — Test suite validating parse l l m response correctness
- **test_synteleia.py** — Synteleia 2層オーケストレーター + 基底クラスの包括テスト
