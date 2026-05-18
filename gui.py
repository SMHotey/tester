#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main GUI module for the test application.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from tkinter import Tk, messagebox, PhotoImage

from _utils import get_base_path, get_output_path

# Import GUI components
from mode_selection import ModeSelectionWindow
from study_mode import StudyModeWindow
from test_mode import TestModeWindow
from scenario_test_mode import ScenarioTestModeWindow
from results_viewer import ResultsViewerWindow

# Import managers and editors
from question_bank_manager import QuestionBankManager
from scenario_manager import ScenarioManager
from question_list_window import QuestionListWindow
from scenario_editor_window import ScenarioEditorWindow



class TestApp:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        self.root = Tk()
        self.root.withdraw()  # Hide main window initially

        # Set application icon
        try:
            base = get_base_path()
            icon_path = base / "app_icon.png"
            if icon_path.exists():
                self.icon_img = PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, self.icon_img)
        except Exception:
            pass  # Silently fail if icon can't be loaded

        output_base = get_output_path()
        self.user_data_file = output_base / "user_data.json"
        self.results_file = output_base / "test_results.json"

        # Managers for editable data
        self.bank_manager = QuestionBankManager()
        self.scenario_manager = ScenarioManager()

        self.load_user_data()
        self.load_reglament()
        self.load_test_questions()
        self.load_scenarios()
        self.current_window = None
        self.show_mode_selection()

    def load_user_data(self):
        """Load saved user data."""
        try:
            if self.user_data_file.exists():
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    self.user_data = json.load(f)
            else:
                self.user_data = {"last_name": "", "first_name": ""}
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.user_data = {"last_name": "", "first_name": ""}

    def save_user_data(self):
        """Save user data."""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")

    def load_reglament(self):
        """Load regulation data."""
        try:
            reglament_path = get_base_path() / "reglament.json"
            with open(reglament_path, 'r', encoding='utf-8') as f:
                self.reglament = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reglament.json: {e}")
            self.reglament = []

    def load_test_questions(self):
        """Load test questions via QuestionBankManager (prefers active bank)."""
        self.test_questions = self.bank_manager.load_questions()
        if not self.test_questions:
            messagebox.showerror("Error", "Не удалось загрузить вопросы")

    def load_scenarios(self):
        """Load test scenarios via ScenarioManager (prefers user-edited scenarios)."""
        self.scenarios = self.scenario_manager.load_scenarios()

    def save_test_result(self, result):
        """Save test result to JSON file."""
        try:
            results = []
            if self.results_file.exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)

            results.append(result)

            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving test result: {e}")

    def show_mode_selection(self):
        """Show mode selection window."""
        if self.current_window:
            self.current_window.destroy()
        # Always pass the callback; scenario window will handle empty case
        self.current_window = ModeSelectionWindow(
            self.root,
            on_study_mode=self.show_study_mode,
            on_test_mode=self.show_test_mode,
            on_view_results=self.show_results_viewer,
            on_scenario_test_mode=self.show_scenario_test_mode,
            on_edit_questions=self.show_question_editor,
            on_edit_scenarios=self.show_scenario_editor,
        )

    def show_question_editor(self):
        """Show question editor window."""
        if self.current_window:
            self.current_window.destroy()

        # Ensure there's an active bank to edit
        filename, created = self.bank_manager.ensure_active_bank_exists()
        bank_name = self.bank_manager.get_active_bank_name() or "Мои вопросы"
        if not filename:
            messagebox.showerror("Ошибка", "Не удалось создать банк вопросов")
            self.show_mode_selection()
            return

        self.current_window = QuestionListWindow(
            self.root,
            self.bank_manager,
            bank_filename=filename,
            bank_name=bank_name,
            on_back=self.show_mode_selection,
            on_bank_changed=self._reload_test_questions,
        )

    def show_scenario_editor(self):
        """Show scenario editor window."""
        if self.current_window:
            self.current_window.destroy()
        self.current_window = ScenarioEditorWindow(
            self.root,
            self.scenario_manager,
            on_back=self.show_mode_selection,
        )

    def _reload_test_questions(self):
        """Reload test questions after bank changes."""
        self.load_test_questions()

    def show_study_mode(self):
        """Show study mode window."""
        if self.current_window:
            self.current_window.destroy()
        self.current_window = StudyModeWindow(
            self.root,
            self.reglament,
            on_back=self.show_mode_selection
        )

    def show_test_mode(self):
        """Show test mode window."""
        if self.current_window:
            self.current_window.destroy()
        self.current_window = TestModeWindow(
            self.root,
            self.user_data,
            self.test_questions,
            self.reglament,
            self.save_user_data,
            self.save_test_result,
            on_back=self.show_mode_selection
        )

    def show_scenario_test_mode(self):
        """Show scenario test mode window."""
        if self.current_window:
            self.current_window.destroy()
        self.current_window = ScenarioTestModeWindow(
            self.root,
            self.user_data,
            self.scenarios,
            self.reglament,
            self.save_user_data,
            self.save_test_result,
            on_back=self.show_mode_selection
        )

    def show_results_viewer(self):
        """Show results viewer window."""
        if self.current_window:
            self.current_window.destroy()
        self.current_window = ResultsViewerWindow(
            self.root,
            self.results_file,
            on_back=self.show_mode_selection
        )

    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = TestApp()
    app.run()
