#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix questions.json by removing extra closing bracket."""

import json

# Read file
with open('questions.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original length: {len(content)} chars')
print(f'Ends with: {repr(content[-30:])}')

# Fix: remove extra ] if present
if content.rstrip().endswith(']]'):
    content = content.rstrip()[:-1]  # Remove last ]
    print('Fixed! Removed extra ]')
    
    # Write back
    with open('questions.json', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verify
    with open('questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'Now loaded: {len(data)} questions')
    print(f'Last ID: {data[-1]["id"]}')
else:
    print('No fix needed')
