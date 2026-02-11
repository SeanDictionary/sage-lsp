from sagelsp import NAME, __version__
from sagelsp.plugins.manager import create_plugin_manager
from sagelsp.config import StyleConfig

from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument
from lsprotocol import types
from typing import Union, List
import logging

log = logging.getLogger(__name__)


class SageLanguageServer(LanguageServer):
    def __init__(self, *args):
        super().__init__(*args)
        self.pm = create_plugin_manager()
        self.log = log
        self.StyleConfig = None

    def refresh_styleconfig(self):
        """Refresh style configuration from workspace."""
        self.StyleConfig = StyleConfig(self.workspace)


server = SageLanguageServer(NAME, __version__)


@server.feature(types.INITIALIZE)
def initialize(ls: SageLanguageServer, params):
    ls.refresh_styleconfig()


@server.feature(types.WORKSPACE_DID_CHANGE_CONFIGURATION)
def did_change_configuration(ls: SageLanguageServer, params):
    ls.refresh_styleconfig()


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def open_change(ls: SageLanguageServer, params: Union[types.DidOpenTextDocumentParams, types.DidChangeTextDocumentParams]):
    """Handle document open and change events to trigger linting."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    all_diagnostics: List[List[types.Diagnostic]] = ls.pm.hook.sagelsp_lint(doc=doc, config=ls.StyleConfig)
    diagnostics = [diag for plugin_diags in all_diagnostics for diag in plugin_diags]

    params = types.PublishDiagnosticsParams(
        uri=doc.uri,
        diagnostics=diagnostics,
        version=doc.version,
    )
    ls.text_document_publish_diagnostics(params)


@server.feature(types.TEXT_DOCUMENT_FORMATTING)
def format_document(ls: SageLanguageServer, params: types.DocumentFormattingParams) -> List[types.TextEdit]:
    """Format the entire document."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    all_edits: List[List[types.TextEdit]] = ls.pm.hook.sagelsp_format_document(doc=doc, config=ls.StyleConfig)
    edits = [edit for plugin_edits in all_edits for edit in plugin_edits]

    return edits


@server.feature(types.TEXT_DOCUMENT_RANGE_FORMATTING)
def format_range(ls: SageLanguageServer, params: types.DocumentRangeFormattingParams) -> List:
    """Format a range of the document."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    start_line = params.range.start.line
    end_line = params.range.end.line
    all_edits: List[List[types.TextEdit]] = ls.pm.hook.sagelsp_format_range(doc=doc, start_line=start_line, end_line=end_line, config=ls.StyleConfig)
    edits = [edit for plugin_edits in all_edits for edit in plugin_edits]

    return edits


@server.feature(types.TEXT_DOCUMENT_DEFINITION)
def definition(ls: SageLanguageServer, params: types.DefinitionParams) -> List[types.Location]:
    """Provide definition for a symbol."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    position: types.Position = params.position
    all_locations: List[List[types.Location]] = ls.pm.hook.sagelsp_definition(doc=doc, position=position)
    locations = [loc for plugin_locs in all_locations for loc in plugin_locs]

    return locations


@server.feature(types.TEXT_DOCUMENT_TYPE_DEFINITION)
def type_definition(ls: SageLanguageServer, params: types.TypeDefinitionParams) -> List[types.Location]:
    """Provide type definition for a symbol."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    position: types.Position = params.position
    all_locations: List[List[types.Location]] = ls.pm.hook.sagelsp_type_definition(doc=doc, position=position)
    locations = [loc for plugin_locs in all_locations for loc in plugin_locs]

    return locations


@server.feature(types.TEXT_DOCUMENT_REFERENCES)
def references(ls: SageLanguageServer, params: types.ReferenceParams) -> List[types.Location]:
    """Provide reference for a symbol."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    position: types.Position = params.position
    all_locations: List[List[types.Location]] = ls.pm.hook.sagelsp_references(doc=doc, position=position)
    locations = [loc for plugin_locs in all_locations for loc in plugin_locs]

    return locations


@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(ls: SageLanguageServer, params: types.HoverParams) -> types.Hover:
    """Provide hover information for symbols."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    position: types.Position = params.position
    hover_info = ls.pm.hook.sagelsp_hover(doc=doc, position=position)

    if len(hover_info) > 1:
        log.warning(f"Multiple hover results for {doc.uri} at line {position.line + 1}, char {position.character}: {len(hover_info)} results")

    if hover_info:
        return hover_info[0]
    else:
        return None


@server.feature(types.TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(ls: SageLanguageServer, params: types.FoldingRangeParams) -> List[types.FoldingRange]:
    """Provide folding ranges for the document."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    all_folding_ranges: List[List[types.FoldingRange]] = ls.pm.hook.sagelsp_folding_range(doc=doc)
    folding_ranges = [fr for plugin_frs in all_folding_ranges for fr in plugin_frs]

    return folding_ranges
