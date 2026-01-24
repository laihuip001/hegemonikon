# Prompt-Lang v2 仕様書

**バージョン**: 2.0.0
**作成日**: 2026-01-24
**ステータス**: Draft

---

## 1. 概要

Prompt-Lang v2 は、構造化プロンプト記述言語 v1 に以下の機能を追加する:

| ディレクティブ | 目的 | 優先度 |
|:---|:---|:---:|
| `@rubric` | 自己評価・品質指標の組み込み | 🔴 P1 |
| `@if/@else` | 条件分岐によるプロンプト切替 | 🔴 P1 |
| `@activation` | Glob/ルール連携のメタデータ | 🔴 P1 |
| `@extends` | テンプレート継承 | 🟠 P2 |
| `@mixin` | 共通モジュールの再利用 | 🟠 P2 |

---

## 2. 構文定義

### 2.1 @rubric — 評価指標

**目的**: LLM出力を自己評価させるための評価基準を定義

```bnf
rubric_block    ::= "@rubric:" NEWLINE rubric_content
rubric_content  ::= dimension_list [output_spec]
dimension_list  ::= dimension+
dimension       ::= "  - " dimension_name ":" NEWLINE dimension_body
dimension_name  ::= IDENTIFIER
dimension_body  ::= "      description:" STRING NEWLINE
                    "      scale:" scale_type NEWLINE
                    [criteria_block]
scale_type      ::= "1-5" | "1-10" | "binary" | "percent"
criteria_block  ::= "      criteria:" NEWLINE criteria_item+
criteria_item   ::= "        " NUMBER ":" STRING NEWLINE
output_spec     ::= "  output:" NEWLINE
                    "    format:" STRING NEWLINE
                    "    key:" STRING NEWLINE
```

**例**:
```prompt-lang
@rubric:
  - correctness:
      description: 事実・仕様への整合性
      scale: 1-5
      criteria:
        5: 明示された仕様と完全に一致
        3: 主要点は合っているが細部に曖昧さ
        1: 仕様に反している

  - structure:
      description: フォーマット準拠度
      scale: binary

  output:
    format: json
    key: evaluation
```

---

### 2.2 @if/@else — 条件分岐

**目的**: 環境変数や文脈に応じてプロンプトの一部を切り替え

```bnf
condition_block ::= "@if" condition ":" NEWLINE
                    indented_content
                    ["@else:" NEWLINE indented_content]
                    "@endif"

condition       ::= IDENTIFIER comparison_op value
comparison_op   ::= "==" | "!=" | ">" | "<" | ">=" | "<="
value           ::= STRING | NUMBER | "true" | "false"
indented_content::= ("  " LINE NEWLINE)+
```

**例**:
```prompt-lang
@if env == "prod":
  @constraints:
    - 絶対にファイル削除を行わないこと
    - 外部APIへの書き込み操作は禁止
@else:
  @constraints:
    - テスト環境のため /tmp 配下のみ書き込み可
@endif
```

**変数参照**:
- `env` — 実行環境 (dev/staging/prod)
- `model` — 使用モデル (claude/gemini)
- `lang` — 出力言語 (ja/en)
- `user.*` — ユーザー定義変数

---

### 2.3 @activation — メタデータ

**目的**: Glob統合、ルール連携のためのメタ情報を定義

```bnf
activation_block ::= "@activation:" NEWLINE activation_items
activation_items ::= activation_item+
activation_item  ::= "  " key ":" value NEWLINE
key              ::= "mode" | "pattern" | "priority" | "rules"
```

**mode 値**:
| 値 | 意味 |
|:---|:---|
| `always_on` | 常時適用 |
| `manual` | ユーザー明示時のみ |
| `glob` | パターンマッチ時 |
| `model_decision` | モデル判断で適用 |

**例**:
```prompt-lang
@activation:
  mode: glob
  pattern: "**/src/**/*.prompt"
  priority: 2
  rules: [code_style, security_rules]
```

---

### 2.4 @extends — 継承（P2）

**目的**: ベーステンプレートを継承し、一部だけ上書き

```bnf
extends_block ::= "@extends:" base_name NEWLINE
base_name     ::= IDENTIFIER
```

**例**:
```prompt-lang
#prompt security_review
@extends: base_spec
@goal:
  セキュリティ観点に特化してレビュー
```

> **Note**: v2.0 では構文のみ定義。実装は v2.1 以降。

---

### 2.5 @mixin — 合成（P2）

**目的**: 共通モジュールを複数promptから再利用

```bnf
mixin_def    ::= "#mixin" mixin_name NEWLINE mixin_body
mixin_use    ::= "@mixin:" "[" mixin_list "]" NEWLINE
mixin_list   ::= mixin_name ("," mixin_name)*
mixin_name   ::= IDENTIFIER
```

**例**:
```prompt-lang
#mixin json_output
@format:
  type: json
  required_keys: [summary, risks]

#prompt system_review
@mixin: [json_output, security_constraints]
@role:
  システム設計レビューア
```

> **Note**: v2.0 では構文のみ定義。実装は v2.1 以降。

---

## 3. v1 互換性

| v1 ディレクティブ | v2 ステータス |
|:---|:---|
| `@role` | ✅ 互換 |
| `@goal` | ✅ 互換 |
| `@constraints` | ✅ 互換 |
| `@format` | ✅ 互換 |
| `@examples` | ✅ 互換 |
| `@tools` | ✅ 互換 |
| `@resources` | ✅ 互換 |

---

## 4. パーサー実装マッピング

| ディレクティブ | メソッド | 実装状態 |
|:---|:---|:---:|
| `@rubric` | `_parse_rubric_content()` | 🔴 実装中 |
| `@if/@else` | `_parse_condition_block()` | 🔴 実装中 |
| `@activation` | `_parse_activation_content()` | 🔴 実装中 |
| `@extends` | `_resolve_extends()` | ⚪ v2.1 |
| `@mixin` | `_resolve_mixin()` | ⚪ v2.1 |

---

## 5. 参考文献

- [Structured Prompting (arXiv)](https://arxiv.org/html/2511.20836v1)
- [Multi-level Prompting (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S095070512500591X)
- [Prompt-Lang 統合研究レポート](file:///M:/Hegemonikon/docs/research/prompt-lang-complete-report.md)
