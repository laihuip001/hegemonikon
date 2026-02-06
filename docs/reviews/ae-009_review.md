# import順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- stdlibとthird-partyの混在: `aiohttp` (third-party) が `asyncio` 等のstdlib群の中に混在している (Medium)
- 空行による分離の欠如: stdlib群と `aiohttp` の間に空行がない (Low)

## 重大度
Medium
