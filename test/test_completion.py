import pytest


code_text = """\
def my_function():
    return 42

my_f
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
        line=3,
        character=4,
    )

    print("\nCompletion Response:", result)


if __name__ == "__main__":
    pytest.main([__file__])
