//! 忘却レベルの合成則 — AST 構造に基づく型レベル合成
//!
//! ## 合成規則
//!
//! | AST ノード | 合成 | 根拠 |
//! |:-----------|:-----|:-----|
//! | Sequence   | max  | 順次実行 → 情報は減衰する (pessimistic) |
//! | Oscillation| min  | 反復 → 情報が回復する (optimistic) |
//! | Fusion     | max  | 融合 → 保守的 |
//! | Parallel   | min  | 並列 → 最も保存する分岐が活きる |

use crate::level::ForgetLevel;
use std::cmp;

// ============================================================
// 合成 trait
// ============================================================

/// Sequence の合成: max(L1, L2) — 情報は減衰する
///
/// ```text
/// A_B ⟹ G(A_B) = max(G_A, G_B)
/// ```
///
/// 直感: 順次実行は最も忘却する WF に引きずられる。
/// `/noe+_/dia-` → max(G₁, G₃) = G₃ (Impl)
pub fn sequence_compose<L1: ForgetLevel, L2: ForgetLevel>() -> u8 {
    cmp::max(L1::DEPTH, L2::DEPTH)
}

/// 収束振動 (~*) の合成: min(L1, L2) — 反復は情報を回復する
///
/// ```text
/// A~*B ⟹ G(A~*B) = min(G_A, G_B)
/// ```
///
/// 直感: 収束振動は情報の往復。最も保存する側が残る。
/// `/noe+~*/dia-` → min(G₁, G₃) = G₁ (Context)
pub fn convergent_compose<L1: ForgetLevel, L2: ForgetLevel>() -> u8 {
    cmp::min(L1::DEPTH, L2::DEPTH)
}

/// 発散振動 (~!) の合成: max(L1, L2) — 情報が散乱する
///
/// ```text
/// A~!B ⟹ G(A~!B) = max(G_A, G_B)
/// ```
///
/// 直感: 発散は情報を広げる。最も忘却する側に引きずられる。
/// `/noe+~!/dia-` → max(G₁, G₃) = G₃ (Impl)
pub fn divergent_compose<L1: ForgetLevel, L2: ForgetLevel>() -> u8 {
    cmp::max(L1::DEPTH, L2::DEPTH)
}

/// Fusion の合成: max(L1, L2) — 融合は保守的
pub fn fusion_compose<L1: ForgetLevel, L2: ForgetLevel>() -> u8 {
    cmp::max(L1::DEPTH, L2::DEPTH)
}

/// Parallel の合成: min(L1, L2) — 並列は最も保存する分岐が活きる
pub fn parallel_compose<L1: ForgetLevel, L2: ForgetLevel>() -> u8 {
    cmp::min(L1::DEPTH, L2::DEPTH)
}

// ============================================================
// 動的合成 (depth 値ベース)
// ============================================================

/// Sequence: max
pub fn seq_compose_dyn(depths: &[u8]) -> u8 {
    depths.iter().copied().max().unwrap_or(2) // fallback: Design
}

/// Oscillation: min
pub fn osc_compose_dyn(left: u8, right: u8) -> u8 {
    cmp::min(left, right)
}
