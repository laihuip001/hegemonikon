# 境界値テスター レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **mask_api_key**: `visible_chars=0` の場合、スライス `key[-0:]` が `key` 全体と評価され、意図せずAPIキーが**完全漏洩**する (Critical)
- **mask_api_key**: `visible_chars < 0` の場合、スライスが意図しない範囲となり、キーの大部分が表示される (High)
- **JulesClient.__init__**: `max_concurrent=0` を許容しており、その場合 `Semaphore(0)` が生成され、`batch_execute` 等でタスクが永遠に開始されない（デッドロック） (Medium)
- **with_retry**: `max_attempts=0` の場合、ループが実行されず、関数が呼び出されずに `None` が返る (Medium)
- **poll_session**: `timeout=0` の場合、ステータスチェックを行わずに即座に `TimeoutError` となる可能性がある (Low)

## 重大度
Critical
