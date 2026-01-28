# Prompt-Lang Skill 設計レポート（ダウンロード版）

作成日: 2026-01-25

このレポートは、Antigravity IDE（Claude Sonnet 4）上で動作する **Prompt-Lang コード生成 Skill** を構築するための実務向けガイドです。内容は、Meta-prompting 手法・構造化プロンプト言語・Claude Skills/MCP の最新知見（2024-2026）を統合し、Prompt-Lang v2.0（@context, @if/@else, @rubric, @activation, @extends, @mixin）に直接落とし込める形で整理しています。

---

## 1. 結論サマリー（Prompt-Lang Skill 設計の3本柱）

1. **「テンプレート + 動的最適化」の二層構造にすること**  
   Prompt-Lang の骨格（@role, @goal, @constraints, @format, @examples）を静的テンプレートで固定し、可変部分だけを LLM で最適化する。DSPy v2.0 (Signature + MIPROv2) の設計と同型で、構文エラーとコストを同時に抑えられる。

2. **@rubric を中核に据えた自己評価ループを標準装備にすること**  
   OPRO/PromptWizard 系の Meta-prompting では、「候補プロンプト + スコア + 改善指針」をメタプロンプトに渡すことで、性能を反復的に改善できる。Prompt-Lang の @rubric に評価軸を明示し、「生成 → 自己評価 → 改善」のループを Skill 内に組み込むべき。

3. **Progressive Disclosure で「軽いメタデータ」と「重い完全定義」を分離すること**  
   Claude Skills の設計と同様に、常時ロードするのは Skill 名・目的・トリガー条件など最小限のメタ情報だけに留め、必要になったときだけ詳細な SKILL.md（Prompt-Lang）を読み込む。これを Prompt-Lang の @activation/@context/@resources で実装し、トークン効率とスケーラビリティを確保する。

---

## 2. Meta-prompting 手法の比較と Prompt-Lang への適用

### 2.1 主な手法と特徴

| 手法 | 核心アイデア | 強み | 弱み | Prompt-Lang への適用ポイント |
|------|--------------|------|------|------------------------------|
| **APE** (Automatic Prompt Engineer) | ランダム/ヒューリスティックに生成した候補プロンプトを、タスクスコアで探索 | 実装がシンプルで汎用 | 試行回数が増えるとコスト急増 | 初期テンプレート作成時の「粗い探索」として有用。1〜2ラウンドまでに制限する設計が現実的 |
| **OPRO** (LLM as Optimizer) | 「過去の候補 + スコア + 改善指針」を入力し、LLM 自身を最適化器として使う | 検索空間を賢く辿れる。人間の「レビューコメント」に近い | メタプロンプト設計がやや複雑 | Prompt-Lang の @rubric で定めたスコアを入力し、「次のバージョンの Prompt-Lang コードを出して」と指示するメタ Skill に最適 |
| **PromptBreeder / EvoPrompt** | 進化的アルゴリズムでプロンプトを突然変異・交叉しつつ進化 | 難タスクで伸びることもある | 大量試行が前提で、API コストが非常に高い | 本番運用よりは研究用途向き。Antigravity IDE では基本的に採用しない方がよい |
| **PromptWizard 系** | タスク認識型 + フィードバック駆動で、APE/EvoPrompt を上回る性能を実現 | SOTA クラスの性能 | 実装の複雑さと運用コスト | 既存 meta-prompt-generator Skill に近い設計。Skill 内で「過去の失敗プロンプト + エラー理由 + 期待する修正」を入力とする流れにすれば、実質 PromptWizard 的な挙動を実現できる |

### 2.2 Prompt-Lang Skill での実装パターン

#### フロー設計（推奨）

1. **Phase 1: テンプレート確立（半自動 or 手動）**  
   - 各ドメイン（技術、RAG、要約、医療…）ごとに、「標準的な Prompt-Lang スキル骨格」を用意する。  
   - ここでは APE 的な手法で数パターンを試し、Human-in-the-loop で 1 つに絞る。

2. **Phase 2: OPRO 的な改善ループを Skill 内に実装**  
   - @rubric で「構文正確性・セマンティック適合性・実用性」の3軸スコアを定義。  
   - `candidate_prompt + rubric_scores + failure_modes` を meta-prompt-generator Skill に渡し、「改善版 Prompt-Lang コードを再生成させる」。

3. **Phase 3: 運用時は 1〜3 ラウンドまでに回数を制限**  
   - `max_iterations = 3` など、回数とスコア改善閾値（例: +5pt 未満なら打ち切り）を決める。

---

## 3. 構造化プロンプト言語との比較から Prompt-Lang の設計に取り込むべき点

### 3.1 設計思想レベルでの比較

| 言語/フレームワーク | 制御の中心 | 型安全性 | 実行モデル | Prompt-Lang への示唆 |
|--------------------|------------|----------|------------|-----------------------|
| **DSPy v2.0** | モジュール（Python クラス）と Signature | 弱〜中（型ヒント） | 実行前に「パイプライン」をコンパイル | Prompt-Lang でも「SKILL.md = Signature」に相当。SKILL 単位で入出力仕様を明示し、それを守るコードだけを生成する、という思想を採用すべき |
| **LMQL** | 制御フロー + ロジット制約 | 中 | LLM 呼び出しを含む DSL をインタプリタが実行 | Prompt-Lang の @if/@else は LMQL のように「生成前のガード条件」を書くことに集中させ、複雑なロジックは外部コードに逃がす方がよい |
| **Guidance** | テンプレートとパーサ | 強（JSON/正規表現） | テンプレートをモデルに流し込みつつ構造制約を適用 | Prompt-Lang の @format で、出力構造を Guidance 的に「半構造化テンプレート」として指定すると、Claude 側の安定性が上がる |
| **PDL (IBM)** | YAML でプロンプト宣言 + 型スキーマ | 強 | 宣言 → 静的検証 → 実行 | Prompt-Lang は PDL に近い。将来的には `@types` や `@schema` を追加して、JSON Schema などの型情報を扱えるようにするとよい |
| **TypeChat** | TypeScript 型定義と JSON スキーマ | 強 | 型検査 → LLM 生成 → 型チェック | Prompt-Lang でも、少なくとも「期待する JSON 構造」を @format に明示し、その構造に従っているかをバリデータでチェックする設計が望ましい |

### 3.2 Prompt-Lang ディレクティブとのマッピング

- `@if/@else`  → 「どのテンプレート/ミックスインを使うか」の**ルーティング**に限定し、ビジネスロジックを詰め込みすぎない。
- `@context`   → RAG や外部ファイル、既存ドキュメントを指定する**メタデータ層**として使い、実データ本文は @resources 側に寄せる。
- `@rubric`    → LLM-as-judge と外部テスト（unit test）を組み合わせる**評価仕様**として用いる。  
- `@extends/@mixin` → 「ドメイン横断の共通パターン（例: 多言語対応、RAG 構造、要約スタイル）」を切り出して再利用可能にする。

---

## 4. Claude Skills / MCP 文脈での Prompt-Lang Skill 実装パターン

### 4.1 Claude Skills 公式ガイドからの抽出ベストプラクティス

1. **Skill ごとに「Overview / Prerequisites / Execution Steps / Examples / Error Handling / Limitations」を SKILL.md に必ず書く**  
   Prompt-Lang 側でも、`@role` や `@goal` だけでなく、これらをセクションとして持つテンプレートを最初から定型化しておく。

2. **Progressive Disclosure**  
   - 常時ロードするのは `@metadata`（名前、バージョン、説明、トリガー条件）だけ。  
   - 実際にスキルが有効化されたときにだけ、詳細な @role〜@examples を含んだ Prompt-Lang 本体を `@activation` と `@context` から読み込む。

3. **Skill Registry で組織内ガバナンスを行う**  
   - `SKILL_REGISTRY.md` のようなメタファイルを用意し、Skill 名・バージョン・オーナー・用途・変更履歴を管理。  
   - Prompt-Lang 生成 Skill 自体もこのレジストリに登録し、「どのバージョンを使うか」を IDE 上で明示的に選べるようにする。

### 4.2 Antigravity IDE / MCP を意識したアンチパターン

- **アンチパターン1: なんでも 1 つの巨大 Skill に押し込む**  
  → 解決策: Prompt-Lang の `@mixin` を使って、「ドメイン別」「機能別」に分割。Antigravity IDE では、Skill 切り替えコストよりもコンテキスト肥大の方が高くつく。

- **アンチパターン2: @activation が曖昧で、意図せぬトリガーが頻発する**  
  → 解決策: `input_contains` だけでなく、「入力の長さ」「ファイルタイプ」「ドメイン推定結果」などを条件に含める。

- **アンチパターン3: エラー時の挙動を定義していない**  
  → 解決策: Prompt-Lang 側に `Error Handling` セクションを必須にし、構文エラー・曖昧入力・ドメイン外の 3 パターンは必ずカバーする。

---

## 5. Prompt-Lang Skill の骨格設計案（サンプル）

```yaml
---
version: 2.0
name: "Prompt-Lang Code Generator"
owner: "AI Engineering Team"
last_updated: "2026-01-25"
status: "production"
---

@role: Prompt-Lang Skill Generator
@goal: |
  自然言語による要件説明から、高品質な Prompt-Lang v2.0 スキル定義（SKILL.md）を生成する。
  出力は構文的に正しく、対象ドメインに適合し、実務でそのまま利用できる品質を目指す。

@constraints:
  - 必ず @role, @goal, @constraints, @format, @examples を含めること
  - @rubric を用いて自己評価可能な設計にすること
  - 未定義のディレクティブ（@foo など）は生成しないこと
  - 医療・法律など高リスクドメインでは、免責・根拠を明示すること

@format: |
  出力は 1 つの SKILL.md ブロックとして、以下の順で記述すること:
  1. YAML ヘッダ（version, name, owner, last_updated, status）
  2. @role, @goal, @constraints, @format, @examples
  3. @rubric, @activation, @context, @extends, @mixin（必要に応じて）
  4. Error Handling / Limitations セクション

@rubric:
  - completeness: 0-10  # 必須セクションの網羅度
  - syntactic_correctness: yes/no  # Prompt-Lang v2.0 としてパース可能か
  - semantic_relevance: 0-10  # 入力要件との適合度
  - practical_utility: 0-10  # 実際に業務で使えるか

@activation:
  if input_contains("prompt", "skill", "generate", "Prompt-Lang")
    and input_length > 30
  then activate

@context:
  - template_base: templates/base_prompt_template.yaml
  - domain_templates: templates/domain_templates/
  - rubric_standards: templates/rubric_standards.yaml

@examples:
  - good: |
      入力: "医療記録から患者の基本属性を抽出するスキル"
      出力: 医療ドメイン向け SKILL.md（診療ガイドライン準拠の @constraints 付き）
  - bad: |
      入力: "なんかいい感じのプロンプト作って"
      出力: REJECT（理由: 具体性不足） + 追加質問（ドメイン/タスク/出力形式）
```

---

## 6. 評価テンプレートと失敗パターン

### 6.1 簡易評価テンプレート（5問セット）

1. **ドメイン適合性**: 「医療/法律/技術」など、指定ドメインに応じて @constraints と @rubric が変化しているか。  
2. **構文正確性**: Prompt-Lang v2.0 パーサで 10 個中 9 個以上がエラーなく通るか。  
3. **実用性**: サンプル入力 3 件に対して、生成された Skill で実際に LLM を走らせたとき、期待どおりのフォーマット/内容が得られるか。  
4. **再利用性**: 共通部分が @mixin/@extends に切り出されているか。  
5. **改善ループ有無**: @rubric を使った「自己評価→再生成」のループが存在するか。

### 6.2 典型的失敗パターン（アンチパターン）

- 構文エラー率が高い（YAML インデントやコロン漏れ）
- ドメイン特有の制約が反映されていない（医療で根拠や免責がない）
- @format が曖昧で、出力構造が毎回揺れる
- @activation 条件が緩すぎて、関係ないタスクでもトリガーされる
- @examples が乏しく、モデルの挙動が安定しない

これらはすべて、`@rubric` と簡単な Python バリデータ（構文＋いくつかの静的ルール）で自動検出可能です。

---

## 7. 今後の拡張アイデア

- **型システム拡張**: PDL/TypeChat を参考に、Prompt-Lang に `@schema` ディレクティブを追加し、JSON Schema による型検査を取り入れる。
- **MCP 連携強化**: Prompt-Lang Skill 自体を MCP サーバの「宣言ファイル」としても解釈できるようにし、同じ宣言から IDE 用 Skill と MCP 用エージェントの両方を生成する。
- **Meta-learning 導入**: 一定期間の実行ログ（入力 → 生成 Skill → 実行結果 → 評価）を貯め、MetaSPO 系の手法でシステムプロンプト/テンプレートを自動更新する仕組みを検討する。

---

このダウンロード版レポートを Antigravity IDE 内やローカルエディタで開き、必要に応じて Prompt-Lang のテンプレート定義にコピペしながら調整していく想定です。