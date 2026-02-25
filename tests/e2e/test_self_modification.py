# PROOF: [WO-J02] Phase 5 Self-Modification PoC
# PURPOSE: E2E Test for /ask/agent endpoints

from fastapi.testclient import TestClient
from mekhane.api.server import app

client = TestClient(app)

def test_ask_agent_flow():
    """Test the agent ask and approve flow."""
    # 1. Ask the agent
    response = client.post(
        "/api/ask/agent",
        json={"prompt": "Please optimize the database query."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert data["status"] == "waiting_for_approval"
    assert data["requires_approval"] is True

    # 2. Approve the plan
    response = client.post(
        "/api/ask/agent/approve",
        json={"approved": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "Changes applied successfully."

def test_reject_agent_flow():
    """Test rejecting the agent plan."""
    # 1. Reject the plan directly (simulating a decision after viewing a plan)
    response = client.post(
        "/api/ask/agent/approve",
        json={"approved": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["result"] == "Changes discarded."
