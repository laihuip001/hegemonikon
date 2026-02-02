# Phase 4 実装計画（修正版）

## ゴール
1. `phase3-complete` を `main` に安全にマージ
2. `prompt-lang` 構文設計（Phase A）を開始

---

## 1. マージ戦略（競合解消手順付き）

### 手順

```bash
# 1. mainの現状を確認
git checkout main
git pull origin main

# 2. phase3-completeを正として強制マージ
git merge phase3-complete --strategy-option theirs -m "merge: Phase 3 complete into main (force override)"

# 3. タグ付け
git tag v1.0.0-phase3-complete

# 4. プッシュ
git push origin main --tags
```

### 根拠
- `main` の古い構造（`modules/`, `protocols/`）は放棄する
- `phase3-complete` の構造（`library/`）が新しい正
- `--strategy-option theirs` で競合時は `phase3-complete` を優先

---

## 2. ディレクトリ役割分担

| ディレクトリ | 役割 | 内容 |
|---|---|---|
| `library/` | **運用資産** | 本番で使うプロンプトテンプレート |
| `docs/` | **ドキュメント** | ユーザーマニュアル、引き継ぎ資料 |
| `docs/brain_dump/` | **アーカイブ** | 設計過程の記録（読み専用） |
| `design/` | **実験場** | 未成熟な設計ドラフト（prompt-lang等） |

→ `prompt-lang-vision.md` は `docs/brain_dump/` に残す（アーカイブ）
→ 新規構文仕様は `design/prompt-lang/` に作成（実験場）

---

## 3. prompt-lang構文設計（Phase A）

### 成果物
`design/prompt-lang/syntax_spec_v0.1.md`

### 構文定義（初期ドラフト）

```prompt-lang
// メタデータブロック
@meta {
  task: "customer-support-reply";
  archetype: precision;
  tags: [cot, few-shot];
}

// システム定義
@system {
  role: "Senior Customer Support Agent";
  constraints: [
    no_fabrication,
    empathetic_tone,
    max_tokens(150)
  ];
}

// 思考プロセス
@thinking {
  step analyze: "顧客の感情状態を判定";
  step strategize: "解決策を選定";
  step draft: "回答を構築";
}

// 例示
@examples {
  positive {
    input: "商品が届きません";
    output: "ご不便をおかけし申し訳ございません...";
  }
  negative {
    input: "商品が届きません";
    output: "配送会社に問い合わせてください";
  }
}

// 出力形式
@output {
  format: "挨拶 + 共感 + 解決策 + 次のステップ";
  max_tokens: 150;
}
```

---

## 4. 検証計画

| チェック項目 | コマンド/方法 |
|---|---|
| マージ完了 | `git log --oneline -5` |
| ファイル存在 | `ls library/perceive/` |
| タグ確認 | `git tag -l` |
| 構文レビュー | ユーザー目視 |

---

## 実行順序

1. [ ] `main` にマージ（強制上書き戦略）
2. [ ] タグ `v1.0.0-phase3-complete` 作成
3. [ ] `feature/prompt-lang-design` ブランチ作成
4. [ ] `design/prompt-lang/syntax_spec_v0.1.md` 作成
5. [ ] ユーザーレビュー
