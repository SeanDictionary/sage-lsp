import pytest


code_text = """\
M: Matrix = Matrix(ZZ, [[1, 2], [3, 4]])
"""


def test_type_definition(client):
    """Test that jedi provides correct type definition locations"""
    uri = "file:///test.sage"

    # Open document
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    response = client.type_definition(
        uri=uri,
        line=0,
        character=0,
    )

    print("\nType Definition Response:", response)


if __name__ == "__main__":
    pytest.main([__file__])
