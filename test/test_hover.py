import pytest


code_text = """\
from sage.rings.integer_ring import IntegerRing_class
M,A = Matrix(ZZ, [[1, 2], [3, 4]])
"""


def test_hover(client):
    """Test that hover provides correct information"""
    uri = "file:///test.sage"

    # Open document
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    response = client.hover(
        uri=uri,
        line=1,
        character=0,
    )

    print("\nHover Response:", response)


if __name__ == "__main__":
    pytest.main([__file__])
