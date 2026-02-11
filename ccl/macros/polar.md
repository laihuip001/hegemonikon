# @polar マクロ

> **圏論**: 双対 (反対角ペアリング X)
> **CCL**: 同Series内で対極の定理と対話する

## 定義

```yaml
macro: @polar
parameters:
  theorem: 現在のワークフロー
  mode: "transition" | "tension" (default: auto-detect)
  # partner は自動解決（反対角ペア）
```

## 目的

最も遠い定理（両軸反転）との対話を行う。
遷移型 (>>) は「A したら B」、緊張型 (~) は「A と B の間で揺れる」。

## 構文

```ccl
@polar(/noe)        # → /noe >> /ene  (transition: 認知→運動)
@polar(/bou)        # → /bou ~ /zet   (tension: 望む↔探す)
@polar(/chr)        # → /chr ~ /tel   (tension: 期限↔使命)
@polar(/pat)        # → /pat >> /epi  (transition: 体験→体系)
```

## 全12ペア

| Series | 遷移型 (>>) | 緊張型 (~) |
|:-------|:-----------|:-----------|
| O | noe→ene「認知→運動」 | bou↔zet「望む↔探す」 |
| S | met→pra「基準→実践」 | mek↔sta「設計↔現状」 |
| H | — | pro↔dox, pis↔ore |
| P | kho→tek「探検→知恵」 | hod↔tro「地上↔天空」 |
| K | — | euk↔sop, chr↔tel |
| A | pat→epi「体験→体系」 | dia↔gno「判断↔教訓」 |

## CCL 展開

```ccl
@polar(A)
→ transition: A >> X_partner(A)
→ tension:    A ~ X_partner(A)
```

## 適用例

```ccl
# 考えすぎ → 「手を動かせ」
@polar(/noe)                # = /noe >> /ene

# 望みと探求の間で揺れる
@repeat[x3, @polar(/bou)]   # = @repeat[x3, /bou~/zet]

# 期限と使命の間で葛藤
@polar(/chr)                 # = /chr ~ /tel
```

---

*@polar | duality (反対角ペアリング X)*
