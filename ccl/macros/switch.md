# @switch マクロ

> **圏論**: 自然変換 (横ペアリング H)
> **CCL**: 同Series内で目的軸を切り替える

## 定義

```yaml
macro: @switch
parameters:
  theorem: 現在のワークフロー
  # partner は自動解決（横ペア）
```

## 目的

同じモード（浅い軸）を保ちながら、目的（深い軸）を切り替える。
「知る↔やる」「探索↔選択」のような、同Series内の自然変換。

## 構文

```ccl
@switch(/noe)       # → /bou  (認識→実用: 「で、結局何をすべきか」)
@switch(/zet)       # → /ene  (探求→実行)
@switch(/pro)       # → /pis  (直感→検証: 「本当か？」)
@switch(/euk)       # → /chr  (好機→期限: 「いつまでに」)
```

## 全12ペア

| Series | ペア1 | ペア2 |
|:-------|:------|:------|
| O | noe↔bou | zet↔ene |
| S | met↔mek | sta↔pra |
| H | pro↔pis | ore↔dox |
| P | kho↔hod | tro↔tek |
| K | euk↔chr | tel↔sop |
| A | pat↔dia | gno↔epi |

## CCL 展開

```ccl
@switch(A) → A >> H_partner(A)
```

## 適用例

```ccl
# 深く考えた後、「で、何をする？」
/noe+ >> @switch(/noe)     # = /noe+ >> /bou

# 直感が来た → 検証する
@switch(/pro)              # = /pro >> /pis
```

---

*@switch | natural transformation (横ペアリング H)*
