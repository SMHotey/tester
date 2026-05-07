#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized scenario-based test mode window for testing by scenarios from test_scenarios.json.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from pathlib import Path

from style_config import Colors, Fonts, Spacing


class ScenarioTestModeWindow(tk.Toplevel):
    """Window for scenario-based test mode."""

    def __init__(self, parent, user_data, scenarios, reglament, save_user_data, save_test_result, on_back):
        """Initialize scenario test mode window."""
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.scenarios = scenarios
        self.reglament = reglament
        self.save_user_data = save_user_data
        self.save_test_result = save_test_result
        self.on_back = on_back

        self.current_questions = []
        self.current_question_index = 0
        self.user_answers = {}
        self.start_time = None
        self.selected_scenario = None

        self.title("Тестирование по сценарию")
        self.geometry("1000x700")
        self.configure(bg=Colors.BG)

        self.center_window()

        # Show scenario selection screen first
        self.create_scenario_selection_screen()

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

    def _create_modern_entry(self, parent, label, variable, subtitle=None):
        """Create a modern styled entry with label."""
        entry_frame = tk.Frame(parent, bg=Colors.CARD_BG)
        entry_frame.pack(fill=tk.X, pady=Spacing.XS)

        lbl = tk.Label(
            entry_frame,
            text=label,
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        )
        lbl.pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        if subtitle:
            tk.Label(
                entry_frame,
                text=subtitle,
                font=Fonts.BODY_SMALL,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_SECONDARY,
                anchor=tk.W
            ).pack(fill=tk.X, pady=(0, Spacing.SM))

        e_frame = tk.Frame(entry_frame, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=42)
        e_frame.pack(fill=tk.X)
        e_frame.pack_propagate(False)

        entry = tk.Entry(
            e_frame,
            textvariable=variable,
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

        def fi(e):
            e_frame.configure(bg=Colors.PRIMARY)
        def fo(e):
            e_frame.configure(bg=Colors.BORDER_LIGHT)
        entry.bind("<FocusIn>", fi)
        entry.bind("<FocusOut>", fo)

        return entry

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

    # ─── Scenario Selection Screen ───

    def create_scenario_selection_screen(self):
        """Create the scenario selection screen."""
        self.clear_window()

        self._create_modern_header(self, "Выбор сценария тестирования",
                                   back_cmd=self.on_back,
                                   bg=Colors.SECONDARY)

        # Main card
        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        card = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXXL, pady=Spacing.XXXL)

        tk.Label(
            content,
            text="Введите ваши данные",
            font=Fonts.TITLE_SMALL,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(pady=(0, Spacing.XL))

        self.last_name_var = tk.StringVar(value=self.user_data.get("last_name", ""))
        self._create_modern_entry(content, "Фамилия:", self.last_name_var)

        self.first_name_var = tk.StringVar(value=self.user_data.get("first_name", ""))
        self._create_modern_entry(content, "Имя:", self.first_name_var)

        # Scenario list section
        tk.Label(
            content,
            text="Выберите сценарий:",
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.XXL, Spacing.SM))

        list_frame = tk.Frame(content, bg=Colors.CARD_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(Spacing.SM, Spacing.LG))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scenario_listbox = tk.Listbox(
            list_frame,
            font=Fonts.BODY,
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.SECONDARY_BG,
            selectforeground=Colors.SECONDARY,
            activestyle='none',
            height=10,
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.scenario_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.scenario_listbox.yview)

        for scenario in self.scenarios:
            self.scenario_listbox.insert(tk.END, f"{scenario['id']} - {scenario['title']}")

        self.scenario_listbox.bind("<Double-1>", lambda e: self.select_scenario())

        # Start button
        self._create_modern_button(
            content,
            "▶  Выбрать сценарий и начать тест",
            self.select_scenario,
            bg=Colors.SECONDARY,
            hover_bg=Colors.SECONDARY_LIGHT,
            padx=40,
            pady=12
        ).pack()

    def select_scenario(self):
        """Handle scenario selection."""
        selection = self.scenario_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сценарий из списка")
            return

        scenario_index = selection[0]
        if scenario_index >= len(self.scenarios):
            return

        self.selected_scenario = self.scenarios[scenario_index]

        last_name = self.last_name_var.get().strip()
        first_name = self.first_name_var.get().strip()

        if not last_name or not first_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите фамилию и имя")
            return

        self.user_data["last_name"] = last_name
        self.user_data["first_name"] = first_name
        self.save_user_data()

        self.show_scenario_details()

    # ─── Scenario Details Screen ───

    def show_scenario_details(self):
        """Show selected scenario details and confirm start."""
        self.clear_window()

        self._create_modern_header(self, "Детали сценария",
                                   back_cmd=self.create_scenario_selection_screen,
                                   back_text="←  Назад к выбору",
                                   bg=Colors.SECONDARY)

        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        card = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXXL, pady=Spacing.XXXL)

        # Scenario name
        tk.Label(
            content,
            text=f"Сценарий: {self.selected_scenario['title']}",
            font=Fonts.TITLE_SMALL,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(0, Spacing.MD))

        # Description
        tk.Label(
            content,
            text=f"Описание: {self.selected_scenario['description']}",
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            wraplength=800,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, Spacing.LG))

        # Initial data
        initial_data = self.selected_scenario.get('initial_data', {})
        if initial_data:
            data_outer = tk.Frame(content, bg=Colors.SURFACE, bd=0, highlightthickness=0)
            data_outer.pack(fill=tk.X, pady=(0, Spacing.LG))

            data_content = tk.Frame(data_outer, bg=Colors.SURFACE)
            data_content.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.LG)

            tk.Label(
                data_content,
                text="Начальные данные:",
                font=Fonts.SUBHEADING,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor=tk.W, pady=(0, Spacing.SM))

            for key, value in initial_data.items():
                tk.Label(
                    data_content,
                    text=f"  - {key}: {value}",
                    font=Fonts.BODY,
                    bg=Colors.SURFACE,
                    fg=Colors.TEXT_SECONDARY,
                    justify=tk.LEFT
                ).pack(anchor=tk.W)

        # Question count badge
        q_count = len(self.selected_scenario.get('questions', []))
        badge = tk.Frame(content, bg=Colors.SECONDARY_BG, bd=0, highlightthickness=0)
        badge.pack(fill=tk.X, pady=(0, Spacing.XXL))

        tk.Label(
            badge,
            text=f"📝  Количество вопросов: {q_count}",
            font=Fonts.SUBHEADING,
            bg=Colors.SECONDARY_BG,
            fg=Colors.SECONDARY
        ).pack(padx=Spacing.LG, pady=Spacing.LG)

        # Start button
        self._create_modern_button(
            content,
            "▶  Начать тестирование по сценарию",
            self.start_scenario_test,
            bg=Colors.SECONDARY,
            hover_bg=Colors.SECONDARY_LIGHT,
            padx=40,
            pady=12
        ).pack()

    # ─── Test Execution ───

    def start_scenario_test(self):
        """Start the test with questions from the selected scenario."""
        scenario_questions = self.selected_scenario.get('questions', [])

        if not scenario_questions:
            messagebox.showerror("Ошибка", "В выбранном сценарии нет вопросов")
            return

        self.current_questions = scenario_questions
        self.current_question_index = 0
        self.user_answers = {}
        self.start_time = datetime.now()

        self.show_question()

    def show_question(self):
        """Display the current question."""
        self.clear_window()

        total_questions = len(self.current_questions)
        question_data = self.current_questions[self.current_question_index]

        # Header
        self._create_modern_header(
            self,
            f"Тестирование: {self.selected_scenario['title']}",
            back_cmd=self.confirm_exit_test,
            back_text="←  Завершить",
            bg=Colors.SECONDARY
        )

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
        q_header = tk.Frame(question_frame, bg=Colors.SECONDARY_BG, bd=0, highlightthickness=0)
        q_header.pack(fill=tk.X, pady=(0, Spacing.LG))

        tk.Label(
            q_header,
            text=f"Вопрос {self.current_question_index + 1}",
            font=Fonts.SUBHEADING,
            bg=Colors.SECONDARY_BG,
            fg=Colors.SECONDARY
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

        if self.current_question_index > 0:
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
                bg=Colors.SECONDARY,
                hover_bg=Colors.SECONDARY_LIGHT,
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

    # ─── Question Type Handlers ───

    def show_single_choice(self, parent, question_data):
        """Display single choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved = self.user_answers.get(question_id, None)
        var = tk.IntVar(value=-1)

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
                fg=Colors.SECONDARY if (saved is not None and i == int(saved)) else Colors.TEXT_SECONDARY
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
                inner.configure(bg=Colors.SECONDARY_BG)
                outer.configure(bg=Colors.SECONDARY)

            def make_select(idx, c, inn, out):
                def on_click(e):
                    var.set(idx)
                    for child in parent.winfo_children():
                        for sub in child.winfo_children():
                            if isinstance(sub, tk.Frame):
                                sub.configure(bg=Colors.CARD_BG)
                                if sub.master:
                                    sub.master.configure(bg=Colors.BORDER_LIGHT)
                            for gc in sub.winfo_children():
                                if isinstance(gc, tk.Label) and hasattr(gc, 'is_circle') and gc.is_circle:
                                    gc.configure(text="○", fg=Colors.TEXT_SECONDARY)
                    c.configure(text="●", fg=Colors.SECONDARY)
                    inn.configure(bg=Colors.SECONDARY_BG)
                    out.configure(bg=Colors.SECONDARY)
                return on_click

            cb = make_select(i, circle, inner, outer)
            for w in (inner, circle, text_label):
                w.bind("<Button-1>", cb)

        parent.var = var

    def show_multiple_choice(self, parent, question_data):
        """Display multiple choice question."""
        options = question_data.get("options", [])
        question_id = question_data.get("id")
        saved_answers = self.user_answers.get(question_id, [])
        vars_list = []

        for i, option in enumerate(options):
            is_saved = str(i) in saved_answers
            var = tk.BooleanVar(value=is_saved)
            outer = tk.Frame(parent, bg=Colors.SECONDARY if is_saved else Colors.BORDER_LIGHT,
                             bd=0, highlightthickness=0)
            outer.pack(fill=tk.X, pady=Spacing.XS)

            inner = tk.Frame(outer, bg=Colors.SECONDARY_BG if is_saved else Colors.CARD_BG,
                             bd=0, highlightthickness=0, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            cb = "☑" if is_saved else "☐"
            lbl = tk.Label(
                inner,
                text=f"{cb}  {option}",
                font=Fonts.BODY_LARGE,
                bg=inner.cget('bg'),
                fg=Colors.SECONDARY if is_saved else Colors.TEXT_PRIMARY,
                wraplength=750,
                justify=tk.LEFT,
                anchor=tk.W
            )
            lbl.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)

            def toggle(e, idx=i, v=var, label=lbl, inn=inner, out=outer, opts=options):
                v.set(not v.get())
                if v.get():
                    label.configure(text=f"☑  {opts[idx]}", bg=Colors.SECONDARY_BG, fg=Colors.SECONDARY)
                    inn.configure(bg=Colors.SECONDARY_BG)
                    out.configure(bg=Colors.SECONDARY)
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
            selectbackground=Colors.SECONDARY_BG,
            selectforeground=Colors.SECONDARY,
            activestyle='none',
            height=10,
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for i, idx in enumerate(saved_order):
            listbox.insert(tk.END, f"  {i + 1}. {options[idx]}")

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
            outer = tk.Frame(parent, bg=Colors.SECONDARY if selected else Colors.BORDER_LIGHT,
                             bd=0, highlightthickness=0)
            outer.pack(fill=tk.X, pady=Spacing.XS)

            inner = tk.Frame(outer, bg=Colors.SECONDARY_BG if selected else Colors.CARD_BG,
                             bd=0, highlightthickness=0, cursor="hand2")
            inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            icon = "●" if selected else "○"
            lbl = tk.Label(
                inner,
                text=f"{icon}  {text}",
                font=Fonts.BODY_LARGE,
                bg=inner.cget('bg'),
                fg=Colors.SECONDARY if selected else Colors.TEXT_PRIMARY,
                anchor=tk.W
            )
            lbl.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)

            def make_toggle(v=val, inn=inner, out=outer, label=lbl):
                def on_click(e):
                    var.set(v)
                    for sibling in parent.winfo_children():
                        for sib_inner in sibling.winfo_children():
                            if isinstance(sib_inner, tk.Frame):
                                sib_inner.configure(bg=Colors.CARD_BG)
                                sibling.configure(bg=Colors.BORDER_LIGHT)
                                for sib_label in sib_inner.winfo_children():
                                    if isinstance(sib_label, tk.Label):
                                        txt = sib_label.cget('text')
                                        if txt.startswith("●"):
                                            sib_label.configure(text="○ " + txt[2:],
                                                                bg=Colors.CARD_BG,
                                                                fg=Colors.TEXT_PRIMARY)
                    label.configure(text=f"●  {text}", bg=Colors.SECONDARY_BG, fg=Colors.SECONDARY)
                    inn.configure(bg=Colors.SECONDARY_BG)
                    out.configure(bg=Colors.SECONDARY)
                return on_click

            callback = make_toggle()
            for w in (inner, lbl):
                w.bind("<Button-1>", callback)

        parent.var = var

    # ─── Navigation & Saving ───

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
        if not messagebox.askyesno("Завершение теста", "Вы уверены, что хотите завершить тест?"):
            return

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        questions = self.current_questions
        correct_count = 0
        incorrect_count = 0
        results_details = []

        for question in questions:
            qid = question.get("id")
            qtype = question.get("type")
            correct_answer = question.get("correct_answer")
            user_answer = self.user_answers.get(qid)
            explanation = question.get("explanation", "")
            is_correct = False

            if qtype == "single_choice":
                if user_answer and int(user_answer) == correct_answer[0]:
                    is_correct = True
            elif qtype == "multiple_choice":
                if user_answer and sorted([int(x) for x in user_answer]) == sorted(correct_answer):
                    is_correct = True
            elif qtype == "ordering":
                if user_answer and user_answer == correct_answer:
                    is_correct = True
            elif qtype == "true_false":
                if user_answer:
                    is_correct = (user_answer == "true") == correct_answer

            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            results_details.append({
                "question_id": qid,
                "question": question.get("question"),
                "type": qtype,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "reference": question.get("reference", ""),
                "section_ref": question.get("reference", "").replace("п. ", "").strip() if question.get("reference") else ""
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
            "details": results_details,
            "scenario_title": self.selected_scenario['title']
        }

        self.save_test_result(result)
        self.show_results(result)

    # ─── Results Display ───

    def show_results(self, result):
        """Show test results with modern card design."""
        self.clear_window()

        self._create_modern_header(self, "Результаты тестирования по сценарию",
                                   bg=Colors.SUCCESS)

        card_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XXL)

        card = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXXL, pady=Spacing.XXXL)

        tk.Label(
            content,
            text=f"{result['last_name']} {result['first_name']}",
            font=Fonts.TITLE_MEDIUM,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text=f"Сценарий: {result.get('scenario_title', '')}",
            font=Fonts.BODY,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor=tk.W, pady=(Spacing.XS, Spacing.SM))

        tk.Label(
            content,
            text=f"Время прохождения: {int(result['duration_seconds'] // 60)} мин. {int(result['duration_seconds'] % 60)} сек.",
            font=Fonts.BODY,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor=tk.W, pady=(0, Spacing.XL))

        score_card = tk.Frame(content, bg=Colors.SECONDARY_BG, bd=0, highlightthickness=0)
        score_card.pack(fill=tk.X, pady=(0, Spacing.XXL))

        score_inner = tk.Frame(score_card, bg=Colors.SECONDARY_BG)
        score_inner.pack(padx=Spacing.XXL, pady=Spacing.XXL)

        score_pct = round(result['correct_count'] / result['total_questions'] * 100)
        score_color = Colors.SUCCESS if score_pct >= 80 else (Colors.WARNING if score_pct >= 50 else Colors.ERROR)

        tk.Label(
            score_inner,
            text=f"{result['correct_count']} / {result['total_questions']}",
            font=("Segoe UI", 32, "bold"),
            bg=Colors.SECONDARY_BG,
            fg=score_color
        ).pack()

        grade = "Отлично!" if score_pct >= 90 else ("Хорошо" if score_pct >= 70 else
               ("Удовлетворительно" if score_pct >= 50 else "Нужно повторить"))
        tk.Label(
            score_inner,
            text=f"{score_pct}% — {grade}",
            font=Fonts.HEADING,
            bg=Colors.SECONDARY_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(pady=(Spacing.SM, 0))

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

        self._create_modern_button(
            btn_row,
            "📄  Экспорт в PDF",
            lambda: self.export_to_pdf(result),
            bg=Colors.ERROR,
            hover_bg=Colors.ERROR_DARK,
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT)

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
        """Show detailed results with explanations."""
        details_window = tk.Toplevel(self)
        details_window.title("Детализация результатов")
        details_window.geometry("900x700")
        details_window.configure(bg=Colors.BG)

        header_frame = tk.Frame(details_window, bg=Colors.SECONDARY, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Детализация результатов",
            font=Fonts.HEADING,
            bg=Colors.SECONDARY,
            fg=Colors.TEXT_ON_PRIMARY
        ).pack(pady=Spacing.MD, padx=Spacing.LG)

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

                    def make_click_handler(d=detail):
                        def on_click(e):
                            self.open_reglament(d)
                        return on_click

                    expl_link.bind("<Button-1>", make_click_handler(detail))
                    expl_link.bind("<Enter>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline", "bold")))
                    expl_link.bind("<Leave>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline")))
                else:
                    tk.Label(
                        expl_inner,
                        text=detail["explanation"],
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
                    command=lambda d=detail: self.open_reglament(d),
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

    def _parse_reference(self, reference):
        """Parse reference field to extract section reference and display text."""
        if not reference:
            return None, ""

        import re
        match = re.search(r'(\d+\.\d+)', reference)
        if not match:
            return None, reference

        section_ref = match.group(1)

        # Check if there's additional text besides the section reference
        cleaned_ref = re.sub(r'[пp]\.\s*', '', reference).strip()
        if '(' in cleaned_ref:
            paren_match = re.search(r'\((.*?)\)', reference)
            if paren_match:
                return section_ref, paren_match.group(1).strip()

        return section_ref, ""

    def _get_regulation_section_title(self, section_ref):
        """Get the title of a regulation section by reference."""
        if not self.reglament or not section_ref:
            return ""

        sections = self.reglament.get("sections", [])
        for section in sections:
            section_id = str(section.get("id", ""))
            if section_id == section_ref.split('.')[0]:
                if '.' in section_ref:
                    subsection_id = section_ref.split('.')[1]
                    content = section.get("content", [])
                    for item in content:
                        if item.get("type") == "subsection":
                            title = item.get("title", "")
                            if section_ref in title or f".{subsection_id}" in title:
                                return title
                return section.get("title", "")
        return ""

    def open_reglament(self, detail):
        """Open regulation section based on reference."""
        from study_mode import StudyModeWindow
        section_ref = detail.get("section_ref", "")
        self.study_window = StudyModeWindow(
            self,
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
