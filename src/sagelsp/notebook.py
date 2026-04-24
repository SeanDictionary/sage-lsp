from dataclasses import dataclass
from sagelsp import LANGUAGE_ID
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument
from lsprotocol import types
from typing import Dict, List, Optional, Tuple


@dataclass
class CellLineMapping:
    cell_uri: str
    start_line: int
    end_line: int

    def contains_line(self, line: int) -> bool:
        return self.start_line <= line <= self.end_line


class JupyterNotebook:
    def __init__(self, ls: LanguageServer, nb: types.NotebookDocument):
        self.ls = ls
        self.nb = nb
        self.notebook_type = nb.notebook_type
        self.version = nb.version
        self.cells = nb.cells
        self.uri = nb.uri
        self._get_cell_sources()
        self._build_virtual_document()
    
    def _get_cell_sources(self) -> Dict[str, TextDocument]:
        """Get the source code of each cell by its document URI."""
        cell_sources = {}
        for cell in self.cells:
            if cell.kind == types.NotebookCellKind.Code:
                doc = self.ls.workspace.get_text_document(cell.document)
                cell_sources[cell.document] = doc
        self.cell_sources = cell_sources

    def _build_virtual_document(self) -> Tuple[TextDocument, List[CellLineMapping]]:
        """Build a virtual document by concatenating all code cells."""
        virtual_lines: List[str] = []
        cell_mappings: List[CellLineMapping] = []
        for uri, doc in self.cell_sources.items():
            if doc.language_id != LANGUAGE_ID:
                continue

            source = doc.source
            source_lines = source.splitlines() or [""]
            start_line = len(virtual_lines)
            virtual_lines.extend(source_lines)
            end_line = len(virtual_lines) - 1

            cell_mappings.append(
                CellLineMapping(
                    cell_uri=uri,
                    start_line=start_line,
                    end_line=end_line,
                )
            )

        self.virtual_document = TextDocument(
            uri=self.uri,
            source="\n".join(virtual_lines) + "\n",
            version=self.version,
            language_id=LANGUAGE_ID,
        )
        self.cell_mappings = cell_mappings

    def map_position(self, position: types.Position) -> Optional[Tuple[str, types.Position]]:
        """Map a virtual document position back to a notebook cell position."""
        for mapping in self.cell_mappings:
            if mapping.contains_line(position.line):
                return (
                    mapping.cell_uri,
                    types.Position(
                        line=position.line - mapping.start_line,
                        character=position.character,
                    ),
                )
        return None

    def map_range(self, virtual_range: types.Range) -> Optional[Tuple[str, types.Range]]:
        """Map a virtual document range back to a notebook cell range."""
        mapped_start = self.map_position(virtual_range.start)
        mapped_end = self.map_position(virtual_range.end)
        if mapped_start is None or mapped_end is None:
            return None

        cell_uri_start, start = mapped_start
        cell_uri_end, end = mapped_end

        # In theory, it would be True all the time
        if cell_uri_end != cell_uri_start:
            return None

        return (
            cell_uri_start,
            types.Range(start=start, end=end),
        )

    def map_diagnostic(self, virtual_diagnostic: types.Diagnostic) -> Optional[Tuple[str, types.Diagnostic]]:
        """Map a single diagnostic from the virtual document back to a notebook cell."""
        mapped_range = self.map_range(virtual_diagnostic.range)
        if mapped_range is None:
            return None

        cell_uri, cell_range = mapped_range
        cell_diagnostic = virtual_diagnostic
        cell_diagnostic.range = cell_range
        return cell_uri, cell_diagnostic

    def map_diagnostics(self, virtual_diagnostics: List[types.Diagnostic]) -> Dict[str, List[types.Diagnostic]]:
        """Map diagnostics from the virtual document back to the original notebook cells."""
        diagnostics_by_cell: Dict[str, List[types.Diagnostic]] = {
            mapping.cell_uri: [] for mapping in self.cell_mappings
        }

        for diagnostic in virtual_diagnostics:
            mapped = self.map_diagnostic(diagnostic)
            if mapped is None:
                continue

            cell_uri, cell_diagnostic = mapped
            diagnostics_by_cell[cell_uri].append(cell_diagnostic)

        return diagnostics_by_cell

    def merge_diagnostics(self, *diagnostics_dicts: Dict[str, List[types.Diagnostic]]) -> Dict[str, List[types.Diagnostic]]:
        """Merge diagnostics from multiple sources (e.g., semantic and style) for each cell."""
        merged: Dict[str, List[types.Diagnostic]] = {}
        for diagnostics_dict in diagnostics_dicts:
            for cell_uri, diags in diagnostics_dict.items():
                if cell_uri not in merged:
                    merged[cell_uri] = []
                merged[cell_uri].extend(diags)
        return merged