from typing import List
from sagelsp import hookimpl
import pycodestyle
import logging
from pygls.workspace import TextDocument
from lsprotocol import types
from lsprotocol.types import DiagnosticSeverity, DiagnosticTag
from .pycodestyle_patch import pycodestyle_patch

log = logging.getLogger(__name__)

# Apply Sage syntax sugar patches to pycodestyle
pycodestyle_patch()


@hookimpl
def sagelsp_lint(doc: TextDocument) -> List[types.Diagnostic]:
    """Lint the document using pycodestyle."""
    diagnostics: List[types.Diagnostic] = []

    source = doc.source
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    lines = source.splitlines(keepends=True)

    # TODO: Support custom config
    config = {
        "exclude": None,
        "filename": None,
        "hang_closing": None,
        "ignore": None,
        "max_line_length": None,
        "indent_size": None,
        "select": None,
    }
    config = {k: v for k, v in config.items() if v}
    style = pycodestyle.StyleGuide(**config)

    checker = pycodestyle.Checker(
        filename=doc.uri,
        lines=lines,
        options=style.options,
        report=PyCodeStyleReport(style.options),
    )
    checker.check_all()
    diagnostics = checker.report.diagnostics
    log.info(f"pycodestyle found {len(diagnostics)} issues in {doc.uri}")
    for diag in diagnostics:
        log.debug(f"- {diag.code} at line {diag.range.start.line + 1}, char {diag.range.start.character}: {diag.message}")

    return diagnostics

# Patch for sagemath


"""
Folowing codes are adapted from python-lsp-server
https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/plugins/pycodestyle_lint.py
"""
class PyCodeStyleReport(pycodestyle.BaseReport):
    def __init__(self, options) -> None:
        self.diagnostics = []
        super().__init__(options=options)

    def error(self, line_number, offset, text, check):
        code = text[:4]
        if self._ignore_code(code):
            return

        # Don't care about expected errors or warnings
        if code in self.expected:
            return

        # PyCodeStyle will sometimes give you an error the line after the end of the file
        #   e.g. no newline at end of file
        # In that case, the end offset should just be some number ~100
        # (because why not? There's nothing to underline anyways)
        err_range = {
            "start": {"line": line_number - 1, "character": offset},
            "end": {
                # FIXME: It's a little naiive to mark until the end of the line, can we not easily do better?
                "line": line_number - 1,
                "character": 100
                if line_number > len(self.lines)
                else len(self.lines[line_number - 1]),
            },
        }
        diagnostic = types.Diagnostic(
            message=text,
            severity=_get_severity(code),
            code=code,
            source="pycodestyle",
            range=types.Range(
                start=types.Position(line=err_range["start"]["line"], character=err_range["start"]["character"]),
                end=types.Position(line=err_range["end"]["line"], character=err_range["end"]["character"]),
            )
        )
        if code.startswith("W6"):
            diagnostic.tags = [DiagnosticTag.Deprecated]
        self.diagnostics.append(diagnostic)

def _get_severity(code):
    # Are style errors ever really errors?
    if code[0] == "E" or code[0] == "W":
        return DiagnosticSeverity.Warning
    # If no severity is specified, why wouldn't this be informational only?
    return DiagnosticSeverity.Information