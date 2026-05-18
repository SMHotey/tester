# -*- coding: utf-8 -*-
"""
Question editor window.
Modal dialog for creating or editing a single question.
Supports all 4 question types: single_choice, multiple_choice, ordering, true_false.
"""

import tkinter as tk
from tkinter import messagebox

from style_config import Colors, Fonts, Spacing


class QuestionEditorWindow(tk.Toplevel):
    """Modal dialog for editing a single question."""

    # Type display names
    TYPE_NAMES = {
        "single_choice": "Один правильный ответ",
        "multiple_choice": "Несколько правильных ответов",
        "ordering": "Правильный порядок",
        "true_false": "Верно / Неверно",
    }

    def __init__(self, parent, question_dict=None, on_save=None, scenario_mode=False):
        """
        Args:
            parent: Parent widget.
            question_dict: Existing question dict to edit, or None for new.
            on_save: Callback(question_dict) when saved.
            scenario_mode: If True, use scenario question format (correct_answer as list, string q-id).
        """
        super().__init__(parent)
        self.parent = parent
        self.question_dict = question_dict
        self.on_save = on_save
        self.scenario_mode = scenario_mode
        self.result = None

        w, h = 800, 700
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.title("Редактор вопроса" if question_dict else "Новый вопрос")
        self.configure(bg=Colors.BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._populate_from_dict()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ─── Widget creation ────────────────────────────────────────────

    def _create_widgets(self):
        # Scrollable content
        canvas = tk.Canvas(self, bg=Colors.BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        body = scroll_frame

        # ─── Question type ───────────────────────────────────────────
        tk.Label(
            body, text="Тип вопроса:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        type_frame = tk.Frame(body, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        type_frame.pack(fill=tk.X)
        type_inner = tk.Frame(type_frame, bg=Colors.CARD_BG)
        type_inner.pack(fill=tk.X, padx=1, pady=1)

        self.type_var = tk.StringVar(value="single_choice")
        self.type_combo = tk.OptionMenu(
            type_inner, self.type_var,
            *self.TYPE_NAMES.keys(),
            command=self._on_type_change
        )
        self.type_combo.configure(
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY_BG, activeforeground=Colors.PRIMARY,
            relief=tk.FLAT, bd=0, padx=Spacing.MD, pady=Spacing.SM,
            highlightthickness=0, cursor="hand2",
        )
        self.type_combo.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        self.type_combo["menu"].configure(bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
                                           activebackground=Colors.PRIMARY_BG,
                                           activeforeground=Colors.PRIMARY,
                                           font=Fonts.BODY)

        # Type hint
        self.type_hint = tk.Label(
            body, text="", font=Fonts.BODY_SMALL,
            bg=Colors.BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W
        )
        self.type_hint.pack(fill=tk.X, pady=(Spacing.XS, Spacing.LG))

        # ─── Question text ───────────────────────────────────────────
        tk.Label(
            body, text="Текст вопроса:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        q_frame = tk.Frame(body, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        q_frame.pack(fill=tk.X)
        q_inner = tk.Frame(q_frame, bg=Colors.CARD_BG)
        q_inner.pack(fill=tk.X, padx=1, pady=1)

        self.question_text = tk.Text(
            q_inner, height=4, font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, wrap=tk.WORD,
            insertbackground=Colors.PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY,
        )
        self.question_text.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        self.question_text.bind("<FocusIn>", lambda e: q_frame.configure(bg=Colors.PRIMARY))
        self.question_text.bind("<FocusOut>", lambda e: q_frame.configure(bg=Colors.BORDER_LIGHT))

        # ─── Options ─────────────────────────────────────────────────
        self.options_container = tk.Frame(body, bg=Colors.BG)
        self.options_container.pack(fill=tk.X, pady=(Spacing.LG, 0))

        # ─── Reference ───────────────────────────────────────────────
        tk.Label(
            body, text="Ссылка на регламент:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        ref_frame = tk.Frame(body, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        ref_frame.pack(fill=tk.X)
        ref_inner = tk.Frame(ref_frame, bg=Colors.CARD_BG)
        ref_inner.pack(fill=tk.X, padx=1, pady=1)

        self.ref_var = tk.StringVar()
        ref_entry = tk.Entry(
            ref_inner, textvariable=self.ref_var,
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY,
        )
        ref_entry.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        ref_entry.bind("<FocusIn>", lambda e: ref_frame.configure(bg=Colors.PRIMARY))
        ref_entry.bind("<FocusOut>", lambda e: ref_frame.configure(bg=Colors.BORDER_LIGHT))

        # ─── Explanation ─────────────────────────────────────────────
        tk.Label(
            body, text="Объяснение:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        expl_frame = tk.Frame(body, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        expl_frame.pack(fill=tk.X)
        expl_inner = tk.Frame(expl_frame, bg=Colors.CARD_BG)
        expl_inner.pack(fill=tk.X, padx=1, pady=1)

        self.explanation_text = tk.Text(
            expl_inner, height=4, font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, wrap=tk.WORD,
            insertbackground=Colors.PRIMARY,
        )
        self.explanation_text.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        self.explanation_text.bind("<FocusIn>", lambda e: expl_frame.configure(bg=Colors.PRIMARY))
        self.explanation_text.bind("<FocusOut>", lambda e: expl_frame.configure(bg=Colors.BORDER_LIGHT))

        # ─── Buttons ─────────────────────────────────────────────────
        btn_frame = tk.Frame(body, bg=Colors.BG)
        btn_frame.pack(fill=tk.X, pady=(Spacing.XL, 0))

        tk.Button(
            btn_frame, text="Отмена", font=Fonts.BODY,
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=20, pady=8,
            command=self._on_cancel,
        ).pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        tk.Button(
            btn_frame, text="Сохранить", font=Fonts.BUTTON,
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=20, pady=8,
            command=self._on_save,
        ).pack(side=tk.RIGHT)

        keyboard_frame = tk.Frame(body, bg=Colors.BG)
        keyboard_frame.pack(fill=tk.X, pady=Spacing.MD)
        tk.Label(
            keyboard_frame, text="Enter — сохранить, Esc — отмена",
            font=Fonts.CAPTION, bg=Colors.BG, fg=Colors.TEXT_DISABLED,
        ).pack()

        self.bind("<Return>", lambda e: self._on_save())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Initial render of options
        self._on_type_change()

    # ─── Type-dependent UI ──────────────────────────────────────────

    def _on_type_change(self, *args):
        """Rebuild options section when question type changes."""
        qtype = self.type_var.get()
        hints = {
            "single_choice": "Отметьте правильный вариант ответа (только один).",
            "multiple_choice": "Отметьте все правильные варианты ответа.",
            "ordering": "Укажите правильный порядок: перетащите или задайте номерами.",
            "true_false": "Укажите, верно или неверно утверждение.",
        }
        self.type_hint.config(text=hints.get(qtype, ""))

        for w in self.options_container.winfo_children():
            w.destroy()

        if qtype == "true_false":
            self._build_true_false_ui()
        else:
            self._build_options_list(qtype)

    def _build_true_false_ui(self):
        """UI for true/false type."""
        tk.Label(
            self.options_container, text="Правильный ответ:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        tf_frame = tk.Frame(self.options_container, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        tf_frame.pack(fill=tk.X)
        tf_inner = tk.Frame(tf_frame, bg=Colors.CARD_BG)
        tf_inner.pack(fill=tk.X, padx=1, pady=1)

        self.tf_var = tk.BooleanVar(value=True)
        tk.Radiobutton(
            tf_inner, text="Верно", variable=self.tf_var, value=True,
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectcolor=Colors.CARD_BG, activebackground=Colors.CARD_BG,
            cursor="hand2", padx=Spacing.LG, pady=Spacing.SM,
        ).pack(anchor=tk.W, padx=Spacing.MD, pady=(Spacing.SM, 0))
        tk.Radiobutton(
            tf_inner, text="Неверно", variable=self.tf_var, value=False,
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectcolor=Colors.CARD_BG, activebackground=Colors.CARD_BG,
            cursor="hand2", padx=Spacing.LG, pady=Spacing.SM,
        ).pack(anchor=tk.W, padx=Spacing.MD, pady=(0, Spacing.SM))

    def _build_options_list(self, qtype):
        """UI for option list (single_choice, multiple_choice, ordering)."""
        tk.Label(
            self.options_container, text="Варианты ответа:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        # Container for option rows
        self.option_rows_frame = tk.Frame(self.options_container, bg=Colors.BG)
        self.option_rows_frame.pack(fill=tk.X)

        self.option_frames = []  # list of dicts: {frame, entry_var, correct_var (if applicable)}
        self.correct_vars = []   # for single_choice: list of BooleanVars for radio; for multi: checkboxes
        self.radio_buttons = []  # for single_choice: actual radio widgets to update

        # Add initial empty rows
        initial_count = 4 if qtype == "ordering" else 4
        for _ in range(initial_count):
            self._add_option_row()

        # Buttons to add/remove
        opt_btn_frame = tk.Frame(self.options_container, bg=Colors.BG)
        opt_btn_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        tk.Button(
            opt_btn_frame, text="+ Добавить вариант", font=("Segoe UI", 10),
            bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=12, pady=4,
            command=self._add_option_row,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        tk.Button(
            opt_btn_frame, text="− Убрать последний", font=("Segoe UI", 10),
            bg=Colors.SURFACE, fg=Colors.TEXT_SECONDARY,
            activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=12, pady=4,
            command=self._remove_option_row,
        ).pack(side=tk.LEFT)

    def _add_option_row(self):
        """Add a single option row to the options list."""
        qtype = self.type_var.get()
        row_frame = tk.Frame(self.option_rows_frame, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        row_frame.pack(fill=tk.X, pady=(0, 1))

        idx = len(self.option_frames)

        # Number label
        num_label = tk.Label(
            row_frame, text=f"{idx + 1}.", font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY, width=3, anchor=tk.E
        )
        num_label.pack(side=tk.LEFT, padx=(Spacing.MD, Spacing.XS), pady=Spacing.SM)

        if qtype == "single_choice":
            # Radio button for correct answer
            var = tk.BooleanVar(value=False)
            self.correct_vars.append(var)
            rb = tk.Radiobutton(
                row_frame, variable=None, value=False,
                bg=Colors.CARD_BG, fg=Colors.PRIMARY,
                selectcolor=Colors.CARD_BG, activebackground=Colors.CARD_BG,
                cursor="hand2", bd=0,
            )
            rb.pack(side=tk.LEFT, padx=(0, Spacing.XS), pady=Spacing.SM)
            self.radio_buttons.append(rb)
        elif qtype == "multiple_choice":
            var = tk.BooleanVar(value=False)
            self.correct_vars.append(var)
            cb = tk.Checkbutton(
                row_frame, variable=var,
                bg=Colors.CARD_BG, fg=Colors.PRIMARY,
                selectcolor=Colors.CARD_BG, activebackground=Colors.CARD_BG,
                cursor="hand2", bd=0,
            )
            cb.pack(side=tk.LEFT, padx=(0, Spacing.XS), pady=Spacing.SM)
        elif qtype == "ordering":
            # Entry for order number
            order_var = tk.StringVar(value=str(idx + 1))
            order_entry = tk.Entry(
                row_frame, textvariable=order_var,
                width=4, font=Fonts.BODY,
                bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
                relief=tk.FLAT, bd=0, justify=tk.CENTER,
                insertbackground=Colors.PRIMARY,
            )
            order_entry.pack(side=tk.LEFT, padx=(0, Spacing.SM), pady=Spacing.SM)
            # Store the order var
            row_data = {"frame": row_frame, "entry_var": None, "order_var": order_var}
            self.option_frames.append(row_data)

        # Entry for option text
        entry_var = tk.StringVar()
        entry = tk.Entry(
            row_frame, textvariable=entry_var,
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.MD), pady=Spacing.SM)
        entry.bind("<FocusIn>", lambda e, f=row_frame: f.configure(bg=Colors.PRIMARY))
        entry.bind("<FocusOut>", lambda e, f=row_frame: f.configure(bg=Colors.CARD_BG))

        if qtype in ("single_choice", "multiple_choice"):
            self.option_frames.append({"frame": row_frame, "entry_var": entry_var})
        elif qtype == "ordering":
            pass  # Already added

        # Update radio button command for single_choice to clear others
        if qtype == "single_choice":
            def make_rb_cmd(index):
                def cmd():
                    for i, var in enumerate(self.correct_vars):
                        var.set(i == index)
                return cmd

            rb.configure(command=make_rb_cmd(idx), variable=self.correct_vars[idx])

    def _remove_option_row(self):
        """Remove the last option row."""
        if len(self.option_frames) <= 2:
            return
        row_data = self.option_frames.pop()
        row_data["frame"].destroy()
        if self.correct_vars and len(self.correct_vars) > len(self.option_frames):
            self.correct_vars.pop()
        # Update numbering
        self._renumber_options()

    def _renumber_options(self):
        """Update option number labels."""
        for i, w in enumerate(self.option_rows_frame.winfo_children()):
            children = w.winfo_children()
            for c in children:
                txt = c.cget("text") if hasattr(c, "cget") else ""
                if isinstance(txt, str) and txt.rstrip(".").isdigit():
                    c.configure(text=f"{i + 1}.")
                    break

    # ─── Data population ────────────────────────────────────────────

    def _populate_from_dict(self):
        """Fill UI fields from existing question dict."""
        q = self.question_dict
        if not q:
            return

        self.type_var.set(q.get("type", "single_choice"))
        self._on_type_change()

        self.question_text.insert("1.0", q.get("question", ""))

        qtype = q.get("type", "single_choice")
        options = q.get("options", [])
        correct = q.get("correct_answer")

        if qtype == "true_false":
            if isinstance(correct, bool):
                self.tf_var.set(correct)
            elif isinstance(correct, int):
                self.tf_var.set(bool(correct))
            else:
                self.tf_var.set(True)
        else:
            # Remove existing rows and add correct number
            while self.option_frames:
                row = self.option_frames.pop()
                row["frame"].destroy()
            self.correct_vars.clear()
            self.radio_buttons.clear()

            for opt_text in options:
                self._add_option_row()

            # Fill option texts
            for i, row_data in enumerate(self.option_frames):
                if i < len(options):
                    row_data["entry_var"].set(options[i])

            # Set correct answer
            if qtype == "single_choice":
                if isinstance(correct, int) and 0 <= correct < len(self.correct_vars):
                    self.correct_vars[correct].set(True)
            elif qtype == "multiple_choice":
                if isinstance(correct, list):
                    for ci in correct:
                        if isinstance(ci, int) and 0 <= ci < len(self.correct_vars):
                            self.correct_vars[ci].set(True)
            elif qtype == "ordering":
                if isinstance(correct, list):
                    for i, ci in enumerate(correct):
                        if i < len(self.option_frames):
                            self.option_frames[i]["order_var"].set(str(ci + 1))

        self.ref_var.set(q.get("reference", ""))
        self.explanation_text.insert("1.0", q.get("explanation", ""))

    # ─── Save / Cancel ──────────────────────────────────────────────

    def _build_result_dict(self):
        """Build a question dict from the UI fields."""
        qtype = self.type_var.get()
        question_text = self.question_text.get("1.0", tk.END).strip()
        if not question_text:
            messagebox.showwarning("Внимание", "Текст вопроса не может быть пустым", parent=self)
            return None

        result = {
            "type": qtype,
            "question": question_text,
        }

        options = []
        correct_answer = None

        if qtype == "true_false":
            result["correct_answer"] = bool(self.tf_var.get())
        else:
            for row_data in self.option_frames:
                text = row_data["entry_var"].get().strip()
                if text:
                    options.append(text)

            if not options:
                messagebox.showwarning("Внимание", "Добавьте хотя бы один вариант ответа", parent=self)
                return None

            result["options"] = options

            if qtype == "single_choice":
                selected = [i for i, var in enumerate(self.correct_vars) if var.get()]
                if not selected:
                    messagebox.showwarning("Внимание", "Выберите правильный ответ", parent=self)
                    return None
                result["correct_answer"] = selected[0]
            elif qtype == "multiple_choice":
                selected = [i for i, var in enumerate(self.correct_vars) if var.get()]
                if not selected:
                    messagebox.showwarning("Внимание", "Выберите хотя бы один правильный ответ", parent=self)
                    return None
                result["correct_answer"] = selected
            elif qtype == "ordering":
                try:
                    order = [int(row_data["order_var"].get()) - 1 for row_data in self.option_frames]
                    # Validate no duplicates
                    if len(set(order)) != len(order):
                        messagebox.showwarning("Внимание", "Номера порядка должны быть уникальными", parent=self)
                        return None
                    result["correct_answer"] = order
                except ValueError:
                    messagebox.showwarning("Внимание", "Номера порядка должны быть числами", parent=self)
                    return None

        result["reference"] = self.ref_var.get().strip()
        result["explanation"] = self.explanation_text.get("1.0", tk.END).strip()

        # Preserve original ID if editing
        if self.question_dict and "id" in self.question_dict:
            result["id"] = self.question_dict["id"]

        return result

    def _on_save(self):
        result = self._build_result_dict()
        if result is None:
            return
        self.result = result
        if self.on_save:
            self.on_save(result)
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
