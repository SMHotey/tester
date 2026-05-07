# OpenCode Agent Guidelines for Desktop Test Application

## Essential Commands

**Install:**
```bash
pip install -r requirements.txt
pip install reportlab  # Optional, for PDF export
```

**Run:**
```bash
python main.py
```

**Validate JSON files:**
```bash
python check_json.py      # Validates test_scenarios.json
python diagnose_json.py   # Diagnoses questions.json
python fix_json.py        # Attempts to fix JSON issues
```

## Architecture

**Entry points:**
- `main.py` → `gui.py` (TestApp class) → mode windows (study_mode, test_mode, scenario_test_mode, results_viewer)
- `style_config.py` — centralized Material Design 3 colors, fonts, spacing (used by all mode windows)
- `launcher.py`, `run.bat` — alternative launch methods

**Data files (source of truth, UTF-8 JSON):**
- `reglament.json` — regulation content
- `questions.json` — 601 questions, must have sequential IDs starting from 1
- `test_scenarios.json` — scenario definitions

**Auto-generated (never edit manually):**
- `user_data.json` — user FIO persistence
- `test_results.json` — test history
- `results/` — PDF exports (timestamped filenames)

## Development Guidelines

**JSON changes:**
- Validate with `check_json.py` and `diagnose_json.py` before testing
- Questions require sequential IDs (1, 2, 3...)
- Scenarios must follow structure in `test_scenarios.json`

**Testing:**
- No formal test suite — verify via manual execution
- Test all modes after changes: study, standard test, scenario test, results viewer
- PDF export requires `reportlab` — test via UI

**Design work (study_mode, test_mode, etc.):**
- Colors, fonts, spacing live in `style_config.py` (Colors, Fonts, Spacing classes)
- Hover/active effects use `*_LIGHT` / `*_DARK` color variants
- All windows import from `style_config` — match existing patterns

## File Safety

**Safe to modify:**
- `*.py` files (application logic)
- `questions.json`, `reglament.json`, `test_scenarios.json`

**Never edit manually:**
- `user_data.json`, `test_results.json`, `results/*`

## Requirements

- Python 3.7+
- tkinter (included with standard Python)
- reportlab (optional, for PDF export)
- No external config files — all settings embedded in code
