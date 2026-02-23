# 副作用の追跡者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **暗黙のネットワークI/O (High)**: `get_boot_context` 関数はコンテキスト取得を示唆する命名ですが、内部で `urllib.request.urlopen` を使用して n8n への POST リクエスト送信という副作用を持っています。これは純粋な getter であるべき関数における重大な副作用の隠蔽です。
- **グローバル状態の変更 (High)**: `main` 関数内で `warnings.filterwarnings("ignore")` を実行しており、プロセス全体の警告設定をグローバルに変更しています。これは他のモジュールのデバッグを妨げる可能性があります。
- **隠されたファイル書き込み (Medium)**: `print_boot_summary` は出力を示唆する命名ですが、詳細モード時に `generate_boot_template` を経由して `/tmp` へのファイル書き込みを行っています。I/O操作が関数名から予測できません。
- **例外の握りつぶし (Medium)**: `extract_dispatch_info`, `_load_projects`, `_load_skills`, `get_boot_context` など多数の箇所で `except Exception: pass` が使用されており、予期せぬエラーが隠蔽されています。

## 重大度
High
