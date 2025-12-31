"""LSP feature examples using an injected client.

Each function expects a ready-to-use client (e.g., from a pytest fixture).
No start/initialize/shutdown logic here—callers manage lifecycle.
"""

from typing import Any, Dict, List
from lspclient import LSPClient
import pytest


def example_completion(client: LSPClient) -> Any:
    """Example: request completion at line 0, character 3."""
    client.did_open(
        uri="file:///example.sage",
        language_id="sagemath",
        text="pri",
    )

    req_id = client.send_request(
        "textDocument/completion",
        {
            "textDocument": {"uri": "file:///example.sage"},
            "position": {"line": 0, "character": 3},
        },
    )
    response = client.read_response(expected_id=req_id)
    return response.get("result")


def example_diagnostics(client: LSPClient) -> List[Dict[str, Any]]:
    """Example: open a bad file and wait for diagnostics notification."""
    client.did_open(
        uri="file:///error.sage",
        language_id="sagemath",
        text="x = (",
    )

    # Read a few messages looking for publishDiagnostics
    for _ in range(5):
        msg = client._read_message()  # noqa: SLF001 – simple example use
        if msg.get("method") == "textDocument/publishDiagnostics":
            return msg.get("params", {}).get("diagnostics", [])
    return []


def example_definition(client: LSPClient) -> Any:
    """Example: go-to-definition from a call site."""
    client.did_open(
        uri="file:///definition.sage",
        language_id="sagemath",
        text="def foo():\n    pass\n\nfoo()",
    )

    req_id = client.send_request(
        "textDocument/definition",
        {
            "textDocument": {"uri": "file:///definition.sage"},
            "position": {"line": 3, "character": 0},
        },
    )
    response = client.read_response(expected_id=req_id)
    return response.get("result")


if __name__ == "__main__":
    pytest.main([__file__])