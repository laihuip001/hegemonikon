<!-- PROOF: [L2/Review] <- mekhane/symploke/boot_integration.py EC-001 review -->
# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 内で `registry.yaml` が空の場合、`yaml.safe_load` が `None` を返し、続く `data.get("projects", [])` で `AttributeError` が発生する (Critical)
- `_load_projects` 内で `path` が空文字のプロジェクトが、意図せず「コアランタイム」カテゴリに分類される (High)
- `extract_dispatch_info` が空の `context` を受け取った際、即座に空結果を返さずに `dispatcher.dispatch` を呼び出している (Low)
- `_load_skills` 内で `SKILL.md` が空の場合、空の内容を持つスキルとしてロードされてしまう (Low)

## 重大度
Critical
