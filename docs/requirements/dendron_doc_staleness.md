# Dendron ドキュメント腐敗自動検知 — 要件書

> **目的**: ドキュメント間の依存関係を宣言し、上流が更新されたのに下流が未更新の状態を Dendron が自動検知する
> **FEP 的意味**: ドキュメントの予測誤差を環境的に最小化する仕組み

---

## 背景

2026-02-17 の GCP 引越し監査で、`STRUCTURE.md` (v2.1, 2026-01-27) が `axiom_hierarchy.md` (v7.0, 2026-02-15) と大幅に乖離していた。原因は axiom_hierarchy.md が17回更新される間、STRUCTURE.md は一度も更新されなかったこと。人間の注意力に依存する更新管理は FEP 的に不健全。

## 要件

### R1: 依存関係の宣言

各ドキュメントの YAML frontmatter に `depends_on` フィールドを追加:

```yaml
---
doc_id: "KERNEL_DOCTRINE"
version: "3.2.0"
depends_on:
  - doc_id: "AXIOM_HIERARCHY"
    min_version: "7.0.0"
  - doc_id: "NAMING_CONVENTIONS"
    min_version: "1.1.0"
---
```

### R2: Staleness チェッカー

`mekhane/dendron/` に `doc_staleness.py` を追加:

- 全 `.md` ファイルの YAML frontmatter をパース
- `depends_on` グラフを構築
- 上流の `version` > 下流の `depends_on.min_version` → **STALE** 判定
- `updated` の日付差が N日以上 → **WARNING** 判定

### R3: Boot 統合

`boot_integration.py` の既存軸に Staleness チェックを追加:
- `/boot` 時に自動実行
- STALE 件数を Boot Report に表示

### R4: スコアリング

EPT スコアに Document Health を組み込む:
- 全依存関係のうち STALE でないものの割合 = **Doc Health %**
- EPT 総合スコアに重み付き加算

## 対象ドキュメント (初期)

| doc_id | ファイル | 主な依存先 |
|:-------|:---------|:-----------|
| AXIOM_HIERARCHY | kernel/axiom_hierarchy.md | — (root) |
| KERNEL_DOCTRINE | kernel/doctrine.md | AXIOM_HIERARCHY |
| NAMING_CONVENTIONS | kernel/naming_conventions.md | AXIOM_HIERARCHY |
| ARCHITECTURE | ARCHITECTURE.md | AXIOM_HIERARCHY, registry.yaml |
| MEKHANE_ARCH | mekhane/ARCHITECTURE.md | ARCHITECTURE |
| GEMINI_PROFILE | .gemini/GEMINI.md | AXIOM_HIERARCHY, ARCHITECTURE |
| WF_CLASSIFICATION | ccl/wf_classification.md | workflows/ (ファイル数) |

## 検証計画

1. `doc_staleness.py --check` で STALE 0件を確認 (リファクタ直後)
2. axiom_hierarchy.md を v7.1 に更新 → doctrine.md が STALE になることを確認
3. Boot Report に Doc Health が表示されることを確認

## 制約

- YAML frontmatter のない .md ファイルは対象外
- `knowledge_items/` 以下は対象外 (外部取得コンテンツ)
- 循環依存は検出時にエラーではなく WARNING
