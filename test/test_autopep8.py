import pytest
from pygls.workspace import TextDocument

# Code containing multiple pycodestyle errors
code_text = """\
f = x ^ 3 - 2*x + 1
"""


def test_pycodestyle_diagnostics(client):
    """Test that pycodestyle detects style issues"""
    uri = "file:///test_bad.sage"

    # Open document containing errors
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    client.formatting(
        uri=uri,
    )


if __name__ == "__main__":
    pytest.main([__file__])
