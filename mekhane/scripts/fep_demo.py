# PROOF: [L3/ユーティリティ] O4→運用スクリプトが必要→fep_demo が担う
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Hegemonikón FEP Demo")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="対話モードで起動")
    args = parser.parse_args()
    
    if args.interactive:
        return interactive_mode()
    
    # Non-interactive demos
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
        print("   対話モード: python scripts/fep_demo.py -i")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def interactive_mode():
    """対話型 FEP デモ (REPL)"""
    from mekhane.fep.encoding import encode_to_flat_index, decode_observation
    
    print_separator("FEP Interactive Mode")
    print("\n🧠 Hegemonikón Active Inference Agent")
    print("入力: 自然言語テキスト → FEP 推論 → 行動推奨")
    print("ヘルプ: /help\n")
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    # 初期A行列を保存 (diff 計算用)
    initial_A = agent.agent.A[0].copy() if hasattr(agent.agent.A, '__getitem__') else agent.agent.A.copy()
    
    # 履歴
    history = []
    learning_count = 0
    
    def get_entropy():
        """現在のエントロピーを計算"""
        beliefs = agent.beliefs
        # Handle nested structure from pymdp
        if isinstance(beliefs, np.ndarray):
            if beliefs.dtype == object:
                qs = np.asarray(beliefs[0], dtype=np.float64).flatten()
            else:
                qs = np.asarray(beliefs, dtype=np.float64).flatten()
        elif isinstance(beliefs, list):
            qs = np.asarray(beliefs[0], dtype=np.float64).flatten()
        else:
            qs = np.asarray(beliefs, dtype=np.float64).flatten()
        return float(-np.sum(qs * np.log(qs + 1e-10)))
    
    def show_help():
        print("""
╭─────────────────────────────────────────────────────────╮
│ FEP Interactive Mode - コマンド一覧                      │
├─────────────────────────────────────────────────────────┤
│ [テキスト入力]  → FEP 推論を実行                         │
│ /help          → このヘルプを表示                        │
│ /entropy       → 現在のエントロピー (不確実性) を表示    │
│ /diff          → A行列の累積学習量を表示                 │
│ /history       → 直近の入力履歴を表示                    │
│ /save          → 学習済みA行列を保存                     │
│ /load          → 保存済みA行列を読込                     │
│ /reset         → エージェントを初期化                    │
│ /quit, /q      → 終了                                    │
╰─────────────────────────────────────────────────────────╯
        """)
    
    try:
        while True:
            try:
                user_input = input("fep> ").strip()
            except EOFError:
                break
            
            # 空入力は無視
            if not user_input:
                continue
            
            # コマンド処理
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd in ("/quit", "/q"):
                    print("👋 終了します")
                    break
                    
                elif cmd == "/help":
                    show_help()
                    
                elif cmd == "/reset":
                    agent = HegemonikónFEPAgent(use_defaults=True)
                    initial_A = agent.agent.A[0].copy() if hasattr(agent.agent.A, '__getitem__') else agent.agent.A.copy()
                    history.clear()
                    learning_count = 0
                    print("✅ エージェントリセット")
                    
                elif cmd == "/entropy":
                    print(f"📊 現在のエントロピー: {get_entropy():.3f}")
                    
                elif cmd == "/diff":
                    current_A = agent.agent.A[0].copy() if hasattr(agent.agent.A, '__getitem__') else agent.agent.A.copy()
                    diff = np.abs(current_A - initial_A).sum()
                    print(f"📈 A行列変化量 (L1 norm): {diff:.4f}")
                    print(f"   学習回数: {learning_count}")
                    
                elif cmd == "/history":
                    if not history:
                        print("📜 履歴なし")
                    else:
                        print("📜 直近の履歴:")
                        for i, h in enumerate(history[-10:], 1):
                            print(f"   {i}. \"{h['input'][:30]}...\" → {h['action']} (H={h['entropy']:.2f})")
                            
                elif cmd == "/save":
                    path = agent.save_learned_A()
                    print(f"💾 A行列保存: {path}")
                    
                elif cmd == "/load":
                    if agent.load_learned_A():
                        print("✅ A行列読込完了")
                    else:
                        print("⚠️ 学習済みA行列が見つかりません")
                        
                else:
                    print(f"❓ 不明なコマンド: {cmd}")
                    print("   /help でコマンド一覧を表示")
                    
                continue
            
            # テキスト → FEP 推論
            try:
                obs = encode_to_flat_index(user_input)
                result = agent.infer_states(obs)
                
                # Dirichlet 学習
                agent.update_A_dirichlet(obs)
                learning_count += 1
                
                # ポリシー選択
                q_pi, _ = agent.infer_policies()
                action = agent.sample_action()
                action_name = "observe (深く考える)" if action == 0 else "act (実行する)"
                
                # 出力
                entropy = result['entropy']
                print(f"  📥 obs={obs} → 状態: {result['map_state_names']}")
                print(f"  📊 エントロピー: {entropy:.2f}")
                print(f"  🎯 推奨行動: {action_name} ({q_pi[action]:.1%})")
                
                # 履歴に追加
                history.append({
                    "input": user_input,
                    "obs": obs,
                    "entropy": entropy,
                    "action": action_name.split()[0],
                })
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                
    except KeyboardInterrupt:
        print("\n\n👋 Ctrl+C で終了")
    
    print(f"\n📊 セッション統計: {len(history)} 推論, {learning_count} 学習")
    return 0


if __name__ == "__main__":
    sys.exit(main())

