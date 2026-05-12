#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized test mode window for taking tests.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import math
import random

from style_config import Colors, Fonts, Spacing


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
        self.max_reached_index = 0

        self.title("Режим тестирования")
        self.geometry("1000x700")
        self.configure(bg=Colors.BG)

        self.center_window()
        self.create_input_screen()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_back)

    def center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = 1000
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_modern_header(self, parent, text, back_cmd=None, bg=Colors.PRIMARY, back_text="←  Назад"):
        """Create a modern header bar."""
        header_frame = tk.Frame(parent, bg=bg, height=56)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        if back_cmd:
            back_btn = tk.Button(
                header_frame,
                text=back_text,
                font=Fonts.BODY,
                bg=bg,
                fg=Colors.TEXT_ON_PRIMARY,
                activebackground=Colors.PRIMARY_DARK,
                activeforeground=Colors.TEXT_ON_PRIMARY,
                relief=tk.FLAT,
                cursor="hand2",
                command=back_cmd,
                bd=0,
                padx=12,
                pady=8
            )

            def b_enter(e):
                back_btn.configure(bg=Colors.PRIMARY_DARK)
            def b_leave(e):
                back_btn.configure(bg=bg)
            back_btn.bind("<Enter>", b_enter)
            back_btn.bind("<Leave>", b_leave)
            back_btn.pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        title_label = tk.Label(
            header_frame,
            text=text,
            font=Fonts.HEADING,
            bg=bg,
            fg=Colors.TEXT_ON_PRIMARY
        )
        title_label.pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.LG)

        return header_frame

    def _create_modern_button(self, parent, text, command, bg=Colors.SUCCESS,
                               hover_bg=None, **kwargs):
        """Create a modern styled button with hover effect."""
        if hover_bg is None:
            hover_bg = Colors.SUCCESS_LIGHT if bg == Colors.SUCCESS else Colors.PRIMARY_LIGHT

        btn = tk.Button(
            parent,
            text=text,
            font=Fonts.BUTTON,
            bg=bg,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=hover_bg,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=command,
            bd=0,
            padx=kwargs.pop('padx', 28),
            pady=kwargs.pop('pady', 10),
            **kwargs
        )

        def b_enter(e):
            btn.configure(bg=hover_bg)
        def b_leave(e):
            btn.configure(bg=bg)
        btn.bind("<Enter>", b_enter)
        btn.bind("<Leave>", b_leave)

        return btn

    def create_input_screen(self):
        """Create the input screen for user data and question count."""
        self.clear_window()

        self._create_modern_header(self, "Ввод данных для тестирования",
                                   back_cmd=self.on_back)

        # Main card container
        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        card_inner = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        content = tk.Frame(card_inner, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXXL, pady=Spacing.XXXL)

        # Title
        tk.Label(
            content,
            text="Введите ваши данные",
            font=Fonts.TITLE_SMALL,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(pady=(0, Spacing.XL))

        # Last name
        self.last_name_var = tk.StringVar(value=self.user_data.get("last_name", ""))
        entry_frame = tk.Frame(content, bg=Colors.CARD_BG)
        entry_frame.pack(fill=tk.X, pady=Spacing.XS)

        tk.Label(
            entry_frame,
            text="Фамилия:",
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        e_frame = tk.Frame(entry_frame, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=42)
        e_frame.pack(fill=tk.X)
        e_frame.pack_propagate(False)

        entry = tk.Entry(
            e_frame,
            textvariable=self.last_name_var,
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def fi1(e):
            e_frame.configure(bg=Colors.PRIMARY)
        def fo1(e):
            e_frame.configure(bg=Colors.BORDER_LIGHT)
        entry.bind("<FocusIn>", fi1)
        entry.bind("<FocusOut>", fo1)

        # First name
        self.first_name_var = tk.StringVar(value=self.user_data.get("first_name", ""))
        entry_frame2 = tk.Frame(content, bg=Colors.CARD_BG)
        entry_frame2.pack(fill=tk.X, pady=Spacing.XS)

        tk.Label(
            entry_frame2,
            text="Имя:",
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        e_frame2 = tk.Frame(entry_frame2, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=42)
        e_frame2.pack(fill=tk.X)
        e_frame2.pack_propagate(False)

        entry2 = tk.Entry(
            e_frame2,
            textvariable=self.first_name_var,
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY
        )
        entry2.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def fi2(e):
            e_frame2.configure(bg=Colors.PRIMARY)
        def fo2(e):
            e_frame2.configure(bg=Colors.BORDER_LIGHT)
        entry2.bind("<FocusIn>", fi2)
        entry2.bind("<FocusOut>", fo2)

        # Question count
        self.question_count_var = tk.StringVar(value="10")
        entry_frame3 = tk.Frame(content, bg=Colors.CARD_BG)
        entry_frame3.pack(fill=tk.X, pady=Spacing.XS)

        tk.Label(
            entry_frame3,
            text="Количество вопросов:",
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        tk.Label(
            entry_frame3,
            text=f"Доступно вопросов в базе: {len(self.test_questions)}",
            font=Fonts.BODY_SMALL,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        e_frame3 = tk.Frame(entry_frame3, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=42)
        e_frame3.pack(fill=tk.X)
        e_frame3.pack_propagate(False)

        entry3 = tk.Entry(
            e_frame3,
            textvariable=self.question_count_var,
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY
        )
        entry3.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def fi3(e):
            e_frame3.configure(bg=Colors.PRIMARY)
        def fo3(e):
            e_frame3.configure(bg=Colors.BORDER_LIGHT)
        entry3.bind("<FocusIn>", fi3)
        entry3.bind("<FocusOut>", fo3)

        # Start button
        btn_outer = tk.Frame(content, bg=Colors.CARD_BG)
        btn_outer.pack(pady=(Spacing.XXL, 0))

        self._create_modern_button(
            btn_outer,
            "▶  Начать тестирование",
            self.start_test,
            bg=Colors.SUCCESS,
            hover_bg=Colors.SUCCESS_LIGHT,
            padx=40,
            pady=12
        ).pack()

    def _convert_question_to_internal(self, q):
        """Convert question to internal format, handling both old and new formats."""
        internal_q = q.copy()

        # Handle type mapping (old format uses radio/checkbox/sequence/truefalse)
        type_map = {
            "radio": "single_choice",
            "checkbox": "multiple_choice",
            "sequence": "ordering",
            "truefalse": "true_false"
        }
        q_type = q.get("type", "")
        internal_q["type"] = type_map.get(q_type, q_type)

        # Handle question text (new format uses 'question', old uses 'text')
        internal_q["question"] = q.get("question", q.get("text", ""))

        # Handle correct answer (new format uses 'correct_answer', old uses 'correct')
        # The internal format expects:
        # - single_choice: list with one index (e.g., [1])
        # - multiple_choice: list of indices (e.g., [0, 1, 2])
        # - true_false: boolean
        # - ordering: list of strings (correct order)
        options = q.get("options", [])
        correct = q.get("correct_answer", q.get("correct"))

        # Convert correct_answer to internal format based on type
        internal_type = internal_q["type"]
        if internal_type == "single_choice":
            if isinstance(correct, int):
                internal_q["correct_answer"] = [correct]
            elif isinstance(correct, list):
                internal_q["correct_answer"] = correct
            elif correct in options:
                internal_q["correct_answer"] = [options.index(correct)]
            else:
                internal_q["correct_answer"] = []
        elif internal_type == "multiple_choice":
            if isinstance(correct, list):
                # Check if elements are integers (new format) or strings (old format)
                if correct and isinstance(correct[0], int):
                    internal_q["correct_answer"] = correct
                else:
                    internal_q["correct_answer"] = [options.index(c) for c in correct if c in options]
            else:
                internal_q["correct_answer"] = []
        else:
            # true_false and ordering - use as is
            internal_q["correct_answer"] = correct

        # Handle reference field (new format) - pass through for regulation link
        if "reference" in q:
            internal_q["reference"] = q["reference"]

        # Handle explanation field (new format) - pass through for display
        if "explanation" in q:
            internal_q["explanation"] = q["explanation"]

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

        self.user_data["last_name"] = last_name
        self.user_data["first_name"] = first_name
        self.save_user_data()

        selected_questions = self._select_questions_with_constraints(self.test_questions, question_count)
        self.current_questions = [self._convert_question_to_internal(q) for q in selected_questions]

        self.current_question_index = 0
        self.user_answers = {}
        self.start_time = datetime.now()
        self.max_reached_index = 0

        self.show_question()

    def _show_progress_bar(self, parent, current, total):
        """Show modern progress bar."""
        progress_frame = tk.Frame(parent, bg=Colors.PROGRESS_BG, height=36)
        progress_frame.pack(fill=tk.X)
        progress_frame.pack_propagate(False)

        pct = (current + 1) / total if total > 0 else 0
        fill_frame = tk.Frame(progress_frame, bg=Colors.PROGRESS_FILL, bd=0, highlightthickness=0)
        fill_frame.place(relwidth=pct, relheight=1.0)

        progress_text = tk.Label(
            progress_frame,
            text=f"Вопрос {current + 1} из {total}",
            font=Fonts.BODY,
            bg=Colors.PROGRESS_BG if pct < 0.5 else Colors.PROGRESS_FILL,
            fg=Colors.TEXT_ON_PRIMARY if pct >= 0.5 else Colors.PRIMARY
        )
        progress_text.place(relx=0.5, rely=0.5, anchor="center")

    def show_question(self):
        """Display the current question."""
        self.clear_window()

        total_questions = len(self.current_questions)
        question_data = self.current_questions[self.current_question_index]

        # Header
        self._create_modern_header(self, "Тестирование",
                                   back_cmd=self.confirm_exit_test,
                                   back_text="←  Завершить")

        # Progress bar
        self._show_progress_bar(self, self.current_question_index, total_questions)

        # Question card
        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        card_inner = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        question_frame = tk.Frame(card_inner, bg=Colors.CARD_BG)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        # Question number badge
        q_header = tk.Frame(question_frame, bg=Colors.PRIMARY_BG, bd=0, highlightthickness=0)
        q_header.pack(fill=tk.X, pady=(0, Spacing.LG))

        tk.Label(
            q_header,
            text=f"Вопрос {self.current_question_index + 1}",
            font=Fonts.SUBHEADING,
            bg=Colors.PRIMARY_BG,
            fg=Colors.PRIMARY
        ).pack(padx=Spacing.LG, pady=Spacing.SM)

        # Question text
        question_text = question_data.get("question", "")
        tk.Label(
            question_frame,
            text=question_text,
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W,
            wraplength=880,
            justify=tk.LEFT
        ).pack(fill=tk.X, pady=(0, Spacing.XL))

        # Answer options frame
        options_frame = tk.Frame(question_frame, bg=Colors.CARD_BG)
        options_frame.pack(fill=tk.BOTH, expand=True)

        question_type = question_data.get("type", "single_choice")

        self._current_question_widget = options_frame
        self._current_question_data = question_data

        type_handlers = {
            "single_choice": self.show_single_choice,
            "multiple_choice": self.show_multiple_choice,
            "ordering": self.show_ordering,
            "true_false": self.show_true_false,
        }
        handler = type_handlers.get(question_type, self.show_single_choice)
        handler(options_frame, question_data)

        # Navigation buttons
        nav_frame = tk.Frame(question_frame, bg=Colors.CARD_BG)
        nav_frame.pack(fill=tk.X, pady=(Spacing.XL, 0))

        if self.current_question_index > 0 and self.current_question_index == self.max_reached_index:
            self._create_modern_button(
                nav_frame,
                "←  Предыдущий",
                self.prev_question,
                bg=Colors.TEXT_SECONDARY,
                hover_bg=Colors.PRIMARY_DARK,
                padx=20,
                pady=8
            ).pack(side=tk.LEFT)

        if self.current_question_index < total_questions - 1:
            self._create_modern_button(
                nav_frame,
                "Следующий  →",
                self.next_question,
                bg=Colors.PRIMARY,
                hover_bg=Colors.PRIMARY_LIGHT,
                padx=20,
                pady=8
            ).pack(side=tk.RIGHT)
        else:
            self._create_modern_button(
                nav_frame,
                "✓  Завершить тест",
                self.finish_test,
                bg=Colors.SUCCESS,
                hover_bg=Colors.SUCCESS_LIGHT,
                padx=20,
                pady=8
            ).pack(side=tk.RIGHT)

    def _create_option_row(self, parent, text, selected=False, callback=None):
        """Create a modern clickable option row."""
        outer = tk.Frame(parent, bg=Colors.PRIMARY if selected else Colors.BORDER_LIGHT,
                         bd=0, highlightthickness=0)
        inner = tk.Frame(outer, bg=Colors.PRIMARY_BG if selected else Colors.CARD_BG,
                         bd=0, highlightthickness=0, cursor="hand2")

        for el in (outer, inner):
            el.pack(fill=tk.X)
            if el is inner:
                el.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        label = tk.Label(
            inner,
            text=text,
            font=Fonts.BODY_LARGE,
            bg=inner.cget('bg'),
            fg=Colors.PRIMARY if selected else Colors.TEXT_PRIMARY,
            wraplength=750,
            justify=tk.LEFT,
            anchor=tk.W
        )
        label.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)

        if callback:
            for w in (inner, label):
                w.bind("<Button-1>", lambda e, inn=inner, out=outer, lbl=label:
                       callback(inn, out, lbl))
                w.bind("<Enter>", lambda e, inn=inner:
                       inn.configure(bg=Colors.SURFACE) if not selected else None)
                w.bind("<Leave>", lambda e, inn=inner:
                       inn.configure(bg=Colors.PRIMARY_BG if selected else Colors.CARD_BG))

        return outer, inner, label

    def show_single_choice(self, parent, question_data):
        """Display single choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved = self.user_answers.get(question_id, None)

        var = tk.IntVar(value=-1)
        if saved is not None:
            var.set(int(saved))

        def make_select(idx, circle, inner, outer, label):
            def on_click(e):
                var.set(idx)
                # Reset all
                for child in parent.winfo_children():
                    for sub in child.winfo_children():
                        if isinstance(sub, tk.Frame):
                            sub.configure(bg=Colors.CARD_BG)
                            if sub.master:
                                sub.master.configure(bg=Colors.BORDER_LIGHT)
                        for gc in sub.winfo_children():
                            if isinstance(gc, tk.Label):
                                if hasattr(gc, 'is_circle') and gc.is_circle:
                                    gc.configure(text="○", fg=Colors.TEXT_SECONDARY)
                # Activate this
                circle.configure(text="●", fg=Colors.PRIMARY)
                inner.configure(bg=Colors.PRIMARY_BG)
                outer.configure(bg=Colors.PRIMARY)
            return on_click

        for i, option in enumerate(options):
            outer = tk.Frame(parent, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
            outer.pack(fill=tk.X, pady=Spacing.XS)

            inner = tk.Frame(outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            circle = tk.Label(
                inner,
                text="●" if saved is not None and i == int(saved) else "○",
                font=("Segoe UI", 14, "bold"),
                bg=inner.cget('bg'),
                fg=Colors.PRIMARY if (saved is not None and i == int(saved)) else Colors.TEXT_SECONDARY
            )
            circle.is_circle = True
            circle.pack(side=tk.LEFT, padx=(Spacing.LG, 0), pady=Spacing.MD)

            text_label = tk.Label(
                inner,
                text=option,
                font=Fonts.BODY_LARGE,
                bg=inner.cget('bg'),
                fg=Colors.TEXT_PRIMARY,
                wraplength=750,
                justify=tk.LEFT,
                anchor=tk.W
            )
            text_label.pack(side=tk.LEFT, padx=Spacing.MD, pady=Spacing.MD, fill=tk.X, expand=True)

            if saved is not None and i == int(saved):
                inner.configure(bg=Colors.PRIMARY_BG)
                outer.configure(bg=Colors.PRIMARY)

            callback = make_select(i, circle, inner, outer, text_label)
            for w in (inner, circle, text_label):
                w.bind("<Button-1>", callback)
                w.bind("<Enter>", lambda e, inn=inner:
                       inn.configure(bg=Colors.SURFACE)
                       if var.get() != i else None)
                w.bind("<Leave>", lambda e, inn=inner:
                       inn.configure(bg=Colors.PRIMARY_BG if var.get() == i else Colors.CARD_BG))

        parent.var = var

    def show_multiple_choice(self, parent, question_data):
        """Display multiple choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved_answers = self.user_answers.get(question_id, [])

        vars_list = []
        for i, option in enumerate(options):
            var = tk.BooleanVar(value=str(i) in saved_answers)
            outer = tk.Frame(parent, bg=Colors.PRIMARY if str(i) in saved_answers
                             else Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
            outer.pack(fill=tk.X, pady=Spacing.XS)

            inner = tk.Frame(outer, bg=Colors.PRIMARY_BG if str(i) in saved_answers
                             else Colors.CARD_BG, bd=0, highlightthickness=0, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            selected = str(i) in saved_answers
            cb = "☑" if selected else "☐"
            lbl = tk.Label(
                inner,
                text=f"{cb}  {option}",
                font=Fonts.BODY_LARGE,
                bg=inner.cget('bg'),
                fg=Colors.PRIMARY if selected else Colors.TEXT_PRIMARY,
                wraplength=750,
                justify=tk.LEFT,
                anchor=tk.W
            )
            lbl.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)

            def toggle(e, idx=i, v=var, label=lbl, inn=inner, out=outer, opts=options):
                v.set(not v.get())
                if v.get():
                    label.configure(text=f"☑  {opts[idx]}", bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY)
                    inn.configure(bg=Colors.PRIMARY_BG)
                    out.configure(bg=Colors.PRIMARY)
                else:
                    label.configure(text=f"☐  {opts[idx]}", bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY)
                    inn.configure(bg=Colors.CARD_BG)
                    out.configure(bg=Colors.BORDER_LIGHT)

            for w in (inner, lbl):
                w.bind("<Button-1>", toggle)

            vars_list.append((str(i), var))

        parent.vars = vars_list

    def show_ordering(self, parent, question_data):
        """Display ordering question with up/down buttons."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved_order = self.user_answers.get(question_id, list(range(len(options))))

        content_frame = tk.Frame(parent, bg=Colors.CARD_BG)
        content_frame.pack(fill=tk.BOTH, expand=True)

        list_frame = tk.Frame(content_frame, bg=Colors.CARD_BG)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            list_frame,
            font=Fonts.BODY_LARGE,
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY,
            activestyle='none',
            height=10,
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for idx in saved_order:
            listbox.insert(tk.END, f"  {idx + 1}. {options[idx]}")

        btn_frame = tk.Frame(content_frame, bg=Colors.CARD_BG)
        btn_frame.pack(side=tk.RIGHT, padx=(Spacing.LG, 0))

        tk.Button(
            btn_frame,
            text="↑  Вверх",
            font=("Segoe UI", 10),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=12,
            pady=6,
            command=lambda: self.move_up(listbox, options, saved_order)
        ).pack(pady=Spacing.XS, fill=tk.X)

        tk.Button(
            btn_frame,
            text="↓  Вниз",
            font=("Segoe UI", 10),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=12,
            pady=6,
            command=lambda: self.move_down(listbox, options, saved_order)
        ).pack(pady=Spacing.XS, fill=tk.X)

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
            for i, oi in enumerate(order):
                listbox.insert(tk.END, f"  {i + 1}. {options[oi]}")
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
            for i, oi in enumerate(order):
                listbox.insert(tk.END, f"  {i + 1}. {options[oi]}")
            listbox.selection_set(idx+1)

    def show_true_false(self, parent, question_data):
        """Display true/false question."""
        saved = self.user_answers.get(question_data.get("id"), None)
        var = tk.StringVar(value=saved if saved in ("true", "false") else "")

        for val, text in [("true", "Верно"), ("false", "Неверно")]:
            selected = saved == val
            outer = tk.Frame(parent, bg=Colors.PRIMARY if selected else Colors.BORDER_LIGHT,
                             bd=0, highlightthickness=0)
            outer.pack(fill=tk.X, pady=Spacing.XS)

            inner = tk.Frame(outer, bg=Colors.PRIMARY_BG if selected else Colors.CARD_BG,
                             bd=0, highlightthickness=0, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            icon = "●" if selected else "○"
            lbl = tk.Label(
                inner,
                text=f"{icon}  {text}",
                font=Fonts.BODY_LARGE,
                bg=inner.cget('bg'),
                fg=Colors.PRIMARY if selected else Colors.TEXT_PRIMARY,
                anchor=tk.W
            )
            lbl.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)

            def make_toggle(v=val, txt=text, inn=inner, out=outer, label=lbl):
                def on_click(e):
                    var.set(v)
                    # Reset all siblings
                    for sibling in parent.winfo_children():
                        sib_outer = sibling
                        for sib_inner in sib_outer.winfo_children():
                            if isinstance(sib_inner, tk.Frame):
                                sib_inner.configure(bg=Colors.CARD_BG)
                                sib_outer.configure(bg=Colors.BORDER_LIGHT)
                                for sib_label in sib_inner.winfo_children():
                                    if isinstance(sib_label, tk.Label):
                                        old_txt = sib_label.cget('text')
                                        if old_txt.startswith("●"):
                                            sib_label.configure(text="○ " + old_txt[2:],
                                                                bg=Colors.CARD_BG,
                                                                fg=Colors.TEXT_PRIMARY)
                                        elif old_txt.startswith("○"):
                                            pass  # already unchecked
                    # Activate this
                    label.configure(text=f"●  {txt}", bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY)
                    inn.configure(bg=Colors.PRIMARY_BG)
                    out.configure(bg=Colors.PRIMARY)
                return on_click

            callback = make_toggle()
            for w in (inner, lbl):
                w.bind("<Button-1>", callback)

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
                if val == -1:
                    self.user_answers.pop(question_id, None)
                else:
                    self.user_answers[question_id] = str(val)

        elif question_type == "multiple_choice":
            if hasattr(widget, 'vars'):
                selected = [idx for idx, var in widget.vars if var.get()]
                self.user_answers[question_id] = selected

        elif question_type == "ordering":
            if hasattr(widget, 'order'):
                self.user_answers[question_id] = widget.order.copy()

        elif question_type == "true_false":
            if hasattr(widget, 'var'):
                val = widget.var.get()
                if val not in ("true", "false"):
                    self.user_answers.pop(question_id, None)
                else:
                    self.user_answers[question_id] = val

    def is_current_question_answered(self):
        """Check if the current question has been answered by examining widget state."""
        if not hasattr(self, '_current_question_widget') or not hasattr(self, '_current_question_data'):
            return True

        question_data = self._current_question_data
        if not question_data:
            return True

        question_type = question_data.get("type", "single_choice")
        widget = self._current_question_widget

        # Check widget state directly (answer may not be saved to user_answers yet)
        if question_type == "single_choice":
            if hasattr(widget, 'var'):
                return widget.var.get() != -1
            return False

        elif question_type == "multiple_choice":
            if hasattr(widget, 'vars'):
                return any(var.get() for _, var in widget.vars)
            return False

        elif question_type == "ordering":
            if hasattr(widget, 'order'):
                return len(widget.order) > 0
            return False

        elif question_type == "true_false":
            if hasattr(widget, 'var'):
                return widget.var.get() in ("true", "false")
            return False

        return True

    def show_validation_error(self):
        """Show validation error message."""
        messagebox.showwarning("Внимание", "Пожалуйста, выберите вариант ответа перед продолжением.")

    def _select_questions_with_constraints(self, all_questions, count):
        """Select questions with required distribution constraints:
        - 20% from IDs 201-240
        - 15% type 'ordering'
        - 20% type 'multiple_choice'
        """
        # Categorize questions into pools
        pool_201_240 = [q for q in all_questions if 201 <= q.get("id", 0) <= 240]
        pool_ordering = [q for q in all_questions if q.get("type") == "ordering"]
        pool_multiple = [q for q in all_questions if q.get("type") == "multiple_choice"]

        # Minimum targets (capped by availability)
        min_201_240 = min(max(1, math.ceil(count * 0.2)), len(pool_201_240))
        min_ordering = min(max(1, math.ceil(count * 0.15)), len(pool_ordering))
        min_multiple = min(max(1, math.ceil(count * 0.2)), len(pool_multiple))

        selected = []
        selected_ids = set()

        def pick_from_pool(pool, n):
            """Pick n items from pool not already selected."""
            candidates = [q for q in pool if q["id"] not in selected_ids]
            random.shuffle(candidates)
            take = min(n, len(candidates))
            for q in candidates[:take]:
                selected.append(q)
                selected_ids.add(q["id"])
            return take

        # Phase 1: Pick from IDs 201-240
        pick_from_pool(pool_201_240, min_201_240)

        # Phase 2: Fill ordering quota
        current_ordering = sum(1 for q in selected if q.get("type") == "ordering")
        if current_ordering < min_ordering:
            pick_from_pool(pool_ordering, min_ordering - current_ordering)

        # Phase 3: Fill multiple_choice quota
        current_multiple = sum(1 for q in selected if q.get("type") == "multiple_choice")
        if current_multiple < min_multiple:
            pick_from_pool(pool_multiple, min_multiple - current_multiple)

        # Phase 4: Fill remaining from all questions
        if len(selected) < count:
            remaining = [q for q in all_questions if q["id"] not in selected_ids]
            random.shuffle(remaining)
            take = min(count - len(selected), len(remaining))
            for q in remaining[:take]:
                selected.append(q)
                selected_ids.add(q["id"])

        random.shuffle(selected)
        return selected

    def next_question(self):
        """Go to next question."""
        if not self.is_current_question_answered():
            self.show_validation_error()
            return
        self.save_current_answer()
        self.current_question_index += 1
        self.max_reached_index = max(self.max_reached_index, self.current_question_index)
        self.show_question()

    def prev_question(self):
        """Go to previous question."""
        self.save_current_answer()
        self.current_question_index -= 1
        self.show_question()

    def _parse_reference(self, reference):
        """
        Parse reference field to extract section reference for regulation link.
        Returns: (section_ref, _) where section_ref is e.g., "2.1"
        """
        if not reference:
            return None, ""

        # Extract section reference (e.g., "п. 2.1" -> "2.1")
        import re
        match = re.search(r'(\d+\.\d+)', reference)
        if not match:
            return None, reference

        section_ref = match.group(1)

        # Check if there's additional text besides the section reference
        # e.g., "п. 2.1 (требуется штамп «ОПЛАЧЕНО»)" -> display the part after section
        # If reference is just "п. 2.1" or similar, we'll look up the section title
        cleaned_ref = re.sub(r'[пp]\.\s*', '', reference).strip()
        if '(' in cleaned_ref:
            # Has additional text - use the text in parentheses as display
            paren_match = re.search(r'\((.*?)\)', reference)
            if paren_match:
                return section_ref, paren_match.group(1).strip()

        return section_ref, ""

    def _get_regulation_section_title(self, section_ref):
        """Get the title of a regulation section by reference (e.g., '2.1')."""
        if not self.reglament or not section_ref:
            return ""

        sections = self.reglament.get("sections", [])
        for section in sections:
            section_id = str(section.get("id", ""))
            if section_id == section_ref.split('.')[0]:
                # Found main section, now look for subsection
                if '.' in section_ref:
                    subsection_id = section_ref.split('.')[1]
                    content = section.get("content", [])
                    for item in content:
                        if item.get("type") == "subsection":
                            # Check if subsection title contains the reference
                            title = item.get("title", "")
                            if f"{section_ref}" in title or f".{subsection_id}" in title:
                                return title
                return section.get("title", "")
        return ""

    def finish_test(self):
        """Finish the test and show results."""
        if not self.is_current_question_answered():
            self.show_validation_error()
            return

        self.save_current_answer()

        if not messagebox.askyesno("Завершение теста", "Вы уверены, что хотите завершить тест?"):
            return

        # Check if all questions are answered
        unanswered = []
        for i, question in enumerate(self.current_questions, 1):
            qid = question.get("id")
            if qid not in self.user_answers:
                unanswered.append(i)

        if unanswered:
            msg = f"Следующие вопросы не отвечены: {', '.join(map(str, unanswered[:5]))}"
            if len(unanswered) > 5:
                msg += f" и еще {len(unanswered) - 5}"
            messagebox.showwarning("Не все вопросы отвечены", msg + "\nПожалуйста, ответьте на все вопросы перед завершением.")
            return

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
            reference = question.get("reference", "")

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

            # Use explanation field from question for display, reference for regulation link
            question_explanation = question.get("explanation", "")
            section_ref = ""
            if reference:
                section_ref, _ = self._parse_reference(reference)

            results_details.append({
                "question_id": question_id,
                "question": question.get("question"),
                "type": question_type,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": question_explanation,
                "reference": reference,
                "section_ref": section_ref
            })

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
        self.show_results(result)

    def show_results(self, result):
        """Show test results with modern card design."""
        self.clear_window()

        # Header
        self._create_modern_header(self, "Результаты тестирования",
                                   bg=Colors.SUCCESS)

        # Results card
        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        card = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXXL, pady=Spacing.XXXL)

        # User info
        tk.Label(
            content,
            text=f"{result['last_name']} {result['first_name']}",
            font=Fonts.TITLE_MEDIUM,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text=f"Время прохождения: {int(result['duration_seconds'] // 60)} мин. {int(result['duration_seconds'] % 60)} сек.",
            font=Fonts.BODY,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor=tk.W, pady=(Spacing.SM, Spacing.XL))

        # Score section
        score_card = tk.Frame(content, bg=Colors.PRIMARY_BG, bd=0, highlightthickness=0)
        score_card.pack(fill=tk.X, pady=(0, Spacing.XXL))

        score_inner = tk.Frame(score_card, bg=Colors.PRIMARY_BG)
        score_inner.pack(padx=Spacing.XXL, pady=Spacing.XXL)

        score_pct = round(result['correct_count'] / result['total_questions'] * 100)
        score_color = Colors.SUCCESS if score_pct >= 80 else (Colors.WARNING if score_pct >= 50 else Colors.ERROR)

        tk.Label(
            score_inner,
            text=f"{result['correct_count']} / {result['total_questions']}",
            font=("Segoe UI", 32, "bold"),
            bg=Colors.PRIMARY_BG,
            fg=score_color
        ).pack()

        grade = "Отлично!" if score_pct >= 90 else ("Хорошо" if score_pct >= 70 else
               ("Удовлетворительно" if score_pct >= 50 else "Нужно повторить"))
        tk.Label(
            score_inner,
            text=f"{score_pct}% — {grade}",
            font=Fonts.HEADING,
            bg=Colors.PRIMARY_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(pady=(Spacing.SM, 0))

        # Action buttons
        btn_row = tk.Frame(content, bg=Colors.CARD_BG)
        btn_row.pack(fill=tk.X, pady=(0, Spacing.LG))

        self._create_modern_button(
            btn_row,
            "📊  Показать детализацию",
            lambda: self.show_details(result),
            bg=Colors.PRIMARY,
            hover_bg=Colors.PRIMARY_LIGHT,
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)

        btn_pdf = self._create_modern_button(
            btn_row,
            "📄  Экспорт в PDF",
            lambda: self.export_to_pdf(result),
            bg=Colors.ERROR,
            hover_bg=Colors.ERROR_DARK,
            padx=20,
            pady=8
        )
        btn_pdf.pack(side=tk.RIGHT)

        self._create_modern_button(
            content,
            "←  Вернуться в главное меню",
            self.on_back,
            bg=Colors.TEXT_SECONDARY,
            hover_bg=Colors.PRIMARY_DARK,
            padx=20,
            pady=8
        ).pack(pady=Spacing.SM, anchor=tk.W)

    def show_details(self, result):
        """Show detailed results with explanations in a modern window."""
        details_window = tk.Toplevel(self)
        details_window.title("Детализация результатов")
        details_window.geometry("900x700")
        details_window.configure(bg=Colors.BG)

        # Header
        header_frame = tk.Frame(details_window, bg=Colors.PRIMARY, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Детализация результатов",
            font=Fonts.HEADING,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY
        ).pack(pady=Spacing.MD, padx=Spacing.LG)

        # Scrollable content
        canvas = tk.Canvas(details_window, bg=Colors.BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, detail in enumerate(result["details"], 1):
            card_outer = tk.Frame(scrollable_frame, bg=Colors.BORDER_LIGHT, bd=0,
                                   highlightthickness=0)
            card_outer.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.SM)

            card_inner = tk.Frame(card_outer, bg=Colors.CARD_BG)
            card_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            detail_frame = tk.Frame(card_inner, bg=Colors.CARD_BG)
            detail_frame.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.LG)

            status_color = Colors.SUCCESS if detail["correct"] else Colors.ERROR
            status_text = "✓  Верно" if detail["correct"] else "✗  Неверно"

            tk.Label(
                detail_frame,
                text=f"Вопрос {i}: {status_text}",
                font=Fonts.SUBHEADING,
                bg=Colors.CARD_BG,
                fg=status_color
            ).pack(anchor=tk.W, pady=(0, Spacing.SM))

            tk.Label(
                detail_frame,
                text=detail["question"],
                font=Fonts.BODY,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_PRIMARY,
                wraplength=800,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, Spacing.MD))

            if not detail["correct"]:
                expl_outer = tk.Frame(detail_frame, bg=Colors.WARNING_BG, bd=0,
                                       highlightthickness=0)
                expl_outer.pack(fill=tk.X)

                expl_inner = tk.Frame(expl_outer, bg=Colors.WARNING_BG)
                expl_inner.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.MD)

                tk.Label(
                    expl_inner,
                    text="Объяснение:",
                    font=("Segoe UI", 10, "bold"),
                    bg=Colors.WARNING_BG,
                    fg=Colors.WARNING_DARK
                ).pack(anchor=tk.W)

                # Make explanation clickable if reference exists
                if detail.get("reference"):
                    expl_link = tk.Label(
                        expl_inner,
                        text=detail.get("explanation", detail.get("reference", "")),
                        font=("Segoe UI", 10, "underline"),
                        bg=Colors.WARNING_BG,
                        fg=Colors.PRIMARY,
                        cursor="hand2",
                        wraplength=760,
                        justify=tk.LEFT
                    )
                    expl_link.pack(anchor=tk.W, pady=(Spacing.XS, 0))

                    def make_click_handler(d=detail, win=details_window):
                        def on_click(e):
                            self.open_reglament(d, win)
                        return on_click

                    expl_link.bind("<Button-1>", make_click_handler(detail))
                    expl_link.bind("<Enter>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline", "bold")))
                    expl_link.bind("<Leave>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline")))
                else:
                    tk.Label(
                        expl_inner,
                        text=detail.get("explanation", ""),
                        font=("Segoe UI", 10),
                        bg=Colors.WARNING_BG,
                        fg=Colors.TEXT_PRIMARY,
                        wraplength=760,
                        justify=tk.LEFT
                    ).pack(anchor=tk.W, pady=(Spacing.XS, 0))

                open_btn = tk.Button(
                    detail_frame,
                    text="📖  Открыть регламент",
                    font=("Segoe UI", 9),
                    bg=Colors.PRIMARY_BG,
                    fg=Colors.PRIMARY,
                    activebackground=Colors.PRIMARY,
                    activeforeground=Colors.TEXT_ON_PRIMARY,
                    relief=tk.FLAT,
                    cursor="hand2",
                    command=lambda d=detail, win=details_window: self.open_reglament(d, win),
                    bd=0,
                    padx=10,
                    pady=4
                )

                def o_enter(e, b=open_btn):
                    b.configure(bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY)
                def o_leave(e, b=open_btn):
                    b.configure(bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY)

                open_btn.bind("<Enter>", o_enter)
                open_btn.bind("<Leave>", o_leave)
                open_btn.pack(anchor=tk.W, pady=(Spacing.SM, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def open_reglament(self, detail, parent_window=None):
        """Open regulation section based on reference."""
        from study_mode import StudyModeWindow
        section_ref = detail.get("section_ref", "")
        self.study_window = StudyModeWindow(
            parent_window or self,
            self.reglament,
            on_close=lambda: None,
            section_reference=section_ref
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
