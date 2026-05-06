#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix and validate questions.json to load all 180 questions."""

import json
import re

# Read file
with open('questions.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

# Check structure
open_braces = content.count('{')
close_braces = content.count('}')
open_brackets = content.count('[')
close_brackets = content.count(']')

print(f"{{ count: {open_braces}, }} count: {close_braces}")
print(f"[ count: {open_brackets}, ] count: {close_brackets}")

# Check if file starts and ends correctly
print(f"Starts with: {repr(content[:50])}")
print(f"Ends with: {repr(content[-50:])}")

# Try to load as JSON
try:
    data = json.loads(content)
    print(f"✓ Loaded successfully: {len(data)} questions")
    print(f"Last ID: {data[-1]['id']}")
except json.JSONDecodeError as e:
    print(f"✗ JSON Error at position {e.pos}")
    # Show context around error
    start = max(0, e.pos - 100)
    end = min(len(content), e.pos + 100)
    print(f"Context: {repr(content[start:end])}")
    
    # Try to find what's wrong
    # Maybe there are multiple JSON arrays?
    # Let's try to find all complete question objects
    pattern = r'\{\s*"id"\s*:\s*\d+.*?"correct"\s*:\s*[^}]+\}'
    matches = re.findall(pattern, content, re.DOTALL)
    print(f"Found {len(matches)} question-like patterns")
    
    # Try a different approach: split by } and parse each object
    # Actually, let's just try to fix common issues
    
    # Remove extra ] if present
    if content.rstrip().endswith(']]'):
        print("Fixing: removing extra ]")
        content = content.rstrip()[:-1]  # Remove last ]
        content += '\n'
        
        # Try to parse again
        try:
            data = json.loads(content)
            print(f"✓ Fixed! Now loaded: {len(data)} questions")
            
            # Save fixed file
            with open('questions.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✓ File saved!")
            
        except json.JSONDecodeError as e2:
            print(f"✗ Still broken at position {e2.pos}")
            start = max(0, e2.pos - 100)
            end = min(len(content), e2.pos + 100)
            print(f"Context: {repr(content[start:end])}")
