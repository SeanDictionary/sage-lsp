from sage.misc.dev_tools import import_statements  # type: ignore
from sagelsp import CachePath
from typing import Optional
from pathlib import Path
from enum import IntEnum
import sqlite3
import logging

log = logging.getLogger(__name__)


CACHE_VERSION = 1


class SymbolStatus(IntEnum):
    NOT_FOUND = 0
    AUTO_IMPORT = 1
    NEED_IMPORT = 2


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
        try:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("PRAGMA user_version")
            result = cursor.fetchone()
            if result:
                db_version = int(result[0])
            else:
                db_version = 0

            if db_version != CACHE_VERSION:
                if result:
                    log.info(
                        "Symbols Cache schema version mismatch: db=%s expected=%s, rebuilding cache",
                        db_version,
                        CACHE_VERSION,
                    )
                else:
                    log.info("Initializing Symbols Cache with version %s", CACHE_VERSION)
                cursor.execute("DROP TABLE IF EXISTS symbols")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                name TEXT PRIMARY KEY,
                import_path TEXT,
                status INTEGER NOT NULL
            )
            """)

            if db_version != CACHE_VERSION:
                cursor.execute(f"PRAGMA user_version = {CACHE_VERSION}")

            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

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

    def clear(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM symbols")
            self.conn.commit()
            log.info("Symbols cache cleared")
        except Exception:
            self.conn.rollback()
            raise

    def _check_and_cache(self, name: str) -> Symbol:
        try:
            import_str = import_statements(name, answer_as_str=True)
            import_path = self._parse_import_str(import_str)
            status = SymbolStatus.NOT_FOUND
            if import_path:
                if name.isidentifier():  # make sure no chance to inject
                    try:
                        exec(f"from sage.all import {name}")
                        status = SymbolStatus.AUTO_IMPORT
                    except Exception:
                        status = SymbolStatus.NEED_IMPORT

            symbol = Symbol(
                name=name,
                status=status,
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
        if len(parts)>=3 and parts[0] == "from" and parts[2] == "import":
            if parts[1].startswith('sage.'):
                return parts[1]
            else:
                return ""
        log.warning(f"Unexpected import string format: {import_str}")
        return ""

    def get(self, name: str) -> Symbol:
        symbol = self._lookup(name)
        if symbol:
            return symbol
        return self._check_and_cache(name)


DBPath = Path(CachePath) / "symbols_cache.db"
SymbolsCache = SymbolsCacheBase(DBPath)
