# コピペ痕跡検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **無効なエンドポイント (Hallucination):** `https://jules.googleapis.com/v1alpha` という存在しないGoogle APIエンドポイントがハードコードされている。これは一般的なGoogle APIのパターンを模倣したハルシネーションである。
- **ファントムレビュー参照:** `cl-003`, `th-003`, `cl-004`, `as-008`, `ai-006`, `ai-004`, `th-001`, `as-003`, `ai-009`, `th-010` など、`docs/reviews/` に存在しないレビューIDがコード内のコメントやdocstringで多数参照されており、これらは実在しない。
- **架空のプラン制限:** "Ultra plan limit" (MAX_CONCURRENT = 60) という、このプロジェクトのコンテキストには存在しない外部の経済的仮定（価格プラン）に基づいたコメントが存在する。
- **仕様の不一致 (Synedrion):** docstringやメソッド内で「480 orthogonal perspectives (20 domains × 24 axes)」と謳っているが、実際にインポートされる `mekhane/ergasterion/synedrion` モジュール（prompt_generator.py）は 120 perspectives (20 domains × 6 axes) で実装されており、コピペ元のバージョン違いかハルシネーションによる仕様の乖離がある。
- **誤解を招くCLI出力:** テスト用CLI (`main`関数) が、実際には接続プールを使用していない状態（コンテキストマネージャ外での単発インスタンス化）でも "Connection Pooling: Enabled (TCPConnector)" と静的に出力しており、実態と異なる。
- **自動生成ツールの痕跡:** `NOTE: Removed self-assignment` といった、自動リファクタリングツールのログと思われる冗長なコメントがそのまま残っており、コードの意図とは無関係なアーティファクトである。
- **未検証の数値:** "Refactored based on 58 Jules Synedrion reviews" という具体的な数値の根拠が不明であり、コピペ元のコンテキストをそのまま引きずっている可能性がある。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
