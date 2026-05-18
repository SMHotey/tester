# -*- coding: utf-8 -*-
"""
Question bank manager.
Manages multiple question bank files: import, list, delete, select active.
Banks are stored in {output_path}/questions/ with an index.json manifest.
"""

import json
import shutil
import uuid
from pathlib import Path

from _utils import get_base_path, get_output_path


class QuestionBankManager:
    """Manages question bank files."""

    def __init__(self):
        self.banks_dir = get_output_path() / "questions"
        self.index_file = self.banks_dir / "index.json"
        self._ensure_dirs()

    # ─── Internal helpers ─────────────────────────────────────────────

    def _ensure_dirs(self):
        self.banks_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self._write_index({"active": None, "banks": []})

    def _read_index(self):
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_index(self, data):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _validate_questions(self, questions):
        """Validate a list of question objects. Returns (ok, error_msg)."""
        if not isinstance(questions, list):
            return False, "Файл должен содержать список вопросов"
        if len(questions) == 0:
            return False, "Список вопросов пуст"
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                return False, f"Вопрос #{i + 1}: ожидается объект"
            if "id" not in q:
                return False, f"Вопрос #{i + 1}: отсутствует поле id"
            if "type" not in q:
                return False, f"Вопрос #{i + 1}: отсутствует поле type"
            if "question" not in q:
                return False, f"Вопрос #{i + 1}: отсутствует поле question"
        # Check IDs are sequential starting from 1
        for i, q in enumerate(questions):
            if q.get("id") != i + 1:
                return False, f"Вопрос #{i + 1}: id должен быть {i + 1}, но получен {q.get('id')}"
        return True, None

    # ─── Public API ───────────────────────────────────────────────────

    def list_banks(self):
        """Return list of bank dicts: {name, file, count, active}."""
        data = self._read_index()
        active = data.get("active")
        banks = []
        for b in data.get("banks", []):
            banks.append({
                "name": b["name"],
                "file": b["file"],
                "count": b["count"],
                "active": b["file"] == active,
            })
        return banks

    def get_active_bank_name(self):
        """Return the display name of the active bank, or None."""
        data = self._read_index()
        active_file = data.get("active")
        if active_file:
            for b in data.get("banks", []):
                if b["file"] == active_file:
                    return b["name"]
        return None

    def load_questions(self):
        """
        Load questions from the active bank.
        Falls back to bundled questions.json if no active bank or file missing.
        Returns a list of question dicts, or empty list on failure.
        """
        data = self._read_index()
        active_file = data.get("active")
        if active_file:
            bank_path = self.banks_dir / active_file
            if bank_path.exists():
                try:
                    with open(bank_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass  # Fall through to bundled default

        # Fallback to bundled questions.json
        bundled = get_base_path() / "questions.json"
        if bundled.exists():
            try:
                with open(bundled, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def import_bank(self, source_path, name=None):
        """
        Import a questions.json file as a new bank.
        Returns (success: bool, message: str).
        """
        source = Path(source_path)
        if not source.exists():
            return False, "Файл не найден"

        try:
            with open(source, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Ошибка чтения JSON: {e}"

        valid, err = self._validate_questions(questions)
        if not valid:
            return False, err

        # Generate unique filename
        file_id = uuid.uuid4().hex[:12]
        dest_filename = f"{file_id}.json"
        dest_path = self.banks_dir / dest_filename

        try:
            shutil.copy2(str(source), str(dest_path))
        except OSError as e:
            return False, f"Ошибка копирования: {e}"

        # Add to index
        bank_name = name if name else source.stem
        data = self._read_index()
        data["banks"].append({
            "name": bank_name,
            "file": dest_filename,
            "count": len(questions),
        })
        self._write_index(data)

        return True, f"Импортировано {len(questions)} вопросов как «{bank_name}»"

    def delete_bank(self, filename):
        """
        Delete a bank by filename.
        Returns (success: bool, message: str).
        """
        data = self._read_index()
        original_len = len(data["banks"])
        data["banks"] = [b for b in data["banks"] if b["file"] != filename]

        if len(data["banks"]) == original_len:
            return False, "Банк не найден"

        # Remove the file
        bank_path = self.banks_dir / filename
        if bank_path.exists():
            try:
                bank_path.unlink()
            except OSError:
                pass  # Non-critical, index entry is already removed

        # Clear active if it was the deleted bank
        if data.get("active") == filename:
            data["active"] = None

        self._write_index(data)
        return True, "Банк удалён"

    def set_active(self, filename):
        """
        Set a bank as active by filename.
        Returns (success: bool, message: str).
        """
        data = self._read_index()
        if not any(b["file"] == filename for b in data["banks"]):
            return False, "Банк не найден"
        data["active"] = filename
        self._write_index(data)
        return True, "Банк выбран активным"

    def get_question_count(self):
        """Return the number of questions in the currently active bank."""
        questions = self.load_questions()
        return len(questions) if isinstance(questions, list) else 0

    # ─── Active bank helpers ──────────────────────────────────────────

    def get_active_bank_filename(self):
        """Return the filename of the active bank, or None."""
        data = self._read_index()
        return data.get("active")

    def ensure_active_bank_exists(self):
        """
        Ensure an active bank exists.
        If none, create one from bundled questions.json named 'Мои вопросы'.
        Returns (filename: str, created: bool).
        """
        filename = self.get_active_bank_filename()
        if filename:
            bank_path = self.banks_dir / filename
            if bank_path.exists():
                return filename, False

        # Create a new bank from bundled questions
        bundled_path = get_base_path() / "questions.json"
        if not bundled_path.exists():
            return None, False

        try:
            with open(bundled_path, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except Exception:
            return None, False

        file_id = uuid.uuid4().hex[:12]
        filename = f"{file_id}.json"
        dest_path = self.banks_dir / filename

        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        data = self._read_index()
        data["banks"].append({
            "name": "Мои вопросы",
            "file": filename,
            "count": len(questions),
        })
        data["active"] = filename
        self._write_index(data)
        return filename, True

    def load_questions_from_bank(self, filename):
        """Load questions from a specific bank file."""
        bank_path = self.banks_dir / filename
        if not bank_path.exists():
            return []
        try:
            with open(bank_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_questions_to_bank(self, filename, questions):
        """
        Save questions to a bank file and update index count.
        Returns success: bool.
        """
        bank_path = self.banks_dir / filename
        try:
            with open(bank_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            # Update count in index
            data = self._read_index()
            for b in data.get("banks", []):
                if b["file"] == filename:
                    b["count"] = len(questions)
                    break
            self._write_index(data)
            return True
        except Exception:
            return False

    def renumber_questions(self, questions):
        """Renumber question IDs sequentially starting from 1. Returns new list."""
        for i, q in enumerate(questions):
            q["id"] = i + 1
        return questions

    def add_question_to_bank(self, filename, question_dict):
        """
        Add a question to a bank file. Auto-assigns ID.
        Returns (success: bool, message: str).
        """
        questions = self.load_questions_from_bank(filename)
        if not questions and not isinstance(questions, list):
            return False, "Не удалось загрузить банк"

        # Assign new ID
        max_id = max((q.get("id", 0) for q in questions), default=0)
        question_dict["id"] = max_id + 1
        questions.append(question_dict)

        if self.save_questions_to_bank(filename, questions):
            return True, f"Вопрос #{question_dict['id']} добавлен"
        return False, "Ошибка сохранения"

    def update_question_in_bank(self, filename, question_id, new_data):
        """
        Update a question in a bank by ID.
        Returns (success: bool, message: str).
        """
        questions = self.load_questions_from_bank(filename)
        if not questions:
            return False, "Не удалось загрузить банк"

        for i, q in enumerate(questions):
            if q.get("id") == question_id:
                # Preserve the ID, update everything else
                new_data["id"] = question_id
                questions[i] = new_data
                if self.save_questions_to_bank(filename, questions):
                    return True, f"Вопрос #{question_id} обновлён"
                return False, "Ошибка сохранения"

        return False, f"Вопрос #{question_id} не найден"

    def delete_question_from_bank(self, filename, question_id):
        """
        Delete a question from a bank by ID and renumber.
        Returns (success: bool, message: str).
        """
        questions = self.load_questions_from_bank(filename)
        if not questions:
            return False, "Не удалось загрузить банк"

        new_questions = [q for q in questions if q.get("id") != question_id]
        if len(new_questions) == len(questions):
            return False, f"Вопрос #{question_id} не найден"

        # Renumber
        self.renumber_questions(new_questions)

        if self.save_questions_to_bank(filename, new_questions):
            return True, f"Вопрос #{question_id} удалён, id перенумерованы"
        return False, "Ошибка сохранения"
