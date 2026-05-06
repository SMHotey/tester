#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix questions.json by properly truncating at the correct JSON array end."""

import json

# Read file
with open('questions.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

# Find where the JSON array actually ends
# We need to find the ] that matches the opening [
depth = 0
in_string = False
escape = False
array_end = None

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
    
    if char == '[':
        depth += 1
    elif char == ']':
        depth -= 1
        if depth == 0:
            array_end = i
            break

print(f"Array ends at position: {array_end}")
print(f"Content at end: {repr(content[array_end:array_end+10])}")

if array_end:
    # Truncate to actual JSON array
    content = content[:array_end+1]
    print(f"Truncated length: {len(content)}")
    
    # Verify it's valid JSON
    try:
        data = json.loads(content)
        print(f"[OK] Successfully loaded {len(data)} questions")
        print(f"[OK] ID range: {data[0]['id']} to {data[-1]['id']}")
        
        # Save the fixed file
        with open('questions.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[OK] Fixed file saved!")
        
        # Also save a pretty version for readability
        with open('questions.json', 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i, q in enumerate(data):
                json.dump(q, f, ensure_ascii=False)
                if i < len(data) - 1:
                    f.write(',\n')
                else:
                    f.write('\n')
            f.write(']\n')
        print("[OK] Pretty file saved!")
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON error at position {e.pos}")
        print(f"Context: {repr(content[max(0,e.pos-50):e.pos+50])}")
