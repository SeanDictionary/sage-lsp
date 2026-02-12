import logging
import jedi

from sagelsp import hookimpl, SageAvaliable

from pygls.uris import from_fs_path
from lsprotocol import types
from pygls.workspace import TextDocument
from typing import List

from .sage_utils import _sage_preparse

log = logging.getLogger(__name__)


@hookimpl
def sagelsp_references(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide reference for a symbol."""
    # TODO: It only support reference in the same file
    source = doc.source

    # Preparse Sage code and offset position if Sage is available
    if SageAvaliable:
        source_prep, new_position = _sage_preparse(doc, position)

        if source_prep is not None and new_position is not None:
            lines_orig = doc.source.splitlines()
            source = source_prep
            position = new_position
            lines_prep = source_prep.splitlines()
        else:
            return None

    path = doc.path
    line = position.line
    character = position.character

    try:
        script = jedi.Script(code=source, path=path)
        names = script.get_references(
            line=line + 1,
            column=character,
            scope='file'
        )
    except Exception as e:
        log.error(f"jedi.Script.get_references failed for {doc.uri} at line {line + 1}, char {character}: {e}")
        return None

    locations: List[types.Location] = []

    for name in names:
        if name.module_path is None:
            continue

        # If the finally definition is in the preparsed code which is different from the original code
        # we need to map the position back to the original source code.
        if SageAvaliable and doc.path == str(name.module_path) and\
            (len(lines_orig) < name.line or lines_orig[name.line - 1] != lines_prep[name.line - 1]):
            offset = len(lines_prep) - len(lines_orig)
            def_range = types.Range(
                start=types.Position(
                    line=name.line - 1 - offset,
                    character=lines_orig[name.line - 1 - offset].find(name.name),
                ),
                end=types.Position(
                    line=name.line - 1 - offset,
                    character=lines_orig[name.line - 1 - offset].find(name.name) + len(name.name),
                ),
            )
        else:
            def_range = types.Range(
                start=types.Position(
                    line=name.line - 1,
                    character=name.column,
                ),
                end=types.Position(
                    line=name.line - 1,
                    character=name.column + len(name.name),
                ),
            )
        locations.append(
            types.Location(
                uri=from_fs_path(str(name.module_path)),
                range=def_range,
            )
        )

    return locations
