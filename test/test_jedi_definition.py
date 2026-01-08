import pytest
from pygls.workspace import TextDocument


code_text = """\
def add(a, b):
    return a + b
result = add(2, 3)

print(result)
R = PolynomialRing(ZZ, names=('x',)); (x,) = R._first_ngens(1)
"""

code_text = """\
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

R.<x> = PolynomialRing(ZZ)
f = x^2 + 2*x + 1
"""


def test_jedi_definition(client):
    """Test that jedi provides correct definition locations"""
    uri = "file:///test.sage"

    # Open document
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    # Request definition for 'add' in line 2, character 10
    # 'add' is in line 2, character [9:12]
    # 'result' is in line 4, character [6:12]
    response = client.definition(
        uri=uri,
        line=2,
        character=8,
    )

    print("\nDefinition Response:", response)


def _test_jedi_definition_direct():
    """Direct test of the jedi definition plugin function"""

    # ! line offset relies on pyflakes_lint.UNDEFINED_NAMES_URI,
    # ! so directly using this will have no offset in line
    from sagelsp.plugins.jedi_definition import sagelsp_definition
    from lsprotocol import types
    doc = TextDocument(
        uri="file:///test.sage",
        source=code_text,
        language_id="sagemath",
        version=1
    )

    # 'add' is in line 2, character [9:12]
    # 'result' is in line 4, character [6:12]
    position = types.Position(line=3, character=8)

    locations = sagelsp_definition(doc, position)

    print("\nDefinition Locations:", locations)


if __name__ == "__main__":
    pytest.main([__file__])
