import pytest
import os
import sys
from unittest.mock import patch

from services.resource_utils import resource_path


class TestResourcePath:

    def test_resource_path_development_mode(self):
        """Test resource path resolution in development mode."""
        with patch.dict(sys.modules, {'sys': sys}):
            if hasattr(sys, '_MEIPASS'):
                delattr(sys, '_MEIPASS')
            
            result = resource_path("ui/test.ui")
            expected = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "ui/test.ui"
            )
            assert result == expected

    def test_resource_path_pyinstaller_mode(self):
        """Test resource path resolution in PyInstaller bundled mode."""
        with patch.dict(sys.modules, {'sys': sys}):
            sys._MEIPASS = "/tmp/pyinstaller_bundle"
            result = resource_path("ui/test.ui")
            expected = os.path.join("/tmp/pyinstaller_bundle", "ui/test.ui")
            assert result == expected
            delattr(sys, '_MEIPASS')

    def test_resource_path_exception_handling(self):
        """Test that resource_path handles _MEIPASS access exceptions gracefully."""
        with patch.dict(sys.modules, {'sys': sys}):
            class MockSys:
                def __getattr__(self, name):
                    if name == '_MEIPASS':
                        raise Exception("Access denied")
                    return getattr(sys, name)
            
            with patch('services.resource_utils.sys', MockSys()):
                result = resource_path("ui/test.ui")
                expected = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "ui/test.ui"
                )
                assert result == expected