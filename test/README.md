## LSP Test Guide (pytest)

**[中文版](README.zh_CN.md) | English**

### Files

-   [test/lsp_client.py](test/lsp_client.py) - Thin LSP client wrapper (requests/notifications, response reading)
-   [test/test_lsp_server.py](test/test_lsp_server.py) - Pytest cases: initialize / hover / shutdown
-   [test/conftest.py](test/conftest.py) - Pytest config and path setup

### Run tests

```bash
pytest -s -v test/                                   # all tests with logs
pytest -s -v test/test_lsp_server.py                 # single file
pytest -s -v test/test_lsp_server.py::TestLSPServer::test_hover  # single case
```

Tips for more detail:

-   Add `-vv` for extra verbosity on test names.
-   The client already prints every request/response; keep `-s` to see stdout/stderr.

### Add a new test

Add a test function or class method in [test/test_lsp_server.py](test/test_lsp_server.py) and use the `lsp_client` fixture (auto start/init/cleanup):

```python
def test_my_feature(lsp_client):
    lsp_client.initialize()
    lsp_client.did_open(
        uri="file:///test.sage",
        language_id="sagemath",
        text="x = 1 + 1",
    )

    req_id = lsp_client.send_request("textDocument/myFeature", {
        "textDocument": {"uri": "file:///test.sage"}
    })
    response = lsp_client.read_response(expected_id=req_id)

    assert response.get("result") is not None
```

### LSPClient quick reference

-   initialize() – run initialize handshake
-   shutdown() – graceful shutdown
-   did_open(uri, language_id, text, version=1) – send didOpen
-   hover(uri, line, character) – request hover
-   send_request(method, params=None) – send a request, returns request id
-   send_notification(method, params=None) – send a notification
-   read_response(expected_id=None) – read one response, skipping notifications
