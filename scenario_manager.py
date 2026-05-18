# -*- coding: utf-8 -*-
"""
Scenario manager.
Manages test scenarios: CRUD operations.
Scenarios are stored in {output_path}/scenarios/scenarios.json
Falls back to bundled test_scenarios.json if user file missing.
"""

import json
import re
from pathlib import Path

from _utils import get_base_path, get_output_path


class ScenarioManager:
    """Manages test scenarios."""

    def __init__(self):
        self.scenarios_dir = get_output_path() / "scenarios"
        self.scenarios_file = self.scenarios_dir / "scenarios.json"
        self._ensure_dirs()

    # ─── Internal helpers ─────────────────────────────────────────────

    def _ensure_dirs(self):
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)

    def _load_raw(self):
        """Load scenarios dict from user file or bundled fallback."""
        if self.scenarios_file.exists():
            try:
                with open(self.scenarios_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # Fallback to bundled
        bundled = get_base_path() / "test_scenarios.json"
        if bundled.exists():
            try:
                with open(bundled, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"test_scenarios": []}

    def _save_raw(self, data):
        """Save scenarios dict to user file."""
        try:
            with open(self.scenarios_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _get_next_id(self, scenarios):
        """Generate next scenario ID like S01, S02... S39, S40..."""
        max_num = 0
        pattern = re.compile(r'^S(\d+)$', re.IGNORECASE)
        for s in scenarios:
            m = pattern.match(str(s.get("id", "")))
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
        return f"S{max_num + 1:02d}"

    def _get_next_question_id(self, questions):
        """Generate next question ID like q01, q02... q99, q100..."""
        max_num = 0
        pattern = re.compile(r'^q(\d+)$')
        for q in questions:
            m = pattern.match(str(q.get("id", "")))
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
        # Use variable-width padding; up to 999 keep zero-padded to 2
        if max_num < 99:
            return f"q{max_num + 1:02d}"
        return f"q{max_num + 1}"

    # ─── Public API ───────────────────────────────────────────────────

    def load_scenarios(self):
        """Return the full list of scenario dicts."""
        data = self._load_raw()
        return data.get("test_scenarios", [])

    def list_scenarios(self):
        """Return list of scenario summaries: {id, title, description, question_count}."""
        scenarios = self.load_scenarios()
        result = []
        for s in scenarios:
            result.append({
                "id": s.get("id", ""),
                "title": s.get("title", ""),
                "description": s.get("description", ""),
                "question_count": len(s.get("questions", [])),
            })
        return result

    def get_scenario(self, scenario_id):
        """Return a full scenario dict by ID, or None."""
        scenarios = self.load_scenarios()
        for s in scenarios:
            if s.get("id") == scenario_id:
                return s
        return None

    def add_scenario(self, title, description):
        """
        Add a new scenario with auto-generated ID.
        Returns (success: bool, message: str, scenario_id: str or None).
        """
        scenarios = self.load_scenarios()
        new_id = self._get_next_id(scenarios)

        scenario = {
            "id": new_id,
            "title": title,
            "description": description,
            "questions": [],
        }
        scenarios.append(scenario)

        if self._save_raw({"test_scenarios": scenarios}):
            return True, f"Сценарий {new_id} добавлен", new_id
        return False, "Ошибка сохранения", None

    def update_scenario(self, scenario_id, title, description):
        """
        Update a scenario's title and description.
        Returns (success: bool, message: str).
        """
        scenarios = self.load_scenarios()
        for s in scenarios:
            if s.get("id") == scenario_id:
                s["title"] = title
                s["description"] = description
                if self._save_raw({"test_scenarios": scenarios}):
                    return True, f"Сценарий {scenario_id} обновлён"
                return False, "Ошибка сохранения"
        return False, f"Сценарий {scenario_id} не найден"

    def delete_scenario(self, scenario_id):
        """
        Delete a scenario by ID.
        Returns (success: bool, message: str).
        """
        scenarios = self.load_scenarios()
        new_scenarios = [s for s in scenarios if s.get("id") != scenario_id]
        if len(new_scenarios) == len(scenarios):
            return False, f"Сценарий {scenario_id} не найден"

        if self._save_raw({"test_scenarios": new_scenarios}):
            return True, f"Сценарий {scenario_id} удалён"
        return False, "Ошибка сохранения"

    # ─── Scenario question CRUD ──────────────────────────────────────

    def get_scenario_questions(self, scenario_id):
        """Return questions list for a scenario, or empty list."""
        scenario = self.get_scenario(scenario_id)
        if scenario:
            return scenario.get("questions", [])
        return []

    def add_question_to_scenario(self, scenario_id, question_dict):
        """
        Add a question to a scenario. Auto-assigns q-id.
        Returns (success: bool, message: str).
        """
        scenarios = self.load_scenarios()
        for s in scenarios:
            if s.get("id") == scenario_id:
                questions = s.get("questions", [])
                new_id = self._get_next_question_id(questions)
                question_dict["id"] = new_id
                questions.append(question_dict)
                s["questions"] = questions
                if self._save_raw({"test_scenarios": scenarios}):
                    return True, f"Вопрос {new_id} добавлен в сценарий {scenario_id}"
                return False, "Ошибка сохранения"
        return False, f"Сценарий {scenario_id} не найден"

    def update_question_in_scenario(self, scenario_id, question_id, new_data):
        """
        Update a question in a scenario by its q-id.
        Returns (success: bool, message: str).
        """
        scenarios = self.load_scenarios()
        for s in scenarios:
            if s.get("id") == scenario_id:
                questions = s.get("questions", [])
                for i, q in enumerate(questions):
                    if q.get("id") == question_id:
                        new_data["id"] = question_id
                        questions[i] = new_data
                        s["questions"] = questions
                        if self._save_raw({"test_scenarios": scenarios}):
                            return True, f"Вопрос {question_id} обновлён"
                        return False, "Ошибка сохранения"
                return False, f"Вопрос {question_id} не найден"
        return False, f"Сценарий {scenario_id} не найден"

    def delete_question_from_scenario(self, scenario_id, question_id):
        """
        Delete a question from a scenario by its q-id.
        Returns (success: bool, message: str).
        """
        scenarios = self.load_scenarios()
        for s in scenarios:
            if s.get("id") == scenario_id:
                questions = s.get("questions", [])
                new_questions = [q for q in questions if q.get("id") != question_id]
                if len(new_questions) == len(questions):
                    return False, f"Вопрос {question_id} не найден"
                s["questions"] = new_questions
                if self._save_raw({"test_scenarios": scenarios}):
                    return True, f"Вопрос {question_id} удалён из сценария {scenario_id}"
                return False, "Ошибка сохранения"
        return False, f"Сценарий {scenario_id} не найден"
