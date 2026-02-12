# シンプリシティの門番 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **非推奨ロジックの残留 (`synedrion_review`)** (High): `synedrion_review` メソッドは非推奨であり、SRP違反（ビジネスロジックの混入）を自認しています。外部モジュールへの依存もあり、クライアントクラスを不必要に肥大化させています。`SynedrionReviewer` への移行が示唆されているため、削除すべきです。
- **ライブラリ内のテストコード (`main`)** (Medium): `main` 関数および `if __name__ == "__main__":` ブロックが含まれており、`argparse` を使用したCLIロジックがライブラリコードに混在しています。これらは別スクリプトまたはテストファイルに分離すべきです。
- **冗長なエイリアス (`parse_state`)** (Low): `SessionState.from_string` の単なるラッパーであり、内部的にもこのエイリアスが使用されています。直接メソッドを呼び出すことで、不必要な間接層を排除できます。
- **不要なネスト (`batch_execute`)** (Low): `tracked_execute` は `bounded_execute` を呼び出してリストに追加するためだけのネスト関数です。`TaskGroup` の使用方法を整理することで構造を簡素化できます。

## 重大度
High
