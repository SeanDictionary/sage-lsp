from sagelsp import hookspec
from pygls.workspace import TextDocument

@hookspec
def sagelsp_lint(doc: TextDocument):
    """Lint the document using pycodestyle."""
    pass

