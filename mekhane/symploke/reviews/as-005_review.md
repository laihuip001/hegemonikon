# async/sync混在警察 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `synedrion_review` (async) 内で `PerspectiveMatrix.load()` (sync/blocking I/O) を呼び出しており、ファイル読み込みとYAML解析によりイベントループをブロックしています。(High)
- `__init__` (sync) 内で `asyncio.Semaphore` を生成していますが、実行ループが確定していない段階での生成は、ループの不一致を引き起こす可能性があります。(Low)

## 重大度
High
