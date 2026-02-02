# Jules Client リファクタリング計画

> **Source**: 58 Jules レビューブランチから抽出したアイデア
> **Author**: Claude (独自設計)

---

## 🎯 発見された問題 (8レビューから抽出)

| # | 問題 | 重大度 | 根拠 |
|:--|:-----|:-------|:-----|
| 1 | **DRY違反**: HTTP リクエストロジックの重複 | Medium | ai-006 |
| 2 | **parse_state バグ**: 未知状態を IN_PROGRESS として返す | High | cl-003, cl-008, th-001 |
| 3 | **create_session にリトライなし** | Medium | th-001 |
| 4 | **バックオフロジックの密結合** | Medium | cl-008 |
| 5 | **失敗時の空ID** | Low | cl-003, th-001 |
| 6 | **ドキュメントと実装の乖離** | Medium | cl-008 |
| 7 | **リモートキャンセル未対応** | Low | as-003 |

---

## 🏗️ Claude のリファクタリング設計

### Phase 1: HTTP 層の統一 (DRY)

```python
# Before: create_session と get_session で重複
async with aiohttp.ClientSession() as session:
    async with session.post(...) as resp:
        if resp.status == 429:
            raise RateLimitError(...)
        resp.raise_for_status()
        data = await resp.json()

# After: 共通メソッドに抽出
async def _request(
    self,
    method: str,
    endpoint: str,
    *,
    json: dict | None = None,
    retry_on_rate_limit: bool = True,
) -> dict:
    """統一 HTTP リクエストハンドラ"""
    async with self._session.request(method, endpoint, json=json) as resp:
        if resp.status == 429:
            if retry_on_rate_limit:
                await self._handle_rate_limit(resp)
                return await self._request(method, endpoint, json=json)
            raise RateLimitError(...)
        resp.raise_for_status()
        return await resp.json()
```

**変更点**:

- `aiohttp.ClientSession` をインスタンスで共有（コネクション再利用）
- レート制限リトライを統一
- エラーレスポンスの詳細を例外に含める

---

### Phase 2: parse_state の修正

```python
# Before: 未知状態を IN_PROGRESS として扱う（幻覚）
def parse_state(state_str: str) -> SessionState:
    try:
        return SessionState(state_str)
    except ValueError:
        return SessionState.IN_PROGRESS  # ← バグ

# After: 明示的な UNKNOWN 状態
class SessionState(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"  # ← 新規追加

def parse_state(state_str: str) -> SessionState:
    try:
        return SessionState(state_str)
    except ValueError:
        logger.warning(f"Unknown session state: {state_str}")
        return SessionState.UNKNOWN
```

**poll_session の対応**:

```python
if state in (SessionState.COMPLETED, SessionState.FAILED):
    return session
elif state == SessionState.UNKNOWN:
    logger.error(f"API returned unknown state: {session.state}")
    raise UnknownStateError(session)  # フェイルファスト
```

---

### Phase 3: リトライ戦略の統一

```python
# 共通リトライデコレータ
def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (RateLimitError, aiohttp.ClientError),
):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = 1.0
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Retry {attempt + 1}/{max_attempts}: {e}")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

# 適用
@with_retry(max_attempts=3)
async def create_session(self, ...) -> JulesSession:
    ...
```

---

### Phase 4: 失敗表現の改善

```python
# Before: 空ID で FAILED オブジェクトを返す
return JulesSession(id="", state=SessionState.FAILED, ...)

# After: Optional または専用エラー型
@dataclass
class JulesResult:
    session: JulesSession | None
    error: Exception | None
    
    @property
    def is_success(self) -> bool:
        return self.error is None

# batch_execute の戻り値
async def batch_execute(...) -> list[JulesResult]:
    ...
```

---

## 📊 優先順位

| Phase | 工数 | インパクト | 推奨 |
|:------|:-----|:-----------|:-----|
| Phase 2 (parse_state) | 0.5h | High | ⭐ 最優先 |
| Phase 1 (HTTP DRY) | 2h | Medium | ⭐ 次に |
| Phase 3 (リトライ) | 1h | Medium | ○ |
| Phase 4 (失敗表現) | 1h | Low | △ |

---

## 🔗 参照レビュー

- ai-006: DRY Violation
- cl-003: Mental Model
- cl-008: Code Density
- th-001: FEP Prediction Error
- as-003: Cancellation

---

*Created: 2026-01-28 18:45 JST*
*Source: 58 Jules Synedrion Reviews*
