import pytest
from mekhane.anamnesis.antigravity_logs import AntigravityLogCollector

def test_collector_init():
    collector = AntigravityLogCollector()
    assert collector is not None
    # Verify path logic (basic)
    assert collector._log_base.name == "logs"
