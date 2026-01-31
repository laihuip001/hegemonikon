# コンテキストスイッチ検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`synedrion_review` メソッドにおける `mekhane.ergasterion.synedrion` への強い依存**:
  - `synedrion_review` メソッドは、動的インポートにより `mekhane.ergasterion.synedrion.PerspectiveMatrix` に依存しています。
  - レビューのロジック（パースペクティブのロード、プロンプト生成など）が `mekhane/ergasterion/synedrion/` 以下のファイル群（例: `__init__.py`, `perspectives.yaml`）に分散しており、このメソッドの挙動を理解・修正するためには、クライアントコードと定義ファイルの間を頻繁に行き来する必要があります。
  - 汎用的な API クライアントの中に、特定のビジネスロジック（Synedrion レビュー）が混入しているため、関心が分離されていません。

- **CLI ロジックの混在**:
  - `if __name__ == "__main__":` ブロックに CLI ツールとしての実装が含まれています。
  - これにより、クライアントライブラリとしての機能と、テスト・実行用の CLI ツールとしての機能が同居しており、テストやデバッグの際に `tests/` ディレクトリや他の CLI 定義との間でのコンテキストスイッチが発生する可能性があります。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
