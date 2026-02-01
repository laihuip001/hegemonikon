# [CCL]/mek+ Hermēneus Phase 5 — Production Hardening

---
sel:
  workflow: /mek+
  scope: P5=production_hardening
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - CLI ツール
    - API サーバー
    - ドキュメント
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 5"
  [target: Production Ready]
  {
    /s1 "CLI Tool"        -- コマンドラインインターフェース
    /s2 "Integration"     -- Python API 統合
    /s3 "Documentation"   -- README + ドキュメント
    /s4 "Examples"        -- 使用例・サンプル
  }
  >> Production Ready ✅
```

---

## Phase 5 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | 実運用可能な状態に整備 |
| **成果物** | `cli.py`, `README.md`, examples |
| **依存** | `click` (CLI) |
| **検証** | E2E テスト |

---

## 実装タスク CCL

```ccl
# Phase 5 タスクリスト
let phase_5_tasks = [
  /s1+ "CLI Tool" {
    hermeneus CLI エントリーポイント
    compile サブコマンド
    execute サブコマンド
    verify サブコマンド
    audit サブコマンド
  }
  
  /s2+ "Integration" {
    __main__.py エントリー
    pyproject.toml 更新
    pip install -e . 対応
  }
  
  /s3+ "Documentation" {
    README.md 整備
    API リファレンス
    アーキテクチャ図
  }
  
  /s4+ "Examples" {
    使用例スクリプト
    Jupyter ノートブック (オプション)
  }
]

F:[phase_5_tasks]{/ene+} >> 全タスク完了
```

---

## CLI 設計

```
hermeneus
├── compile <ccl>         # CCL → LMQL コンパイル
├── execute <ccl>         # CCL 実行
│   ├── --context <text>  # コンテキスト
│   ├── --model <name>    # モデル指定
│   └── --output <file>   # 出力ファイル
├── verify <ccl>          # Multi-Agent Debate 検証
│   ├── --rounds <n>      # ディベートラウンド数
│   └── --min-conf <f>    # 最低確信度
├── audit                 # 監査レポート
│   ├── --period <days>   # 期間
│   └── --format <fmt>    # 出力形式 (text/json)
└── version              # バージョン表示
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/cli.py` | [NEW] CLI エントリーポイント |
| `src/__main__.py` | [NEW] python -m hermeneus 対応 |
| `README.md` | [NEW] プロジェクトドキュメント |
| `examples/` | [NEW] 使用例ディレクトリ |

---

## 使用例 (目標)

```bash
# CCL コンパイル
hermeneus compile "/noe+ >> V[] < 0.3"

# CCL 実行
hermeneus execute "/noe+" --context "プロジェクト分析" --model gpt-4o

# 検証
hermeneus verify "/ene+![verify]" --rounds 3 --min-conf 0.8

# 監査レポート
hermeneus audit --period 7 --format json
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 5*
