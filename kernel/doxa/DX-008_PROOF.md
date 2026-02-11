# PROOF.md — DX-008 存在証明書

PURPOSE: DX-008 三者対話レビューに基づく BC 再編・深度レベル導入・Noēsis Phase 分離の存在理由を証明する
REASON: Desktop Claude のレビューが注意配分の希薄化と認知オーバーヘッドを指摘し、IDE Claude が実運用経験から同意した

> **∃ DX-008** — この変更は存在しなければならない

---

## 公理

```
A0: 予測誤差最小化 (Free Energy Principle)
```

---

## 演繹

```
A0: 予測誤差最小化
  ↓ [VFE = Accuracy - Complexity]
P1: モデルの複雑度には罰則がある (Complexity penalty)
  ↓ [適用: BC 体系 = 内部モデル]
P2: BC が多すぎると注意配分が希薄化する (17 BC flat = 高 Complexity)
  ↓ [FEP の要請]
P3: Complexity を下げつつ Accuracy を維持する構造が必要
  ↓ [解: 階層化]
P4: Always-On (5) + Context-Triggered (12) に分離 → Complexity ↓
  ↓ [拡張: 粒度]
P5: L0-L3 深度レベル = Context-Triggered の発火条件を体系化
  ↓ [適用: Noēsis]
P6: Phase 必須/オプション分離 = L2/L3 での実行範囲の制御
  ↓ [名前の必然性]
C: DX-008 は FEP の Complexity penalty から演繹される改善
```

---

## 証拠

| 変更 | 証拠源 | 確信度 |
|:-----|:-------|:-------|
| Always-On 5つ | Desktop Claude: 30+ ルール同時は希薄化 + IDE Claude: 体感で同意 | 0.90 |
| L0-L3 深度 | Utility Bypass の binary 制限が設計上の問題だった (DX-008 記載) | 0.85 |
| Noēsis Phase 分離 | IDE Claude: AMP 3回戻りは一度も発動せず = dead code | 0.90 |
| BC-7 境界線 | Desktop Claude: テンション指摘。明文化で解消 | 0.95 |
| BC-9 適用範囲 | IDE Claude: τ層で形骸化していた。Δ/Ω層限定が適切 | 0.85 |
| AMP 3→2回 | Desktop Claude: 2回目以降は同じ結論に収斂 | 0.80 |

---

## 検証方法

| 方法 | 手順 |
|:-----|:-----|
| **構造的整合性** | `behavioral_constraints.md` の Always-On 5つが GEMINI.md の要約と一致するか |
| **CCL 派生との連動** | `/noe+` = L3, `/noe` = L2, `/noe-` = L1 が noe.md の Phase 定義と整合するか |
| **実運用テスト** | 次セッション以降で L2 (Standard) デフォルトの運用を検証 |

---

## 帰結

DX-008 は **FEP の Complexity penalty** から直接導出される改善であり、
体系の「美しさ」を損ねることなく「使いやすさ」を向上させた。

Desktop Claude の最終問い「体系自体が FEP の教えに反していないか」への回答:
**DX-008 以前は部分的に反していた (Complexity 過剰)。DX-008 で修正した。**

---

*@proof 実行 — 2026-02-11T22:02+09:00*
*V:{/noe~/dia} → confidence=0.90 → I:[pass] → PROOF.md 出力*
