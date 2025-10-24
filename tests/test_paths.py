"""Tests for utility path functions."""
import pytest
from unittest.mock import patch, Mock
import os
import sys

from utils.paths import resource_path


class TestResourcePath:
    """Test resource_path function."""
    
    def test_pyinstaller_path(self):
        """Test resource path in PyInstaller bundled environment."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/templates/test.html"
                
                result = resource_path("templates/test.html")
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", "templates/test.html")
                assert result == "/tmp/pyinstaller_extracted/templates/test.html"
    
    def test_relative_path_handling(self):
        """Test that relative paths are handled correctly."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/ui/test.ui"
                
                result = resource_path("ui/test.ui")
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", "ui/test.ui")
                assert result == "/tmp/pyinstaller_extracted/ui/test.ui"
    
    def test_empty_relative_path(self):
        """Test resource path with empty relative path."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/"
                
                result = resource_path("")
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", "")
                assert result == "/tmp/pyinstaller_extracted/"
    
    def test_none_relative_path(self):
        """Test resource path with None relative path."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/None"
                
                result = resource_path(None)
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", None)
                assert result == "/tmp/pyinstaller_extracted/None"
    
    def test_complex_relative_path(self):
        """Test resource path with complex relative path."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/styles/emp_hour_input_row.qss"
                
                result = resource_path("styles/emp_hour_input_row.qss")
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", "styles/emp_hour_input_row.qss")
                assert result == "/tmp/pyinstaller_extracted/styles/emp_hour_input_row.qss"
    
    def test_pyinstaller_environment_path_calculation(self):
        """Test path calculation in PyInstaller environment."""
        with patch('utils.paths.sys') as mock_sys:
            mock_sys._MEIPASS = "/tmp/pyinstaller_extracted"
            
            with patch('utils.paths.os.path.join') as mock_join:
                mock_join.return_value = "/tmp/pyinstaller_extracted/database/test.mdb"
                
                result = resource_path("database/test.mdb")
                
                mock_join.assert_called_once_with("/tmp/pyinstaller_extracted", "database/test.mdb")
                assert result == "/tmp/pyinstaller_extracted/database/test.mdb"
    
    def test_development_environment_fallback(self):
        """Test that development environment fallback works."""
        # Test the actual function behavior in development environment
        result = resource_path("templates/test.html")
        
        # Should return a path that includes the project root
        assert "templates/test.html" in result
        assert os.path.isabs(result)
    