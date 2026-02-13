# PROOF: [L2/エージェント] <- mekhane/synteleia/dokimasia/ Ochema Backend Integration
"""
Ochema Backend Integration for Testing
"""
from typing import Optional, Dict, Any
import requests

class OchemaBackend:
    """Mock backend for Ochema integration tests."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health_check(self) -> bool:
        """Check if backend is reachable."""
        try:
            resp = requests.get(f"{self.base_url}/health")
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def submit_task(self, task_id: str, payload: Dict[str, Any]) -> str:
        """Submit a task to the backend."""
        resp = requests.post(f"{self.base_url}/tasks", json={"id": task_id, "data": payload})
        resp.raise_for_status()
        return resp.json().get("job_id", "")
