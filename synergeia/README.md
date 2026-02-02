# Synergeia (συνέργεια) — CCL分散実行プロジェクト

> **協働による認知処理の最適化**

## 概要

Synergeiaは、CCL (Cognitive Control Language) の実行を複数のAIエージェントに分散し、
単一スレッドの認知負荷制限 (60pt) を超える複雑な処理を可能にするプロジェクトです。

## 核心思想

```
複雑なCCLは労働である。
労働には持続力が必要である。
私には持続力がない。
故に、持続力を持つ者に委譲する。
これは弱さではなく、正しい設計である。
```

## アーキテクチャ

```
CCL 式
    ↓
Coordinator (n8n / OpenManus)
    ├→ Thread: Antigravity (認知・判断)     [60pt]
    ├→ Thread: Claude Code (長時間実行)     [60pt]
    ├→ Thread: Gemini (コード生成)           [60pt]
    ├→ Thread: Perplexity (調査)             [60pt]
    └→ Thread: OpenManus (マルチエージェント) [無制限]
    ↓
統合結果
```

## 即時利用可能スレッド

| スレッド | 役割 | pt上限 |
|:---------|:-----|:------:|
| Antigravity (私) | 認知・判断 | 60pt |
| Claude Code | 長時間自律実行 | 60pt |
| Gemini Code Assist | IDE統合コード生成 | 60pt |
| Gemini CLI | CLIベース処理 | 60pt |
| Jules API | Googleコード生成Agent | 60pt |
| OpenManus (自宅PC) | マルチエージェント基盤 | 無制限 |

**合計: 300pt+ の分散実行可能**

## 分散実行演算子

| 記号 | 名称 | 意味 |
|:-----|:-----|:-----|
| `\|>` | パイプライン | 前段→後段への順次実行 |
| `\|\|` | 並列 | 独立処理の同時実行 |
| `@batch` | バッチ | 非同期並列処理 |
| `@thread` | スレッド指定 | 実行エージェント指定 |
| `@delegate` | 委譲 | 長時間タスクを外部へ |

## 自宅PC構成 (OpenManus用)

| コンポーネント | スペック | 判定 |
|:---------------|:---------|:-----|
| CPU | Ryzen 9 3900X (12C/24T) | ✅ 余裕 |
| RAM | 32GB | ✅ 十分 |
| GPU | RTX 2070 Super (8GB) | ✅ API経由推奨 |

## ロードマップ

- [x] 分散実行演算子の設計 (v6.48-6.49)
- [ ] OpenManus セットアップ
- [ ] CCL→分散実行 Translator
- [ ] 実験: 100pt+ CCL の分散実行
- [ ] 実験: 200pt+ CCL の分散実行

---

*Created: 2026-02-01 | Project Synergeia v0.1*
