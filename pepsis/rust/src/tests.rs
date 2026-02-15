//! テスト — 忘却関手の型理論
//!
//! ## テスト戦略
//!
//! 1. **正方向テスト**: 忘却レベルの昇格が成功する
//! 2. **ε テスト**: Recoverable<L> の型レベル保証
//! 3. **Affine テスト**: move 後の再利用がコンパイルエラー (trybuild なしで論理確認)
//! 4. **統合テスト**: Concept/Workflow/SessionState の消化シミュレーション

use crate::forgotten::{compute_epsilon, Forgotten};
use crate::level::*;
use crate::recover::*;

// ============================================================
// 1. 忘却レベルの基本テスト
// ============================================================

#[test]
fn test_level_depth_order() {
    assert_eq!(Nothing::DEPTH, 0);
    assert_eq!(Context::DEPTH, 1);
    assert_eq!(Design::DEPTH, 2);
    assert_eq!(Impl::DEPTH, 3);
    assert_eq!(All::DEPTH, 4);
}

#[test]
fn test_level_names() {
    assert_eq!(Nothing::NAME, "Nothing");
    assert_eq!(Context::NAME, "Context");
    assert_eq!(All::NAME, "All");
}

// ============================================================
// 2. Forgotten<T, L> の基本テスト
// ============================================================

#[test]
fn test_forgotten_new() {
    let f = Forgotten::new("hello");
    assert_eq!(f.depth(), 0);
    assert_eq!(f.level_name(), "Nothing");
    assert_eq!(*f.peek(), "hello");
}

#[test]
fn test_forget_one_level() {
    let f = Forgotten::new("concept");
    let f_ctx: Forgotten<&str, Context> = f.forget();
    assert_eq!(f_ctx.depth(), 1);
    assert_eq!(*f_ctx.peek(), "concept"); // データは保存
}

#[test]
fn test_forget_chain() {
    let f = Forgotten::new("data");
    let f1 = f.forget::<Context>();
    let f2 = f1.forget::<Design>();
    let f3 = f2.forget::<Impl>();
    let f4 = f3.forget::<All>();

    assert_eq!(f4.depth(), 4);
    assert_eq!(*f4.peek(), "data"); // 型レベルの意味であり、データ自体は保存
}

#[test]
fn test_forget_skip_levels() {
    // Nothing → Impl (中間レベルをスキップ)
    let f = Forgotten::new(42);
    let f_impl: Forgotten<i32, Impl> = f.forget();
    assert_eq!(f_impl.depth(), 3);
}

// ============================================================
// 3. From 変換テスト
// ============================================================

#[test]
fn test_from_nothing_to_context() {
    let f = Forgotten::new("via From");
    let f_ctx: Forgotten<&str, Context> = f.into();
    assert_eq!(f_ctx.depth(), 1);
}

// ============================================================
// 4. ε 計算テスト
// ============================================================

#[test]
fn test_epsilon_perfect() {
    assert_eq!(compute_epsilon(10, 10), 1.0);
}

#[test]
fn test_epsilon_partial() {
    let e = compute_epsilon(10, 7);
    assert!((e - 0.7).abs() < 1e-10);
}

#[test]
fn test_epsilon_zero() {
    assert_eq!(compute_epsilon(10, 0), 0.0);
}

#[test]
fn test_epsilon_empty() {
    assert_eq!(compute_epsilon(0, 0), 1.0); // vacuous truth
}

// ============================================================
// 5. Recoverable (ε = 1 の型保証) テスト
// ============================================================

#[test]
fn test_concept_recoverable_at_impl() {
    // Concept は Impl レベルまで忘却しても回復可能
    let concept = Concept {
        name: "Noēsis".into(),
        definition: "認識の本質的機能".into(),
    };

    let forgotten = Forgotten::new(concept.clone()).forget::<Impl>();
    let recovered = Concept::recover(forgotten);

    assert_eq!(recovered, concept);
}

#[test]
fn test_concept_recoverable_at_context() {
    let concept = Concept {
        name: "FEP".into(),
        definition: "自由エネルギー原理".into(),
    };

    let forgotten = Forgotten::new(concept.clone()).forget::<Context>();
    let recovered = Concept::recover(forgotten);

    assert_eq!(recovered, concept);
}

#[test]
fn test_workflow_recoverable_at_context_only() {
    // Workflow は Context レベルでのみ回復可能
    let wf = Workflow {
        id: "noe".into(),
        steps: vec!["Phase 1".into(), "Phase 2".into()],
        design_rationale: "FEP に基づく深い認識".into(),
    };

    let forgotten = Forgotten::new(wf.clone()).forget::<Context>();
    let recovered = Workflow::recover(forgotten);

    assert_eq!(recovered, wf);

    // Design レベルでは Recoverable を実装していない → コンパイルエラー
    // let forgotten_design = Forgotten::new(wf).forget::<Design>();
    // Workflow::recover(forgotten_design); // ← コンパイル不可
}

// ============================================================
// 6. is_recoverable ユーティリティテスト
// ============================================================

#[test]
fn test_is_recoverable_concept_impl() {
    assert!(is_recoverable::<Concept, Impl>());
}

#[test]
fn test_is_recoverable_workflow_context() {
    assert!(is_recoverable::<Workflow, Context>());
}

// ============================================================
// 7. 消化シミュレーション
// ============================================================

#[test]
fn test_digestion_simulation() {
    // 論文を消化するプロセスをシミュレート
    //
    // Phase 0: 論文 = Nothing レベル (全情報保持)
    // Phase 1: 文脈忘却 (議論の流れを忘れる)
    // Phase 2: 設計忘却 (なぜその理論を選んだかを忘れる)
    // Phase 3: 実装忘却 (具体的な手法を忘れる)
    //
    // 概念は最後まで生き残る → ε = 1 at Impl
    // WF は途中で情報損失 → ε < 1 at Design

    let paper_concept = Concept {
        name: "Terminal Coalgebra".into(),
        definition: "最大不動点としての収束構造".into(),
    };

    // 消化プロセス: Nothing → Context → Design → Impl
    let phase0 = Forgotten::new(paper_concept.clone());
    let phase1 = phase0.forget::<Context>();
    let phase2 = phase1.forget::<Design>();
    let phase3 = phase2.forget::<Impl>();

    // 概念は Impl でも回復可能 (ε = 1)
    let recovered = Concept::recover(phase3);
    assert_eq!(recovered.name, "Terminal Coalgebra");
    assert_eq!(recovered.definition, "最大不動点としての収束構造");

    // ε の数値計算 (型保証の補足)
    let original_chunks = 5; // name + definition + 例3つ
    let preserved_chunks = 5; // 全て保存 (Concept なので)
    let epsilon = compute_epsilon(original_chunks, preserved_chunks);
    assert_eq!(epsilon, 1.0);
}

#[test]
fn test_display() {
    let f = Forgotten::new("HGK");
    let s = format!("{}", f);
    assert!(s.contains("Nothing"));
    assert!(s.contains("HGK"));
}
