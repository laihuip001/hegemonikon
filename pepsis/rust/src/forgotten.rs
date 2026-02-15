//! Forgotten<T, L> — 忘却されたデータ
//!
//! `Forgotten<T, Nothing>` ≅ `T` (何も忘れていない)
//! `Forgotten<T, All>` → 情報ゼロ (全忘却)
//!
//! 所有権 (Affine) + PhantomData (Forget Level) で
//! 二次元の不可逆性を一つの型で表現する。

use std::marker::PhantomData;

use crate::level::{CanForgetTo, Context, Design, ForgetLevel, Impl, Nothing};

// ============================================================
// Forgotten<T, L>
// ============================================================

/// 忘却レベル `L` で忘却されたデータ。
///
/// # 不可逆性の二次元保証
///
/// 1. **時間方向** (Affine): `forget()` は `self` を消費 (move)。
///    呼び出し後、元の `Forgotten<T, L>` は使えない。
/// 2. **情報方向** (Forget): `L` から `M` へのレベル昇格は
///    `CanForgetTo<M>` 制約でコンパイル時に検証される。
///    逆方向 (M → L) はコンパイルエラー。
#[derive(Debug)]
pub struct Forgotten<T, L: ForgetLevel> {
    /// 保存された情報 (忘却レベルに応じて意味が変わる)
    inner: T,
    /// 忘却レベルの証拠 (ゼロコスト)
    _level: PhantomData<L>,
}

impl<T> Forgotten<T, Nothing> {
    /// 新しい「忘却されていない」データを作成。
    ///
    /// `Forgotten<T, Nothing>` ≅ `T`
    pub fn new(data: T) -> Self {
        Forgotten {
            inner: data,
            _level: PhantomData,
        }
    }
}

impl<T, L: ForgetLevel> Forgotten<T, L> {
    /// 忘却レベルを上げる。**不可逆操作**。
    ///
    /// - `self` は消費される (Affine: 時間方向の不可逆性)
    /// - `L: CanForgetTo<M>` でのみ呼べる (Forget: 情報方向の不可逆性)
    ///
    /// # 例
    ///
    /// ```
    /// use hgk_forgetful::forgotten::Forgotten;
    /// use hgk_forgetful::level::{Nothing, Context, Design};
    ///
    /// let original = Forgotten::new("HGK concept");
    /// let ctx_forgotten = original.forget::<Context>();
    /// let des_forgotten = ctx_forgotten.forget::<Design>();
    /// // original は使えない (move 済み)
    /// // ctx_forgotten も使えない (move 済み)
    /// ```
    pub fn forget<M: ForgetLevel>(self) -> Forgotten<T, M>
    where
        L: CanForgetTo<M>,
    {
        Forgotten {
            inner: self.inner,
            _level: PhantomData,
        }
    }

    /// 現在の忘却レベル深度を返す。
    pub fn depth(&self) -> u8 {
        L::DEPTH
    }

    /// 現在の忘却レベル名を返す。
    pub fn level_name(&self) -> &'static str {
        L::NAME
    }

    /// 内部データへの参照 (借用 — Affine ではなく Fn 的)
    pub fn peek(&self) -> &T {
        &self.inner
    }

    /// 忘却レベルを捨てて内部データを取り出す。
    ///
    /// これは `Recoverable<L>` の実装で使われる。
    /// 型安全性は `Recoverable` trait の実装有無で保証される。
    pub(crate) fn into_inner(self) -> T {
        self.inner
    }
}

// ============================================================
// From 実装 — 隣接レベル間の暗黙変換
// ============================================================

impl<T> From<Forgotten<T, Nothing>> for Forgotten<T, Context> {
    fn from(f: Forgotten<T, Nothing>) -> Self {
        f.forget()
    }
}

impl<T> From<Forgotten<T, Context>> for Forgotten<T, Design> {
    fn from(f: Forgotten<T, Context>) -> Self {
        f.forget()
    }
}

impl<T> From<Forgotten<T, Design>> for Forgotten<T, Impl> {
    fn from(f: Forgotten<T, Design>) -> Self {
        f.forget()
    }
}

impl<T> From<Forgotten<T, crate::level::Impl>> for Forgotten<T, crate::level::All> {
    fn from(f: Forgotten<T, crate::level::Impl>) -> Self {
        f.forget()
    }
}

// ============================================================
// Display
// ============================================================

impl<T: std::fmt::Display, L: ForgetLevel> std::fmt::Display for Forgotten<T, L> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Forgotten<{}>({})  ", L::NAME, self.inner)
    }
}

// ============================================================
// ε 計算ヘルパー
// ============================================================

/// 忘却前後のデータを比較して ε (構造回復率) を計算する。
///
/// `ε = |preserved ∩ original| / |original|`
///
/// # 引数
/// - `original_len`: 元データの情報量 (チャンク数など)
/// - `preserved_len`: 忘却後に保存された情報量
///
/// # 戻り値
/// ε ∈ [0.0, 1.0]
pub fn compute_epsilon(original_len: usize, preserved_len: usize) -> f64 {
    if original_len == 0 {
        return 1.0; // 空データの忘却は完全保存
    }
    (preserved_len as f64) / (original_len as f64)
}
