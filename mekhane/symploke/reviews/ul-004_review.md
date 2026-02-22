# コード量減少主義者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context` 内のインラインロジック肥大化 (Low)**
  - WAL読み込み (~30行)、BC違反チェック (~15行)、Incoming確認 (~10行)、n8n通知 (~15行) が関数内に直書きされている。
  - `boot_axes.py` の `load_wal`, `load_bc_violations`, `load_incoming`, `notify_session_start` 等に委譲すべき。
  - これにより `get_boot_context` は純粋なオーケストレーターとなり、可読性が向上する。

- **循環参照と責務の配置ミス: `extract_dispatch_info` (Low)**
  - `boot_integration.py` で定義されているが、呼び出し元は `boot_axes.py` (`load_attractor`) である。
  - `boot_integration.py` が `boot_axes.py` を import し、逆に `boot_axes.py` が `boot_integration.py` を import する循環構造を生んでいる。
  - `extract_dispatch_info` を `boot_axes.py` または独立したユーティリティに移動すべき。

- **ヘルパー関数の逆流: `_load_projects`, `_load_skills` (Low)**
  - これらは `boot_integration.py` で定義されているが、実態は `boot_axes.py` から import して使用されている。
  - `get_boot_context` -> `boot_axes.load_projects` -> `boot_integration._load_projects` という非効率な呼び出し構造になっている。
  - `boot_axes.py` に移動することで、`boot_integration.py` から約100行を削減できる。

- **手続的テキスト生成: `generate_boot_template` (Low)**
  - 約100行にわたり文字列連結で Markdown を生成している。
  - テンプレートファイル (`boot_report_template.md`) を用意し、プレースホルダー置換する方式に変更すべき。
  - コードの見通しが悪く、修正も困難。

- **検証ロジックの混入: `postcheck_boot_report` (Low)**
  - 約80行のバリデーションロジックが含まれている。
  - `boot_validator.py` 等に切り出し、統合層から分離すべき。

- **巨大な定数定義: `THEOREM_REGISTRY` (Low)**
  - 約30行の定数定義がファイルの冒頭を占有している。
  - 別の定数定義ファイル (`boot_constants.py` や `kernel/constants.py`) に移動すべき。

## 重大度
Low
