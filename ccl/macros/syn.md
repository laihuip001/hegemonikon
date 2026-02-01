# @syn マクロ

## 概要

Synteleia 認知アンサンブルを呼び出し、多角的監査を実行する。

## 派生

| マクロ | 意味 | 層 |
|:-------|:-----|:---|
| `@syn·` | 内積モード（統合）| 全層 |
| `@syn×` | 外積モード（交差検証）| 全層 |
| `@poiesis` | 生成層のみ | O,S,H |
| `@dokimasia` | 審査層のみ | P,K,A |
| `@S{...}` | 指定エージェント | 選択 |

## CCL 展開

```ccl
@syn· $target
→
synteleia_audit($target, mode="inner_product")
```

```ccl
@syn× $target
→
synteleia_audit($target, mode="outer_product")
```

```ccl
@S{O,A,K} $target
→
synteleia_audit($target, agents=["O", "A", "K"])
```

## 実装

- **Parser**: `hermeneus/src/parser.py` L212-238
- **Translator**: `hermeneus/src/translator.py` L103-195
- **Tests**: `hermeneus/tests/test_synteleia.py` (17 tests)

## 関連

- [synteleia.md](../../docs/architecture/synteleia.md)
- [orchestrator.py](../../mekhane/synteleia/orchestrator.py)
