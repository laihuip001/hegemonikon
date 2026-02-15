# Modules / Visibility — 見せるものと隠すもの

> **CCL**: `/gno+{source=rust.modules}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust のモジュールとは何か

```rust
// lib.rs
pub mod api {                    // 外部に公開
    pub fn serve() { ... }       // 外部から呼べる
    fn internal() { ... }        // api モジュール内のみ

    pub(crate) mod helpers {     // クレート内のみ
        pub fn format() { ... }
    }
}

mod engine {                     // 非公開モジュール
    fn compute() { ... }
    pub(super) fn result() { ... } // 親モジュールのみ
}
```

**3 つの可視性レベル**:

| 修飾子 | スコープ | 意味 |
|:-------|:---------|:-----|
| `pub` | 全世界 | 誰でもアクセス可能 |
| `pub(crate)` | クレート内 | 同じプロジェクト内 |
| なし (private) | モジュール内 | 定義したモジュールのみ |

---

## 2. HGK の三層可視性

### 2.1 WF 層 = 可視性レベル

| Rust | HGK WF 層 | スコープ | 例 |
|:-----|:----------|:--------|:---|
| `pub` | **Ω層** (1-2文字) | 全体に公開。統合オーケストレーター | `/o`, `/s`, `/h`, `/ax` |
| `pub(crate)` | **Δ層** (3文字) | 体系内の専門家。組合せて使う | `/noe`, `/dia`, `/ene` |
| private | **τ層** (3-4文字) | タスク固有。内部実行 | `/dev`, `/exp`, `/bye` |

```
Ω層 (pub)           → /o, /s, /h, /p, /k, /a, /ax, /x
  ↓ 使用
Δ層 (pub(crate))    → /noe, /bou, /zet, /ene, /dia, /mek ...
  ↓ 使用
τ層 (private)       → /dev, /bye, /now, /boot, /plan ...
```

**Ω層の WF は他者にも説明できる** (pub)。
**τ層の WF は内部の運用手順** (private)。

### 2.2 ディレクトリ = モジュール

```
hegemonikon/
├── kernel/           # pub — 公理は全世界に公開
│   ├── SACRED_TRUTH.md
│   └── axiom_hierarchy.md
├── mekhane/          # pub(crate) — エンジン群は内部利用
│   ├── hermeneus/
│   ├── anamnesis/
│   └── ccl/
├── .agent/           # private — エージェント設定
│   ├── rules/
│   ├── workflows/
│   └── skills/
└── pepsis/           # pub(crate) — 消化プロジェクト
    ├── rust/
    └── python/
```

| ディレクトリ | Rust 可視性 | 誰が読むか |
|:-----------|:-----------|:---------|
| `kernel/` | `pub` | 全員 (Creator, AI, 外部レビュアー) |
| `mekhane/` | `pub(crate)` | 開発者 (Creator + AI) |
| `.agent/` | private | AI のみ |
| `pepsis/` | `pub(crate)` | Creator + AI の消化作業 |

---

## 3. 深い洞察: 可視性 = 信頼の境界

### Rust の観点

```rust
pub fn api_endpoint() {
    // ここは安全でなければならない。外部が使うから。
    let result = internal_compute();  // 内部は最適化優先
}
```

可視性はAPIの安定性保証。`pub` を変更するとユーザーが壊れる。
private は自由に変更できる。

### HGK の観点

| 層 | 変更の自由度 | 理由 |
|:---|:-----------|:-----|
| `kernel/` (pub) | **極低**。SACRED_TRUTH は Pin されている | 全てがこれに依存 |
| `mekhane/` (pub(crate)) | 中。interface を保ちつつ実装を変更 | WF 定義は安定、実装は改善 |
| `.agent/` (private) | **高**。自由に変更可能 | AI 固有の設定 |
| `pepsis/` (pub(crate)) | 高。消化作業は実験的 | 試行錯誤 |

**可視性 = 変更の安全性**:

- 多く公開するほど、変更が難しくなる (依存関係)
- 少なく公開するほど、変更が自由になる (カプセル化)

> **Rust と HGK の共通真理**:
> 「見せるものが多いほど、縛られる」。

---

## 4. re-export と WF のアクセスパターン

```rust
// Rust: 内部構造を隠して再エクスポート
pub use internal::ImportantType;  // 内部のパスを隠す
```

```ccl
# CCL: Ω層は Δ層を隠して提供する
/o   = /noe + /bou + /zet + /ene  の統合
# ユーザーは /o を呼べば、内部の 4 つの WF を知らなくていい
```

**Ω層 WF は re-export**: 複雑な内部構造を隠して、
シンプルなインターフェースを提供する。

---

## 5. `pub(super)` — 親モジュールのみ

```rust
mod parent {
    mod child {
        pub(super) fn helper() { ... }  // parent からのみ呼べる
    }
    fn use_helper() {
        child::helper();  // OK
    }
}
```

HGK 対応: **CCL マクロの内部 WF**

```ccl
# /ccl-dig マクロ内部の WF は外部から直接呼ばない
# /pro _ /s+~(/p*/a) _ /ana _ /dia*/o+ _ /pis _ /dox-
#   ^^^ /pro はマクロ内部のステップ。マクロ外から /pro だけ呼ぶことは意味がない
```

マクロ内の個別 WF = `pub(super)`。マクロを通してのみ呼ぶことが意図されている。

---

## 6. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「公開と非公開」は普遍的 |
| 新しい構文が必要か | ❌ 不要。WF 層 + ディレクトリ構造 |
| HGK に既に存在していたか | ✅ Ω/Δ/τ 層が可視性を実現 |
| 消化で何を学んだか | 可視性 = 信頼の境界 = 変更の自由度 |

---

*Pepsis Rust T2 | Modules/Visibility — 見せるものと隠すもの (2026-02-15)*
