# SRP外科医 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **get_boot_context の責務過多**: データ取得（Logic）、文字列フォーマット（View）、n8n Webhook送信（IO/Side-effect）が単一関数に混在している。(Critical)
- **ローダー関数の責務混在**: `_load_projects` および `_load_skills` が、データの読み込み・フィルタリング（Logic）と、表示用Markdownの生成（View）を同時に行っている。(High)
- **検証と表示の結合**: `postcheck_boot_report` がバリデーションロジックと結果の整形表示を混在させている。(Medium)
- **副作用の隠蔽**: `get_boot_context` という名前（取得）にもかかわらず、外部システムへの通知（n8n webhook）という副作用を含んでいる。(Medium)

## 重大度
Critical
