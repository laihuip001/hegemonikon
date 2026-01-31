# mekhane/ccl/ PROOF

> **存在証明**: このディレクトリは CCL パーサー・ジェネレーター実装を格納

## 必然性の導出

```
CCL (認知制御言語) が存在する
→ CCL を解析・生成するコードが必要
→ ccl/ ディレクトリが担う
```

## 粒度

**L1/定理**: 24定理を記号的に操作する中核機能

## 主要ファイル

| File | 役割 |
|------|------|
| `generator.py` | 自然言語 → CCL 式生成 |
| `llm_parser.py` | CCL 式 → 構造化データ |
| `macro_expander.py` | マクロ展開 |
| `semantic_validator.py` | 意味検証 |
| `tracer.py` | 実行トレース |
