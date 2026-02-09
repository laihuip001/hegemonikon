# PROOF: [L3/ユーティリティ] <- mekhane/anamnesis/
# PURPOSE: LanceDB API compatibility
"""LanceDB compatibility layer.

Provides `get_table_names(db)` that works across LanceDB versions:
  - Old API: db.table_names()  → list[str]      (deprecated)
  - New API: db.list_tables()  → ListTablesResponse (resp.tables: list[str])

Usage:
    from mekhane.anamnesis.lancedb_compat import get_table_names
    names = get_table_names(db)
    if "knowledge" in names: ...
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import lancedb


def get_table_names(db: "lancedb.DBConnection") -> list[str]:
    """Return table names as a plain list[str], suppressing deprecation warnings.

    Tries list_tables().tables first (new API), falls back to table_names() (old API).
    """
    # New API: list_tables() returns ListTablesResponse with .tables attribute
    if hasattr(db, "list_tables"):
        try:
            resp = db.list_tables()
            # ListTablesResponse has .tables: list[str]
            if hasattr(resp, "tables"):
                return resp.tables
            # If it's already a list (future API change), return directly
            if isinstance(resp, list):
                return resp
        except Exception:
            pass

    # Fallback: old API (deprecated but functional)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return db.table_names()
