import jedi
from jedi.api import classes
import re
import logging

from sagelsp import hookimpl, SageAvaliable
from .cython_utils import definition as cython_definition

from pygls.uris import from_fs_path
from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types

log = logging.getLogger(__name__)

MAX_JEDI_GOTO_HOPS = 100
SYMBOL = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


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


def _sage_add_import_path(doc: TextDocument):
    """Add import path for Sage symbols to help jedi definition resolution"""
    from sagelsp.plugins.pyflakes_lint import UNDEFINED_NAMES_URI

    import_path_list = []
    if doc.uri not in UNDEFINED_NAMES_URI:
        # In theory this should not happen
        log.error(f"No sage symbols found for {doc.uri} in UNDEFINED_NAME_URI")
        return "", 0

    undefined_names = UNDEFINED_NAMES_URI[doc.uri]
    log.debug(f"Detected sage symbols in {doc.uri}: {undefined_names}")
    for name, import_path in undefined_names.items():
        import_path_list.append(f"from {import_path} import {name}\n")
    
    return "".join(import_path_list), len(import_path_list)


def _sage_preparse(doc: TextDocument, position: types.Position):
    """Trace column offest for sage-preparse code"""
    from sage.repl.preparse import preparse  # type: ignore

    source_orig = doc.source
    source_prep = preparse(source_orig)

    # Add import paths for undefined sage symbols
    # And offset the line number accordingly
    import_path_text, import_num = _sage_add_import_path(doc)
    source_prep = import_path_text + source_prep
    pos_prep_line = position.line + import_num

    lines_orig = source_orig.splitlines()
    line_orig = lines_orig[position.line]

    lines_prep = source_prep.splitlines()
    line_prep = lines_prep[pos_prep_line]

    if line_orig != line_prep:
        match = SYMBOL.finditer(line_orig)
        for m in match:
            if m.start() <= position.character <= m.end():
                symbol_name = m.group()
                break
        else:
            return None, None

        # FIXME: it can't handel multiple same symbols in one line
        new_character = line_prep.find(symbol_name)
        new_position = types.Position(
            line=pos_prep_line,
            character=new_character,
        )

        return source_prep, new_position
    else:
        new_position = types.Position(
            line=pos_prep_line,
            character=position.character,
        )

        return source_prep, new_position


def pyx_definition(symbol_name: str, import_path: str) -> List[types.Location]:
    """Provide definition for a symbol in .pyx file"""
    from sage.env import SAGE_LIB

    log.debug(f"Finding definition for symbol '{symbol_name}' from '{import_path}'")
    pyx_path = SAGE_LIB + "/" + import_path.replace(".", "/") + ".pyx"

    return cython_definition(pyx_path, symbol_name)
    


@hookimpl
def sagelsp_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide definition for a symbol."""
    # ?OPTIMIZE: If it need a delay when user is typing?
    # TODO: Jedi can't follow file like .pyx (ps. now i'm working for it
    source = doc.source

    # Preparse Sage code and offset position if Sage is available
    if SageAvaliable:
        source_prep, new_position = _sage_preparse(doc, position)

        if source_prep is not None and new_position is not None:
            source = source_prep
            position = new_position
            lines_orig = source.splitlines()
            lines_prep = source_prep.splitlines()
        else:
            return None

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
        return None

    locations: List[types.Location] = []

    for name in names:
        name = _resolve_definition(name, script)

        if not name.is_definition():
            continue

        if name.module_path is None:
            continue

        # If the finally definition is in the preparsed code which is different from the original code,
        # we need to map the position back to the original source code.
        if SageAvaliable and doc.path == str(name.module_path) and lines_orig[name.line - 1] != lines_prep[name.line - 1]:
            def_range = types.Range(
                start=types.Position(
                    line=name.line - 1,
                    character=lines_orig[name.line - 1].find(name.name),
                ),
                end=types.Position(
                    line=name.line - 1,
                    character=lines_orig[name.line - 1].find(name.name) + len(name.name),
                ),
            )
        else:
            def_range = types.Range(
                start=types.Position(line=name.line - 1, character=name.column),
                end=types.Position(line=name.line - 1, character=name.column + len(name.name),),
            )
        locations.append(
            types.Location(
                uri=from_fs_path(str(name.module_path)),
                range=def_range,
            )
        )

    if SageAvaliable:
        match = SYMBOL.finditer(lines_orig[position.line])
        for m in match:
            if m.start() <= position.character <= m.end():
                symbol_name = m.group()
                break
        
        from sagelsp.plugins.pyflakes_lint import UNDEFINED_NAMES_URI # type: ignore

        if doc.uri in UNDEFINED_NAMES_URI:
            undefined_names = UNDEFINED_NAMES_URI[doc.uri]
            if symbol_name in undefined_names:
                locations.extend(pyx_definition(symbol_name, undefined_names[symbol_name]))


    if locations:
        log.info(f"jedi found {len(locations)} definitions for symbol at line {line + 1}, char {character} in {doc.uri}")
        for loc in locations:
            log.debug(f"- Definition at {loc.uri} line {loc.range.start.line + 1}, char {loc.range.start.character}")
        return locations
        


@hookimpl
def sagelsp_type_definition(doc: TextDocument, position: types.Position) -> List[types.Location]:
    """Provide type definition for a symbol."""
    # TODO: It may need type inference for Sage code, now using definition for simplicity
    return sagelsp_definition(doc, position)

