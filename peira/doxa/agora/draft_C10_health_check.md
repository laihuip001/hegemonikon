# AI の「健全性」を9項目でチェックする

> **ID**: C10
> **想定媒体**: Zenn → Note
> **想定読者**: Agent 開発者、DevOps
> **フック**: AI システムのヘルスチェックをどう設計するか

---

## リード文（案）

Web サーバーには `/health` エンドポイントがある。
AI エージェントにはないのか？

**ある。** 9 項目でチェックする。

---

## 本文構成（案）

### 1. 9項目ヘルスチェック

| # | 項目 | チェック内容 |
|:--|:-----|:-----------|
| 1 | Gnōsis (論文) | インデックス健全性、論文数 |
| 2 | Sophia (KI) | KI 数、最終更新日 |
| 3 | Kairos (Handoff) | Handoff 数、破損チェック |
| 4 | Chronos (ログ) | ログ数、インデキシング状態 |
| 5 | CCL パーサー | dispatch() 動作確認 |
| 6 | MCP ゲートウェイ | 各サーバーの応答 |
| 7 | Dendron | PURPOSE カバレッジ |
| 8 | テスト | pytest 通過率 |
| 9 | Git 状態 | 未コミットファイル数 |

### 2. 出力形式

```
[2026-02-14 14:00]
✅ Gnōsis:    596 papers, index OK
✅ Sophia:    200 KIs, last update 2h ago
⚠️ Kairos:    100 handoffs, 3 corrupted
✅ Chronos:   33,000 docs, index OK
✅ CCL:       dispatch() OK
✅ MCP:       7/7 servers responding
⚠️ Dendron:   PURPOSE coverage 92% (target: 95%)
✅ Tests:     148/150 passed
⚠️ Git:       5 uncommitted files
```

### 3. 閾値設計

| 状態 | 基準 |
|:-----|:-----|
| ✅ OK | 全基準クリア |
| ⚠️ WARN | 基準を下回るが機能する |
| ❌ FAIL | 機能に影響がある |

### 4. CI/CD への統合

- pre-commit hook で Dendron チェック
- GitHub Actions で定期ヘルスチェック
- 異常検知時に Slack 通知

### 5. 読者が試せること

```python
def health_check():
    results = {}
    results['index'] = check_index_health()
    results['tests'] = run_pytest()
    results['git'] = check_uncommitted()
    return results
```

---

*ステータス: たたき台*
*関連: C8 (Dendron), C9 (PKS CLI)*
