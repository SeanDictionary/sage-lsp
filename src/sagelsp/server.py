from sagelsp import NAME, __version__, LANGUAGE_ID
from sagelsp.plugins.manager import create_plugin_manager
from sagelsp.config import StyleConfig
from sagelsp.notebook import JupyterNotebook

from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument
from lsprotocol import types
from typing import Union, List
import logging

log = logging.getLogger(__name__)


class SageLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pm = create_plugin_manager()
        self.log = log
        self.StyleConfig = None

    def refresh_styleconfig(self):
        """Refresh style configuration from workspace."""
        self.StyleConfig = StyleConfig(self.workspace)


server = SageLanguageServer(
    name=NAME,
    version=__version__,
    text_document_sync_kind=types.TextDocumentSyncKind.Incremental,
    notebook_document_sync=types.NotebookDocumentSyncOptions(
        notebook_selector=[
            types.NotebookDocumentFilterWithCells(
                cells=[
                    types.NotebookCellLanguage(
                        language=LANGUAGE_ID
                    ),
                ],
            ),
        ],
    ),
)


def notebook_check(ls: SageLanguageServer, params) -> bool:
    return ls.workspace.get_notebook_document(cell_uri=params.text_document.uri) is not None


@server.feature(types.INITIALIZE)
def initialize(ls: SageLanguageServer, params):
    ls.refresh_styleconfig()


@server.feature(types.WORKSPACE_DID_CHANGE_CONFIGURATION)
def did_change_configuration(ls: SageLanguageServer, params):
    ls.refresh_styleconfig()


@server.feature(types.NOTEBOOK_DOCUMENT_DID_OPEN)
@server.feature(types.NOTEBOOK_DOCUMENT_DID_CHANGE)
def notebook_open_change(ls: SageLanguageServer, params: Union[types.DidOpenNotebookDocumentParams, types.DidChangeNotebookDocumentParams]):
    """Handle notebook open and change events to trigger linting."""
    nb: types.NotebookDocument = ls.workspace.get_notebook_document(notebook_uri=params.notebook_document.uri)
    log.info(f"[notebook] uri={params.notebook_document.uri} version={params.notebook_document.version}")
    if nb is None:
        return

    notebook = JupyterNotebook(ls, nb)
    doc = notebook.virtual_document

    # Handle semantic linting for notebook in virtual document
    all_diagnostics: List[List[types.Diagnostic]] = ls.pm.hook.sagelsp_semantic_lint(doc=doc, config=ls.StyleConfig, notebook=True)
    virtual_diagnostics = [diag for plugin_diags in all_diagnostics for diag in plugin_diags]
    diagnostics_semantic = notebook.map_diagnostics(virtual_diagnostics)

    # Handle style linting for notebook in original cell documents
    diagnostics_style: dict[str, List[types.Diagnostic]] = {}
    for cell in notebook.cells:
        if cell.kind != types.NotebookCellKind.Code:
            continue
        cell_doc = ls.workspace.get_text_document(cell.document)
        if cell_doc.language_id != LANGUAGE_ID:
            continue
        all_diagnostics: List[List[types.Diagnostic]] = ls.pm.hook.sagelsp_style_lint(doc=cell_doc, config=ls.StyleConfig, notebook=True)
        diagnostics = [diag for plugin_diags in all_diagnostics for diag in plugin_diags]

        diagnostics_style[cell.document] = diagnostics

    # publish diagnostics with semantic and style diagnostics
    diagnostics_all = notebook.merge_diagnostics(diagnostics_semantic, diagnostics_style)

    for cell_uri, diagnostics in diagnostics_all.items():
        cell_doc = ls.workspace.get_text_document(cell_uri)
        params = types.PublishDiagnosticsParams(
            uri=cell_uri,
            diagnostics=diagnostics,
            version=cell_doc.version,
        )
        ls.text_document_publish_diagnostics(params)


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def open_change(ls: SageLanguageServer, params: Union[types.DidOpenTextDocumentParams, types.DidChangeTextDocumentParams]):
    """Handle document open and change events to trigger linting."""
    if notebook_check(ls, params):   # Seems that it'll not appear
        return
    doc: TextDocument = ls.workspace.get_text_document(doc_uri=params.text_document.uri)
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
    all_edits: List[List[types.TextEdit]] = ls.pm.hook.sagelsp_format_document(doc=doc, config=ls.StyleConfig, notebook=notebook_check(ls, params))
    edits = [edit for plugin_edits in all_edits for edit in plugin_edits]

    return edits


@server.feature(types.TEXT_DOCUMENT_RANGE_FORMATTING)
def format_range(ls: SageLanguageServer, params: types.DocumentRangeFormattingParams) -> List[types.TextEdit]:
    """Format a range of the document."""
    doc: TextDocument = ls.workspace.get_text_document(params.text_document.uri)
    start_line = params.range.start.line
    end_line = params.range.end.line
    all_edits: List[List[types.TextEdit]] = ls.pm.hook.sagelsp_format_range(doc=doc, start_line=start_line, end_line=end_line, config=ls.StyleConfig, notebook=notebook_check(ls, params))
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

    # In theory, there should be only one hover result, just check for safety
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


@server.feature(
    types.TEXT_DOCUMENT_CODE_ACTION,
    types.CodeActionOptions(
        code_action_kinds=[
            types.CodeActionKind.QuickFix,
        ]
    )
)
def code_actions(params: types.CodeActionParams) -> List[types.CodeAction]:
    """Provide code actions for a given range."""
    diagnostics: List[types.Diagnostic] = params.context.diagnostics
    uri: str = params.text_document.uri
    all_code_actions: List[List[types.CodeAction]] = server.pm.hook.sagelsp_code_actions(uri=uri, diagnostics=diagnostics)
    code_actions = [ca for plugin_cas in all_code_actions for ca in plugin_cas]

    return code_actions


@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(
        trigger_characters=['.', '(', '[', ',', ' '],
        resolve_provider=False
    )
)
def completion(params: types.CompletionParams) -> List[types.CompletionItem]:
    """Provide completion for a symbol."""
    doc: TextDocument = server.workspace.get_text_document(params.text_document.uri)
    position: types.Position = params.position
    all_completions: List[List[types.CompletionItem]] = server.pm.hook.sagelsp_completion(doc=doc, position=position)
    completions = [comp for plugin_comps in all_completions for comp in plugin_comps]

    return completions
