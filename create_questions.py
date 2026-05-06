#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create questions.json from test_scenarios.json"""

import json
import os

# Load test_scenarios.json
scenarios_path = r"C:\Projects\tester\test_scenarios.json"
with open(scenarios_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract all questions
all_questions = []
for scenario in data.get("test_scenarios", []):
    scenario_id = scenario.get("id", "")
    scenario_title = scenario.get("title", "")
    for q in scenario.get("questions", []):
        # Add scenario reference
        q_copy = q.copy()
        q_copy["scenario_id"] = scenario_id
        q_copy["scenario_title"] = scenario_title
        all_questions.append(q_copy)

# Save to questions.json
questions_path = r"C:\Projects\tester\questions.json"
with open(questions_path, 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

print(f"Created questions.json with {len(all_questions)} questions")
