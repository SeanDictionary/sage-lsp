import jedi
from jedi.api import classes
import logging

from sagelsp import hookimpl, SageAvaliable
from .cython_utils import (
    pyx_path,
    definition as cython_definition
)
from .sage_utils import _sage_preparse, SYMBOL
from .jedi_utils import _to_location, _type_hints

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
    # ?OPTIMIZE: If it need a delay when user is typing?
    # // TODO: Jedi can't follow file like .pyx (ps. now it can
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
            return []

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
        log.error(f"jedi.Script.goto failed for {doc.uri} at line {line + 1}, char {character}: {e}")
        return []

    locations: List[types.Location] = []

    for name in names:
        name = _resolve_definition(name, script)

        if not name.is_definition():
            continue

        location = _to_location(name, doc, lines_orig if SageAvaliable else None, lines_prep if SageAvaliable else None)
        if location is not None:
            locations.append(location)

    if SageAvaliable:
        symbol_name = None
        match = SYMBOL.finditer(lines_prep[position.line])
        for m in match:
            if m.start() <= position.character <= m.end():
                symbol_name = m.group()
                break

        from sagelsp.plugins.pyflakes_lint import ALL_NAMES_URI  # type: ignore

        if doc.uri in ALL_NAMES_URI and symbol_name is not None:
            undefined_names = ALL_NAMES_URI[doc.uri]
            if symbol_name in undefined_names:
                path = pyx_path(undefined_names[symbol_name])
                if path:
                    locations.extend(cython_definition(path, symbol_name))

    if locations:
        log.info(f"jedi found {len(locations)} definitions for symbol at line {line + 1}, char {character} in {doc.uri}")
        for loc in locations:
            log.debug(f"- Definition at {loc.uri} line {loc.range.start.line + 1}, char {loc.range.start.character}")
    
    return locations


@hookimpl
def sagelsp_type_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide type definition for a symbol."""
    source = doc.source

    if SageAvaliable:
        source_prep, new_position = _sage_preparse(doc, position)

        if source_prep is not None and new_position is not None:
            lines_orig = doc.source.splitlines()
            source = source_prep
            position = new_position
            lines_prep = source_prep.splitlines()
        else:
            return []

    path = doc.path
    line = position.line
    character = position.character

    try:
        script = jedi.Script(code=source, path=path)
        inferred_names: List[classes.Name] = script.infer(
            line=line + 1,
            column=character,
        )
    except Exception as e:
        log.error(f"jedi.Script.infer failed for {doc.uri} at line {line + 1}, char {character}: {e}")
        return []

    if not inferred_names:
        _, locations = _type_hints(source, position)
        return locations

    locations: List[types.Location] = []

    for name in inferred_names:
        # Special handling for .pyi in Sage 10.8+
        if name.module_name.startswith('sage.') and pyx_path(name.module_name):
            locations.extend(cython_definition(pyx_path(name.module_name), name.full_name.split('.')[-1]))

        location = _to_location(name, doc, lines_orig if SageAvaliable else None, lines_prep if SageAvaliable else None)
        if location is not None:
            locations.append(location)

    if locations:
        log.info(f"jedi found {len(locations)} type definitions for symbol at line {line + 1}, char {character} in {doc.uri}")
        for loc in locations:
            log.debug(f"- Type definition at {loc.uri} line {loc.range.start.line + 1}, char {loc.range.start.character}")

    return locations
