#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple launcher that checks dependencies and starts the application.
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are available."""
    missing = []

    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (usually comes with Python)")

    try:
        import reportlab
        print("✓ reportlab is available (PDF export enabled)")
    except ImportError:
        print("⚠ reportlab not found (PDF export will be disabled)")
        print("  Install with: pip install reportlab")

    if missing:
        print("\n❌ Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        return False

    return True


def main():
    """Main launcher function."""
    print("=" * 50)
    print("  Desktop Test Application")
    print("  Testing System for Deal Regulations")
    print("=" * 50)

    print("\nChecking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)

    print("\nStarting application...")

    try:
        from main import main as start_app
        start_app()
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
