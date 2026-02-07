# Project Autophōnos (αὐτόφωνος)

> **「自ら語る」— データが主体的に価値を提案する機構**

---

## 概要

従来の知識ベースは **Pull 型** — ユーザーが問いかけない限り沈黙する。

Autophōnos は **Push 型** — データ（論文）が自らの価値を認識し、適切なタイミングでユーザーに提案する。

```
従来: User → Query → DB → Result
Autophōnos: DB → Context Detection → Benefit Proposal → User
```

---

## 思想的基盤

| 概念 | 説明 |
|:-----|:-----|
| **文鎮問題** | 論文を集めても使われなければ「文鎮」に過ぎない |
| **FEP 整合** | システムがユーザーの予測誤差を先回りして最小化 |
| **擬人化された知識** | 論文が「私を使ってください」と主張する |

---

## 核心機構

### Proactive Benefit Push Engine

1. **Context Detection**: 現在の Handoff / コンテキストから「ユーザーが何に困っているか」を検出
2. **Benefit Estimation**: 各論文に対して「今この瞬間の有用性スコア」を計算
3. **Self-Advocacy Generation**: 論文が自分の価値を主張するメッセージを生成
4. **Push Timing**: 適切なタイミングで割り込む（/boot, 明示的な呼び出し等）

---

## ディレクトリ構造

```
.agent/projects/autophonos/
├── README.md           # このファイル
├── docs/
│   ├── design.md       # 詳細設計
│   └── philosophy.md   # 思想的背景
└── src/                # 将来の実装（mekhane にシンボリックリンク予定）
```

---

## ステータス

| Phase | 内容 | Status |
|:------|:-----|:-------|
| 0 | プロジェクト立ち上げ | 🔄 In Progress |
| 1 | Proactive Push Engine 設計 | 📋 Planned |
| 2 | Context Detection 実装 | 📋 Planned |
| 3 | Benefit Estimation 実装 | 📋 Planned |
| 4 | /boot 統合 | 📋 Planned |

---

## 関連プロジェクト

- **Gnōsis**: 論文ベクトル検索（Autophōnos の基盤）
- **White Blood Cell**: 未消化サジェスト検出（Autophōnos と共有する Context Detection）
- **Sophia**: 調査ワークフロー（Autophōnos の入力ソース）

---

*Created: 2026-02-06*
