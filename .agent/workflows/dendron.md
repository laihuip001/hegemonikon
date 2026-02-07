---
lcm_state: draft
description: Dendron 存在証明チェック。粒度・スコープを自由に指定可能。
---

# /dendron: 存在証明チェック

> **モジュール**: Dendron (存在証明検証ツール)
> **目的**: PROOF ヘッダーと親参照の検証

## Cognitive Algebra

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/dendron+` | **Deep Check** | 全ディレクトリ、詳細レポート |
| `/dendron-` | **Quick Check** | 現在ディレクトリのみ、最小出力 |
| `/dendron*` | **Meta Check** | Dendron 自体の整合性診断 |
| `/dendron~` | **Compare** | 前回との差分表示 |

---

## 基本使用法

```bash
# 全体チェック
python -m mekhane.dendron check mekhane/ --ci

# 特定ディレクトリ
python -m mekhane.dendron check hermeneus/ --format text

# 詳細レポート
python -m mekhane.dendron check mekhane/ --format markdown
```

---

## スコープ指定

| スコープ | コマンド例 |
|---------|-----------|
| 全体 | `/dendron mekhane/` |
| 単一プロジェクト | `/dendron mekhane/dendron/` |
| 複数ディレクトリ | `/dendron hermeneus/ synergeia/` |

**Prompt 形式**:
```text
/dendron [スコープ] [オプション]

例:
/dendron mekhane/fep/
/dendron+ hermeneus/ --strict
/dendron- .  (現在ディレクトリ)
```

---

## オプション

| オプション | 説明 |
|-----------|------|
| `--ci` | CI モード (失敗時 exit 1) |
| `--strict` | ORPHAN も ERROR 扱い |
| `--format [text/markdown/json/ci]` | 出力形式 |
| `--coverage [N]` | 最小カバレッジ率 |

---

## 出力例

### 通常モード
```text
============================================================
Dendron PROOF Check Report
============================================================

Total files: 240
With proof:  180
Orphan:      55     ← v2: 親参照なし
Missing:     5
Coverage:    97.9%
Levels:      L1:38 | L2:116 | L3:86

✅ PASS (⚠️ 55 orphan: 親参照を追加してください)
```

### CI モード
```text
✅ Dendron: 100.0% coverage (L1:38/L2:116/L3:86) ⚠️55 orphan
```

---

## v2: 親参照

```python
# v1 (orphan 扱い)
# PROOF: [L2/インフラ]

# v2 (OK)
# PROOF: [L2/インフラ] <- mekhane/dendron/

# 特殊親
# PROOF: [L1/定理] <- FEP
# PROOF: [L2/インフラ] <- external
# PROOF: [L2/インフラ] <- legacy
```

---

## 統合

| 統合先 | 説明 |
|--------|------|
| `/boot` | セッション開始時にサマリ表示 |
| `pre-commit` | commit 前に自動実行 |
| GitHub Actions | push/PR 時に自動実行 |

---

*v2.0 — 親参照義務化 (2026-02-01)*
