# PROOF: [L3/テスト] <- hermeneus/tests/ 統合テスト
"""
Hermēneus Verifier Integration Tests — Convergent Debate

実際の LLM (Antigravity LS) を使って収束型ラリーを実行し、
ラリーの質・収束挙動・レイテンシを観察する。

前提: Antigravity LS が起動していること (synteleia-sandbox WS)
"""

import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.verifier import (
    AgentRole,
    DebateAgent,
    DebateEngine,
    ConvergenceDetector,
    RallyTurn,
)


def check_ls_available() -> bool:
    """Antigravity LS が起動しているか確認"""
    try:
        from mekhane.ochema.antigravity_client import AntigravityClient
        client = AntigravityClient(workspace="synteleia-sandbox")
        status = client.get_status()
        return status is not None
    except Exception as e:
        print(f"⚠️  LS 未起動: {e}")
        return False


@pytest.mark.asyncio
async def test_single_agent_generate():
    """単一エージェントの LLM 生成テスト"""
    if not check_ls_available():
        pytest.skip("Antigravity LS not available")

    print("\n" + "=" * 60)
    print("Test 1: 単一エージェント LLM 生成")
    print("=" * 60)
    
    agent = DebateAgent(AgentRole.PROPOSER)
    
    start = time.time()
    turn = await agent.respond(
        claim="FEP (Free Energy Principle) は認知科学の統一理論として有効である",
        rally_history=[],
        context="Hegemonikón は FEP に基づく認知ハイパーバイザーフレームワーク",
    )
    elapsed = time.time() - start
    
    print(f"\n📝 @Proposer (Turn {turn.turn_number}):")
    print(f"   確信度: {turn.confidence:.2f}")
    print(f"   レイテンシ: {elapsed:.1f}s")
    print(f"   内容 (先頭200字):\n   {turn.content[:200]}...")
    
    assert turn.speaker == AgentRole.PROPOSER
    assert len(turn.content) > 10, "応答が短すぎる"
    assert turn.confidence > 0, "確信度が0"
    
    print("   ✅ passed")


@pytest.mark.asyncio
async def test_two_agent_rally():
    """Proposer ↔ Critic のラリーテスト (3ターン)"""
    if not check_ls_available():
        pytest.skip("Antigravity LS not available")

    print("\n" + "=" * 60)
    print("Test 2: Proposer ↔ Critic ラリー (3ターン)")
    print("=" * 60)
    
    proposer = DebateAgent(AgentRole.PROPOSER)
    critic = DebateAgent(AgentRole.CRITIC)
    
    claim = "CCL の収束型ラリー (~*) は単発ラウンドより検証精度が高い"
    context = "Multi-Agent Debate for LLM validation"
    
    rally_history = []
    total_start = time.time()
    
    for turn_idx in range(3):
        agent = proposer if turn_idx % 2 == 0 else critic
        role_name = "@Proposer" if turn_idx % 2 == 0 else "@Critic"
        
        start = time.time()
        turn = await agent.respond(claim, rally_history, context)
        elapsed = time.time() - start
        
        rally_history.append(turn)
        
        print(f"\n📝 {role_name} (Turn {turn.turn_number}):")
        print(f"   確信度: {turn.confidence:.2f}")
        print(f"   レイテンシ: {elapsed:.1f}s")
        print(f"   内容 (先頭150字):\n   {turn.content[:150]}...")
    
    total_elapsed = time.time() - total_start
    
    # 収束判定を試行
    converged, reason = ConvergenceDetector.check(rally_history, min_turns=3)
    
    print(f"\n📊 ラリー統計:")
    print(f"   総ターン数: {len(rally_history)}")
    print(f"   総レイテンシ: {total_elapsed:.1f}s")
    print(f"   平均レイテンシ: {total_elapsed / len(rally_history):.1f}s/turn")
    print(f"   収束判定: {'✅ 収束' if converged else '❌ 未収束'}")
    if reason:
        print(f"   理由: {reason}")
    
    # 検証: ラリー履歴の引用が行われているか
    for turn in rally_history[1:]:
        has_reference = any(
            keyword in turn.content
            for keyword in ["@Proposer", "@Critic", "指摘", "反論", "主張", "批判"]
        )
        print(f"   Turn {turn.turn_number} 文脈参照: {'✅' if has_reference else '⚠️ 弱い'}")
    
    print("   ✅ passed")


@pytest.mark.asyncio
async def test_full_debate():
    """フル debate エンジンテスト (ラリー + Arbiter)"""
    if not check_ls_available():
        pytest.skip("Antigravity LS not available")

    print("\n" + "=" * 60)
    print("Test 3: フル Debate エンジン (ラリー + Arbiter)")
    print("=" * 60)
    
    engine = DebateEngine()
    
    claim = "Hegemonikón の 24 定理体系は FEP から数学的に導出可能である"
    context = (
        "Hegemonikón は 1公理 (FEP) + 6座標 + 24定理 + 72関係の体系。"
        "数学的導出は距離 d=0,1,2 で配置されている。"
    )
    
    start = time.time()
    result = await engine.debate(
        claim=claim,
        context=context,
        max_rounds=1,
        max_rally_turns=4,
        min_rally_turns=3,
    )
    elapsed = time.time() - start
    
    print(f"\n🏛️ Debate 結果:")
    print(f"   判定: {'✅ ACCEPT' if result.accepted else '❌ REJECT'}")
    print(f"   確信度: {result.confidence:.2f}")
    print(f"   ラウンド数: {len(result.rounds)}")
    
    if result.rounds:
        r = result.rounds[0]
        print(f"   ラリーターン数: {len(r.rally)}")
        print(f"   収束: {'✅' if r.converged else '❌'} ({r.convergence_reason})")
    
    print(f"   総レイテンシ: {elapsed:.1f}s")
    print(f"   メタデータ: {result.metadata}")
    
    if result.dissent_reasons:
        print(f"   反対理由:")
        for dr in result.dissent_reasons:
            print(f"     - {dr}")
    
    # ラリーの各ターンをダンプ
    if result.rounds:
        print(f"\n📜 ラリー履歴:")
        for turn in result.rounds[0].rally:
            role_label = {
                AgentRole.PROPOSER: "@Proposer",
                AgentRole.CRITIC: "@Critic",
                AgentRole.ARBITER: "@Arbiter",
            }.get(turn.speaker, "???")
            print(f"\n   --- Turn {turn.turn_number}: {role_label} (conf={turn.confidence:.2f}) ---")
            print(f"   {turn.content[:200]}...")
    
    assert result.confidence > 0, "確信度が0"
    assert len(result.rounds) > 0, "ラウンドが空"
    
    print("\n   ✅ passed")
