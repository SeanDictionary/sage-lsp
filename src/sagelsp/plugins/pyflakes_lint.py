from pyflakes import api, reporter
from pyflakes import messages
import logging
from sagelsp import hookimpl

from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types
from lsprotocol.types import DiagnosticSeverity

log = logging.getLogger(__name__)


@hookimpl
def sagelsp_lint(doc: TextDocument) -> List[types.Diagnostic]:
    """Lint the document using pyflakes."""
    diagnostics: List[types.Diagnostic] = []

    source = doc.source
    # source = source.replace("\r\n", "\n").replace("\r", "\n")

    reporter = DiagnosticReporter(doc.lines)
    api.check(source, doc.uri, reporter=reporter)

    diagnostics = reporter.diagnostics
    log.info(f"pyflakes found {len(diagnostics)} issues in {doc.uri}")
    for diag in diagnostics:
        log.debug(f"- Error at line {diag.range.start.line + 1}, char {diag.range.start.character}: {diag.message}")

    return diagnostics


"""
Folowing codes are adapted from python-lsp-server
https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/plugins/pyflakes_lint.py
"""
PYFLAKES_ERROR_MESSAGES = (
    messages.UndefinedName,
    messages.UndefinedExport,
    messages.UndefinedLocal,
    messages.DuplicateArgument,
    messages.FutureFeatureNotDefined,
    messages.ReturnOutsideFunction,
    messages.YieldOutsideFunction,
    messages.ContinueOutsideLoop,
    messages.BreakOutsideLoop,
    messages.TwoStarredExpressions,
)

class DiagnosticReporter(reporter.Reporter):
    def __init__(self, lines) -> None:
        self.lines = lines
        self.diagnostics = []
    
    def syntaxError(self, filename, msg, lineno, offset, text):
        # We've seen that lineno and offset can sometimes be None
        lineno = lineno or 1
        offset = offset or 0
        # could be None if the error is due to an invalid encoding
        # see e.g. https://github.com/python-lsp/python-lsp-server/issues/429
        text = text or ""

        err_range = types.Range(
            start=types.Position(line=lineno - 1, character=offset),
            end=types.Position(line=lineno - 1, character=offset + len(text)),
        )

        diagnostic = types.Diagnostic(
            range=err_range,
            message=f"Syntax error: {msg}",
            severity=DiagnosticSeverity.Error,
            source="pyflakes",
        )
        self.diagnostics.append(diagnostic)

    def unexpectedError(self, filename, msg):
        err_range = types.Range(
            start=types.Position(line=0, character=0),
            end=types.Position(line=0, character=0),
        )

        diagnostic = types.Diagnostic(
            range=err_range,
            message=f"Unexpected error: {msg}",
            severity=DiagnosticSeverity.Error,
            source="pyflakes",
        )
        self.diagnostics.append(diagnostic)

    def flake(self, message):
        err_range = types.Range(
            start=types.Position(line=message.lineno - 1, character=message.col),
            end=types.Position(line=message.lineno - 1, character=len(self.lines[message.lineno - 1])),
        )
    
        severity = DiagnosticSeverity.Warning
        for message_type in PYFLAKES_ERROR_MESSAGES:
            if isinstance(message, message_type):
                severity = DiagnosticSeverity.Error
                break
        
        diagnostic = types.Diagnostic(
            range=err_range,
            message=message.message % message.message_args,
            severity=severity,
            source="pyflakes",
        )
        self.diagnostics.append(diagnostic)