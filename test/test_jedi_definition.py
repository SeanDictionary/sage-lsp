from sagelsp import SageAvaliable
import pytest
from pygls.workspace import TextDocument


code_text = """\
def add(a, b):
    return a + b
result = add(2, 3)

print(result)
"""

# code_text = """\
# from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
# from sage.rings.integer_ring import ZZ

# PolynomialRing(ZZ)
# """

# if SageAvaliable:
#     from sage.repl.preparse import preparse  # type: ignore
#     code_text = preparse(code_text)
#     print(code_text)


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

    # Request definition for 'add' in line 2, character 11
    # 'add' is in line 2, character [9:12]
    # 'result' is in line 4, character [6:12]
    response = client.definition(
        uri=uri,
        line=2,
        character=10,
    )

    print("\nDefinition Response:", response)


def _test_jedi_definition_direct():
    """Direct test of the jedi definition plugin function"""
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
    position = types.Position(line=3, character=0)

    locations = sagelsp_definition(doc, position)

    print("\nDefinition Locations:", locations)


if __name__ == "__main__":
    pytest.main([__file__])
