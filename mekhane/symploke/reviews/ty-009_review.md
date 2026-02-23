# Protocolの伝道師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **具体的なクラスへの依存 (`IntentWALManager`, `AttractorDispatcher`)**:
  `get_boot_context` 内で `IntentWALManager` を、`extract_dispatch_info` 内で `AttractorDispatcher` を直接インスタンス化して使用している。これらは「振る舞い」ではなく「実装」に依存している。将来的に異なる保存バックエンドやディスパッチロジックに差し替える際、コードの変更が必要になる。`load_latest()` を持つ `SessionLoader` Protocol や、`dispatch()` を持つ `Dispatcher` Protocol として定義すべきである。

- **データ構造の具体的な型への依存 (`IntentWAL`)**:
  `IntentWAL` データクラスの具体的なフィールド構成に依存している。必要な属性（`session_goal`, `progress` 等）のみを持つ Protocol を定義することで、データ構造の実装詳細（フィールドの追加・削除や内部表現の変更）からロジックを分離できる。

## 重大度
Low
