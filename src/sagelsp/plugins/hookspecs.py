from sagelsp import hookspec
from sagelsp.config import StyleConfig
from lsprotocol import types
from typing import List
from pygls.workspace import TextDocument


@hookspec
def sagelsp_lint(doc: TextDocument, config: StyleConfig, notebook: bool) -> List[types.Diagnostic]:
    """Lint the document using pycodestyle. It includes both style and semantic linting."""
    pass

@hookspec
def sagelsp_semantic_lint(doc: TextDocument, config: StyleConfig, notebook: bool) -> List[types.Diagnostic]:
    """Lint diagnostics that are safe on virtual notebook documents. Specially for Jupyter notebook"""
    pass


@hookspec
def sagelsp_style_lint(doc: TextDocument, config: StyleConfig, notebook: bool) -> List[types.Diagnostic]:
    """Lint diagnostics that should run on original document or cell text. Specially for Jupyter notebook"""
    pass


@hookspec
def sagelsp_format_document(doc: TextDocument, config: StyleConfig, notebook: bool) -> List[types.TextEdit]:
    """Format the document using autopep8."""
    pass


@hookspec
def sagelsp_format_range(doc: TextDocument, start_line: int, end_line: int, config: StyleConfig, notebook: bool) -> List[types.TextEdit]:
    """Format a range of the document using autopep8."""
    pass


@hookspec
def sagelsp_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide definition for a symbol."""
    pass


@hookspec
def sagelsp_type_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide type definition for a symbol."""
    # * using definition for simplicity
    pass


@hookspec
def sagelsp_references(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide reference for a symbol."""
    pass


@hookspec
def sagelsp_hover(doc: TextDocument, position: types.Position) -> types.Hover:
    pass


@hookspec
def sagelsp_folding_range(doc: TextDocument) -> List[types.FoldingRange]:
    """Provide folding ranges for the document."""
    pass


@hookspec
def sagelsp_code_actions(uri: str, diagnostics: List[types.Diagnostic]) -> List[types.CodeAction]:
    """Provide code actions for a given range."""
    pass


@hookspec
def sagelsp_completion(doc: TextDocument, position: types.Position) -> List[types.CompletionItem]:
    """Provide completion for a symbol."""
    pass