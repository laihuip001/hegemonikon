# LLM痕跡検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- 過剰な `# PURPOSE:` コメントが多数存在し、直後のコードやdocstringと重複している (例: `decorator の処理`, `wrapper の処理`, `Get session status` など)。これらは「以下のコードは〜を行います」というLLM特有の解説パターンに相当する。

## 重大度
Low
