## LSP Test Guide (pytest)

**[中文版](README.zh_CN.md) | English**

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
- [test_autopep8.py](test_autopep8.py) - Code formatting tests (autopep8)
- [test_pycodestyle.py](test_pycodestyle.py) - Style checking tests (pycodestyle)
- [test_pyflakes.py](test_pyflakes.py) - Linting tests (pyflakes)
- [test_cython_utils.py](test_cython_utils.py) - Cython utility tests

### Run tests

```bash
pytest test/                                   # all tests
pytest test/ -v                                # verbose output
pytest test/test_hover.py                      # single test file
pytest test/test_hover.py::test_hover          # specific test case
pytest test/ -k "hover"                        # run tests matching pattern
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
- `formatting(uri)` – request document formatting edits

**Note**: The `client` fixture automatically calls `initialize()` and handles `shutdown()/stop()` cleanup.
