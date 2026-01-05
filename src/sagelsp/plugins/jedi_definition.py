import jedi
from jedi.api import classes
import logging
from sagelsp import hookimpl, SageAvaliable

from pygls.uris import from_fs_path
from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types

log = logging.getLogger(__name__)

MAX_JEDI_GOTO_HOPS = 100

def _resolve_definition(name: classes.Name, script: jedi.Script) -> classes.Name:
    for _ in range(MAX_JEDI_GOTO_HOPS):
        if name.is_definition():
            break

        defs = script.goto(
            line=name.line,
            column=name.column,
            follow_imports=True,
            follow_builtin_imports=True,
        )

        if len(defs) != 1:
            break
        name = defs[0]

    return name


@hookimpl
def sagelsp_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide definition for a symbol."""
    source = doc.source
    path = doc.path
    line = position.line
    character = position.character

    try:
        script = jedi.Script(code=source, path=path)
        names = script.goto(
            line=line + 1,          # Jedi is 1-based
            column=character,
            follow_imports=True,
            follow_builtin_imports=True,
        )
    except Exception as e:
        return None

    locations: List[types.Location] = []

    for name in names:
        name = _resolve_definition(name, script)

        if not name.is_definition():
            continue

        if name.module_path is None:
            continue

        locations.append(
            types.Location(
                uri=from_fs_path(str(name.module_path)),
                range=types.Range(
                    start=types.Position(
                        line=name.line - 1,
                        character=name.column,
                    ),
                    end=types.Position(
                        line=name.line - 1,
                        character=name.column + len(name.name),
                    ),
                ),
            )
        )

    return locations or None