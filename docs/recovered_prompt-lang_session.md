# Prompt-Lang セッション復旧ドキュメント

> **復旧元セッション**: `8bf17ae7-f290-4126-a4ce-425a29511cc0`
> **復旧日時**: 2026-01-23

---

## 概要

IDE「Agent loading...」無限ループ問題により読み込み不可となったセッションから、prompt-lang関連ドキュメントを直接抽出。

---

## 復旧ファイル一覧

| ファイル | 内容 | 元パス |
|----------|------|--------|
| prompt-lang-vision.md | 構想・工数・ROI分析 | [元ファイル](file:///C:/Users/makar/.gemini/antigravity/brain/8bf17ae7-f290-4126-a4ce-425a29511cc0/prompt-lang-vision.md) |
| design-alternatives.md | 軍事級メタプロンプト設計5案 | [元ファイル](file:///C:/Users/makar/.gemini/antigravity/brain/8bf17ae7-f290-4126-a4ce-425a29511cc0/design-alternatives.md) |
| implementation_plan.md | Phase 4移行計画 | [元ファイル](file:///C:/Users/makar/.gemini/antigravity/brain/c6545ad1-bde4-4a9a-ba9d-0698de9106da/implementation_plan.md) |

---

## prompt-lang 構想サマリー

### コンセプト
プロンプトエンジニアリングを**プログラミング言語**として形式化する。

```prompt-lang
@system {
  role: "Senior Customer Support Agent";
  constraints: [no_fabrication, empathetic_tone, max_tokens(150)];
}

@archetype precision {
  win_condition: error_rate < 0.01;
  sacrifice: speed;
}

@thinking {
  step analyze: "顧客の感情状態を判定";
  step strategize: "解決策を選定";
  step draft: "回答を構築";
}
```

### 工数見積もり

| フェーズ | 内容 | 工数 |
|---|---|---|
| Phase A | 構文設計 | 2-3日 |
| Phase B | パーサー | 3-5日 |
| Phase C | トランスパイラ | 2-3日 |
| Phase D | VSCode拡張 | 2-3日 |
| Phase E | Jules統合 | 1-2日 |
| Phase F | ドキュメント | 2-3日 |

**合計: 12-19日（約2-3週間）**

### 実行条件
1. Forge Phase 1が完了
2. XMLベースの運用が2週間以上継続
3. prompt-langで解決したい具体的痛みが3つ以上

---

## 関連セッション

| Session ID | タイトル/内容 |
|------------|---------------|
| `8bf17ae7-f290-4126-a4ce-425a29511cc0` | メイン開発セッション（56ファイル） |
| `c6545ad1-bde4-4a9a-ba9d-0698de9106da` | Phase 4移行計画 |
| `a064fa0c-4076-48d4-8985-e123e8418fe1` | パプ君返答（Prompt-Lang言及） |

---

## IDE問題について

### 症状
- 会話リストで過去履歴クリック → 「Agent loading...」無限表示
- 「Open editor」→ 現在チャットにリダイレクト

### 原因分析
- `.pb`（Protocol Buffer）ファイルは正常に存在（58件）
- `brain/` ディレクトリのアーティファクトも正常（59セッション）
- **Antigravity IDE内部の会話ロード機構に障害**

### 回避策
- このドキュメントのように、直接ファイルシステムからデータを抽出
- `chat-history-kb.py search "キーワード"` でセマンティック検索
