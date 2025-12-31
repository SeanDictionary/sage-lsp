from sagelsp import NAME, __version__
from sagelsp.plugins.manager import create_plugin_manager
from pygls.lsp.server import LanguageServer
from lsprotocol import types
import logging

log = logging.getLogger(__name__)

class SageLanguageServer(LanguageServer):
    def __init__(self, *args):
        super().__init__(*args)
        self.pm = create_plugin_manager()
        self.log = log


server = SageLanguageServer(NAME, __version__)

@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: SageLanguageServer, params: types.DidChangeTextDocumentParams):
    """Handle document change events."""
    doc = ls.workspace.get_document(params.text_document.uri)
    diagnostics = ls.pm.hook.sagelsp_lint(doc=doc)

    params = types.PublishDiagnosticsParams(
        uri=doc.uri,
        diagnostics=diagnostics
    )
    ls.text_document_publish_diagnostics(params)
