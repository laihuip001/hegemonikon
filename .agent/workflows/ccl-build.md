---
description: "組む — /bou-_/met_/tek_/s+_/ene+_V:{/dia-}_I:[✓]{/dox-}"
lcm_state: beta
version: "1.0"
---

# /ccl-build: 構築マクロ

> **CCL**: `@build = /bou-_/met_/tek_/chr_/kho_/s+_/ene+_V:{/dia-}_I:[✓]{/dox-}`
> **用途**: 0から作る。設計→実装→検証→記録の一気通貫
> **圏論**: @eat (外→内: 消化) の随伴。内→外の具現化 = 自然関手

## 展開

1. `/bou-` — 目的を軽量定義
2. `/met` — スケール判定: どの粒度で組むか (S1 Metron)
3. `/tek` — 技法選択: どの技法で組むか (P4 Tekhnē)
4. `_/s+` — 戦略を詳細化
5. `_/ene+` — 詳細実行
6. `_V:{/dia-}` — 軽量判定で検証
7. `_I:[✓]{/dox-}` — 成功時のみ Doxa を記憶

## 使用例

```ccl
@build                     # 標準構築
@build _ @vet              # 構築後に自己検証
F:[api,ui,db]{@build}      # 3コンポーネントそれぞれに構築
```
