## LSP Test Guide (pytest)

**[中文版](README.zh_CN.md) | English**

### Scope

These tests mainly cover:

- LSP request/response flow (`hover`, `definition`, `typeDefinition`, `completion`)
- Formatting and diagnostics integration (`autopep8`, `pycodestyle`, `pyflakes`)
- Internal utility behavior (`cython_utils`, `symbols_cache`)

Most LSP tests are smoke/integration checks and print server responses for manual inspection.

### Files

- [lspclient.py](lspclient.py) - LSP client wrapper (requests/notifications, response reading)
- [lspclientbase.py](lspclientbase.py) - Base LSP client implementation
- [conftest.py](conftest.py) - Pytest config and fixtures
- [examples.py](examples.py) - Example code snippets for testing
- [color.py](color.py) - Terminal color utilities

#### Test Files

- [test_lsp_server.py](test_lsp_server.py) - LSP server initialization and basic functionality
- [test_hover.py](test_hover.py) - Hover information tests
- [test_definition.py](test_definition.py) - Go to definition tests
- [test_type_definition.py](test_type_definition.py) - Go to type definition tests
- [test_completion.py](test_completion.py) - Completion request tests
- [test_autopep8.py](test_autopep8.py) - Code formatting tests (autopep8)
- [test_pycodestyle.py](test_pycodestyle.py) - Style checking tests (pycodestyle)
- [test_pyflakes.py](test_pyflakes.py) - Linting tests (pyflakes)
- [test_cython_utils.py](test_cython_utils.py) - Cython utility tests
- [test_symbols_cache.py](test_symbols_cache.py) - Symbol cache unit tests

### Prerequisites

- Run from repository root (`sage-lsp/`)
- Install test dependencies (for example via project extras/dev dependencies)
- Ensure `sagelsp` can be imported in the current Python environment

### Run tests

```bash
pytest tests/                                   # all tests
pytest tests/test_hover.py                      # single test file
pytest tests/test_hover.py::test_hover          # specific test case
```

### Add a new test

Create a new test function using the `client` fixture (auto start/init/cleanup):

```python
import pytest

code_text = """\
R = PolynomialRing(ZZ)
"""

def test_my_feature(client):
    uri = "file:///test.sage"

    # Open document
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    # Test your feature
    response = client.hover(
        uri=uri,
        line=0,
        character=4,
    )

    assert response is not None
    print("\nResponse:", response)

if __name__ == "__main__":
    pytest.main([__file__])
```

### LSPClient quick reference

#### LSPClientBase methods (low-level)

- `initialize()` – run initialize handshake
- `shutdown()` – graceful shutdown
- `send_request(method, params=None)` – send a request, returns request id
- `send_notification(method, params=None)` – send a notification
- `read_response(expected_id=None)` – read one response, skipping notifications
- `start()` – start the LSP server process
- `stop()` – stop the LSP server process

#### LSPClient methods (high-level)

- `did_open(uri, language_id, text, version=1)` – notify server that document is opened
- `did_change(uri, text, version)` – notify server that document is changed
- `hover(uri, line, character)` – request hover info at position
- `definition(uri, line, character)` – request definition locations
- `type_definition(uri, line, character)` – request type definition locations
- `completion(uri, line, character)` – request completion items
- `formatting(uri)` – request document formatting edits

**Note**: The `client` fixture automatically calls `initialize()` and handles `shutdown()/stop()` cleanup.

### Notes

- The `client` fixture in [conftest.py](conftest.py) starts `python -m sagelsp --log DEBUG`.
- Some tests validate behavior through logs/printed responses rather than strict assertions.
- Use `-s` when running tests if you want to inspect LSP responses and diagnostics in terminal output.
