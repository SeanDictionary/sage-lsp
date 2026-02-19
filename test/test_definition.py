import pytest


code_text = """\
M: Matrix = Matrix(ZZ, [[1, 2], [3, 4]])
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

    response = client.definition(
        uri=uri,
        line=0,
        character=15,
    )

    print("\nDefinition Response:", response)


if __name__ == "__main__":
    pytest.main([__file__])
