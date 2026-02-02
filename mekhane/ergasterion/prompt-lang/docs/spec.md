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
| `@context` | リソース参照（ファイル/会話/MCP） | 🔴 P1 |
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

### 2.4 @context — リソース参照（P1）

**目的**: ファイル、会話履歴、MCP サーバなどのリソースをコンテキストに明示的にアタッチ

> **設計原則**: `@context` は「リソース ID の宣言」であり、テキスト展開ではない。
> どの部分を何トークン分プロンプトに注入するかは、エージェント側のコンテキスト戦略に委ねる。

```bnf
context_block   ::= "@context:" NEWLINE context_items
context_items   ::= context_item+
context_item    ::= "  - " resource_ref [options] NEWLINE
resource_ref    ::= file_ref | dir_ref | conv_ref | mcp_ref | ki_ref
file_ref        ::= "file:" STRING
dir_ref         ::= "dir:" STRING [filter_options]
conv_ref        ::= "conv:" STRING
mcp_ref         ::= "mcp:" IDENTIFIER ["." tool_chain]
ki_ref          ::= "ki:" STRING
filter_options  ::= "(" filter_list ")"
filter_list     ::= filter_item ("," filter_item)*
filter_item     ::= "filter=" STRING | "depth=" NUMBER
options         ::= "[" option_list "]"
option_list     ::= option ("," option)*
option          ::= "priority=" priority_level | "section=" STRING
priority_level  ::= "HIGH" | "MEDIUM" | "LOW"
tool_chain      ::= "tool(" STRING ")" ["." "with(" resource_ref ")"]
```

**リソース種別**:

| 種別 | 構文 | 説明 |
|:---|:---|:---|
| `file:` | `file:"src/api/user.py"` | 単一ファイル参照 |
| `dir:` | `dir:"src/"(filter="*.ts", depth=2)` | ディレクトリ参照（フィルタ付き） |
| `conv:` | `conv:"Auth Flow Design"` | 会話履歴（タイトルまたはID） |
| `mcp:` | `mcp:gnosis.tool("search")` | MCP サーバ/ツール参照 |
| `ki:` | `ki:"API設計原則"` | Knowledge Item 参照 |

**優先度のセマンティクス**:

| 優先度 | 意味 |
|:---|:---|
| `HIGH` | 全文または詳細抜粋を維持。要約・圧縮を避ける |
| `MEDIUM` | 通常のコンテキスト管理に従う（デフォルト） |
| `LOW` | 必要時のみ参照。積極的に要約・省略可 |

**例**:

```prompt-lang
#prompt api_refactoring

@context:
  - file:"src/api/user_controller.py" [priority=HIGH]
  - file:"src/api/auth_controller.py" [priority=HIGH]
  - dir:"src/models/"(filter="*.py", depth=1) [priority=MEDIUM]
  - conv:"HLD: Authentication Flow" [priority=HIGH]
  - mcp:gnosis.tool("search").with(file:"docs/query.txt")
  - ki:"REST API 設計原則" [priority=LOW]

@goal:
  上記のコンテキストを参照し、API のリファクタリング計画を策定

@constraints:
  - 既存の公開 API エンドポイントを破壊しないこと
  - 会話で決定した認証フローの設計に準拠すること
```

**Antigravity との対応**:

| Prompt-Lang | Antigravity UI | 備考 |
|:---|:---|:---|
| `file:"path"` | `@path/to/file` | 同等 |
| `dir:"path"` | `@dir/` | フィルタはPrompt-Lang固有 |
| `conv:"title"` | `@Conversation Title` | 同等 |
| `mcp:server` | `@mcp:server:` | 同等 |
| `ki:"name"` | Knowledge自動参照 | Prompt-Langで明示化 |

---

### 2.5 @extends — 継承（P2）

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

### 2.6 @mixin — 合成（P2）

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
| `@rubric` | `_parse_rubric_content()` | ✅ 完了 |
| `@if/@else` | `_parse_condition_block()` | ✅ 完了 |
| `@activation` | `_parse_activation_content()` | ✅ 完了 |
| `@context` | `_parse_context_content()` | 🟡 v2.0.1 |
| `@extends` | `_resolve_extends()` | ⚪ v2.1 |
| `@mixin` | `_resolve_mixin()` | ⚪ v2.1 |

---

## 5. 参考文献

- [Structured Prompting (arXiv)](https://arxiv.org/html/2511.20836v1)
- [Multi-level Prompting (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S095070512500591X)
- [Prompt-Lang 統合研究レポート](file:///M:/Hegemonikon/docs/research/prompt-lang-complete-report.md)
- [Antigravity メンション機能調査](file:///M:/Hegemonikon/docs/research/antigravity-mention-syntax-20260124.md)
