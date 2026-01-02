from sagelsp import hookspec
from lsprotocol import types
from typing import List
from pygls.workspace import TextDocument

@hookspec
def sagelsp_lint(doc: TextDocument):
    """Lint the document using pycodestyle."""
    pass

@hookspec
def sagelsp_format_document(doc: TextDocument) -> List[types.TextEdit]:
    """Format the document using pycodestyle."""
    pass

@hookspec
def sagelsp_format_range(doc: TextDocument, start_line: int, end_line: int) -> List[types.TextEdit]:
    """Format a range of the document using autopep8."""
    pass