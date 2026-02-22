import jedi
import logging

from sagelsp import hookimpl, SageAvaliable
from .sage_utils import _sage_preparse
from .jedi_utils import _doc_prase

from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types
from jedi.api.classes import Completion


log = logging.getLogger(__name__)


_TYPE_MAP = {
    "module": types.CompletionItemKind.Module,
    "namespace": types.CompletionItemKind.Module,  # to be added in Jedi 0.18+
    "class": types.CompletionItemKind.Class,
    "instance": types.CompletionItemKind.Reference,
    "function": types.CompletionItemKind.Function,
    "param": types.CompletionItemKind.Variable,
    "path": types.CompletionItemKind.File,
    "keyword": types.CompletionItemKind.Keyword,
    "property": types.CompletionItemKind.Property,  # added in Jedi 0.18
    "statement": types.CompletionItemKind.Variable,
}


@hookimpl
def sagelsp_completion(doc: TextDocument, position: types.Position) -> List[types.CompletionItem]:
    """Provide completion for a symbol."""
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

    script = jedi.Script(code=source, path=path)  # Jedi uses 1-based indexing
    completions: List[Completion] = script.complete(line=line + 1, column=character)

    completion_items = []
    for c in completions:
        signature = c.get_signatures()
        signature_str = "\n\n".join([f"```python\n{sig.to_string()}\n```" for sig in signature])
        docstring = _doc_prase(c.docstring(raw=True))
        value = f"{signature_str}{'\n\n---\n\n' + docstring if docstring else ''}" if signature_str else docstring

        item = types.CompletionItem(
            label=c.name,
            kind=_TYPE_MAP.get(c.type, types.CompletionItemKind.Text),  # Default to Text
            documentation=types.MarkupContent(
                kind=types.MarkupKind.Markdown,
                value=value,
            ),
            insert_text=c.name,
        )
        completion_items.append(item)

    return completion_items
