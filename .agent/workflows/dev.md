---
description: 開発プロトコルを明示的に参照する。Creator用の手動起動コマンド。
hegemonikon: M6-Praxis
---

# /dev ワークフロー

> **目的**: 開発プロトコル（旧資産 Module 01-25）を明示的に参照
> **主体**: Creator（手動起動）

---

## 使用方法

```
/dev              # 一覧表示
/dev 04           # 番号指定（Module 04 を展開）
/dev tdd          # ショートカット指定
/dev xml 04       # Module 04 の XML テンプレートのみ抽出
```

---

## 実行手順

// turbo-all

1. **引数なし（一覧表示）**:
   ```
   [Code Protocols - 25 Modules]
   🔴 Core (必須)
     01. DMZ Protocol - 設定ファイル保護
     04. TDD Enforcement - テスト駆動開発
     14. Narrative Commit - コミット物語化
   
   🟠 Recommended (推奨)
     06. Complexity Budget - 複雑度管理
     07. Devil's Advocate - 多視点批評
     10. Ripple Effect - 影響範囲予測
     11. Red Teaming - セキュリティテスト
     13. Code Archaeology - Chesterton's Fence
   
   🟡 Optional (オプション)
     02-03, 05, 08-09, 12, 15-25
   
   使用: /dev [番号] または /dev [ショートカット]
   ```

2. **番号指定（原典展開）**:
   ```powershell
   view_file "{BASE_PATH}\Module {XX} {Name}.md"
   ```

3. **XML抽出（xml オプション）**:
   - モジュール内の `<module>...</module>` ブロックを抽出
   - システムプロンプトにコピペ可能な形式で出力

---

## 全25モジュール対応表

| # | ショートカット | モジュール名 |
|:---:|:---|:---|
| 01 | `dmz` | DMZ Protocol（設定ファイル保護） |
| 02 | `topology` | Directory Topology Lock |
| 03 | `deps` | Dependency Quarantine |
| 04 | `tdd` | TDD Enforcement |
| 05 | `lang` | Ubiquitous Language |
| 06 | `budget` | Complexity Budget |
| 07 | `devils` | Devil's Advocate |
| 08 | `checkpoint` | Cognitive Checkpoint |
| 09 | `mutate` | Mutation Testing |
| 10 | `ripple` | Ripple Effect Analysis |
| 11 | `redteam` | Automated Red Teaming |
| 12 | `chaos` | Chaos Monkey |
| 13 | `arch` | Code Archaeology |
| 14 | `commit` | Narrative Commit |
| 15 | `atomic` | Atomic Design Protocol |
| 16 | `a11y` | Accessibility Mandate |
| 17 | `log` | Structured Logging |
| 18 | `flag` | Feature Flag Protocol |
| 19 | `docker` | Docker First Protocol |
| 20 | `reap` | Dead Code Reaper |
| 21 | `todo` | TODO Expiration |
| 22 | `docs` | Auto-Documentation |
| 23 | `mock` | Mock First Protocol |
| 24 | `perf` | Performance Budget |
| 25 | `rollback` | Rollback Strategy |

---

## 原典ベースパス

```
M:\Brain\99_🗃️_保管庫｜Archive\プロンプト ライブラリー\モジュール（開発用）\個別のモジュール\
```

---

## XML テンプレート抽出

`/dev xml [番号]` で以下を実行:

1. `view_file` でモジュールを読み込み
2. `<module>...</module>` ブロックを検出
3. 抽出結果をコードブロックで出力

```xml
<!-- 出力例 -->
<module name="DMZ_Protocol" priority="CRITICAL">
    ...
</module>
```

---

## 補足

- **Creator主体**: このワークフローは Creator が手動で起動
- **Claude自動**: `/do` 実行時は Code Protocols Skill が自動参照
- **両者補完**: 手動（明示的）+ 自動（暗黙的）で完全カバー
