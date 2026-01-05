from sage.misc.dev_tools import import_statements  # type: ignore
from sagelsp import CachePath
from typing import Optional
from pathlib import Path
from enum import IntEnum
import sqlite3
import logging

log = logging.getLogger(__name__)


class SymbolStatus(IntEnum):
    FOUND = 1
    NOT_FOUND = 0


class Symbol:
    def __init__(self, name: str, status: SymbolStatus, import_path: str = ""):
        self.name = name
        self.status = status
        self.import_path = import_path

class SymbolsCacheBase:
    def __init__(self, cachePath: Path):
        self.cachePath = Path(cachePath)
        self.cachePath.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.cachePath, check_same_thread=False)
        self._initialize_db()
    
    def _initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbols (
            name TEXT PRIMARY KEY,
            import_path TEXT,
            status INTEGER NOT NULL
        )
        """)
        self.conn.commit()
    
    def _insert(self, symbol: Symbol):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO symbols (name, import_path, status)
        VALUES (?, ?, ?)
        """, (symbol.name, symbol.import_path, symbol.status.value))
        self.conn.commit()
        

    def _lookup(self, name: str) -> Optional[Symbol]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, import_path, status FROM symbols WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Symbol(
                name=row[0],
                import_path=row[1],
                status=SymbolStatus(row[2]),
            )
        return None

    def _check_and_cache(self, name: str) -> Symbol:
        try:
            import_str = import_statements(name, answer_as_str=True)
            import_path = self._parse_import_str(import_str)
            symbol = Symbol(
                name=name,
                status=SymbolStatus.FOUND,
                import_path=import_path
            )
            self._insert(symbol)
        except LookupError:
            symbol = Symbol(
                name=name,
                status=SymbolStatus.NOT_FOUND,
                import_path=""
            )
            self._insert(symbol)
        except Exception:
            # In theory, this should not happen
            log.warning(f"Failed to get import statement for symbol {name}", exc_info=True)
            return None
        return symbol
    
    def _parse_import_str(self, import_str: str) -> str:
        parts = import_str.split()
        if parts[0] == "from" and parts[2] == "import":
            return parts[1]
        log.warning(f"Unexpected import string format: {import_str}")
        return ""
    
    def get(self, name: str) -> Symbol:
        symbol = self._lookup(name)
        if symbol:
            return symbol
        return self._check_and_cache(name)

DBPath = Path(CachePath) / "symbols_cache.db"
SymbolsCache = SymbolsCacheBase(DBPath)