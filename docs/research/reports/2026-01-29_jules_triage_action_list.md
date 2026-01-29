# Jules Review Branch Triage Report

**日付**: 2026-01-29
**対象**: 130+ レビューブランチ
**主対象ファイル**: `mekhane/symploke/jules_client.py`

---

## Executive Summary

Jules の 130+ レビューブランチを精査した結果、**一貫したパターン**が浮かび上がりました。
多くのエキスパートが**同一の問題**を異なる視点から指摘しており、これは修正の優先度が高いことを示しています。

### 沈黙の原則

- **発言**: 問題あり → 要修正
- **沈黙**: 問題なし → 変更不要

---

## 🔴 Critical / High Priority

### 1. ClientSession Pooling (接続プーリング)

**言及回数**: 8+ ブランチ (ai-009, cl-004, as-008, th-003, ai-004, etc.)

**問題**:

```python
# 現在の実装 (各リクエストで新規セッション)
async with aiohttp.ClientSession() as session:
    async with session.post(...) as resp:
        ...
```

**改善案**:

```python
class JulesClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=30, keepalive_timeout=30)
        self._session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
```

**効果**:

- TCP 接続・SSL ハンドシェイクの削減
- Ephemeral Port 枯渇防止
- レイテンシ低減

---

### 2. parse_state の UNKNOWN 処理

**言及回数**: 6+ ブランチ (th-001, th-010, ai-004, etc.)

**問題**:

```python
# 現在: 未知の状態を IN_PROGRESS にマッピング
except ValueError:
    return SessionState.IN_PROGRESS  # "likely active"
```

**改善案**:

```python
class SessionState(Enum):
    UNKNOWN = "unknown"  # 既存 (未使用)
    # ...

    @classmethod
    def from_string(cls, value: str) -> "SessionState":
        """状態文字列をパース。未知の終端状態に対応。"""
        try:
            return cls(value.lower())
        except ValueError:
            logger.warning(f"Unknown session state: {value}")
            # 未知の状態は UNKNOWN として扱う
            return cls.UNKNOWN
```

**効果**:

- API 仕様変更時の無限ポーリング防止
- 予測誤差（FEP）の適切な処理
- デバッグ容易性向上

---

### 3. Semaphore スコープ (グローバル並行性制御)

**言及回数**: 3+ ブランチ (th-003, etc.)

**問題**:

```python
# 現在: メソッドローカルの Semaphore
async def batch_execute(self, ..., max_concurrent: int = 30):
    semaphore = asyncio.Semaphore(max_concurrent)
```

**改善案**:

```python
class JulesClient:
    MAX_CONCURRENT = 60  # API グローバル制限
    
    def __init__(self, ...):
        # インスタンスレベルの Semaphore
        self._global_semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)
```

**効果**:

- 複数の `batch_execute` 呼び出し間での制限順守
- API レート制限超過の防止

---

## 🟠 Medium Priority

### 4. API キーマスキング改善

**言及回数**: 2+ ブランチ (ai-009, th-010)

**問題**:

```python
# 短いキーで情報漏洩リスク
print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
```

**改善案**:

```python
def mask_key(key: str, visible_chars: int = 4) -> str:
    if len(key) <= visible_chars * 2:
        return "***"  # 短いキーは完全マスク
    return f"{key[:visible_chars]}...{key[-visible_chars:]}"
```

---

### 5. MAX_CONCURRENT 定数の活用

**言及ブランチ**: ai-016 (デッドコード検出)

**問題**:

- `MAX_CONCURRENT = 60` が定義されているが `batch_execute` のデフォルトは `30`
- 定数が実際のロジックで未使用

**改善案**:

```python
async def batch_execute(
    self,
    prompts: list[str],
    max_concurrent: int | None = None,  # None = クラス定数使用
    ...
):
    limit = max_concurrent or self.MAX_CONCURRENT
```

---

### 6. バックオフ復帰ロジック

**言及ブランチ**: ai-004

**問題**:

```python
# 成功後も増加した backoff が使われる
backoff = min(backoff * 2, 60)  # エラー時
# 次の成功時も 60秒待機してしまう
```

**改善案**:

```python
while True:
    try:
        session = await self.get_session(session_id)
        backoff = poll_interval  # 成功時はリセット
        if session.state in terminal_states:
            return session
    except RateLimitError:
        backoff = min(backoff * 2, 60)
    await asyncio.sleep(backoff)
```

---

## 🟢 Low Priority / Already Good

### 認知負荷 (Cognitive Load)

**評価**: 低（良好）

- 変数スコープの局所化が適切
- ネスト深度 3 以下
- 命名が明確

### Orphaned Task

**評価**: 問題なし

- タスクキャンセル時の適切なクリーンアップ

### 例外境界のグループ化

**評価**: 適切

- `bounded_execute` による個別エラー隔離が正しく実装

---

## 📊 ブランチカテゴリ分類

| カテゴリ | 件数 | 代表ブランチ |
|:--------|-----:|:-------------|
| Connection/Pool | 8+ | `connection-pool-review-*`, `chunking-*` |
| FEP/Prediction | 6+ | `th-00*-review-*`, `th-01*-review-*` |
| Hallucination | 4+ | `*-hallucination-review-*` |
| Security | 3+ | `doc-security-review-*` |
| Cognitive Load | 5+ | `cognitive-load-review-*`, `cl-*-review-*` |
| Logic/Code Quality | 10+ | `logic-*`, `dead-code-*`, `scope-*` |
| Stoic/Philosophy | 1 | `jules-stoic-review-*` |

---

## 🎯 実装優先順位

| 優先度 | 改善項目 | 見積り | 影響 |
|:------:|:---------|:------:|:-----|
| 1 | ClientSession Pooling | 30min | パフォーマンス大幅改善 |
| 2 | parse_state → from_string | 15min | 堅牢性向上 |
| 3 | Semaphore グローバル化 | 20min | レート制限順守 |
| 4 | API キーマスキング | 5min | セキュリティ |
| 5 | MAX_CONCURRENT 活用 | 5min | コード品質 |
| 6 | バックオフリセット | 10min | 効率性 |

**合計見積り**: ~1.5時間

---

## 🗑️ ブランチクリーンアップ

レビュー完了後、以下のブランチは削除候補:

- 「沈黙」判定のブランチ（問題なし）
- 重複する指摘のブランチ

```bash
# 削除例 (要確認後)
git push origin --delete <branch-name>
```

---

*Generated by Hegemonikón O1 Noēsis Jules Triage*
