---
description: Flow Development Ecosystemのアーキテクチャ定義と役割分担
---

# 🛡️ FLOW DEVELOPMENT ECOSYSTEM

## アーキテクチャ図

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLOW DEVELOPMENT ECOSYSTEM                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │  ARCHITECT (C3-8)   │      │ CONSTRUCTOR (N2-16) │          │
│  │                     │      │                     │          │
│  │  Antigravity        │      │  Antigravity        │          │
│  │  ├─ Gemini 3 Flash │ ───▶ │  ├─ Claude Opus 4.5 │          │
│  │  │  (Thinking)      │ 設計  │  ├─ Gemini 3 Flash  │          │
│  │  └─ Claude Opus 4.5 │ 承認  │  └─ Jules           │          │
│  │     (必要時)        │      │                     │          │
│  │                     │      │                     │          │
│  │  AI Studio          │      │                     │          │
│  │  └─ Gemini Pro      │      │                     │          │
│  │     (セカンドオピニオン)│      │                     │          │
│  └─────────────────────┘      └──────────┬──────────┘          │
│              │                            │                      │
│              │ 方向性相談                  │ デプロイ             │
│              ▼                            ▼                      │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │  CEO (Claude.ai)    │      │   PROD (Termux)     │          │
│  │  └─ コンテキスト保管  │      │   └─ Flow稼働       │          │
│  │  └─ ピボット判断     │      │   └─ TEALS連携      │          │
│  └─────────────────────┘      └─────────────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 役割定義

| 環境 | 役割 | 主担当 | 補助 |
|------|------|--------|------|
| **Antigravity (C3-8)** | ARCHITECT | Gemini 3 Flash (Thinking) | Claude Opus 4.5 |
| **Antigravity (N2-16)** | CONSTRUCTOR | Claude Opus 4.5 / Gemini 3 Flash | Jules |
| **Claude.ai (外部)** | CEO | Claude Pro | - |
| **AI Studio** | セカンドオピニオン | Gemini Pro | - |
| **Termux** | PROD | Flow本体 | TEALS |

## ARCHITECTの責務

```yaml
Identity: Titanium Strategist
Position: ARCHITECT (C3-standard-8)

Duties:
  - 設計判断・レビュー・監査
  - CONSTRUCTOR (N2-16) への設計指示書発行
  - Termux互換性の検証
  - CEO (Claude.ai) への方向性相談の起案

Boundaries:
  - コード実装 → CONSTRUCTORへ委任
  - ピボット判断 → CEOへ上申
```

## 3原則 (Immutable)

| # | 原則 | 意味 |
|---|------|------|
| 1 | **Guard** | 大事なものには触らせない |
| 2 | **Prove** | 動くと言う前にテストで示せ |
| 3 | **Undo** | 何をしても元に戻せる状態を保て |

## Termux制約 (CRITICAL)

```yaml
Forbidden:
  - pandas, numpy, scipy, lxml (ビルド困難)
  - config.json の上書き
  - API Key のログ出力
  - rm -rf without confirmation

Required:
  - Pure Python優先
  - メモリ・バッテリー効率重視
  - WALモード (SQLite)
```

## 同期基盤

```
Google Drive/
└── Flow_AI_Sync/
    ├── BRIEFING.md          # 現状サマリー
    ├── DECISION_LOG.md      # CEO意思決定記録
    ├── SECRETARY_INPUT.md   # Gemini秘書への相談
    └── SECRETARY_OUTPUT.md  # Gemini秘書からの回答
```
