# 非同期リソース管理評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` および `get_session` メソッド内で、呼び出しごとに `aiohttp.ClientSession` を新規作成・破棄しています。
    - `async with aiohttp.ClientSession() as session:` が各メソッド内で使用されています。
    - これにより、TCPコネクションの再利用（Keep-Alive）が行われず、特にポーリング処理（`poll_session`）やバッチ処理（`batch_execute`）において不要なオーバーヘッド（ハンドシェイク、リソース確保）が発生します。
    - また、高負荷時にはポート枯渇のリスクがあります。
- `JulesClient` クラスのインスタンスレベルで `ClientSession` を保持し、再利用する設計（または外部から注入する設計）に変更することが推奨されます。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
