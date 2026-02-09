"""Tests for mekhane.anamnesis.lancedb_compat."""

import unittest
from unittest.mock import MagicMock, patch


class TestGetTableNames(unittest.TestCase):
    """Test get_table_names() compatibility wrapper."""

    def _call(self, db):
        from mekhane.anamnesis.lancedb_compat import get_table_names
        return get_table_names(db)

    # --- New API path: list_tables().tables ---

    def test_new_api_returns_tables_attribute(self):
        """list_tables() returns object with .tables attribute."""
        db = MagicMock()
        resp = MagicMock()
        resp.tables = ["alpha", "beta"]
        db.list_tables.return_value = resp
        result = self._call(db)
        self.assertEqual(result, ["alpha", "beta"])

    def test_new_api_returns_list_directly(self):
        """list_tables() returns a plain list (future API)."""
        db = MagicMock()
        db.list_tables.return_value = ["one", "two"]
        result = self._call(db)
        self.assertEqual(result, ["one", "two"])

    def test_new_api_empty_tables(self):
        """list_tables().tables is empty list."""
        db = MagicMock()
        resp = MagicMock()
        resp.tables = []
        db.list_tables.return_value = resp
        result = self._call(db)
        self.assertEqual(result, [])

    def test_new_api_exception_falls_back(self):
        """If list_tables() raises, falls back to table_names()."""
        db = MagicMock()
        db.list_tables.side_effect = RuntimeError("broken")
        db.table_names.return_value = ["fallback"]
        result = self._call(db)
        self.assertEqual(result, ["fallback"])

    # --- Old API path: table_names() ---

    def test_old_api_no_list_tables(self):
        """DB has no list_tables method, uses table_names()."""
        db = MagicMock(spec=[])
        db.table_names = MagicMock(return_value=["old_table"])
        result = self._call(db)
        self.assertEqual(result, ["old_table"])

    def test_deprecation_warning_suppressed(self):
        """table_names() deprecation warnings are suppressed."""
        import warnings
        db = MagicMock(spec=[])

        def warn_table_names():
            warnings.warn("deprecated", DeprecationWarning)
            return ["warned"]

        db.table_names = warn_table_names
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self._call(db)
            # No DeprecationWarning should leak
            dep_warns = [x for x in w if issubclass(x.category, DeprecationWarning)]
            self.assertEqual(len(dep_warns), 0)
        self.assertEqual(result, ["warned"])

    # --- Membership checks (the actual use case) ---

    def test_in_operator_works(self):
        """'table_name' in get_table_names(db) works."""
        db = MagicMock()
        resp = MagicMock()
        resp.tables = ["knowledge", "papers"]
        db.list_tables.return_value = resp
        result = self._call(db)
        self.assertIn("knowledge", result)
        self.assertNotIn("nonexistent", result)

    def test_return_type_is_list(self):
        """Return value is always a plain list."""
        db = MagicMock()
        resp = MagicMock()
        resp.tables = ["t1"]
        db.list_tables.return_value = resp
        result = self._call(db)
        self.assertIsInstance(result, list)


class TestGetTableNamesIntegration(unittest.TestCase):
    """Integration test with real lancedb (if available)."""

    def test_real_lancedb_connection(self):
        """Test with actual lancedb.connect()."""
        try:
            import lancedb
        except ImportError:
            self.skipTest("lancedb not installed")

        import tempfile, os
        from mekhane.anamnesis.lancedb_compat import get_table_names

        with tempfile.TemporaryDirectory() as tmp:
            db = lancedb.connect(tmp)
            names = get_table_names(db)
            self.assertIsInstance(names, list)
            self.assertEqual(len(names), 0)


if __name__ == "__main__":
    unittest.main()
