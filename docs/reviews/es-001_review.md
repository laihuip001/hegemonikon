# 査読バイアス検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **内集団言語 (In-group Language)**: `Hegemonikón`, `Symplokē`, `Synedrion`, `Ergasterion` といったギリシャ語由来の特殊用語が多用されており、外部の開発者にとって文脈理解の障壁となっている。また、`th-003`, `ai-006` などの内部レビューIDへの参照がコードコメントに散在しており、文脈を知らない者には意味不明である。
- **特権バイアス (Privilege Bias)**: `MAX_CONCURRENT = 60` のコメントに "Ultra plan limit" とあり、ユーザーが高位のプランを利用していることを暗黙の前提としている。これ以下のプランを利用するユーザーにとっては、デフォルト設定がレート制限違反を引き起こす可能性がある。
- **楽観性バイアス (Optimism Bias)**: `create_session` メソッドのデフォルト引数が `auto_approve=True` (承認スキップ) および `automation_mode="AUTO_CREATE_PR"` となっている。これはAIの生成物が常に安全または正確であるという楽観的な仮定に基づいており、安全性よりも利便性を優先している。
- **権威主義的記述**: "Refactored based on 58 Jules Synedrion reviews" や "Hegemonikón theorem grid" といった記述は、システムの複雑さや権威を強調する方向に作用しており、実用的な説明よりも内輪の正当性を主張する傾向が見られる。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
