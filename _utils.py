# -*- coding: utf-8 -*-
"""
Utility functions for the application.
Handles path resolution for both development and PyInstaller bundled modes.
"""

import sys
from pathlib import Path


def get_base_path():
    """
    Get the base path for data files (read-only).
    Works both in development (script path) and PyInstaller bundle (_MEIPASS path).
    """
    if getattr(sys, '_MEIPASS', None):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_output_path():
    """
    Get the path for output files (writable).
    Returns the directory next to the executable (bundled) or script (development).
    """
    if getattr(sys, '_MEIPASS', None):
        # Running from PyInstaller bundle - save next to the exe
        return Path(sys.executable).parent
    return Path(__file__).parent
