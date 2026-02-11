# CCL (Cognitive Control Language)

> **Hegemonikón の顔（Interface）** — 認知プロセスを代数的に記述する言語

## はじめに

CCL は Hegemonikón を「呼び出す」言語です。Python における構文 (Syntax) に相当し、
FEP (公理) と定理群 (builtins) を操作するためのインタフェースを提供します。

## クイックスタート

| したいこと | CCL 式 | 説明 |
|:-----------|:-------|:-----|
| 深く考える | `/noe+` | 認識を詳細展開 |
| 意志を明確にする | `/bou+` | 意志を深掘り |
| 設計→実行 | `/s+_/ene` | 設計後に実行 |
| 両面を見る | `/noe~\noe` | 正逆の往復 |
| 融合+メタ | `/noe*dia^` | 統合して過程も表示 |

## 演算子一覧

→ 詳細は [operators.md](operators.md) を参照

### 単項演算子 (6個)

| 記号 | 名称 | 作用 |
|:-----|:-----|:-----|
| `+` | 深化 | 3-5倍出力、詳細化 |
| `-` | 縮約 | 最小出力、要点のみ |
| `^` | 上昇 | メタ層へシフト |
| `/` | 下降 | 具体層へシフト |
| `?` | 照会 | 制約・確信度の確認 |
| `\` | 反転 | 視点を逆転 |

### 二項演算子 (3個)

| 記号 | 名称 | 作用 |
|:-----|:-----|:-----|
| `*` | 融合 | 複数を統合して1出力 |
| `~` | 振動 | 複数を往復して探索 |
| `_` | シーケンス | Aの後にBを実行 |

## Python との対応

| CCL 概念 | Python 対応 |
|:---------|:------------|
| CCL 式 | 式 (Expression) |
| 演算子 | `operator` モジュール |
| WF | 関数定義 |
| マクロ (@) | デコレータ (@) |
| 定理 | builtins |

## ディレクトリ構成

```
ccl/
├── README.md       # この文書
├── operators.md    # 演算子仕様
├── examples/       # 実行例
│   ├── basic.md
│   └── advanced.md
└── macros/         # マクロ定義
    ├── proof.md
    └── ground.md
```

## 関連リソース

- **[Python 実装 → `mekhane/ccl/`](../mekhane/ccl/)** — パーサ、バリデータ、マクロ展開器
- [Hegemonikón README](../README.md)
- [kernel/SACRED_TRUTH.md](../kernel/SACRED_TRUTH.md)
- [KI: Cognitive Algebra System](../.gemini/antigravity/knowledge/cognitive_algebra_system/)

---

*CCL v6.36 | Hegemonikón の顔 (Interface)*
