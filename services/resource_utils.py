"""Resource utilities for PyInstaller compatibility.

This module provides utilities for handling resource files (UI, templates, styles)
that need to work both in development and when packaged as a Windows executable.
"""
import os
import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to the project root
        
    Returns:
        Absolute path to the resource file
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)
