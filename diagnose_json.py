#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose and fix questions.json to load all 180 questions."""

import json
import re

# Read file
with open('questions.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} chars")
print(f"Ends with: {repr(content[-50:])}")

# Count question objects by counting "id": patterns
id_matches = re.findall(r'"id"\s*:\s*(\d+)', content)
print(f"Found {len(id_matches)} 'id' fields")
if id_matches:
    ids = [int(x) for x in id_matches]
    print(f"ID range: {min(ids)} to {max(ids)}")
    print(f"Unique IDs: {len(set(ids))}")

# Try to load as JSON
try:
    data = json.loads(content)
    print(f"\n✓ Loaded successfully: {len(data)} questions")
    print(f"Last loaded ID: {data[-1]['id']}")
    print(f"Missing IDs: {sorted(set(range(1, 181)) - set(q['id'] for q in data))}")
except json.JSONDecodeError as e:
    print(f"\n✗ JSON Error at position {e.pos}")
    # Show context
    start = max(0, e.pos - 100)
    end = min(len(content), e.pos + 100)
    print(f"Context around error:")
    print(repr(content[start:end]))
    
    # The issue might be that JSON stops at first ]]
    # Let's see what's at position 71591 (first ])
    print(f"\nChecking position 71591:")
    print(repr(content[71585:71598]))
    
    # Try to find where the actual array ends
    # Count braces and brackets
    stack = []
    in_string = False
    escape = False
    array_start = None
    
    for i, char in enumerate(content):
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        
        if char == '[' and array_start is None:
            array_start = i
            stack.append('[')
        elif char == ']' and stack and stack[-1] == '[':
            stack.pop()
            if not stack:
                print(f"\nFound matching ] at position {i}")
                print(f"Context: {repr(content[max(0,i-20):i+5])}")
                break
