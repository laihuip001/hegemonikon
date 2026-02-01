# オンボーディング障壁検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **未定義の専門用語 (Undefined Jargon):** "Hegemonikón", "Symplokē", "Synedrion", "Ultra plan" などの用語が説明なく使用されており、新規参加者が文脈を理解するのを妨げている。
- **不安全なデフォルト設定 (Unsafe Defaults):** `MAX_CONCURRENT` が "Ultra plan" 向けの 60 にハードコードされており、通常プランのユーザーが意図せずレート制限に抵触するリスクがある。また、`BASE_URL` が `googleapis.com` ドメインになっているが、一般の開発者がアクセス可能か不明確である。
- **誤解を招くCLI出力 (Misleading CLI Output):** CLI テスト実行時、コンテキストマネージャ (`async with`) を使用していないにもかかわらず `Connection Pooling: Enabled` と表示される。実際にはリクエスト毎に新しいセッションが作成・破棄されており、ユーザーに誤った安心感を与える。
- **部族的な知識への依存 (Tribal Knowledge):** `th-003 fix`, `cl-004` などのレビューIDがコード内のコメントに散在しており、背景を知らない開発者にとってノイズとなっている。
- **隠れた依存関係 (Hidden Dependencies):** `synedrion_review` メソッド内で `mekhane.ergasterion.synedrion` を動的にインポートしており、モジュールの冒頭で依存関係が把握できないため、環境構築時のトラブル要因となり得る。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
