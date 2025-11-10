"""
Tests for text utils fallback functionality (when unidecode is not available)
"""

import sys
from unittest.mock import patch


class TestTextUtilsFallback:
    """Test the fallback implementation when unidecode is not available"""

    def test_fallback_implementation(self):
        """Test that the fallback implementation works when unidecode is not available"""
        # Mock the import to raise ImportError
        with patch.dict(sys.modules, {"unidecode": None}):
            # Force re-import of the module
            import importlib
            from catalogmx.utils import text
            
            # Reload the module to trigger the except block
            importlib.reload(text)
            
            # Now test the fallback implementation
            result = text.normalize_text("México")
            assert result == "MEXICO"
            
            result = text.normalize_text("São Paulo")
            assert result == "SAO PAULO"
            
            result = text.normalize_text("Michoacán")
            assert result == "MICHOACAN"

    def test_fallback_normalize_for_search(self):
        """Test normalize_for_search with fallback"""
        with patch.dict(sys.modules, {"unidecode": None}):
            import importlib
            from catalogmx.utils import text
            
            importlib.reload(text)
            
            result = text.normalize_for_search("Jalisco")
            assert result == "JALISCO"

