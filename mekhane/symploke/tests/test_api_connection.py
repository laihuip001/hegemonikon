# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_api_connection が担う
#!/usr/bin/env python3
"""
Quick API connection test for Jules API.
Tests if the API key is valid and can connect to Jules.
"""

import asyncio
import os
import sys
import pytest

# Add repo root to path dynamically
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# NOTE: Moved import inside try-except to handle optional dependency in some envs,
# or ensure it's installed in CI.
try:
    from mekhane.symploke.jules_client import JulesClient
    import aiohttp
except ImportError:
    # If dependencies are missing, we might be in a minimal env.
    # But for tests, they should be present.
    pass


# PURPOSE: Test API connection by listing sources
@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("JULES_API_KEY"), reason="JULES_API_KEY not set")
async def test_connection():
    """Test API connection by listing sources."""
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("❌ JULES_API_KEY not set")
        return False

    print(f"Testing API Key: {api_key[:10]}...{api_key[-4:]}")
    print("-" * 50)

    try:
        import aiohttp

        headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}

        async with aiohttp.ClientSession(headers=headers) as session:
            # Test 1: Get sources (repos)
            print("\n[Test 1] Getting sources...")
            async with session.get(
                "https://jules.googleapis.com/v1alpha/sources",
            ) as resp:
                print(f"  Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    sources = data.get("sources", [])
                    print(f"  ✅ Found {len(sources)} source(s)")
                    for src in sources[:5]:  # Show first 5
                        print(f"    - {src.get('name', 'Unknown')}")
                else:
                    text = await resp.text()
                    print(f"  ⚠️  Response: {text[:200]}")

            # Test 2: Get sessions (should work even if empty)
            print("\n[Test 2] Getting sessions...")
            async with session.get(
                "https://jules.googleapis.com/v1alpha/sessions",
            ) as resp:
                print(f"  Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    sessions = data.get("sessions", [])
                    print(f"  ✅ Found {len(sessions)} session(s)")
                else:
                    text = await resp.text()
                    print(f"  ⚠️  Response: {text[:200]}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_connection())
        sys.exit(0 if result else 1)
    except NameError:
        print("❌ asyncio or test_connection not defined (import error?)")
        sys.exit(1)
