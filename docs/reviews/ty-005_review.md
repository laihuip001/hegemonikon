# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesSession` に `@dataclass(frozen=True)` が指定されていません (Medium)
- `JulesResult` に `@dataclass(frozen=True)` が指定されていません (Medium)

## 重大度
Medium
