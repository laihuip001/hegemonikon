# Zero-Trust CCL Executor アーキテクチャ

## 構成コンポーネント

`mekhane/ccl/` パッケージに実装された、LLM の仕様遵守を強制するエンジン群。

### 1. SpecInjector (`spec_injector.py`)

- **役割**: 実行前に CCL 式から演算子を抽出し、`operators.md` の定義と「理解確認クイズ」をプロンプトに動的に注入する。
- **機能**:
  - 演算子抽出
  - 定義テーブル生成
  - 回答必須クイズの生成

### 2. OutputSchema (`output_schema.py`)

- **役割**: Pydantic を使用して、CCL 出力の各セクション（演算子理解、推論過程、検証、結果）の構造を定義する。
- **機能**:
  - `min_length` による省略監視
  - 演算子別必須フィールドの定義 (例: `!`, `~`, `*` 専用の出力クラス)

### 3. OutputValidator (`validators.py`)

- **役割**: 生成されたテキストまたは JSON を事後検証する。
- **機能**:
  - 必須セクションの存在確認
  - 振動演算子の双方向性チェック
  - 違反時の「再生成指示 (Regeneration Instruction)」の自動生成

### 4. FailureDB (`learning/failure_db.py`)

- **役割**: 過去の失敗原因を永続化し、知見を再利用する。
- **機能**:
  - 失敗レコードの保存 (`failures.json`)
  - 知見に基づく警告の自動生成
  - 成功パターンの蓄積

### 5. Unified Executor (`executor.py`)

- **役割**: 上記を統合し、Hegemonikón システムからの単一エントリポイントを提供する。

## 5段強制実行ワークフロー (5-Phase Zero-Trust Flow)

Hegemonikón は、LLM に対する「広義の期待 (希望)」を「狭義の期待 (予測)」に置き換え、以下の 5 段階で実行を強制する。

1. **Phase 0: Spec Injection + Quiz**
   - 実行前に `operators.md` の定義を注入し、理解確認クイズを必須回答とする。
2. **Phase 1: Output Schema Enforcement**
   - Pydantic を使用し、欠落のない構造化出力を強制する (`min_length` 監視)。
3. **Phase 2: Semantic Reasoning Validation**
   - 各演算子に対応する「必須セクション」の存在を文字レベルで検証する。
4. **Phase 3: Multi-Agent Audit**
   - 3エージェント（Operator, Logic, Completeness）による論理整合性のクロスチェックを行う。
   - インフラストラクチャとして `mekhane.audit` を利用。
   - **3x3 Cognitive Matrix**: 処理・出力・監査の各フェーズで並列エージェントによる検証を行う高信頼性アプローチをサポート。

5. **Phase 4: Learning/Feedback Loop**
   - 失敗パターンを `failure_db.json` に記録し、次回のプロンプトに警告として反映する。

## Standard Macros (Integrity)

- `@audit`: `Σ[/dia.lex~/dia-~/dia.epo]*^` — 3エージェント並列監査
- `@@audit`: 出力+監査の2フェーズ検証
- `@@@audit`: 3x3 マトリクスによる全段階検証 (Critical)

## 構造的強制（セクション・マッピング）

AI の「省略」や「無視」を防ぐため、CCL 式に含まれる演算子に基づき、以下のセクション出力を強制する。

| 演算子 | 要求される見出し/構造 | 検証内容 |
| :--- | :--- | :--- |
| **!** | `## 全派生同時実行` | 同時並列処理の証明 |
| **~** | `## 振動演算` | A ↔ B の双方向性確認 |
| ***** | `## 融合` | 二項対立の止揚プロセス |
| **^** | `## メタ分析` | 推論過程の自己参照 |
| **+** | `## 詳細` | 粒度の深掘り |
| **_** | `## ステップ` | 線形推論の記録 |

## LLM 認知的負荷への対策 (Cognitive Solutions)

- **Lost-in-the-Middle 対策**: 重要仕様はプロンプトの冒頭と末尾に冗長に配置。
- **Context Rot 対策**: 必要な演算子仕様のみを動的に厳選注入し、注意予算を節約。
- **省略バイアス対策**: `min_tokens` 設定や、セクション見出しがない場合のリジェクト・再生成ループの構築。

## 実行ワークフロー (API)

1. **Prepare**: `executor.prepare(ccl_expr)`
   - 仕様注入 + 過去の警告取得 → プロンプト完成
2. **Execute**: LLM 生成実行
3. **Validate**: `executor.validate(output, context)`
   - 成功 → 成功記録 (Phase 4)
   - 失敗 → 失敗記録 + 再生成プロンプト生成
4. **Retry**: 失敗時は再生成プロンプトで再試行

## 参照ファイル

- `mekhane/ccl/executor.py`
- `mekhane/ccl/spec_injector.py`
- `mekhane/ccl/output_schema.py`
- `mekhane/ccl/guardrails/validators.py`
- `mekhane/ccl/learning/failure_db.py`

---
*v2.6 (Zero-Trust Doctrine Edition) | 2026-02-01*
