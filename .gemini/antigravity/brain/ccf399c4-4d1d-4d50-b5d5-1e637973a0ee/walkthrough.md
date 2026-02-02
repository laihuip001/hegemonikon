# Walkthrough: Prompt-Lang v2.1 統合

## 成果サマリ

| 項目 | 結果 |
|:-----|:-----|
| **Part 1** | tekhne-maker v5.0 統合 ✅ |
| **Part 2** | @extends/@mixin 実装 ✅ |
| **テスト** | 全20件 PASSED |

---

## Part 1: tekhne-maker v5.0 統合

- `meta-prompt-generator` → `tekhne-maker` へリネーム
- SKILL.md を v5.0 へ統合（v3.0 + v4.0 マージ）
- 8つの参照ファイルを `references/` に配置
- README.md に格言追加

---

## Part 2: @extends/@mixin 実装

### 追加ファイル/関数

| ファイル | 追加 |
|:---------|:-----|
| [prompt_lang.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/prompt-lang/prompt_lang.py) | `Mixin`, `ParseResult`, `CircularReferenceError`, `parse_all()`, `resolve()`, `_merge()` |
| [test_prompt_lang.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/prompt-lang/test_prompt_lang.py) | `TestExtendsAndMixin` クラス（9テスト） |

### 機能

| 機能 | 説明 |
|:-----|:-----|
| `@extends: name` | テンプレート継承（子が親を継承） |
| `@mixin: [a, b]` | テンプレート合成（複数モジュール適用） |
| `#mixin name` | 再利用可能なテンプレートフラグメント定義 |
| `parse_all()` | 複数プロンプト/mixin を一括パース |
| `resolve()` | 継承解決（循環検出付き） |

### マージルール

| フィールド | 動作 |
|:-----------|:-----|
| `role`, `goal`, `format` | 子で上書き |
| `constraints`, `examples`, `context` | 追加（親 + 子） |
| `tools`, `resources` | マージ（子が優先） |

---

## テスト結果

```
test_prompt_lang.py::TestExtendsAndMixin::test_already_resolved_prompt PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_basic_extends PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_circular_reference_detection PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_dict_merge_child_priority PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_extends_with_mixin PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_mixin_composition PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_multiple_mixins PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_parse_all_multiple_prompts PASSED
test_prompt_lang.py::TestExtendsAndMixin::test_undefined_reference PASSED

============================== 20 passed ==============================
```

---

## 次のステップ

| 優先度 | タスク |
|:------:|:-------|
| 1 | tekhne-maker を `.prompt` 形式に移行 |
| 2 | V2.2 で削除演算子追加（`!parent.rule`） |
| 3 | @use/@include 将来検討 |
