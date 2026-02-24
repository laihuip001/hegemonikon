# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **責務の混在 (Logic & Presentation)**: `_load_projects`, `_load_skills`, `get_boot_context`, `postcheck_boot_report` がデータの取得・計算と Markdown 文字列の整形を同一関数内で行っている。データ構造と表示形式は分離すべきである。(High)
- **Getter内の副作用 (Side Effects)**: `get_boot_context` という命名でありながら、n8n への Webhook 送信という副作用を含んでいる。「取得」と「通知」は別の責務である。(High)
- **オーケストレーションとアクションの混在**: `print_boot_summary` がデータのロード、計算（定理使用率）、出力、テンプレート生成をすべて担っている。(High)
- **複合的な戻り値**: 各関数が「生データ」と「整形済み文字列」の両方を辞書に詰めて返しており、戻り値の意味が複数化している。(High)

## 重大度
High
