# tests/

> テスト群 — このサブパッケージのユニットテストを集約

## 構成

- **__init__.py**
- **test_ccl_batch3.py** — CCL Guardrails, DoxaLearner, SemanticValidator の包括テスト
- **test_ccl_modules.py** — CCL Pattern Cache, Workflow Signature, Output Schema, Tracer の包括テスト
- **test_macro_system.py** — CCL Macro Registry & Expander の包括テスト
- **test_operator_loader.py**
- **test_output_schema.py** — CCL Output Schema (Pydantic) の包括テスト
- **test_pattern_cache.py** — Test suite validating pattern cache generate correctness
- **test_sel_validator.py** — CCL SEL Validator の包括テスト — WF出力がSEL要件を満たすか検証
- **test_syntax_validator.py** — CCL SyntaxValidator の包括テスト — v2.0仕様準拠を検証
