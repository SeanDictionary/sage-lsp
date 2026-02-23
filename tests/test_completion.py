import pytest


code_text = """\
ZZ
"""


def test_completion(client):
    """Test completion functionality"""
    uri = "file:///test.sage"

    # Open document
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    # Request completion
    result = client.completion(
        uri=uri,
        line=0,
        character=2,
    )

    print("\nCompletion Response:", result)


if __name__ == "__main__":
    pytest.main([__file__])
