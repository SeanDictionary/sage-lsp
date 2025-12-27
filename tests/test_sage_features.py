"""
Basic tests for the SageMath language server.
"""

import pytest
from sage_lsp.sage_features import SageFeatures


class TestSageFeatures:
    """Test SageMath-specific features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sage_features = SageFeatures()
    
    def test_initialization(self):
        """Test that SageFeatures initializes correctly."""
        assert self.sage_features is not None
    
    def test_get_completions_basic(self):
        """Test basic completion functionality."""
        source = "x = 1\ny = "
        completions = self.sage_features.get_completions(source, 1, 4)
        assert isinstance(completions, list)
    
    def test_get_completions_with_prefix(self):
        """Test completions with a prefix."""
        source = "def"
        completions = self.sage_features.get_completions(source, 0, 3)
        assert isinstance(completions, list)
        # Should include 'def' keyword
        labels = [c.label for c in completions]
        assert 'def' in labels
    
    def test_get_word_at_position(self):
        """Test word extraction at a position."""
        line = "hello world"
        word = self.sage_features._get_word_at_position(line, 3)
        assert word == "hello"
        
        word = self.sage_features._get_word_at_position(line, 8)
        assert word == "world"
    
    def test_get_hover_no_match(self):
        """Test hover with no matching symbol."""
        source = "x = 1"
        hover = self.sage_features.get_hover(source, 0, 0)
        # May return None or a value depending on SageMath availability
        assert hover is None or isinstance(hover, str)
    
    def test_python_completions(self):
        """Test that Python keywords are completed."""
        completions = self.sage_features._get_python_completions("de")
        labels = [c.label for c in completions]
        assert 'def' in labels
    
    def test_empty_source(self):
        """Test handling of empty source."""
        completions = self.sage_features.get_completions("", 0, 0)
        assert isinstance(completions, list)
    
    def test_out_of_bounds_line(self):
        """Test handling of out-of-bounds line number."""
        source = "x = 1"
        completions = self.sage_features.get_completions(source, 10, 0)
        assert completions == []
