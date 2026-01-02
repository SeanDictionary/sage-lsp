from sagelsp import NAME, __version__
from sagelsp.plugins.manager import create_plugin_manager
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument
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
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    all_diagnostics = ls.pm.hook.sagelsp_lint(doc=doc)
    diagnostics = [diag for plugin_diags in all_diagnostics for diag in plugin_diags]

    params = types.PublishDiagnosticsParams(
        uri=doc.uri,
        diagnostics=diagnostics,
        version=doc.version,
    )
    ls.text_document_publish_diagnostics(params)


@server.feature(types.TEXT_DOCUMENT_FORMATTING)
def format_document(ls: SageLanguageServer, params: types.DocumentFormattingParams) -> list[types.TextEdit]:
    """Format the entire document."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    all_edits = ls.pm.hook.sagelsp_format_document(doc=doc)
    edits = [edit for plugin_edits in all_edits for edit in plugin_edits]
    
    return edits