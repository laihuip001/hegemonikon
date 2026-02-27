# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **責務混在 (_load_projects)**: `registry.yaml` の読み込み (IO)、フィルタリング (Logic)、および表示用文字列の整形 (Presentation) が一つの関数に混在しています。(High)
- **責務混在 (_load_skills)**: ディレクトリ走査 (IO)、YAML解析 (Logic)、および表示用文字列の整形 (Presentation) が一つの関数に混在しています。(High)
- **責務混在 (get_boot_context)**: 軸の統合 (Orchestration)、GPUチェックやWebhook送信 (Side Effects)、および最終出力の整形 (Presentation) が混在しています。特に n8n Webhook 送信は副作用であり、データ取得関数に含まれるべきではありません。(High)
- **責務混在 (postcheck_boot_report)**: ファイル読み込み (IO)、検証ロジック (Validation)、および結果の整形 (Presentation) が混在しています。(Medium)
- **責務混在 (generate_boot_template)**: テンプレート生成ロジック (Logic/Presentation) とファイル書き込み (IO) が混在しており、テストが困難です。(Medium)

## 重大度
High
