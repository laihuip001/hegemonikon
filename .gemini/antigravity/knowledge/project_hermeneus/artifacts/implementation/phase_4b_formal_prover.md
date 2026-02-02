# Implementation: Phase 4b — Formal Prover Interface

## 1. 概要
Phase 4b では、LLM による検証（Phase 4: Debate）を補完するため、決定論的かつ数学的な検証手段である **Formal Prover Interface** を導入した。これにより、生成されたコードの型安全性やデータのスキーマ妥当性を厳格に保証することが可能となった。

## 2. 構成コンポーネント (`prover.py`)

### 2.1 MypyProver (Type Verification)
- **機能**: Python の型ヒントを `mypy` ツールを用いて検証する。
- **実装手法**: 動的なスクリプト生成とサブプロセスによる静的解析。
- **Strict Mode**: 厳格な型チェックをオプションで提供。

### 2.2 SchemaProver (Schema Verification)
- **機能**: 生成された JSON などのデータ構造を `jsonschema` で検証する。
- **フォールバック**: ライブラリ不在時のためのシンプルな JSON キー存在チェック機能を搭載。

### 2.3 Lean4Prover (Formal Proof)
- **機能**: Lean 4 定理証明支援系を用いた数学的証明の検証。
- **ステータス**: オプション機能。環境内に `lean` コマンドが存在する場合のみ動作する。

### 2.4 ProofCache
- **機能**: 計算コストの高い証明結果を SQLite データベースにキャッシュする。
- **TTL**: キャッシュの有効期限を設定可能。

## 3. 実装のポイント
- **Interface 抽象化**: `ProverInterface` 基底クラスにより、将来的な Z3 や Dafny への拡張を容易にしている。
- **ハイブリッド検証**: `verify_code` 関数は、複数の Prover を組み合わせて一括検証を行う。

## 4. API 使用例
```python
from hermeneus.src import verify_code, MypyProver

# 型チェックの実行
result = verify_code(
    code="def add(a: int, b: int) -> int: return a + b",
    prover=MypyProver()
)
if result.verified:
    print("Code is type-safe.")
```

---
*最終更新: 2026-02-01 | Hermēneus Phase 4b Implementation*
