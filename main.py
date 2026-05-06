#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop application for studying and testing knowledge of deal regulations.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Ensure the script directory is in the path
sys.path.insert(0, str(Path(__file__).parent))

from gui import TestApp


def main():
    """Main entry point for the application."""
    app = TestApp()
    app.run()


if __name__ == "__main__":
    main()
