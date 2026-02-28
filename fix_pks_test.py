with open("mekhane/pks/tests/test_gateway_stats.py", "r") as f:
    content = f.read()

import_str = """import pytest
from unittest.mock import patch, MagicMock
try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None"""

content = content.replace("""import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient""", import_str)

skip_str = """class TestGatewayStatsEndpoint:
    \"\"\"GET /api/pks/gateway-stats のテスト。\"\"\"

    @pytest.fixture(autouse=True)
    def skip_if_no_fastapi(self):
        if TestClient is None:
            pytest.skip("fastapi is not installed")"""

content = content.replace("""class TestGatewayStatsEndpoint:
    \"\"\"GET /api/pks/gateway-stats のテスト。\"\"\"""", skip_str)

with open("mekhane/pks/tests/test_gateway_stats.py", "w") as f:
    f.write(content)
