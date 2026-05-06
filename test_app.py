#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the application modules can be imported correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    import tkinter as tk
    print("[OK] tkinter imported")
except ImportError as e:
    print(f"[FAIL] tkinter import failed: {e}")

try:
    import json
    print("[OK] json imported")
except ImportError as e:
    print(f"[FAIL] json import failed: {e}")

try:
    from pathlib import Path
    print("[OK] pathlib imported")
except ImportError as e:
    print(f"[FAIL] pathlib import failed: {e}")

# Test JSON files
print("\nTesting JSON files...")
try:
    with open("reglament.json", 'r', encoding='utf-8') as f:
        reglament = json.load(f)
    print(f"[OK] reglament.json loaded ({len(reglament.get('processes', []))} processes)")
except Exception as e:
    print(f"[FAIL] reglament.json failed: {e}")

try:
    with open("test_scenarios.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    scenarios = data.get("test_scenarios", [])
    print(f"[OK] test_scenarios.json loaded ({len(scenarios)} scenarios)")
except Exception as e:
    print(f"[FAIL] test_scenarios.json failed: {e}")

# Test module imports
print("\nTesting module imports...")
try:
    from gui import TestApp
    print("[OK] gui module imported")
except Exception as e:
    print(f"[FAIL] gui module failed: {e}")

try:
    from mode_selection import ModeSelectionWindow
    print("[OK] mode_selection module imported")
except Exception as e:
    print(f"[FAIL] mode_selection module failed: {e}")

try:
    from study_mode import StudyModeWindow
    print("[OK] study_mode module imported")
except Exception as e:
    print(f"[FAIL] study_mode module failed: {e}")

try:
    from test_mode import TestModeWindow
    print("[OK] test_mode module imported")
except Exception as e:
    print(f"[FAIL] test_mode module failed: {e}")

try:
    from results_viewer import ResultsViewerWindow
    print("[OK] results_viewer module imported")
except Exception as e:
    print(f"[FAIL] results_viewer module failed: {e}")

try:
    from pdf_generator import generate_pdf
    print("[OK] pdf_generator module imported")
except ImportError as e:
    print(f"[WARN] pdf_generator module failed (reportlab not installed?): {e}")
except Exception as e:
    print(f"[FAIL] pdf_generator module failed: {e}")

print("\nDone!")
