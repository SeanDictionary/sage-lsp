import logging
import re

from pygls.workspace import TextDocument
from lsprotocol import types

log = logging.getLogger(__name__)


SYMBOL = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


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
