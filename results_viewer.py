#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Results viewer window for viewing test results in table format.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from datetime import datetime


class ResultsViewerWindow(tk.Toplevel):
    """Window for viewing test results."""

    def __init__(self, parent, results_file, on_back):
        """Initialize results viewer window."""
        super().__init__(parent)
        self.results_file = results_file
        self.on_back = on_back
        self.results = []

        self.title("Просмотр результатов тестирования")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")

        self.load_results()
        self.create_widgets()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_back)

    def load_results(self):
        """Load results from JSON file."""
        try:
            if Path(self.results_file).exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить результаты: {e}")
            self.results = []

    def create_widgets(self):
        """Create window widgets."""
        # Header
        header_frame = tk.Frame(self, bg="#FF9800", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_btn = tk.Button(
            header_frame,
            text="← Назад",
            font=("Arial", 11),
            bg="#F57C00",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text="Результаты тестирования",
            font=("Arial", 16, "bold"),
            bg="#FF9800",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, pady=15, padx=20)

        # Stats frame
        stats_frame = tk.Frame(self, bg="white", relief=tk.RIDGE, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        stats_frame.configure(padx=20, pady=10)

        total_tests = len(self.results)
        total_correct = sum(r.get("correct_count", 0) for r in self.results)
        total_questions = sum(r.get("total_questions", 0) for r in self.results)

        tk.Label(
            stats_frame,
            text=f"Всего тестов: {total_tests}",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(
            stats_frame,
            text=f"Всего вопросов: {total_questions}",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(
            stats_frame,
            text=f"Правильных ответов: {total_correct}",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#4CAF50"
        ).pack(side=tk.LEFT)

        # Table frame
        table_frame = tk.Frame(self, bg="#f0f0f0")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Create treeview with scrollbars
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ("Фамилия", "Имя", "Правильно", "Неправильно", "Всего", "Дата", "Время", "Длительность")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            height=25
        )

        # Configure columns
        col_widths = {
            "Фамилия": 120,
            "Имя": 120,
            "Правильно": 80,
            "Неправильно": 90,
            "Всего": 80,
            "Дата": 100,
            "Время": 80,
            "Длительность": 100
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # Populate table
        self.populate_table()

        # Buttons frame
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # View incorrect answers button
        view_incorrect_btn = tk.Button(
            btn_frame,
            text="Посмотреть неправильные ответы",
            font=("Arial", 10),
            bg="#F44336",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.view_incorrect_answers
        )
        view_incorrect_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete selected result button
        delete_btn = tk.Button(
            btn_frame,
            text="Удалить выбранный результат",
            font=("Arial", 10),
            bg="#9E9E9E",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.delete_selected
        )
        delete_btn.pack(side=tk.LEFT)

        # Double-click to view details
        self.tree.bind("<Double-1>", lambda e: self.view_incorrect_answers())

    def populate_table(self):
        """Populate the table with results."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add results
        for i, result in enumerate(self.results):
            # Parse datetime
            start_time = result.get("start_time", "")
            date_str = ""
            time_str = ""
            duration_str = ""

            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time)
                    date_str = dt.strftime("%d.%m.%Y")
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    pass

            # Calculate duration
            duration_seconds = result.get("duration_seconds",0)
            if duration_seconds:
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                duration_str = f"{minutes}м {seconds}с"

            # Insert row
            item_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    result.get("last_name", ""),
                    result.get("first_name", ""),
                    result.get("correct_count", 0),
                    result.get("incorrect_count", 0),
                    result.get("total_questions", 0),
                    date_str,
                    time_str,
                    duration_str
                )
            )

            # Color code based on performance
            correct = result.get("correct_count",0)
            total = result.get("total_questions", 1)
            ratio = correct / total if total > 0 else 0

            if ratio == 1.0:
                self.tree.item(item_id, tags=("perfect",))
            elif ratio >= 0.7:
                self.tree.item(item_id, tags=("good",))
            else:
                self.tree.item(item_id, tags=("poor",))

        # Configure tags
        self.tree.tag_configure("perfect", background="#C8E6C9")
        self.tree.tag_configure("good", background="#FFF9C4")
        self.tree.tag_configure("poor", background="#FFCDD2")

    def view_incorrect_answers(self):
        """View incorrect answers for selected result."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите результат из таблицы")
            return

        # Get selected index
        item = selection[0]
        item_index = self.tree.index(item)

        if item_index >= len(self.results):
            return

        result = self.results[item_index]
        details = result.get("details", [])

        # Filter incorrect answers
        incorrect = [d for d in details if not d.get("correct", True)]

        if not incorrect:
            messagebox.showinfo("Информация", "Нет неправильных ответов")
            return

        # Show incorrect answers window
        self.show_incorrect_details(result, incorrect)

    def show_incorrect_details(self, result, incorrect):
        """Show window with incorrect answers."""
        window = tk.Toplevel(self)
        window.title(f"Неправильные ответы - {result.get('last_name')} {result.get('first_name')}")
        window.geometry("900x600")
        window.configure(bg="#f0f0f0")

        # Header
        header_frame = tk.Frame(window, bg="#F44336", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"Неправильные ответы: {result.get('last_name')} {result.get('first_name')}",
            font=("Arial", 12, "bold"),
            bg="#F44336",
            fg="white"
        ).pack(side=tk.LEFT, pady=12, padx=20)

        # Close button
        close_btn = tk.Button(
            header_frame,
            text="✖ Закрыть",
            font=("Arial", 10),
            bg="#D32F2F",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=window.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=15, pady=10)

        # Content with scrollbar
        canvas = tk.Canvas(window, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add incorrect answers
        for i, detail in enumerate(incorrect, 1):
            detail_frame = tk.Frame(scrollable_frame, bg="white", relief=tk.RIDGE, bd=1)
            detail_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                detail_frame,
                text=f"Вопрос {detail.get('question_id', '')}: {detail.get('question', '')}",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#333",
                wraplength=850,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(10, 5))

            tk.Label(
                detail_frame,
                text=f"Ваш ответ: {self.format_answer(detail)}",
                font=("Arial", 10),
                bg="white",
                fg="#F44336",
                wraplength=850,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))

            tk.Label(
                detail_frame,
                text=f"Правильный ответ: {self.format_correct_answer(detail)}",
                font=("Arial", 10),
                bg="white",
                fg="#4CAF50",
                wraplength=850,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))

            # Explanation
            explanation_frame = tk.Frame(detail_frame, bg="#FFF9C4")
            explanation_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

            tk.Label(
                explanation_frame,
                text="Объяснение:",
                font=("Arial", 9, "bold"),
                bg="#FFF9C4",
                fg="#333"
            ).pack(anchor=tk.W, padx=10, pady=(5, 0))

            explanation_text = detail.get("explanation", "")
            tk.Label(
                explanation_frame,
                text=explanation_text,
                font=("Arial", 9),
                bg="#FFF9C4",
                fg="#333",
                wraplength=830,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))

            # Button to open regulation
            btn_frame = tk.Frame(detail_frame, bg="white")
            btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            tk.Button(
                btn_frame,
                text="Открыть регламент",
                font=("Arial", 8),
                bg="#2196F3",
                fg="white",
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda d=detail: self.open_reglament_from_result(d)
            ).pack(side=tk.LEFT)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Handle window close
        window.protocol("WM_DELETE_WINDOW", window.destroy)

    def open_reglament_from_result(self, detail):
        """Open regulation window from test results."""
        explanation = detail.get("explanation", "")

        # Import here to avoid circular imports
        from study_mode import StudyModeWindow

        def close_study():
            pass  # Just close, no need to go back anywhere

        study_window = StudyModeWindow(
            self,
            self.load_reglament(),
            on_close=lambda: None
        )

    def format_answer(self, detail):
        """Format user answer for display."""
        question_type = detail.get("type")
        user_answer = detail.get("user_answer")

        if question_type == "single_choice":
            return f"Вариант {int(user_answer) + 1 if user_answer else 'нет'}"
        elif question_type == "multiple_choice":
            if isinstance(user_answer, list):
                return f"Варианты: {', '.join(str(int(x) + 1) for x in user_answer)}"
            return "Нет ответа"
        elif question_type == "ordering":
            if isinstance(user_answer, list):
                return f"Порядок: {', '.join(str(int(x) + 1) for x in user_answer)}"
            return "Нет ответа"
        elif question_type == "true_false":
            if user_answer == "true":
                return "Верно"
            elif user_answer == "false":
                return "Неверно"
            return "Нет ответа"

        return str(user_answer)

    def format_correct_answer(self, detail):
        """Format correct answer for display."""
        question_type = detail.get("type")
        correct_answer = detail.get("correct_answer")

        if question_type == "single_choice":
            return f"Вариант {int(correct_answer[0]) + 1 if correct_answer else 'нет'}"
        elif question_type == "multiple_choice":
            if isinstance(correct_answer, list):
                return f"Варианты: {', '.join(str(int(x) + 1) for x in correct_answer)}"
            return "Нет ответа"
        elif question_type == "ordering":
            if isinstance(correct_answer, list):
                return f"Порядок: {', '.join(str(int(x) + 1) for x in correct_answer)}"
            return "Нет ответа"
        elif question_type == "true_false":
            if correct_answer == True:
                return "Верно"
            elif correct_answer == False:
                return "Неверно"
            return "Нет ответа"

        return str(correct_answer)

    def delete_selected(self):
        """Delete selected result from the list."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите результат для удаления")
            return

        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранный результат?"):
            return

        # Get selected indices
        indices = [self.tree.index(item) for item in selection]
        indices.sort(reverse=True)  # Delete from end to avoid index shifting

        for idx in indices:
            if 0 <= idx < len(self.results):
                del self.results[idx]

        # Save updated results
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.populate_table()
            messagebox.showinfo("Успех", "Результат удален")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить результат: {e}")
