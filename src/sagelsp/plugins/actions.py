import logging

from sagelsp.symbols_cache import SymbolsCache, SymbolStatus

from sagelsp import hookimpl
from pygls.workspace import TextDocument
from lsprotocol import types
from typing import List

log = logging.getLogger(__name__)


def _edit_UndefinedName(uri: str, diagnostic: types.Diagnostic) -> tuple[str, types.WorkspaceEdit]:
    """Generate code action for UndefinedName diagnostic, which is common for Sage users who forget to import a symbol from Sage."""
    # ! Only for Sage
    name = diagnostic.message.split("'")[1]
    symbol = SymbolsCache.get(name)
    if symbol and symbol.status == SymbolStatus.NEED_IMPORT:
        import_path = symbol.import_path
        text = f"from {import_path} import {name}"
        edit = types.TextEdit(
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=0, character=0),
            ),
            new_text=f"from {import_path} import {name}\n",
        )
        return text, types.WorkspaceEdit(
            changes={
                uri: [edit]
            }
        )


@hookimpl
def sagelsp_code_actions(uri: str, diagnostics: List[types.Diagnostic]) -> List[types.CodeAction]:
    """Provide code actions for a given range."""
    actions = []
    for diagnostic in diagnostics:
        if diagnostic.code == "UndefinedName":
            text, edit = _edit_UndefinedName(uri, diagnostic)
            if edit:
                actions.append(types.CodeAction(
                    title=text,
                    kind=types.CodeActionKind.QuickFix,
                    diagnostics=[diagnostic],
                    edit=edit,
                ))

    return actions
