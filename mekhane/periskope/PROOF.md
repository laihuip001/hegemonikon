# PROOF.md — Periskopē

> **存在証明**: HGK Deep Research Engine

## 動作確認

| テスト | 結果 | 日付 |
|:-------|:-----|:-----|
| SearXNG Docker 起動 | ✅ `localhost:8888` で応答 | 2026-02-15 |
| JSON API 検索 | ✅ 72 results for "test" | 2026-02-15 |
| test_health_check | ✅ PASSED | 2026-02-15 |
| test_basic_search | ✅ PASSED | 2026-02-15 |
| test_academic_search | ✅ PASSED | 2026-02-15 |
| test_search_result_metadata | ✅ PASSED | 2026-02-15 |
| test_empty_query | ✅ PASSED | 2026-02-15 |

## 構成

```
mekhane/periskope/
  __init__.py          — パッケージ定義
  models.py            — 共通データモデル (8 dataclass)
  searchers/
    __init__.py
    searxng.py         — SearXNG async クライアント
  docker/
    docker-compose.yml — SearXNG コンテナ
    settings.yml       — 検索エンジン設定
  tests/
    test_searchers.py  — 5 tests, all passed
```

## Sprint 状態

| Sprint | 内容 | 状態 |
|:-------|:-----|:-----|
| **S1** | models + SearXNG Docker + searxng.py | ✅ 完了 |
| S2 | exa + internal searchers | 未着手 |
| S3 | synthesizer (Cortex + LS) | 未着手 |
| S4 | CitationAgent | 未着手 |
| S5 | engine + CLI + CCL 統合 | 未着手 |
