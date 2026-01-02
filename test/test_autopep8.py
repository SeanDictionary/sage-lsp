import pytest
from pygls.workspace import TextDocument

# Code containing multiple pycodestyle errors
code_text = """\
x = 1 +1
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
    
    res = client.formatting(
        uri=uri,
    )
    
    print(res)

if __name__ == "__main__":
    pytest.main([__file__])
