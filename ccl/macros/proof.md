# @proof マクロ

> **定義**: `/noe{axiom=FEP}_/dia*{validate=∃}`

## 目的

構成要素の「存在の必然性」を証明する。

## 構文

```ccl
@proof <対象>
```

## 実行プロセス

1. **認識フェーズ** (`/noe{axiom=FEP}`): 対象が FEP から演繹されるか確認
2. **判定フェーズ** (`/dia*{validate=∃}`): 存在検証を融合

## 使用例

```ccl
@proof kernel/     # kernel ディレクトリの必然性を証明
@proof mekhane/    # mekhane ディレクトリの証明
@proof <any_file>  # 任意ファイルの証明
```

## 出力

PROOF.md ファイルとして証明書を生成。

---

*@proof | CCL v6.36*
