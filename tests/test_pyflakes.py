import pytest
from types import SimpleNamespace
from pygls.workspace import TextDocument
from sagelsp.config import StyleConfig

source = """\
v = VectorSpace(ZZ, 3)
R.<x, y> = PolynomialRing(QQ)
A = Matr
"""


TEST_STYLE_CONFIG = StyleConfig(SimpleNamespace(root_path=None))


def test_pyflakes_diagnostics(client):
    """Test that pyflakes detects syntax issues"""
    uri = "file:///test.sage"
    
    # Open document containing errors
    client.did_open(
        uri=uri,
        text=source,
        language_id="sagemath",
        version=1,
    )
    
    # Modify the document to trigger diagnostics
    client.did_change(
        uri=uri,
        text=source,
        version=1,
    )
    
    print("\nTest completed. Check the output above for pyflakes diagnostics.")

def _test_pyflakes_direct():
    """Direct test of the pyflakes plugin function"""
    from sagelsp.plugins.pyflakes_lint import sagelsp_lint
    
    doc = TextDocument(
        uri="file:///test_direct.sage",
        source=source,
        language_id="sagemath",
        version=1
    )

    diagnostics = sagelsp_lint(doc=doc, config=TEST_STYLE_CONFIG, notebook=False)
    for diag in diagnostics:
        print(f"Diagnostic: {diag}")

if __name__ == "__main__":
    pytest.main([__file__])
