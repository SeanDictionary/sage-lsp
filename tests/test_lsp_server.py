import pytest
from pygls.workspace import TextDocument


code_text = """
x = 1+1
y=2
def foo( ):
    pass

z  =  3
"""

doc = TextDocument(
    uri="file:///test.sage",
    source=code_text,
    language_id="sagemath",
    version=1
)


def test_lsp(client):
    client.did_open(
        uri=doc.uri,
        text=doc.source,
        language_id=doc.language_id,
    )

    client.did_change(
        uri=doc.uri,
        text=doc.source,
    )

if __name__ == "__main__":
    pytest.main([__file__])