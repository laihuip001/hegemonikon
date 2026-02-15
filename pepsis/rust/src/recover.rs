//! Recoverable<L> — ε の型レベル保証
//!
//! F7 知見: ε ≠ 1 は「忘却関手のレベルが対象のレベルと不一致」を意味する。
//!
//! 型システムでの表現:
//! - `T: Recoverable<L>` ⟹ レベル L まで忘却しても ε = 1 (完全回復可能)
//! - `T: !Recoverable<L>` ⟹ レベル L では ε < 1 (情報損失あり)
//!
//! つまり `recover()` を呼べるかどうかが ε の型レベル判定。

use crate::forgotten::Forgotten;
use crate::level::ForgetLevel;

// ============================================================
// Recoverable trait
// ============================================================

/// レベル `L` まで忘却しても完全に回復可能であることを示す。
///
/// `Recoverable<L>` を実装する型は、`Forgotten<Self, L>` から
/// 元の `Self` を完全に復元できる (ε = 1)。
///
/// # 設計意図
///
/// `/eat` の消化プロセスで:
/// - 概念 (Concept) → `Recoverable<Impl>`: 実装まで忘却しても回復可能
/// - ワークフロー (Workflow) → `Recoverable<Context>` のみ: 文脈忘却までは OK
/// - セッション状態 → NOT Recoverable<Design>: 設計忘却で情報が失われる
pub trait Recoverable<L: ForgetLevel>: Sized {
    /// 忘却されたデータから元のデータを回復する。
    ///
    /// この関数が存在すること自体が ε = 1 の型レベル証明。
    fn recover(forgotten: Forgotten<Self, L>) -> Self;
}

// ============================================================
// 具体例: HGK の概念型
// ============================================================

/// HGK の概念 (定理、公理) — 骨格情報
///
/// 概念は実装詳細を忘却しても回復可能。
/// ε = 1 at Impl level.
#[derive(Debug, Clone, PartialEq)]
pub struct Concept {
    pub name: String,
    pub definition: String,
}

/// HGK のワークフロー — 手順情報
///
/// WF は文脈忘却までは回復可能だが、設計忘却で情報が失われる。
/// ε = 1 at Context, ε < 1 at Design.
#[derive(Debug, Clone, PartialEq)]
pub struct Workflow {
    pub id: String,
    pub steps: Vec<String>,
    pub design_rationale: String, // これが Design 忘却で失われる
}

/// セッション状態 — 揮発的情報
///
/// セッション状態はいかなる忘却でも完全回復できない。
/// ε < 1 at all levels (Nothing を除く)。
#[derive(Debug, Clone, PartialEq)]
pub struct SessionState {
    pub context: String,
    pub wm_variables: Vec<(String, String)>,
}

// ============================================================
// Recoverable implementations
// ============================================================

// Concept: Impl レベルまで回復可能
impl Recoverable<crate::level::Context> for Concept {
    fn recover(forgotten: Forgotten<Self, crate::level::Context>) -> Self {
        forgotten.into_inner()
    }
}

impl Recoverable<crate::level::Design> for Concept {
    fn recover(forgotten: Forgotten<Self, crate::level::Design>) -> Self {
        forgotten.into_inner()
    }
}

impl Recoverable<crate::level::Impl> for Concept {
    fn recover(forgotten: Forgotten<Self, crate::level::Impl>) -> Self {
        forgotten.into_inner()
    }
}

// Workflow: Context レベルのみ回復可能
impl Recoverable<crate::level::Context> for Workflow {
    fn recover(forgotten: Forgotten<Self, crate::level::Context>) -> Self {
        forgotten.into_inner()
    }
}

// SessionState: Nothing レベルでのみ (= 忘却なしでのみ) 回復可能
// → Recoverable を実装しない = 全忘却レベルで ε < 1

// ============================================================
// ε 判定ユーティリティ
// ============================================================

/// 型 T がレベル L で回復可能かどうかを判定する。
///
/// Recoverable<L> を実装していれば true (ε = 1)。
/// 実装していなければ false (ε < 1)。
///
/// # 注意
///
/// この関数は const fn にはできない (trait bound の制約)。
/// コンパイル時の判定は Recoverable<L> の有無自体で行う。
pub fn is_recoverable<T: Recoverable<L>, L: ForgetLevel>() -> bool {
    true // この関数が呼べること自体が証明
}
