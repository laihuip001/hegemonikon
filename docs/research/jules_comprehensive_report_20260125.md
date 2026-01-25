# Antigravity IDE × Jules × Claude Opus 4.5 協働ワークフロー設計レポート
## 2025年11月～2026年1月 最新情報ベース

> **調査日**: 2026-01-25
> **情報源**: Perplexity Deep Research（パプ君）

---

## 要約

2025年12月のメジャーアップデート以降、Jules は **Scheduled Tasks / Suggested Tasks** で従来のオンデマンド実行から**背景での連続自動化**へシフトしている。同時に Antigravity IDE はプレビュー中（無料）で、Gemini 3.0 Pro と Claude Opus 4.5 のデュアルモデルワークフローに対応した。

---

## I. 製品の現在位置づけ

### Jules の進化：オンデマンド → プロアクティブ

| 項目 | 状態 | 更新日 |
|------|------|-------|
| **基盤モデル** | Gemini 3 Pro（従来: 2.5 Pro） | 2025年12月 |
| **Suggested Tasks** | Pro/Ultra で有効（#TODO スキャン） | 2025年12月9日 |
| **Scheduled Tasks** | cron ベースの定期実行 | 2025年12月9日 |
| **Web Surfing** | ドキュメント・コード参照の自動検索 | 2025年12月 |
| **API バージョン** | v1alpha（ベータ、仕様変動可能） | 2025年10月以降 |

---

## II. Antigravity IDE の制限（2026年1月）

### Pro ユーザーの Claude Opus 4.5 = **7日間待機**

| 項目 | 詳細 |
|------|------|
| **プラン** | Google AI Pro ($19.99/月) |
| **制限内容** | Claude Opus 4.5 (Thinking) を 5時間で上限に達した場合 |
| **回復期限** | 7日間のローリング（元仕様: 5時間） |

**対策**:
- Google AI Ultra への移行（+$230/月）
- Gemini 3.0 Pro へ切り替え（クォータ制限なし）

---

## III. CLI・API・GitHub Actions

### A. Jules CLI

| コマンド | 機能 |
|---------|------|
| `julius login` | Google 認証 |
| `julius remote new --repo <name> --session "<prompt>"` | 新規タスク |
| `julius remote list --session` | 進行中タスク一覧 |
| `julius remote pull --session <id>` | 結果取得・PR作成 |

### B. REST API（v1alpha）

**ベース**: `https://julius.googleapis.com`
**認証**: X-Goog-Api-Key ヘッダー

```bash
curl -X POST https://julius.googleapis.com/v1alpha/sessions \
  -H "X-Goog-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Update all dependency versions",
    "sourceContext": {
      "source": "sources/github/owner/repo",
      "githubRepoContext": {"startingBranch": "main"}
    },
    "automationMode": "AUTO_CREATE_PR"
  }'
```

### C. GitHub Actions

**公式アクション**: `google-labs-code/julius-action`

---

## IV. 実行環境

| 項目 | 値 |
|------|-----|
| **OS** | Ubuntu Linux |
| **ディスク** | 20 GB |
| **ランタイム** | Node.js, Python, Go, Rust, Java, Bun |
| **ネットワーク** | 外部 API 呼び出し可能 |

---

## V. 料金表

### Jules

| プラン | 日次上限 | 同時実行 | 月額 |
|-------|--------|--------|------|
| **Free** | 15 | 3 | $0 |
| **Pro** | 100 | 15 | $19.99 |
| **Ultra** | 300 | 60 | $249.99 |

### Antigravity + Google AI

| Plan | Claude Opus 制限 | 推奨 |
|------|-----------------|------|
| **Free** | N/A | Gemini のみ |
| **Pro** | **7日待機** ⚠️ | 実用的でない |
| **Ultra** | なし | 推奨 |

---

## VI. Antigravity 統合パターン

### 結論：**公式統合なし**

#### パターン1：Antigravity ターミナル → Jules CLI
```bash
julius remote new --repo owner/repo --session "Add tests"
```

#### パターン2：GitHub Actions + REST API（推奨）
- 完全自動化
- スケジューラブル

#### パターン3：MCP（制限あり）
- Jules は MCP 非対応
- curl で代替

---

## VII. 3層協働戦略

| レイヤー | ツール | 得意領域 |
|---------|--------|--------|
| **計画** | Antigravity (Gemini 3) | 高速スケッチ |
| **実装** | Jules (REST API) | 大規模非同期 |
| **品質** | Claude Code (GH Actions) | レビュー |

---

## VIII. 推奨構成

### 最小コスト（$19.99/月）
- Antigravity Free + Jules Pro
- Gemini 3.0 Pro のみ使用

### フル機能（$499.98/月）
- Google AI Ultra + Jules Ultra
- Claude Opus 4.5 制限なし

---

## IX. 実装可否

### ✅ 可能
- Antigravity ターミナル → Jules CLI
- GitHub Actions + Jules REST API
- Scheduled/Suggested Tasks

### ❌ 不可
- Antigravity Agent → Jules 直接呼び出し
- Claude Opus Pro 制限の回避

---

## 参考リンク

- https://jules.google/docs/changelog/
- https://blog.google/innovation-and-ai/technology/developers-tools/jules-proactive-updates/
- https://developers.google.com/jules/api
