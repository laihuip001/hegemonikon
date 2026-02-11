# @poc — プロトタイプマクロ

> **Origin**: Forge v2.0 "🧪 Prototype" モジュール
> **Category**: 行為マクロ (Act/Create)
> **CCL**: `/zet _ /ene+ _ V:{/dia-}`

---

## 定義

```yaml
macro: @poc
parameters: []
expansion: |
  /zet _ /ene+ _ V:{/dia-}
```

---

## 処理フロー

```
Phase 1: /zet (探求)
├─ 仮説を立てる
├─ 最小限の検証ポイントを決める
└─ 完成度は無視 — 速度を優先

Phase 2: /ene+ (行為・深化)
├─ 試作品を最速で作る
├─ 動くものを優先（品質は後回し）
└─ 検証可能な状態にする

Phase 3: V:{/dia-} (検証 → 判断・縮約)
├─ 試作品が仮説を検証できるか判定
├─ 縮約: 成功/失敗の二値判定
└─ 学びを抽出
```

---

## 使用例

```ccl
@poc                       # 基本形
@poc |> @build             # 試作 → 本構築
F:[×3]{@poc} |> /bou       # 3つ試作 → 最良を選定
@poc ~ @devil              # 試作 ↔ 攻撃（改善ループ）
```

---

*Forge Prototype → HGK CCL v1.0*
