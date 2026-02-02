# Prompt-Lang 統合レポート作成マニュアル

> **目的**: パプ君（Perplexity）が3部作で生成したリサーチ結果を1つの「聖典レベル」ドキュメントに統合する。
> **実行者**: Gemini Code Assist（Jules）
> **正本**: 以下の3ファイル

---

## 正本ファイル

| # | ファイル | 内容 | 行数 |
|---|----------|------|------|
| 1 | [調査依頼書（パプ君とのやりとり全文）](file:///C:/Users/makar/%E9%96%8B%E7%99%BA%E4%BB%A5%E5%A4%96/Downloads/%23%20%E8%AA%BF%E6%9F%BB%E4%BE%9D%E9%A0%BC%E6%9B%B8_%E4%BB%B6%E5%90%8D%EF%BC%9AGemini%203%20Pro%EF%BC%88Thinking%EF%BC%89_%20Claude%20Opus%204.5%20(1).md) | 調査依頼 + 第1弾 + 第2弾 | 約950行 |
| 2 | [第3弾レポート](file:///M:/Hegemonikon/docs/research/prompt-lang-report-part3.md) | Glob設計 + @activation + FEP + 評価スイート | 約1000行 |
| 3 | [過去セッション資料](file:///M:/Hegemonikon/docs/recovered_prompt-lang_session.md) | Prompt-Lang開発履歴 | 約90行 |

---

## 生成するファイル

```
M:\Hegemonikon\docs\research\prompt-lang-complete-report.md
```

---

## 統合ルール

### 必須事項

1. **重複排除**: 3ファイル間で重複する内容は1回のみ記載
2. **構造統一**: 以下の章構成で統合する（後述）
3. **出典保持**: 各主張のURL引用を必ず保持する
4. **日本語**: 全文日本語（コード例・技術用語は除く）

### 禁止事項

- 内容を「要約」「短縮」しない（聖典レベルの情報量を維持）
- パプ君の分析結果を「改変」しない（引用として保持）
- 表のフォーマットを変更しない

---

## 統合後の章構成（必須）

```markdown
# Prompt-Lang 統合研究レポート
## Claude Opus 4.5 × Gemini 3 Pro × Jules（Antigravity IDE）プロンプト生成能力比較

**作成日**: 2026年1月24日
**ソース**: Perplexity AI リサーチ + Claude 批評 + 過去セッション成果物

---

## 目次

1. Executive Summary（第1弾から抽出）
2. 3層比較分析（Layer 1/2/3）
3. エージェント制御プロンプト詳細
4. Prompt-Lang 改善提案（@rubric, @if/@else, @extends, @mixin, @activation）
5. Glob統合設計（.prompt拡張子 + Antigravity Rules）
6. FEP/Active Inference 理論的接続
7. 評価スイート（15+テストケース + ルーブリック）
8. 日本語プロンプト固有の考慮事項
9. 実装ガイド
10. 参考文献（全出典統合）

---
```

---

## 各章の統合元

| 章 | 統合元 |
|---|--------|
| 1. Executive Summary | 第1弾（調査依頼書内） |
| 2. 3層比較分析 | 第1弾 |
| 3. エージェント制御 | 第1弾 |
| 4. Prompt-Lang改善 | 第2弾（調査依頼書内） |
| 5. Glob統合設計 | 第3弾 |
| 6. FEP/Active Inference | 第3弾 |
| 7. 評価スイート | 第3弾 |
| 8. 日本語プロンプト | 第2弾 |
| 9. 実装ガイド | 第2弾 + 過去セッション資料 |
| 10. 参考文献 | 全ファイルから統合 |

---

## 作業手順

### Step 1: ファイル読み込み

```
1. C:\Users\makar\開発以外\Downloads\# 調査依頼書_件名：Gemini 3 Pro（Thinking）_ Claude Opus 4.5 (1).md を読み込む
2. M:\Hegemonikon\docs\research\prompt-lang-report-part3.md を読み込む
3. M:\Hegemonikon\docs\recovered_prompt-lang_session.md を読み込む
```

### Step 2: 章ごとに統合

各章について:
1. 統合元ファイルから該当部分を抽出
2. 重複を排除
3. 順序を整理
4. 出典URLを保持

### Step 3: 出力

```
M:\Hegemonikon\docs\research\prompt-lang-complete-report.md
```

に書き出す。

---

## チェックリスト

### 統合前
- [ ] 3ファイルすべてを読み込んだ
- [ ] 章構成を理解した

### 統合中
- [ ] 重複が排除されている
- [ ] 出典URLが保持されている
- [ ] 表のフォーマットが維持されている

### 統合後
- [ ] 全10章が含まれている
- [ ] 参考文献が統合されている
- [ ] ファイルが正しいパスに保存された

---

## 作業完了時の引継書生成

作業完了後、以下の形式で引継書を生成すること:

```
docs/handoff_20260124_prompt-lang-integration.md
```

内容:
- 実行したコミット一覧
- 変更ファイルリスト
- 残課題（あれば）
- 次のセッションへの推奨事項

---

*このマニュアルはパプ君（Perplexity）の3部作リサーチを正本として生成された。*
