#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check questions.json count and IDs."""

import json

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total questions in file: {len(data)}')

ids = [q['id'] for q in data]
print(f'ID range: {min(ids)} to {max(ids)}')
print(f'Unique IDs: {len(set(ids))}')

# Find missing IDs
all_ids = set(range(1, max(ids) + 1))
missing = sorted(all_ids - set(ids))
if missing:
    print(f'Missing IDs ({len(missing)}): {missing[:20]}...' if len(missing) > 20 else f'Missing IDs: {missing}')
else:
    print('No missing IDs - all questions from 1 to {max(ids)} present')
