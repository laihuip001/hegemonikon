# ccl/ PROOF

> **存在証明**: CCL 言語仕様・ドキュメントを格納

## 必然性の導出

```
CCL (認知制御言語) が存在する
→ 言語仕様ドキュメントが必要
→ ccl/ ディレクトリが担う
```

## 構造

```
ccl/
├── README.md           # CCL 概要
├── operators.md        # 演算子仕様
├── wf_classification.md # ワークフロー分類
├── examples/           # 使用例
└── macros/             # マクロ定義
```

## mekhane/ccl/ との関係

- **ccl/**: 仕様・ドキュメント (言語設計)
- **mekhane/ccl/**: 実装・パーサー (言語処理)
