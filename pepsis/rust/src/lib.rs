//! # hgk-forgetful — 忘却関手の型理論
//!
//! Hegemonikón (HGK) における忘却関手 G の粒度を
//! Rust のゼロコスト型で形式化する。
//!
//! ## 核心概念
//!
//! **Affine × Forget = 二次元不可逆モデル**
//!
//! - 時間方向の不可逆性: Rust の所有権 (move)
//! - 情報方向の不可逆性: PhantomData による忘却レベル
//!
//! ## 忘却レベルの階層
//!
//! ```text
//! Nothing → Context → Design → Impl → All
//! (T)       (T-ctx)   (T-des)  (T-impl) (())
//! ```
//!
//! 忘却は**単調増加のみ**。レベルを下げる（情報を回復する）ことは
//! 型システムが禁止する。
//!
//! ## F7 知見との対応
//!
//! ε ≠ 1 ⟺ `Recoverable<L>` を実装しない型 at level L
//! ε = 1 ⟺ `Recoverable<L>` を実装する型 at level L

pub mod level;
pub mod forgotten;
pub mod recover;
pub mod compose;

#[cfg(test)]
mod tests;
