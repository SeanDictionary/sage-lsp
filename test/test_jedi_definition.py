import pytest
from pygls.workspace import TextDocument


code_text = """\
R = PolynomialRing(ZZ)
a = ZZ(123)
"""

code_text = """\
M = Matrix([[1, 2], [3, 4]])
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
        line=1,
        character=4,
    )

    print("\nDefinition Response:", response)


def _test_jedi_definition_direct():
    """Direct test of the jedi definition plugin function"""

    # ! line offset relies on plugins.pyflakes_lint.UNDEFINED_NAMES_URI,
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
    position = types.Position(line=0, character=4)

    locations = sagelsp_definition(doc, position)

    print("\nDefinition Locations:", locations)


if __name__ == "__main__":
    pytest.main([__file__])
