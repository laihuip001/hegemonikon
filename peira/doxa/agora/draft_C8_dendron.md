# コードの「存在証明」を自動化する — Dendron

> **ID**: C8
> **想定媒体**: Zenn（技術記事）
> **想定読者**: ソフトウェアエンジニア、テックリード
> **フック**: 全てのファイルに「なぜ存在するか」を書かせる

---

## リード文（案）

プロジェクトが大きくなると、「このファイル、何のためにある？」が頻発する。

Dendron は、**全ファイルに存在証明 (PURPOSE コメント) を強制する**ツール。
書かれていなければ警告。形式が不正なら指摘。

「存在理由のないコードは、存在すべきではない」。

---

## 本文構成（案）

### 1. PURPOSE コメント

```python
# PURPOSE: VectorDB アダプタの抽象基底クラス。
# hnswlib/faiss/sqlite-vss を統一インターフェースで切り替え可能にする。
```

### 2. PROOF.md — モジュールレベルの存在証明

```markdown
# mekhane/symploke/ — PROOF

## 存在理由
VectorDB の実装詳細を隠蔽し、アダプタパターンで切り替え可能にする。

## 証明レベル
Level 3: テスト通過 + 実運用

## 依存先
- mekhane/anamnesis/ (Gnōsis)
- mekhane/gnosis/ (Sophia)
```

### 3. Dendron Checker

```bash
python mekhane/dendron/checker.py mekhane/symploke/
```

出力:

```
[PASS] adapter.py — PURPOSE あり
[FAIL] utils.py — PURPOSE なし
[WARN] __init__.py — PURPOSE が短すぎる (< 10文字)
```

### 4. 証明レベル (5段階)

| Level | 名称 | 基準 |
|:------|:-----|:-----|
| L0 | 未証明 | PURPOSE なし |
| L1 | 主張 | PURPOSE + 通常コメント |
| L2 | テスト | L1 + テスト通過 |
| L3 | 実運用 | L2 + 実運用で使用 |
| L4 | 不動点 | L3 + リファクタ後も構造不変 |

### 5. 143K 行での実績

| 指標 | 値 |
|:-----|:---|
| 総ファイル数 | ~500 |
| PURPOSE カバレッジ | 92% |
| PROOF.md 数 | 15 |
| L3+ ファイル | 60% |

### 6. 読者が試せること

```python
# PURPOSE チェッカー (最小版)
import ast, sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Module) and ast.get_docstring(node):
            print(f"[PASS] {sys.argv[1]}")
            break
    else:
        print(f"[FAIL] {sys.argv[1]} — docstring なし")
```

---

*ステータス: たたき台*
*関連: C2 (787コミット), E8 (バージョン管理)*
