import jedi
from jedi.api import classes
import re
import logging

from sagelsp import hookimpl, SageAvaliable
from .cython_utils import (
    pyx_path,
    definition as cython_definition
)
from .sage_utils import _sage_preparse, SYMBOL

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


def _to_location(name: classes.Name, doc: TextDocument, lines_orig: List[str] = None, lines_prep: List[str] = None) -> types.Location | None:
    if name.module_path is None or name.line is None or name.column is None:
        return None

    if (
        SageAvaliable
        and lines_orig is not None
        and lines_prep is not None
        and doc.path == str(name.module_path)
        and (len(lines_orig) < name.line or lines_orig[name.line - 1] != lines_prep[name.line - 1])
    ):
        offset = len(lines_prep) - len(lines_orig)
        mapped_line = name.line - 1 - offset
        if mapped_line < 0 or mapped_line >= len(lines_orig):
            return None

        start_char = lines_orig[mapped_line].find(name.name)
        if start_char < 0:
            start_char = 0

        def_range = types.Range(
            start=types.Position(
                line=mapped_line,
                character=start_char,
            ),
            end=types.Position(
                line=mapped_line,
                character=start_char + len(name.name),
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

    return types.Location(
        uri=from_fs_path(str(name.module_path)),
        range=def_range,
    )


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

        from sagelsp.plugins.pyflakes_lint import UNDEFINED_NAMES_URI  # type: ignore

        if doc.uri in UNDEFINED_NAMES_URI and symbol_name is not None:
            undefined_names = UNDEFINED_NAMES_URI[doc.uri]
            if symbol_name in undefined_names:
                locations.extend(cython_definition(pyx_path(undefined_names[symbol_name]), symbol_name))

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
        inferred_names = script.infer(
            line=line + 1,
            column=character,
        )
    except Exception as e:
        log.error(f"jedi.Script.infer failed for {doc.uri} at line {line + 1}, char {character}: {e}")
        return []

    locations: List[types.Location] = []
    seen = set()

    for inferred in inferred_names:
        resolved = _resolve_definition(inferred, script)
        location = _to_location(resolved, doc, lines_orig if SageAvaliable else None, lines_prep if SageAvaliable else None)
        if location is None:
            continue

        key = (location.uri, location.range.start.line, location.range.start.character)
        if key in seen:
            continue
        seen.add(key)
        locations.append(location)

    if locations:
        log.info(f"jedi found {len(locations)} type definitions for symbol at line {line + 1}, char {character} in {doc.uri}")
        for loc in locations:
            log.debug(f"- Type definition at {loc.uri} line {loc.range.start.line + 1}, char {loc.range.start.character}")

    return locations
