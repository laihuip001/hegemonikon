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
/dev              # プロトコル一覧を表示
/dev tdd          # TDD プロトコル (Module 04) を展開
/dev dmz          # DMZ プロトコル (Module 01) を展開
/dev commit       # Narrative Commit (Module 14) を展開
/dev [番号]       # 指定番号のモジュールを展開
```

---

## 実行手順

1. **引数なし**: プロトコル一覧を表示
   ```
   [Code Protocols]
   01. DMZ Protocol - 設定ファイル保護
   04. TDD Enforcement - テスト駆動開発
   06. Complexity Budget - 複雑度管理
   07. Devil's Advocate - 多視点批評
   ...
   ```

2. **引数あり**: 該当モジュールを `view_file` で展開
   ```powershell
   view_file "M:\Brain\99_🗃️_保管庫｜Archive\プロンプト ライブラリー\モジュール（開発用）\個別のモジュール\Module {XX} ....md"
   ```

3. **XMLテンプレート抽出**: モジュール内の `<module>` ブロックを提示

---

## ショートカットマッピング

| ショートカット | モジュール |
|:---|:---|
| `tdd` | Module 04 - TDD Enforcement |
| `dmz` | Module 01 - DMZ Protocol |
| `commit` | Module 14 - Narrative Commit |
| `test` | Module 07 - Devil's Advocate |
| `impact` | Module 10 - Ripple Effect Analysis |
| `security` | Module 11 - Red Teaming |
| `arch` | Module 13 - Code Archaeology |

---

## 補足

- このワークフローは **Creator が主体**
- Claude は `/do` 実行時に **自動で** Code Protocols Skill を参照
- 両者が補完的に機能する
