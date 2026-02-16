from pyflakes import api, reporter
from pyflakes import messages
import logging
import ast
from sagelsp import hookimpl, SageAvaliable
from sagelsp.config import StyleConfig

from pygls.workspace import TextDocument
from typing import List, Dict
from lsprotocol import types
from lsprotocol.types import DiagnosticSeverity

if SageAvaliable:
    from sagelsp import SymbolsCache, SymbolStatus

log = logging.getLogger(__name__)
UNDEFINED_NAMES_URI: Dict[str, Dict[str, str]] = {}         # this dict is used to store sage symbols(need to import) for different uris
NO_NEED_IMPORT_NAMES_URI: Dict[str, Dict[str, str]] = {}    # this dict is used to store sage symbols(not need to import) for different uris
IMPORTED_NAMES_URI: Dict[str, Dict[str, str]] = {}          # this dict is used to store already imported sage symbols for different uris
ALL_NAMES_URI: Dict[str, Dict[str, str]] = {}               # this dict is used to store all sage symbols for different uris (including both need to import and not need to import)


def get_imported_names(source: str) -> Dict[str, str]:
    """Get already imported names from the source code.
    Returns a dict where key is the imported name and value is the full import path.
    Only handles `from sage.xxx import yyy` and `import sage.xxx.yyy` style.
    """
    from sage.repl.preparse import preparse  # type: ignore
    source_prep = preparse(source)
    imported_names = {}
    try:
        tree = ast.parse(source_prep)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Handle: from sage.xxx.yyy import zzz (or as alias)
                module = node.module
                if module and module.startswith('sage'):
                    for alias in node.names:
                        if alias.name == '*' or alias.asname:
                            continue
                        imported_names[alias.name] = module
            elif isinstance(node, ast.Import):
                # pass import sage.xxx.yyy (or as alias)
                pass

    except SyntaxError:
        # If syntax error, return empty dict
        pass
    return imported_names


@hookimpl
def sagelsp_lint(doc: TextDocument, config: StyleConfig) -> List[types.Diagnostic]:
    """Lint the document using pyflakes."""
    diagnostics: List[types.Diagnostic] = []

    source = doc.source
    if SageAvaliable and doc.uri.endswith(".sage"):
        from sage.repl.preparse import preparse  # type: ignore
        source = preparse(source)

    reporter = DiagnosticReporter(doc.lines)
    api.check(source, doc.uri, reporter=reporter)

    # Store sage symbols
    if SageAvaliable:
        UNDEFINED_NAMES_URI[doc.uri] = reporter.UNDEFINED_NAMES
        NO_NEED_IMPORT_NAMES_URI[doc.uri] = reporter.NO_NEED_IMPORT_NAMES
        IMPORTED_NAMES_URI[doc.uri] = get_imported_names(doc.source)
    else:
        UNDEFINED_NAMES_URI[doc.uri] = {}
        NO_NEED_IMPORT_NAMES_URI[doc.uri] = {}
        IMPORTED_NAMES_URI[doc.uri] = {}

    # log.debug(f"\n\n{UNDEFINED_NAMES_URI}\n\n{NO_NEED_IMPORT_NAMES_URI}\n\n{IMPORTED_NAMES_URI}\n\n")

    ALL_NAMES_URI[doc.uri] = {**UNDEFINED_NAMES_URI[doc.uri], **NO_NEED_IMPORT_NAMES_URI[doc.uri], **IMPORTED_NAMES_URI[doc.uri]}

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
        self.UNDEFINED_NAMES = {}
        self.NO_NEED_IMPORT_NAMES = {}

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

        if SageAvaliable and isinstance(message, messages.UndefinedName):
            name = message.message_args[0]
            symbol = SymbolsCache.get(name)
            if symbol.status == SymbolStatus.AUTO_IMPORT:
                self.NO_NEED_IMPORT_NAMES[name] = symbol.import_path
                return
            elif symbol.status == SymbolStatus.NEED_IMPORT:
                self.UNDEFINED_NAMES[name] = symbol.import_path

        diagnostic = types.Diagnostic(
            range=err_range,
            message=message.message % message.message_args,
            severity=severity,
            source="pyflakes",
        )
        self.diagnostics.append(diagnostic)
