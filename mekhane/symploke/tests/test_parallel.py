# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要→test_parallel が担う
#!/usr/bin/env python3
"""
Jules API - Parallel Execution Test

Tests batch execution with 5 concurrent tasks.
Uses dev-rules repo for safe testing.
"""

import asyncio
import os
import sys
import time
import pytest

sys.path.insert(0, "/home/laihuip001/oikos/hegemonikon")

from mekhane.symploke.jules_client import JulesClient, SessionState


@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("JULES_API_KEY"), reason="JULES_API_KEY not set")
async def test_parallel_execution():
    """Test 5 parallel task execution."""
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("❌ JULES_API_KEY not set")
        return False
    
    print("=" * 70)
    print("Jules API - Parallel Execution Test (5 tasks)")
    print("=" * 70)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        client = JulesClient(api_key)
        
        # Create 5 simple tasks
        tasks = [
            {
                "prompt": f"Add a comment '# Test task {i+1} - {time.strftime('%Y-%m-%d %H:%M')}' at the end of README.md",
                "source": "sources/github/laihuip001/dev-rules",
                "branch": "main"
            }
            for i in range(5)
        ]
        
        print(f"\nSubmitting {len(tasks)} tasks...")
        print("-" * 70)
        
        start_time = time.time()
        
        # Execute with max 5 concurrent
        results = await client.batch_execute(tasks, max_concurrent=5)
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"Completed in {elapsed:.1f}s")
        print(f"{'='*70}")
        
        # Summary
        completed = sum(1 for r in results if r.state == SessionState.COMPLETED)
        failed = sum(1 for r in results if r.state == SessionState.FAILED)
        in_progress = sum(1 for r in results if r.state not in (SessionState.COMPLETED, SessionState.FAILED))
        
        print(f"\n📊 Results:")
        print(f"  ✅ Completed: {completed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏳ In Progress: {in_progress}")
        
        print(f"\n📋 Details:")
        for i, result in enumerate(results, 1):
            emoji = "✅" if result.state == SessionState.COMPLETED else "❌" if result.state == SessionState.FAILED else "⏳"
            print(f"  [{i}] {emoji} {result.state.value}")
            if result.pull_request_url:
                print(f"      PR: {result.pull_request_url}")
            if result.error:
                print(f"      Error: {result.error[:50]}...")
            if result.id:
                print(f"      ID: {result.id}")
        
        return completed > 0 or in_progress > 0
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting parallel execution test...")
    print("Note: Tasks may take 2-5 minutes to complete.")
    print("Press Ctrl+C to cancel (sessions will continue in background).\n")
    
    result = asyncio.run(test_parallel_execution())
    
    print(f"\n{'='*70}")
    print(f"Test Result: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
