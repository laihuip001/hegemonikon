with open("mekhane/symploke/tests/test_api_connection.py", "r") as f:
    content = f.read()

import_str = """import os
import pytest
from unittest.mock import patch

try:
    import aiohttp
    from aioresponses import aioresponses
    from mekhane.symploke.jules_client import JulesClient
except ImportError:
    aiohttp = None
"""

content = content.replace("""import os
import pytest
from unittest.mock import patch
from aioresponses import aioresponses

from mekhane.symploke.jules_client import JulesClient""", import_str)

skip_str = """class TestJulesAPIConnection:
    \"\"\"Test API connection and error handling in JulesClient.\"\"\"

    @pytest.fixture(autouse=True)
    def skip_if_no_aiohttp(self):
        if aiohttp is None:
            pytest.skip("aiohttp is not installed")"""

content = content.replace("""class TestJulesAPIConnection:
    \"\"\"Test API connection and error handling in JulesClient.\"\"\"""", skip_str)

with open("mekhane/symploke/tests/test_api_connection.py", "w") as f:
    f.write(content)
