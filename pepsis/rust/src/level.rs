//! 忘却レベル — sealed hierarchy
//!
//! G₀ (Nothing) → G₁ (Context) → G₂ (Design) → G₃ (Impl) → G₄ (All)
//!
//! 各レベルは ZST (Zero-Sized Type) で、ランタイムコストはゼロ。

use std::fmt;

// ============================================================
// Sealed trait pattern — 外部クレートからの拡張を防ぐ
// ============================================================

mod private {
    pub trait Sealed {}
}

// ============================================================
// ForgetLevel trait
// ============================================================

/// 忘却レベルを表す trait。
///
/// `DEPTH` は忘却の深さを数値で表す。
/// 値が大きいほど、より多くの情報を忘却している。
pub trait ForgetLevel: private::Sealed + fmt::Debug + Copy + Clone + 'static {
    /// 忘却の深さ (0 = 何も忘れない, 4 = 全忘却)
    const DEPTH: u8;

    /// レベル名 (デバッグ用)
    const NAME: &'static str;
}

// ============================================================
// 5 段階の忘却レベル型
// ============================================================

/// G₀ — 何も忘れない。Forgotten<T, Nothing> ≅ T
#[derive(Debug, Copy, Clone)]
pub struct Nothing;

/// G₁ — 文脈を忘却 (議論の流れ、対話履歴)
#[derive(Debug, Copy, Clone)]
pub struct Context;

/// G₂ — 設計意図を忘却 (なぜその構造を選んだか)
#[derive(Debug, Copy, Clone)]
pub struct Design;

/// G₃ — 実装詳細を忘却 (コード構造、API)
#[derive(Debug, Copy, Clone)]
pub struct Impl;

/// G₄ — 全忘却。Forgotten<T, All> は情報をゼロにする。
#[derive(Debug, Copy, Clone)]
pub struct All;

// ============================================================
// Sealed implementations
// ============================================================

impl private::Sealed for Nothing {}
impl private::Sealed for Context {}
impl private::Sealed for Design {}
impl private::Sealed for Impl {}
impl private::Sealed for All {}

// ============================================================
// ForgetLevel implementations
// ============================================================

impl ForgetLevel for Nothing {
    const DEPTH: u8 = 0;
    const NAME: &'static str = "Nothing";
}

impl ForgetLevel for Context {
    const DEPTH: u8 = 1;
    const NAME: &'static str = "Context";
}

impl ForgetLevel for Design {
    const DEPTH: u8 = 2;
    const NAME: &'static str = "Design";
}

impl ForgetLevel for Impl {
    const DEPTH: u8 = 3;
    const NAME: &'static str = "Impl";
}

impl ForgetLevel for All {
    const DEPTH: u8 = 4;
    const NAME: &'static str = "All";
}

// ============================================================
// CanForgetTo — 忘却方向の型レベル制約
// ============================================================

/// L から M への忘却が許可されることを示す marker trait。
///
/// `L::DEPTH < M::DEPTH` の場合のみ実装される。
/// 逆方向の忘却 (情報の回復) は **型システムが禁止** する。
pub trait CanForgetTo<M: ForgetLevel>: ForgetLevel {}

// Nothing → 全てへ
impl CanForgetTo<Context> for Nothing {}
impl CanForgetTo<Design> for Nothing {}
impl CanForgetTo<Impl> for Nothing {}
impl CanForgetTo<All> for Nothing {}

// Context → 下位へ
impl CanForgetTo<Design> for Context {}
impl CanForgetTo<Impl> for Context {}
impl CanForgetTo<All> for Context {}

// Design → 下位へ
impl CanForgetTo<Impl> for Design {}
impl CanForgetTo<All> for Design {}

// Impl → All のみ
impl CanForgetTo<All> for Impl {}

// All → 忘却先なし (もう忘れられない)
