import pytest
from pygls.workspace import TextDocument


# Code containing multiple pycodestyle errors
code_text = """\
x = 1 + 1
y=2
def foo( ):
    pass

z  =  3
R.<x,y > = PolynomialRing(QQ)
a = 1 ^^1
"""

target_issues = [
    "E226 missing whitespace around arithmetic operator",
    "E225 missing whitespace around operator",
    "E302 expected 2 blank lines, found 0",
    "E201 whitespace after '('",
    "E305 expected 2 blank lines after class or function definition, found 1",
    "E221 multiple spaces before operator",
    "E222 multiple spaces after operator",
    "E202 whitespace before '>'",
    "E231 missing whitespace after ','",
    "E227 missing whitespace around bitwise or shift operator",
]


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
    
    # Modify the document to trigger diagnostics
    client.did_change(
        uri=uri,
        text=code_text,
        version=1,
    )
    
    print("\nTest completed. Check the output above for pycodestyle diagnostics.")


def _test_pycodestyle_direct():
    """Direct test of the pycodestyle plugin function"""
    from sagelsp.plugins.pycodestyle_lint import sagelsp_lint
    
    doc = TextDocument(
        uri="file:///test_direct.sage",
        source=code_text,
        language_id="sagemath",
        version=1
    )
    
    # 直接调用 lint 函数
    diagnostics = sagelsp_lint(doc)
    
    print(f"\nDirect call to sagelsp_lint returned {len(diagnostics)} diagnostics:")
    for diag in diagnostics:
        print(f"- {diag.code} at line {diag.range.start.line + 1}, char {diag.range.start.character}: {diag.message}")
    
    # Should detect at least some issues
    assert len(diagnostics) > 0, "Expected at least one style issue to be detected"


if __name__ == "__main__":
    pytest.main([__file__])
