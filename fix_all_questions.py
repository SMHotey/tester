#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix questions.json to load all 180 questions."""

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

# The issue: file might have invalid JSON structure
# Let's try a different approach: extract each question object manually

# Find all complete question objects (from { to matching })
def extract_json_objects(content):
    objects = []
    i = 0
    while i < len(content):
        if content[i] == '{' and content[i:i+2] != '{"':
            # Find matching closing brace
            depth = 0
            start = i
            in_string = False
            escape = False
            while i < len(content):
                if escape:
                    escape = False
                    i += 1
                    continue
                if content[i] == '\\':
                    escape = True
                    i += 1
                    continue
                if content[i] == '"' and not escape:
                    in_string = not in_string
                if not in_string:
                    if content[i] == '{':
                        depth += 1
                    elif content[i] == '}':
                        depth -= 1
                        if depth == 0:
                            objects.append(content[start:i+1])
                            break
                i += 1
        i += 1
    return objects

# Find the array content (between [ and ])
bracket_depth = 0
array_start = None
array_content_start = None

for i, char in enumerate(content):
    if char == '[' and bracket_depth == 0:
        array_start = i
        bracket_depth += 1
    elif char == '[':
        bracket_depth += 1
    elif char == ']':
        bracket_depth -= 1
        if bracket_depth == 0 and array_start is not None:
            array_content = content[array_start+1:i]
            print(f"\nFound array from {array_start} to {i}")
            print(f"Array content length: {len(array_content)}")
            
            # Try to parse each object in the array
            questions = []
            # Split by }, but careful with nested structures
            obj_start = None
            depth = 0
            in_str = False
            esc = False
            
            for j, c in enumerate(array_content):
                if esc:
                    esc = False
                    continue
                if c == '\\':
                    esc = True
                    continue
                if c == '"' and not esc:
                    in_str = not in_str
                if not in_str:
                    if c == '{':
                        if depth == 0:
                            obj_start = j
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0 and obj_start is not None:
                            obj_str = array_content[obj_start:j+1]
                            try:
                                obj = json.loads(obj_str)
                                questions.append(obj)
                            except:
                                pass
                            obj_start = None
            
            print(f"Successfully parsed {len(questions)} questions")
            
            if len(questions) == 180:
                # Save properly formatted file
                with open('questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print("✓ Fixed! All 180 questions saved properly")
            break

print("\nDone!")
