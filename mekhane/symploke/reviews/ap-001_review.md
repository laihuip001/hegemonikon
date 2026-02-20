# RESTの弁護士 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **REST原則違反 (URI内の動詞)**:
  - 313行目付近のn8n Webhook URL `http://localhost:5678/webhook/session-start` に動詞 `start` が含まれています。
  - **原則**: "動詞はHTTPメソッド、名詞はリソース"。
  - **推奨**: リソースを表す名詞（例: `/webhook/sessions`）を使用し、開始の意図はHTTPメソッド（POST）で表現すべきです。

## 重大度
Medium
