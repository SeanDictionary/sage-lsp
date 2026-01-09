import autopep8
import logging
from sagelsp import hookimpl
from sagelsp.config import StyleConfig

from pygls.workspace import TextDocument
from typing import List
from lsprotocol import types

log = logging.getLogger(__name__)

@hookimpl
def sagelsp_format_document(doc: TextDocument, config: StyleConfig) -> List[types.TextEdit]:
    """Format the document using autopep8."""
    return _format(doc, config)


@hookimpl
def sagelsp_format_range(doc: TextDocument, start_line: int, end_line: int, config: StyleConfig) -> List[types.TextEdit]:
    """Format a range of the document using autopep8."""
    return _format(doc, config, line_range=[start_line, end_line])


def _format(doc: TextDocument, config: StyleConfig, line_range: List[int] = None) -> List[types.TextEdit]:
    if line_range:
        log.info(f"Formatting document {doc.uri} from line {line_range[0]} to {line_range[1]} with autopep8")
    else:
        log.info(f"Formatting document {doc.uri} with autopep8")
    source = doc.source
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    
    # Load configuration from global and project sources
    config = config.get_autopep8_config()

    new_source = autopep8.fix_code(source, options=config)

    if new_source == source:
        log.info(f"No formatting changes needed for document {doc.uri}")
        return []
    else:
        log.info(f"Document {doc.uri} formatted with autopep8")
        return [types.TextEdit(
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=len(doc.lines), character=0)
            ),
            new_text=new_source
        )]
