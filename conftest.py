"""Root pytest configuration.

SAFETY: This project's unit tests use fixtures that call
`DatabaseEngine.drop_all_tables()` and `create_all_tables()`. Running those
against the production `sonar_debris.db` would wipe real scan results (this
happened once). To guarantee tests never touch real data, we redirect the
database to an isolated temporary SQLite file BEFORE any backend module is
imported, so every fixture operates on throwaway test data only.
"""

import os
import tempfile
from pathlib import Path

# Point the whole test process at a throwaway SQLite database. Because
# backend.database.session reads DATABASE_URL at initialize-time, setting the
# env var here (before any backend import) safely isolates every test.
_OVERRIDE = "DATABASE_URL"
if _OVERRIDE not in os.environ:
    _test_db = Path(tempfile.gettempdir()) / f"sonar_debris_test_{os.getpid()}.db"
    os.environ[_OVERRIDE] = f"sqlite:///{_test_db.as_posix()}"

# Keep SQLAlchemy from echoing every SQL statement during tests.
os.environ.setdefault("DATABASE_ECHO", "false")
