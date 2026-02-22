import re
import ast
import jedi
import logging
import docstring_to_markdown

from sagelsp import SageAvaliable
from .cython_utils import (
    pyx_path,
    definition as cython_definition
)

from pygls.uris import from_fs_path
from pygls.workspace import TextDocument
from typing import List
from jedi.api import classes
from lsprotocol import types


log = logging.getLogger(__name__)


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


def _doc_prase(docstring: str) -> str:
    """
    Using docstring-to-markdown to convert docstring to markdown format for hover display.

    Supports:
    - ...
    """
    if not docstring:
        return ""
    try:
        parse_doc = docstring_to_markdown.convert(docstring)
        return parse_doc
    except docstring_to_markdown.UnknownFormatError:
        # Fallback to basic parsing if format is unknown
        doc = re.sub(r"([\\*_#[\]])", r"\\\1", docstring)
        parse_doc = doc.replace("\t", "\u00a0" * 4)\
                       .replace("\n", "\n\n")\
                       .replace("  ", "\u00a0" * 2)
        return parse_doc


def _type_hints(source: str, pos: types.Position) -> tuple[str, List[types.Location]]:
    """Preparse Sage code and extract type hints for variables. Return type name and type location"""
    line = pos.line
    character = pos.character

    type_name = "Any"
    code = ""
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if any(isinstance(node, t) for t in [ast.Import, ast.ImportFrom]):
                code += ast.unparse(node) + "\n"
            if isinstance(node, ast.AnnAssign) and node.lineno == line + 1 and node.col_offset <= character < node.col_offset + len(node.target.id):
                annotation = node.annotation
                type_name = ast.unparse(annotation)

    except Exception as e:
        log.debug(f"ast.parse failed to parse AST for type hints at line {line + 1}, char {character}: {e}")

    code += f"var: {type_name}"
    script = jedi.Script(code=code)
    try:
        inferred_names: List[classes.Name] = script.infer(line=len(code.splitlines()), column=0)
    except Exception as e:
        log.error(f"jedi.Script.infer failed for type hints at line {line + 1}, char {character}: {e}")
    
    if not inferred_names:
        from sagelsp.symbols_cache import SymbolsCache, SymbolStatus
        symbol = SymbolsCache.get(type_name)
        if symbol.status != SymbolStatus.NOT_FOUND:
            return type_name, cython_definition(pyx_path(symbol.import_path), symbol.name)


    locations = []
    for name in inferred_names:
        if name.module_name.startswith('sage.') and pyx_path(name.module_name):
            locations.extend(cython_definition(pyx_path(name.module_name), name.full_name.split('.')[-1]))

        location = types.Location(
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
            )
        )
        locations.append(location)
    return type_name, locations


if __name__ == "__main__":
    source = """\
import math
from typing import List
from sage.rings.integer_ring import IntegerRing_class
a: IntegerRing_class
"""
    _type_hints(source, types.Position(line=3, character=0))
