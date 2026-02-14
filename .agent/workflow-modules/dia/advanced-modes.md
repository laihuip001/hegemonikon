---
summary: 高度モード。epochē, audit, panorama, cross-model, cold_mirror, deliberative。
parent: /dia
---

# 高度モード

> メタ判定とクロスモデル検証。基本モードより高い認知負荷を要する。
>
> **制約**: 各モードの出力形式に従うこと。確信度レベルを必ず含めること。

---

## epochē (判断停止)

> `/dia.epochē` — LLM の過信 (Overconfidence) を低減

発動: `/dia epochē` または「確信度を宣言」「判断を保留」

| 項目 | 内容 |
|:-----|:-----|
| 主張 | {評価対象の主張} |
| 確信度 | HIGH/MEDIUM/LOW |
| 根拠 | なぜその確信度か |
| CoVe Q1 | 情報源は確か？ |
| CoVe Q2 | 反例は考慮した？ |
| CoVe Q3 | バイアスはないか？ |
| 判定 | 判断停止 / 継続 |

---

## audit (消化品質診断)

> `/dia.audit` — モジュール統合が Naturalized 状態か検証

発動: `/dia audit` または「消化できてる？」

| 項目 | 内容 |
|:-----|:-----|
| 対象 | {監査対象モジュール} |
| 境界残存 | Y/N |
| 機能重複 | Y/N |
| 強化度 | HIGH/MEDIUM/LOW |
| 消化レベル | Superficial / Absorbed / Naturalized |
| 判定 | レベルと根拠 |

---

## panorama (6層メタ認知スキャン)

> `/dia.panorama` — 「我々が見ていないもの」を可視化

発動: `/dia panorama` または「盲点」「見落とし」

6層:

| 層 | 名称 | 観点 |
|:---|:-----|:-----|
| L1 | Domain Shift | 領域シフト |
| L2 | Synedrion | 偉人評議会 |
| L3 | User Perspective | 5人ペルソナ |
| L4 | Inversion | 反転 |
| L5 | 10th Man | 悪魔の代弁者 |
| L6 | Graveyard Walk | 墓場歩き |

出力: 各層で発見した盲点 + 優先対処すべき最も危険な盲点

---

## cross-model (Cross-Model Verification + Cortex Auto)

> `/dia.cross-model` — 異なるモデルによる相互検証 (Cortex API 自動統合)
>
> **起源**: BOU #3 "Debate Partner — 対等な批判者"
> **手段**: `mcp_ochema_ask_cortex` で Gemini 3 Pro に同じ問題を投げ、差分を検出

発動: `/dia cross-model` または「Claude に聞く」「別のAI」「セカンドオピニオン」

### 自動セカンドオピニオン (3フェーズ)

| Phase | 名称 | 内容 |
|:------|:-----|:-----|
| **P1** | 問い投射 | Claude の判定/分析結果を要約し、Gemini に同じ問題を独立で問う |
| **P2** | 応答取得 | `mcp_ochema_ask_cortex` で Gemini 3 Pro の回答を取得 |
| **P3** | 差分分析 | Claude vs Gemini の一致点・相違点・盲点を構造化 |

#### P1: 問い投射テンプレート

```
以下の問題について、独立した分析を行ってください。
他のAIの分析結果は見ないでください。

## 問題
{対象の問題/設計/コード}

## 求める分析
1. 主要な論点の特定
2. リスク/問題点の指摘
3. 改善提案
4. 確信度 (0-100%)
```

#### P2: Cortex 呼び出し

```
mcp_ochema_ask_cortex(
  message="{P1 のプロンプト}",
  model="gemini-2.5-pro",   # デフォルト。gemini-3-pro-preview も可
  system_instruction="あなたは独立した技術レビュアーです。他のAIの意見は参照せず、自分の分析を行ってください。"
)
```

#### P3: 差分分析テーブル

| 項目 | Claude | Gemini | 差分 |
|:-----|:-------|:-------|:-----|
| 主要論点 | ... | ... | 一致/相違 |
| リスク指摘 | ... | ... | 一致/相違 |
| 改善提案 | ... | ... | 一致/相違 |
| 確信度 | ...% | ...% | Δ |
| **盲点** | Gemini が指摘し Claude が見落とした点 | Claude が指摘し Gemini が見落とした点 | — |

### 手動チェックリスト (従来互換)

| 項目 | 内容 |
|:-----|:-----|
| 対象 | {検証対象} |
| 検証モデル | Claude/Gemini/GPT |
| L1 成果物正確性 | Pass/Warn/Fail |
| L2 プロセス遵守 | Pass/Warn/Fail |
| L3 計画一致 | Pass/Warn/Fail |
| L4 品質基準 | Pass/Warn/Fail |
| 不一致箇所 | 発見された問題 |

---

## cold_mirror (冷徹な鏡)

> `/dia.cold_mirror` — 認知歪み・論理的欠陥を容赦なく指摘

発動: `/dia cold_mirror` または「厳しく」「容赦なく」

| 項目 | 内容 |
|:-----|:-----|
| 対象 | {評価対象} |
| 認知歪み | 種類と具体例 (Catastrophizing, Black-and-White等) |
| 論理的欠陥 | 種類と具体例 (Ad Hominem, False Dichotomy等) |
| 現実 | 事実に基づく冷徹な評価 |
| 修正案 | どう考え直すべきか |

---

## deliberative (三視点反復改善)

> `/dia.deliberative` — 三人の専門家視点で反復改善

発動: `/dia deliberative` または「反復改善」「三視点」

プロセス:

1. **ROUND 1 — 三視点生成**: Expert A(ドメイン専門家), B(批評家), C(実装者)
2. **ROUND 2 — 根拠提示**: 各専門家が根拠を明示、相互矛盾を検出
3. **ROUND 3 — 統合改定**: 三視点を統合し改定版を生成
4. **品質ゲート**: 改善が収束したか評価。未収束なら ROUND 1 へ (最大3サイクル)

---

> **制約リマインダ**: 確信度を必ず含める。出力形式テーブルに従うこと。

*/dia サブモジュール — v2.0 FBR*
