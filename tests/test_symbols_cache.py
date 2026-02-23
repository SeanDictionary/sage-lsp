import pytest

from sagelsp.symbols_cache import Symbol, SymbolStatus, SymbolsCache


def test_insert_and_lookup():
    symbol = Symbol(name="IntegerRing_class", status=SymbolStatus.NEED_IMPORT, import_path="sage.rings.integer_ring")
    SymbolsCache._insert(symbol)

    found = SymbolsCache._lookup("IntegerRing_class")
    assert found is not None
    assert found.name == "IntegerRing_class"
    assert found.status == SymbolStatus.NEED_IMPORT
    assert found.import_path == "sage.rings.integer_ring"


def test_get_caches_not_found_symbol():
    symbol = Symbol(name="funccccccccc", status=SymbolStatus.NOT_FOUND)
    SymbolsCache._insert(symbol)

    found = SymbolsCache._lookup("funccccccccc")
    assert found is not None
    assert found.name == "funccccccccc"
    assert found.status == SymbolStatus.NOT_FOUND
    assert found.import_path == ""

if __name__ == "__main__":
    pytest.main([__file__])