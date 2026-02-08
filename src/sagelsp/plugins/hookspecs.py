from sagelsp import hookspec
from sagelsp.config import StyleConfig
from lsprotocol import types
from typing import List
from pygls.workspace import TextDocument


@hookspec
def sagelsp_lint(doc: TextDocument, config: StyleConfig) -> None:
    """Lint the document using pycodestyle."""
    pass


@hookspec
def sagelsp_format_document(doc: TextDocument, config: StyleConfig) -> List[types.TextEdit]:
    """Format the document using autopep8."""
    pass


@hookspec
def sagelsp_format_range(doc: TextDocument, start_line: int, end_line: int, config: StyleConfig) -> List[types.TextEdit]:
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
def sagelsp_hover(doc: TextDocument, position: types.Position) -> types.Hover:
    pass
