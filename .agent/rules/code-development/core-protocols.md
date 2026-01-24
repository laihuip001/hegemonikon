---
description: コード開発時の基本プロトコル（旧資産から蒸留）
activation: manual
priority: 2
hegemonikon: M6-Praxis, M7-Dokime
---

# コード開発プロトコル

> **ソース**: Legacy Modules 01, 04, 14 から蒸留
> **適用**: 実装フェーズ（`/code`）で参照

---

## 1. DMZ Protocol（保護資産）

以下のファイルは **Read-Only**。変更時は明示的な確認を要求。

```
# 保護対象パターン
^\.env$
^config\.py$
^secrets\.json$
^docker-compose\.yml$
^requirements\.txt$
```

**違反時の対応**:
```
⚠️ DMZ ALERT: `{filename}` は保護資産です。
変更を続行しますか？ (y/N)
```

---

## 2. TDD Protocol（テスト駆動）

機能実装の順序:

1. **Red**: テストを先に書く（失敗することを確認）
2. **Green**: テストを通す最小限のコードを書く
3. **Refactor**: テストが通った後に最適化

**禁止事項**:
- テストなしの実装
- テストより先の実装

---

## 3. Commit Protocol（物語化）

コミットメッセージの構造:

```
{type}({scope}): {summary}

**Context:** なぜこの変更が必要か
**Solution:** 何をしたか
**Alternatives:** 検討したが採用しなかった案

Refs: #{issue}
```

**禁止メッセージ**:
- `fix bug`
- `update`
- `wip`
- 日本語なし英語のみの曖昧な表現

---

## 参照元

詳細が必要な場合は旧資産を参照:
- [Legacy Modules Index](file:///M:/Hegemonikon/docs/archive/legacy-rules/legacy-modules-index.md)
- [Module 01 DMZ](file:///M:/Brain/99_🗃️_保管庫｜Archive/プロンプト%20ライブラリー/モジュール（開発用）/個別のモジュール/)
