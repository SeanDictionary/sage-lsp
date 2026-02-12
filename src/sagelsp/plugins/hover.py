import jedi
import docstring_to_markdown
import logging
import re

from sagelsp import hookimpl, SageAvaliable
from .cython_utils import (
    pyx_path,
    docstring as cython_docstring,
    signature as cython_signature,
)
from .sage_utils import _sage_preparse, SYMBOL

from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types
from jedi.api import classes


log = logging.getLogger(__name__)


def doc_prase(docstring: str) -> str:
    """
    Using docstring-to-markdown to convert docstring to markdown format for hover display.

    Supports:
    - ...
    """
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


@hookimpl
def sagelsp_hover(doc: TextDocument, position: types.Position) -> types.Hover:
    """Provide hover information for symbols"""
    source = doc.source
    old_position = position

    symbol_name = None
    start = end = None
    match = SYMBOL.finditer(source.splitlines()[position.line])
    for m in match:
        if m.start() <= position.character <= m.end():
            start, end = m.span()
            symbol_name = m.group()
            break

    if start is None or end is None:
        return None

    highlight_range = types.Range(
        start=types.Position(
            line=old_position.line,
            character=start,
        ),
        end=types.Position(
            line=old_position.line,
            character=end,
        ),
    )

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
        names: List[classes.Name] = script.infer(
            line=line + 1,          # Jedi is 1-based
            column=character
        )
    except Exception as e:
        log.error(f"jedi.Script.goto failed for {doc.uri} at line {line + 1}, char {character}: {e}")
        return None

    if not names:
        return types.Hover(
            contents=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value="",
            ),
            range=highlight_range,
        )

    name = names[0]
    signature = name.get_signatures()
    signature_str = "\n\n".join([f"```python\n{sig.to_string()}\n```" for sig in signature])
    docstring = name.docstring(raw=True)

    if SageAvaliable and not (signature_str and docstring):
        from sagelsp.plugins.pyflakes_lint import UNDEFINED_NAMES_URI  # type: ignore

        if doc.uri in UNDEFINED_NAMES_URI and symbol_name is not None:
            undefined_names = UNDEFINED_NAMES_URI[doc.uri]
            if symbol_name in undefined_names:
                path = pyx_path(undefined_names[symbol_name])
                signature = cython_signature(path, symbol_name)
                docstring = cython_docstring(path, symbol_name)

                return types.Hover(
                    contents=types.MarkupContent(
                        kind=types.MarkupKind.Markdown,
                        value=f"```python\n{signature}\n```\n\n---\n\n{doc_prase(docstring)}" if signature else doc_prase(docstring),
                    ),
                    range=highlight_range,
                )

    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=f"{signature_str}\n\n---\n\n{doc_prase(docstring)}" if signature_str else doc_prase(docstring),
        ),
        range=highlight_range,
    )
