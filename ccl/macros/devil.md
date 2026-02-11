# @devil — 悪魔の代弁者マクロ

> **Origin**: Forge v2.0 "🛡️ Devil's Advocate" モジュール
> **Category**: 認知マクロ (Think/Focus)
> **CCL**: `/dia+ |> /noe! |> /pis`

---

## 定義

```yaml
macro: @devil
parameters: []
expansion: |
  /dia+ |> /noe! |> /pis
```

---

## 処理フロー

```
Phase 1: /dia+ (判断・深化)
├─ 対象の案/設計を徹底的に攻撃
├─ 論理の脆弱性を洗い出す
├─ 前提の妥当性を疑問視
└─ 最悪のシナリオを列挙

Phase 2: /noe! (認識・全展開)  [パイプ: 攻撃結果を入力]
├─ 攻撃結果から本質的弱点を抽出
├─ 弱点の全パターンを展開
└─ 各弱点に対する補強策を生成

Phase 3: /pis (確信度評価)  [パイプ: 補強結果を入力]
├─ 補強後の案に対して確信度を判定
├─ C (Confident) / U (Uncertain) を付与
└─ 残存リスクを明示
```

---

## 使用例

```ccl
@devil                     # 基本形
@devil+                    # 各フェーズを詳細化
F:[×3]{@devil} |> /bou     # 3回攻撃 → 意志決定
@devil ~ /ene              # 攻撃 ↔ 実行（改善ループ）
```

---

*Forge Devil's Advocate → HGK CCL v1.0*
