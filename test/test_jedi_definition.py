import pytest
from pygls.workspace import TextDocument

code_text = """\
def add(a, b):
    return a + b
result = add(2, 3)

print(result)
"""


def test_jedi_definition_direct():
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
    # 'result' is in line 4, character [0:6]
    position = types.Position(line=2, character=10)

    locations = sagelsp_definition(doc, position)

    print("Definition Locations:", locations)

if __name__ == "__main__":
    pytest.main([__file__])