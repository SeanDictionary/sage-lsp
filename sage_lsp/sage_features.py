"""
SageMath-specific features for the language server.

This module provides SageMath-specific functionality including
completion, hover information, and other IDE features.
"""

import logging
import re
from typing import List, Optional

from lsprotocol.types import CompletionItem, CompletionItemKind

logger = logging.getLogger(__name__)


class SageFeatures:
    """
    Provides SageMath-specific language features.
    
    This class handles completion, hover, and other features
    specific to SageMath syntax and libraries.
    """
    
    def __init__(self):
        """Initialize SageMath features."""
        self._sage_available = False
        self._initialize_sage()
        
    def _initialize_sage(self):
        """Try to initialize SageMath environment."""
        try:
            # Try to import sage - this will work if SageMath is installed
            import sage.all
            self._sage_available = True
            logger.info("SageMath environment initialized successfully")
        except ImportError:
            logger.warning(
                "SageMath not available. "
                "Language server will provide basic Python support only."
            )
            self._sage_available = False
    
    def get_completions(
        self,
        source: str,
        line: int,
        character: int
    ) -> List[CompletionItem]:
        """
        Get completion suggestions for the given position.
        
        Args:
            source: Full source code of the document
            line: Line number (0-based)
            character: Character position in the line (0-based)
            
        Returns:
            List of completion items
        """
        try:
            lines = source.split('\n')
            if line >= len(lines):
                return []
            
            current_line = lines[line][:character]
            
            # Extract the word being typed
            word_match = re.search(r'(\w+)$', current_line)
            if not word_match:
                return []
            
            prefix = word_match.group(1)
            
            completions = []
            
            # Add SageMath-specific completions if available
            if self._sage_available:
                completions.extend(self._get_sage_completions(prefix, source))
            
            # Add basic Python completions
            completions.extend(self._get_python_completions(prefix))
            
            return completions
            
        except Exception as e:
            logger.error(f"Error getting completions: {e}")
            return []
    
    def _get_sage_completions(self, prefix: str, source: str) -> List[CompletionItem]:
        """
        Get SageMath-specific completions.
        
        Args:
            prefix: The prefix to complete
            source: Full source code for context
            
        Returns:
            List of SageMath-specific completion items
        """
        completions = []
        
        try:
            import sage.all as sage
            
            # Get completions from sage namespace
            sage_namespace = dir(sage)
            
            for name in sage_namespace:
                if name.startswith(prefix) and not name.startswith('_'):
                    try:
                        obj = getattr(sage, name)
                        kind = self._get_completion_kind(obj)
                        completions.append(
                            CompletionItem(
                                label=name,
                                kind=kind,
                                detail=f"SageMath: {type(obj).__name__}",
                                documentation=self._get_short_doc(obj)
                            )
                        )
                    except Exception:
                        # Skip items that can't be accessed
                        continue
                        
        except ImportError:
            pass
        
        return completions
    
    def _get_python_completions(self, prefix: str) -> List[CompletionItem]:
        """
        Get basic Python completions.
        
        Args:
            prefix: The prefix to complete
            
        Returns:
            List of Python completion items
        """
        # Common Python keywords and built-ins
        python_keywords = [
            'def', 'class', 'if', 'elif', 'else', 'for', 'while',
            'return', 'import', 'from', 'as', 'try', 'except',
            'finally', 'with', 'lambda', 'yield', 'pass', 'break',
            'continue', 'and', 'or', 'not', 'in', 'is'
        ]
        
        completions = []
        for keyword in python_keywords:
            if keyword.startswith(prefix):
                completions.append(
                    CompletionItem(
                        label=keyword,
                        kind=CompletionItemKind.Keyword,
                        detail="Python keyword"
                    )
                )
        
        return completions
    
    def get_hover(
        self,
        source: str,
        line: int,
        character: int
    ) -> Optional[str]:
        """
        Get hover information for the symbol at the given position.
        
        Args:
            source: Full source code of the document
            line: Line number (0-based)
            character: Character position in the line (0-based)
            
        Returns:
            Hover text in Markdown format, or None
        """
        try:
            lines = source.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            
            # Find the word at the cursor position
            word = self._get_word_at_position(current_line, character)
            if not word:
                return None
            
            # Try to get documentation from SageMath
            if self._sage_available:
                sage_doc = self._get_sage_documentation(word)
                if sage_doc:
                    return sage_doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting hover info: {e}")
            return None
    
    def _get_word_at_position(self, line: str, character: int) -> Optional[str]:
        """
        Extract the word at the given character position.
        
        Args:
            line: The line of text
            character: Character position in the line
            
        Returns:
            The word at the position, or None
        """
        if character > len(line):
            character = len(line)
        
        # Find word boundaries
        start = character
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        
        end = character
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        word = line[start:end]
        return word if word else None
    
    def _get_sage_documentation(self, symbol: str) -> Optional[str]:
        """
        Get documentation for a SageMath symbol.
        
        Args:
            symbol: The symbol to document
            
        Returns:
            Documentation in Markdown format, or None
        """
        try:
            import sage.all as sage
            
            if hasattr(sage, symbol):
                obj = getattr(sage, symbol)
                doc = self._format_documentation(symbol, obj)
                return doc
                
        except Exception as e:
            logger.debug(f"Could not get documentation for {symbol}: {e}")
        
        return None
    
    def _format_documentation(self, name: str, obj) -> str:
        """
        Format object documentation as Markdown.
        
        Args:
            name: Name of the object
            obj: The object to document
            
        Returns:
            Formatted documentation
        """
        doc_parts = [f"## {name}"]
        
        # Add type information
        obj_type = type(obj).__name__
        doc_parts.append(f"\n**Type:** `{obj_type}`")
        
        # Add docstring if available
        if hasattr(obj, '__doc__') and obj.__doc__:
            docstring = obj.__doc__.strip()
            # Limit docstring length for hover
            if len(docstring) > 500:
                docstring = docstring[:500] + "..."
            doc_parts.append(f"\n\n{docstring}")
        
        return "\n".join(doc_parts)
    
    def _get_short_doc(self, obj) -> Optional[str]:
        """
        Get a short documentation string for an object.
        
        Args:
            obj: The object to document
            
        Returns:
            Short documentation string
        """
        if hasattr(obj, '__doc__') and obj.__doc__:
            doc = obj.__doc__.strip()
            # Get first line only
            first_line = doc.split('\n')[0]
            if len(first_line) > 100:
                first_line = first_line[:100] + "..."
            return first_line
        return None
    
    def _get_completion_kind(self, obj) -> CompletionItemKind:
        """
        Determine the appropriate completion kind for an object.
        
        Args:
            obj: The object to classify
            
        Returns:
            Appropriate CompletionItemKind
        """
        if callable(obj):
            if isinstance(obj, type):
                return CompletionItemKind.Class
            return CompletionItemKind.Function
        return CompletionItemKind.Variable
