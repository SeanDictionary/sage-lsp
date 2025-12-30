from sagelsp import NAME, __version__
from pygls.lsp.server import LanguageServer
from lsprotocol import types
from lsprotocol.types import Hover, HoverParams, MarkupContent, MarkupKind

class SageLanguageServer(LanguageServer):
    def __init__(self, *args):
        super().__init__(*args)

server = SageLanguageServer(NAME, __version__)

@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(ls: SageLanguageServer, params: HoverParams) -> Hover:
    """Return a simple hover so clients can verify the server is alive."""

    return Hover(
        contents=MarkupContent(
            kind=MarkupKind.PlainText,
            value="SageLSP is running. Hover works!",
        ),
    )