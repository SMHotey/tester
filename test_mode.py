#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test mode window for taking tests.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import random


class TestModeWindow(tk.Toplevel):
    """Window for test mode."""

    def __init__(self, parent, user_data, test_questions, reglament, save_user_data, save_test_result, on_back):
        """Initialize test mode window."""
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.test_questions = test_questions
        self.reglament = reglament
        self.save_user_data = save_user_data
        self.save_test_result = save_test_result
        self.on_back = on_back

        self.current_questions = []
        self.current_question_index = 0
        self.user_answers = {}
        self.start_time = None

        self.title("Режим тестирования")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")

        self.create_input_screen()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_back)

    def create_input_screen(self):
        """Create the input screen for user data and question count."""
        self.clear_window()

        # Header
        header_frame = tk.Frame(self, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_btn = tk.Button(
            header_frame,
            text="← Назад",
            font=("Arial", 11),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text="Ввод данных для тестирования",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, pady=15, padx=20)

        # Main container
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)

        # Input form
        form_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        form_frame.configure(padx=30, pady=30)

        tk.Label(
            form_frame,
            text="Введите ваши данные",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(pady=(0, 20))

        # Last name
        tk.Label(
            form_frame,
            text="Фамилия:",
            font=("Arial", 11),
            bg="white",
            anchor=tk.W
        ).pack(fill=tk.X, pady=(10, 5))

        self.last_name_var = tk.StringVar(value=self.user_data.get("last_name", ""))
        last_name_entry = tk.Entry(
            form_frame,
            textvariable=self.last_name_var,
            font=("Arial", 11),
            relief=tk.SOLID,
            bd=1
        )
        last_name_entry.pack(fill=tk.X, pady=(0, 10))

        # First name
        tk.Label(
            form_frame,
            text="Имя:",
            font=("Arial", 11),
            bg="white",
            anchor=tk.W
        ).pack(fill=tk.X, pady=(10, 5))

        self.first_name_var = tk.StringVar(value=self.user_data.get("first_name", ""))
        first_name_entry = tk.Entry(
            form_frame,
            textvariable=self.first_name_var,
            font=("Arial", 11),
            relief=tk.SOLID,
            bd=1
        )
        first_name_entry.pack(fill=tk.X, pady=(0, 20))

        # Question count selection
        tk.Label(
            form_frame,
            text="Введите количество вопросов для тестирования:",
            font=("Arial", 11, "bold"),
            bg="white",
            anchor=tk.W
        ).pack(fill=tk.X, pady=(10, 5))

        tk.Label(
            form_frame,
            text=f"Доступно вопросов в базе: {len(self.test_questions)}",
            font=("Arial", 9),
            bg="white",
            fg="#666",
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 10))

        self.question_count_var = tk.StringVar(value="10")
        question_count_entry = tk.Entry(
            form_frame,
            textvariable=self.question_count_var,
            font=("Arial", 11),
            relief=tk.SOLID,
            bd=1
        )
        question_count_entry.pack(fill=tk.X, pady=(0, 20))

        # Start button
        start_btn = tk.Button(
            form_frame,
            text="Начать тестирование",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.start_test
        )
        start_btn.pack()

    def _convert_question_to_internal(self, q):
        """Convert question from new format to internal format."""
        internal_q = q.copy()

        # Map type
        type_map = {
            "radio": "single_choice",
            "checkbox": "multiple_choice",
            "sequence": "ordering",
            "truefalse": "true_false"
        }
        internal_q["type"] = type_map.get(q.get("type"), q.get("type"))

        # Map question text
        internal_q["question"] = q.get("text", "")

        # Convert correct to correct_answer (using indices for comparison)
        correct = q.get("correct")
        options = q.get("options", [])
        q_type = q.get("type")

        if q_type == "radio":
            if correct in options:
                internal_q["correct_answer"] = [options.index(correct)]
            else:
                internal_q["correct_answer"] = []
        elif q_type == "checkbox":
            internal_q["correct_answer"] = [options.index(c) for c in correct if c in options]
        elif q_type == "sequence":
            internal_q["correct_answer"] = [options.index(c) for c in correct if c in options]
        elif q_type == "truefalse":
            internal_q["correct_answer"] = correct

        return internal_q

    def start_test(self):
        """Start the test with randomly selected questions."""
        last_name = self.last_name_var.get().strip()
        first_name = self.first_name_var.get().strip()
        question_count_str = self.question_count_var.get().strip()

        if not last_name or not first_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите фамилию и имя")
            return

        if not question_count_str.isdigit():
            messagebox.showerror("Ошибка", "Количество вопросов должно быть числом")
            return

        question_count = int(question_count_str)
        if question_count < 1:
            messagebox.showerror("Ошибка", "Количество вопросов должно быть больше 0")
            return

        if question_count > len(self.test_questions):
            messagebox.showerror("Ошибка", f"Максимальное количество вопросов: {len(self.test_questions)}")
            return

        # Save user data
        self.user_data["last_name"] = last_name
        self.user_data["first_name"] = first_name
        self.save_user_data()

        # Randomly select questions and convert to internal format
        selected_questions = random.sample(self.test_questions, question_count)
        self.current_questions = [self._convert_question_to_internal(q) for q in selected_questions]

        # Reset test state
        self.current_question_index = 0
        self.user_answers = {}
        self.start_time = datetime.now()

        # Show first question
        self.show_question()

    def show_question(self):
        """Display the current question."""
        self.clear_window()

        total_questions = len(self.current_questions)

        # Header
        header_frame = tk.Frame(self, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_btn = tk.Button(
            header_frame,
            text="← Завершить",
            font=("Arial", 11),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.confirm_exit_test
        )
        back_btn.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text="Тестирование",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, pady=15, padx=20)

        # Progress bar
        progress_frame = tk.Frame(self, bg="#E3F2FD", height=30)
        progress_frame.pack(fill=tk.X)
        progress_frame.pack_propagate(False)

        progress_text = tk.Label(
            progress_frame,
            text=f"Вопрос {self.current_question_index + 1} из {total_questions}",
            font=("Arial", 10),
            bg="#E3F2FD",
            fg="#1976D2"
        )
        progress_text.pack(pady=5)

        # Question frame
        question_frame = tk.Frame(self, bg="white", relief=tk.RIDGE, bd=2)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Question text
        question_data = self.current_questions[self.current_question_index]
        question_text = question_data.get("question", "")

        tk.Label(
            question_frame,
            text=f"Вопрос {self.current_question_index + 1}:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333",
            anchor=tk.W
        ).pack(fill=tk.X, padx=20, pady=(20, 5))

        tk.Label(
            question_frame,
            text=question_text,
            font=("Arial", 11),
            bg="white",
            fg="#333",
            anchor=tk.W,
            wraplength=900,
            justify=tk.LEFT
        ).pack(fill=tk.X, padx=20, pady=(0, 20))

        # Answer options frame
        options_frame = tk.Frame(question_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        question_type = question_data.get("type", "single_choice")
        options = question_data.get("options", [])

        # Store reference to current question widget
        self._current_question_widget = options_frame
        self._current_question_data = question_data

        if question_type == "single_choice":
            self.show_single_choice(options_frame, question_data)
        elif question_type == "multiple_choice":
            self.show_multiple_choice(options_frame, question_data)
        elif question_type == "ordering":
            self.show_ordering(options_frame, question_data)
        elif question_type == "true_false":
            self.show_true_false(options_frame, question_data)

        # Navigation buttons
        nav_frame = tk.Frame(question_frame, bg="white")
        nav_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        if self.current_question_index > 0:
            prev_btn = tk.Button(
                nav_frame,
                text="← Предыдущий",
                font=("Arial", 10),
                bg="#9E9E9E",
                fg="white",
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                command=self.prev_question
            )
            prev_btn.pack(side=tk.LEFT)

        if self.current_question_index < total_questions - 1:
            next_btn = tk.Button(
                nav_frame,
                text="Следующий →",
                font=("Arial", 10),
                bg="#2196F3",
                fg="white",
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                command=self.next_question
            )
            next_btn.pack(side=tk.RIGHT)
        else:
            finish_btn = tk.Button(
                nav_frame,
                text="Завершить тест",
                font=("Arial", 10, "bold"),
                bg="#4CAF50",
                fg="white",
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                command=self.finish_test
            )
            finish_btn.pack(side=tk.RIGHT)

    def show_single_choice(self, parent, question_data):
        """Display single choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved = self.user_answers.get(question_id, None)
        
        # Use IntVar with default -1 to ensure no radio is selected initially
        var = tk.IntVar(value=-1)
        
        for i, option in enumerate(options):
            rb = tk.Radiobutton(
                parent,
                text=option,
                variable=var,
                value=i,
                font=("Arial", 10),
                bg="white",
                wraplength=800,
                justify=tk.LEFT,
                cursor="hand2"
            )
            rb.pack(anchor=tk.W, pady=5)
            if saved is not None and i == int(saved):
                rb.select()
        
        # Store the variable for later retrieval
        parent.var = var

    def show_multiple_choice(self, parent, question_data):
        """Display multiple choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved_answers = self.user_answers.get(question_id, [])

        vars_list = []
        for i, option in enumerate(options):
            var = tk.BooleanVar(value=str(i) in saved_answers)
            cb = tk.Checkbutton(
                parent,
                text=option,
                variable=var,
                font=("Arial", 10),
                bg="white",
                wraplength=800,
                justify=tk.LEFT,
                cursor="hand2"
            )
            cb.pack(anchor=tk.W, pady=5)
            vars_list.append((str(i), var))

        parent.vars = vars_list

    def show_ordering(self, parent, question_data):
        """Display ordering question with up/down buttons."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved_order = self.user_answers.get(question_id, list(range(len(options))))

        # Frame for the listbox and buttons
        content_frame = tk.Frame(parent, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Listbox with current order
        list_frame = tk.Frame(content_frame, bg="white")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set,
            bg="white",
            selectbackground="#2196F3",
            height=10
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox with current order
        for idx in saved_order:
            listbox.insert(tk.END, f"{options[idx]}")

        # Buttons frame
        btn_frame = tk.Frame(content_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(
            btn_frame,
            text="↑ Вверх",
            font=("Arial", 9),
            bg="#E0E0E0",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.move_up(listbox, options, saved_order)
        ).pack(pady=5, fill=tk.X)

        tk.Button(
            btn_frame,
            text="↓ Вниз",
            font=("Arial", 9),
            bg="#E0E0E0",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.move_down(listbox, options, saved_order)
        ).pack(pady=5, fill=tk.X)

        parent.listbox = listbox
        parent.options = options
        parent.order = saved_order

    def move_up(self, listbox, options, order):
        """Move selected item up in ordering."""
        selection = listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx > 0:
            order[idx], order[idx-1] = order[idx-1], order[idx]
            listbox.delete(0, tk.END)
            for i in order:
                listbox.insert(tk.END, f"{options[i]}")
            listbox.selection_set(idx-1)

    def move_down(self, listbox, options, order):
        """Move selected item down in ordering."""
        selection = listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(order) - 1:
            order[idx], order[idx+1] = order[idx+1], order[idx]
            listbox.delete(0, tk.END)
            for i in order:
                listbox.insert(tk.END, f"{options[i]}")
            listbox.selection_set(idx+1)

    def show_true_false(self, parent, question_data):
        """Display true/false question."""
        saved = self.user_answers.get(question_data.get("id"), None)
        var = tk.StringVar(value=saved if saved in ("true", "false") else "")

        tk.Radiobutton(
            parent,
            text="Верно",
            variable=var,
            value="true",
            font=("Arial", 10),
            bg="white",
            cursor="hand2"
        ).pack(anchor=tk.W, pady=10)

        tk.Radiobutton(
            parent,
            text="Неверно",
            variable=var,
            value="false",
            font=("Arial", 10),
            bg="white",
            cursor="hand2"
        ).pack(anchor=tk.W, pady=10)

        parent.var = var

    def save_current_answer(self):
        """Save the current question's answer."""
        if not hasattr(self, '_current_question_widget'):
            return

        question_data = self._current_question_data
        if not question_data:
            return

        question_id = question_data.get("id")
        question_type = question_data.get("type", "single_choice")
        widget = self._current_question_widget

        if question_type == "single_choice":
            if hasattr(widget, 'var'):
                val = widget.var.get()
                # -1 means no selection (IntVar default)
                if val == -1:
                    self.user_answers.pop(question_id, None)
                else:
                    self.user_answers[question_id] = str(val)

        elif question_type == "multiple_choice":
            if hasattr(widget, 'vars'):
                selected = []
                for idx, var in widget.vars:
                    if var.get():
                        selected.append(idx)
                self.user_answers[question_id] = selected

        elif question_type == "ordering":
            if hasattr(widget, 'order'):
                self.user_answers[question_id] = widget.order.copy()

        elif question_type == "true_false":
            if hasattr(widget, 'var'):
                val = widget.var.get()
                # Empty string means no selection
                if val not in ("true", "false"):
                    self.user_answers.pop(question_id, None)
                else:
                    self.user_answers[question_id] = val

    def next_question(self):
        """Go to next question."""
        self.save_current_answer()
        self.current_question_index += 1
        self.show_question()

    def prev_question(self):
        """Go to previous question."""
        self.save_current_answer()
        self.current_question_index -= 1
        self.show_question()

    def finish_test(self):
        """Finish the test and show results."""
        self.save_current_answer()

        # Confirm finish
        if not messagebox.askyesno("Завершение теста", "Вы уверены, что хотите завершить тест?"):
            return

        # Calculate results
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        questions = self.current_questions
        correct_count = 0
        incorrect_count = 0
        results_details = []

        for question in questions:
            question_id = question.get("id")
            question_type = question.get("type")
            correct_answer = question.get("correct_answer")
            user_answer = self.user_answers.get(question_id)
            explanation = question.get("explanation", "")

            is_correct = False

            if question_type == "single_choice":
                if user_answer and int(user_answer) == correct_answer[0]:
                    is_correct = True
            elif question_type == "multiple_choice":
                if user_answer and sorted([int(x) for x in user_answer]) == sorted(correct_answer):
                    is_correct = True
            elif question_type == "ordering":
                if user_answer and user_answer == correct_answer:
                    is_correct = True
            elif question_type == "true_false":
                if user_answer:
                    user_bool = user_answer == "true"
                    if user_bool == correct_answer:
                        is_correct = True

            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            results_details.append({
                "question_id": question_id,
                "question": question.get("question"),
                "type": question_type,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": explanation
            })

        # Save result
        result = {
            "last_name": self.user_data.get("last_name"),
            "first_name": self.user_data.get("first_name"),
            "total_questions": len(questions),
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "details": results_details
        }

        self.save_test_result(result)

        # Show results window
        self.show_results(result)

    def show_results(self, result):
        """Show test results."""
        self.clear_window()

        # Header
        header_frame = tk.Frame(self, bg="#4CAF50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Результаты тестирования",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        title_label.pack(pady=15, padx=20)

        # Results summary
        summary_frame = tk.Frame(self, bg="white", relief=tk.RIDGE, bd=2)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        summary_frame.configure(padx=20, pady=20)

        tk.Label(
            summary_frame,
            text=f"Тестируемый: {result['last_name']} {result['first_name']}",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W)

        tk.Label(
            summary_frame,
            text=f"Время прохождения: {int(result['duration_seconds'] // 60)} мин. {int(result['duration_seconds'] % 60)} сек.",
            font=("Arial", 10),
            bg="white",
            fg="#666"
        ).pack(anchor=tk.W, pady=(5, 10))

        # Score
        score_frame = tk.Frame(summary_frame, bg="white")
        score_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            score_frame,
            text=f"Правильных ответов: {result['correct_count']}/{result['total_questions']}",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#4CAF50" if result['correct_count'] == result['total_questions'] else "#FF9800"
        ).pack(anchor=tk.W)

        # Details button
        details_btn = tk.Button(
            summary_frame,
            text="Показать детализацию",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: self.show_details(result)
        )
        details_btn.pack(pady=(10, 0))

        # Export to PDF button
        pdf_btn = tk.Button(
            summary_frame,
            text="Экспорт в PDF",
            font=("Arial", 10),
            bg="#F44336",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: self.export_to_pdf(result)
        )
        pdf_btn.pack(pady=(10, 0))

        # Back to main button
        back_btn = tk.Button(
            summary_frame,
            text="Вернуться в главное меню",
            font=("Arial", 10),
            bg="#9E9E9E",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(pady=(10, 0))

    def show_details(self, result):
        """Show detailed results with explanations."""
        details_window = tk.Toplevel(self)
        details_window.title("Детализация результатов")
        details_window.geometry("900x700")
        details_window.configure(bg="#f0f0f0")

        # Header
        header_frame = tk.Frame(details_window, bg="#2196F3", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Детализация результатов",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=12, padx=20)

        # Scrollable content
        canvas = tk.Canvas(details_window, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add details
        for i, detail in enumerate(result["details"], 1):
            detail_frame = tk.Frame(scrollable_frame, bg="white", relief=tk.RIDGE, bd=1)
            detail_frame.pack(fill=tk.X, padx=10, pady=5)

            # Question number and status
            status_color = "#4CAF50" if detail["correct"] else "#F44336"
            status_text = "✓ Верно" if detail["correct"] else "✗ Неверно"

            tk.Label(
                detail_frame,
                text=f"Вопрос {i}: {status_text}",
                font=("Arial", 10, "bold"),
                bg="white",
                fg=status_color
            ).pack(anchor=tk.W, padx=10, pady=(10, 5))

            # Question text
            tk.Label(
                detail_frame,
                text=detail["question"],
                font=("Arial", 10),
                bg="white",
                fg="#333",
                wraplength=850,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(0, 10))

            # Explanation
            if not detail["correct"]:
                explanation_frame = tk.Frame(detail_frame, bg="#FFF9C4")
                explanation_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

                tk.Label(
                    explanation_frame,
                    text="Объяснение:",
                    font=("Arial", 9, "bold"),
                    bg="#FFF9C4",
                    fg="#333"
                ).pack(anchor=tk.W, padx=10, pady=(5, 0))

                tk.Label(
                    explanation_frame,
                    text=detail["explanation"],
                    font=("Arial", 9),
                    bg="#FFF9C4",
                    fg="#333",
                    wraplength=830,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, padx=10, pady=(0, 5))

                # Button to open regulation section
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
                    command=lambda d=detail: self.open_reglament(d)
                ).pack(side=tk.LEFT)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def open_reglament(self, detail):
        """Open regulation section based on explanation."""
        explanation = detail.get("explanation", "")

        # Parse section from explanation
        # For now, just open study mode
        from study_mode import StudyModeWindow
        self.study_window = StudyModeWindow(
            self,
            self.reglament,
            lambda: None
        )

    def export_to_pdf(self, result):
        """Export results to PDF."""
        try:
            from pdf_generator import generate_pdf
            generate_pdf(result, self.reglament)
            messagebox.showinfo("Успех", "PDF файл успешно создан!")
        except ImportError:
            messagebox.showerror("Ошибка", "Модуль генерации PDF не найден. Установите reportlab: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании PDF: {e}")

    def confirm_exit_test(self):
        """Confirm exit from test."""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти? Все ответы будут потеряны."):
            self.on_back()

    def clear_window(self):
        """Clear all widgets from window."""
        for widget in self.winfo_children():
            widget.destroy()
