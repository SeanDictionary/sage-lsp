import pytest


code_text = """\
a = 1
b = a
c = b
d = c
print(d+2)
print(d)
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
        line=5,
        character=6,
    )

    print("\nDefinition Response:", response)


if __name__ == "__main__":
    pytest.main([__file__])
