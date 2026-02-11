import pytest
import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from synergeia.jules_api import JulesPool

@pytest.fixture
def mock_paths(tmp_path):
    config_file = tmp_path / "jules_accounts.yaml"
    state_file = tmp_path / "jules_pool_state.json"
    db_file = tmp_path / "jules_pool_state.db"

    # Create dummy config
    config_data = {
        "accounts": [
            {"id": "acc1", "email": "test1@example.com", "config_dir": str(tmp_path / "acc1")},
            {"id": "acc2", "email": "test2@example.com", "config_dir": str(tmp_path / "acc2")}
        ]
    }
    import yaml
    config_file.write_text(yaml.dump(config_data))

    return config_file, state_file, db_file

def test_migration_from_json(mock_paths):
    config_file, state_file, db_file = mock_paths

    # Create existing JSON state
    state_data = {
        "accounts": {
            "acc1": {"status": "busy", "sessions_count": 5, "last_used": "2023-01-01T12:00:00"},
            "acc2": {"status": "inactive", "sessions_count": 0, "last_used": None}
        },
        "updated": "2023-01-01T12:00:00"
    }
    state_file.write_text(json.dumps(state_data))

    # Patch constants
    with patch("synergeia.jules_api.POOL_STATE_FILE", state_file), \
         patch("synergeia.jules_api.POOL_DB_FILE", db_file, create=True):

        # Initialize pool - should trigger migration
        pool = JulesPool(config_path=config_file)

        # Verify state loaded into memory
        acc1 = next(a for a in pool.accounts if a.id == "acc1")
        assert acc1.status == "busy"
        assert acc1.sessions_count == 5
        assert acc1.last_used.isoformat() == "2023-01-01T12:00:00"

        # Verify DB created and populated
        assert db_file.exists()
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT status, sessions_count, last_used FROM accounts WHERE id=?", ("acc1",))
        row = cursor.fetchone()
        assert row == ("busy", 5, "2023-01-01T12:00:00")
        conn.close()

def test_update_account_state(mock_paths):
    config_file, state_file, db_file = mock_paths

    with patch("synergeia.jules_api.POOL_STATE_FILE", state_file), \
         patch("synergeia.jules_api.POOL_DB_FILE", db_file, create=True):

        pool = JulesPool(config_path=config_file)
        # Ensure DB is initialized (if migration didn't run because no JSON)
        if hasattr(pool, "_init_db"):
             pool._init_db()

        acc1 = next(a for a in pool.accounts if a.id == "acc1")

        # Modify state
        acc1.status = "cooldown"
        acc1.sessions_count += 1

        # Call update (check if method exists, otherwise skip - this test is for AFTER implementation)
        if hasattr(pool, "_update_account_state"):
            pool._update_account_state(acc1)

            # Verify DB updated
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT status, sessions_count FROM accounts WHERE id=?", ("acc1",))
            row = cursor.fetchone()
            assert row == ("cooldown", 1)
            conn.close()
        else:
            pytest.skip("Method _update_account_state not implemented yet")
