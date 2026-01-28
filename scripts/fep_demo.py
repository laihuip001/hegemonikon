#!/usr/bin/env python3
"""
FEP Demo: Hegemonikón Active Inference Agent

Demonstrates the pymdp integration with Stoic philosophy concepts.

Usage:
    python scripts/fep_demo.py
"""

import sys
sys.path.insert(0, ".")

from mekhane.fep import HegemonikónFEPAgent
from mekhane.fep.state_spaces import (
    PHANTASIA_STATES,
    ASSENT_STATES,
    HORME_STATES,
    OBSERVATION_MODALITIES,
    index_to_state,
)
import numpy as np


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'═' * 60}")
        print(f"  {title}")
        print(f"{'═' * 60}")
    else:
        print(f"{'─' * 60}")


def print_beliefs(beliefs: np.ndarray, title: str = "信念分布"):
    """Pretty print belief distribution."""
    print(f"\n📊 {title}:")
    for idx, prob in enumerate(beliefs):
        if prob > 0.01:  # Only show significant beliefs
            p, a, h = index_to_state(idx)
            bar = "█" * int(prob * 20)
            print(f"   [{p:9s} / {a:8s} / {h:7s}]: {prob:.2%} {bar}")


def demo_single_observation():
    """Demonstrate single observation inference."""
    print_separator("O1 Noēsis: 単一観測からの信念更新")
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    # Initial beliefs
    print("\n🔹 初期信念 (Epistemic Humility を反映):")
    print_beliefs(agent.beliefs)
    
    # Observation: clear context (index 1)
    print("\n🔹 観測: clear (明確な文脈)")
    result = agent.infer_states(observation=1)
    
    print_beliefs(result["beliefs"], "更新後の信念")
    print(f"\n   MAP 状態: {result['map_state_names']}")
    print(f"   エントロピー: {result['entropy']:.3f}")


def demo_policy_selection():
    """Demonstrate policy selection (O2 Boulēsis)."""
    print_separator("O2 Boulēsis: ポリシー選択")
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    # First, update beliefs
    agent.infer_states(observation=1)  # Clear context observed
    
    # Then, infer policies
    q_pi, neg_efe = agent.infer_policies()
    
    print("\n📊 ポリシー確率:")
    actions = ["observe (O1 Noēsis)", "act (O4 Energeia)"]
    for i, (prob, efe) in enumerate(zip(q_pi, neg_efe)):
        bar = "█" * int(prob * 20)
        print(f"   Action {i} ({actions[i]}): {prob:.2%} {bar}")
        print(f"      Expected Free Energy: {-efe:.3f}")


def demo_full_cycle():
    """Demonstrate full inference-action cycle."""
    print_separator("完全サイクル: O1 → O2 → O4")
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    observations = [
        (1, "clear context"),
        (6, "high confidence"),
        (3, "medium urgency"),
    ]
    
    for obs_idx, obs_name in observations:
        print(f"\n🔹 観測 {obs_idx}: {obs_name}")
        result = agent.step(observation=obs_idx)
        
        print(f"   MAP 状態: {result['map_state_names']}")
        print(f"   エントロピー: {result['entropy']:.3f}")
        print(f"   選択行動: {result['action_name']}")
        print_separator()


def demo_entropy_as_uncertainty():
    """Demonstrate entropy as a measure of uncertainty."""
    print_separator("エントロピー: 不確実性の定量化")
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    print("\n観測によるエントロピー変化:")
    print(f"   初期エントロピー: {-np.sum(agent.beliefs * np.log(agent.beliefs + 1e-10)):.3f}")
    
    # Different observations
    observations = [
        (0, "ambiguous context"),
        (1, "clear context"),
        (2, "low urgency"),
        (4, "high urgency"),
        (5, "low confidence"),
        (7, "high confidence"),
    ]
    
    for obs_idx, obs_name in observations:
        agent = HegemonikónFEPAgent(use_defaults=True)  # Reset
        result = agent.infer_states(observation=obs_idx)
        print(f"   {obs_name:20s} → エントロピー: {result['entropy']:.3f}")


def main():
    """Run all demonstrations."""
    print_separator("Hegemonikón FEP Demo")
    print("\npymdp Active Inference を用いたストア派認知モデル")
    print("O1 Noēsis (認識) → O2 Boulēsis (意志) → O4 Energeia (行動)")
    
    try:
        demo_single_observation()
        demo_policy_selection()
        demo_full_cycle()
        demo_entropy_as_uncertainty()
        
        print_separator("デモ完了")
        print("\n✅ pymdp 統合は正常に動作しています。")
        print("   次のステップ: /noe, /bou ワークフローへの統合")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
