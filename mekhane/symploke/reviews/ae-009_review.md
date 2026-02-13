# import順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- standard library (`asyncio`, `functools`等) と third-party library (`aiohttp`) が混在している (Medium)
- standard library と third-party library の間に空行による分離がない (Medium)

## 重大度
Medium
