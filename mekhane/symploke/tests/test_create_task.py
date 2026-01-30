# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要→test_create_task が担う
#!/usr/bin/env python3
"""
Jules API - Create a simple test task.
Creates a minimal PR to test the full workflow.
"""

import asyncio
import os
import sys

sys.path.insert(0, "/home/laihuip001/oikos/hegemonikon")

from mekhane.symploke.jules_client import JulesClient, SessionState


async def create_test_task():
    """Create a simple test task."""
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("❌ JULES_API_KEY not set")
        return False
    
    print("=" * 60)
    print("Jules API - Create Test Task")
    print("=" * 60)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        client = JulesClient(api_key)
        
        # Use dev-rules repo (exists in sources)
        repo = "sources/github/laihuip001/dev-rules"
        prompt = "Add a comment to the README.md file with today's date: 2026-01-27"
        
        print(f"\nCreating task:")
        print(f"  Repo: {repo}")
        print(f"  Prompt: {prompt}")
        print("-" * 60)
        
        session = await client.create_session(
            prompt=prompt,
            source=repo,
            branch="main",
            auto_approve=True
        )
        
        print(f"\n✅ Session created!")
        print(f"  ID: {session.id}")
        print(f"  Name: {session.name}")
        print(f"  State: {session.state.value}")
        
        print("\nPolling for completion (timeout: 120s)...")
        final = await client.poll_session(session.id, timeout=120, poll_interval=5)
        
        print(f"\n{'='*60}")
        print(f"Final State: {final.state.value}")
        
        if final.pull_request_url:
            print(f"✅ PR Created: {final.pull_request_url}")
        elif final.error:
            print(f"❌ Error: {final.error}")
        
        return final.state == SessionState.COMPLETED
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(create_test_task())
    print(f"\n{'='*60}")
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
