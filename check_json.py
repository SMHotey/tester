#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and fix JSON file."""

import json
from pathlib import Path

file_path = Path(__file__).parent / "test_scenarios.json"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to parse
    data = json.loads(content)
    print(f"JSON is valid! Found {len(data.get('test_scenarios', []))} scenarios")
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
    print(f"Error at position: {e.pos}")
    # Show context around error
    start = max(0, e.pos - 50)
    end = min(len(content), e.pos + 50)
    print(f"Context: ...{content[start:e.pos]}[ERROR HERE]{content[e.pos:end]}...")
