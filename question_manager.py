#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question and scenario management module.
Password-protected interface for CRUD operations on questions and scenarios.
"""

import tkinter as tk
from tkinter import messagebox
import json
from copy import deepcopy

from style_config import Colors, Fonts, Spacing
from _utils import get_base_path


ADMIN_PASSWORD = "admin123321"


def _load_json(filename):
    """Load JSON from base path."""
    path = get_base_path() / filename
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _save_json(filename, data):
    """Save JSON to base path."""
    path = get_base_path() / filename
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить {filename}: {e}")
        return False


# ─── Password Dialog ───────────────────────────────────────────────────────

def show_password_dialog(parent, on_success):
    """Show a modal password dialog. Calls on_success() if correct."""
    dialog = tk.Toplevel(parent)
    dialog.title("Вход в управление")
    dialog.geometry("380x220")
    dialog.configure(bg=Colors.CARD_BG)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    # Center on parent
    dialog.update_idletasks()
    px = parent.winfo_rootx() + (parent.winfo_width() - 380) // 2
    py = parent.winfo_rooty() + (parent.winfo_height() - 220) // 2
    dialog.geometry(f"+{px}+{py}")

    # Content
    tk.Label(
        dialog,
        text="🔒",
        font=("Segoe UI", 32),
        bg=Colors.CARD_BG,
        fg=Colors.PRIMARY
    ).pack(pady=(Spacing.XL, Spacing.SM))

    tk.Label(
        dialog,
        text="Управление вопросами и сценариями",
        font=Fonts.SUBHEADING,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_PRIMARY
    ).pack()

    tk.Label(
        dialog,
        text="Введите пароль для доступа:",
        font=Fonts.BODY,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_SECONDARY
    ).pack(pady=(Spacing.SM, Spacing.MD))

    entry_frame = tk.Frame(dialog, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=40)
    entry_frame.pack(fill=tk.X, padx=Spacing.XXL)
    entry_frame.pack_propagate(False)

    pwd_var = tk.StringVar()
    pwd_entry = tk.Entry(
        entry_frame,
        textvariable=pwd_var,
        font=Fonts.BODY_LARGE,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_PRIMARY,
        relief=tk.FLAT,
        bd=0,
        show="*",
        insertbackground=Colors.PRIMARY
    )
    pwd_entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

    def on_submit():
        if pwd_var.get() == ADMIN_PASSWORD:
            dialog.destroy()
            on_success()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")
            pwd_var.set("")
            pwd_entry.focus_set()

    def on_focus_in(e):
        entry_frame.configure(bg=Colors.PRIMARY)
    def on_focus_out(e):
        entry_frame.configure(bg=Colors.BORDER_LIGHT)
    pwd_entry.bind("<FocusIn>", on_focus_in)
    pwd_entry.bind("<FocusOut>", on_focus_out)
    pwd_entry.bind("<Return>", lambda e: on_submit())

    btn = tk.Button(
        dialog,
        text="Войти",
        font=Fonts.BUTTON,
        bg=Colors.PRIMARY,
        fg=Colors.TEXT_ON_PRIMARY,
        activebackground=Colors.PRIMARY_LIGHT,
        activeforeground=Colors.TEXT_ON_PRIMARY,
        relief=tk.FLAT,
        cursor="hand2",
        command=on_submit,
        bd=0,
        padx=32,
        pady=8
    )
    btn.pack(pady=Spacing.LG)

    def b_enter(e): btn.configure(bg=Colors.PRIMARY_LIGHT)
    def b_leave(e): btn.configure(bg=Colors.PRIMARY)
    btn.bind("<Enter>", b_enter)
    btn.bind("<Leave>", b_leave)

    pwd_entry.focus_set()
    dialog.wait_window()


# ─── Question Edit Dialog ──────────────────────────────────────────────────

QUESTION_TYPES = [
    "single_choice",
    "multiple_choice",
    "ordering",
    "true_false"
]

TYPE_LABELS = {
    "single_choice": "Один правильный ответ",
    "multiple_choice": "Несколько правильных ответов",
    "ordering": "Правильный порядок",
    "true_false": "Верно / Неверно"
}


class QuestionEditDialog(tk.Toplevel):
    """Dialog for creating or editing a question."""

    def __init__(self, parent, question=None, scenario_mode=False, existing_ids=None):
        """
        Args:
            parent: Parent window
            question: Existing question dict to edit, or None for new
            scenario_mode: If True, uses 'qXX' IDs; else integer IDs
            existing_ids: Set of existing IDs to avoid duplicates
        """
        super().__init__(parent)
        self.question = question  # None for new question
        self.scenario_mode = scenario_mode
        self.existing_ids = existing_ids or set()
        self.result = None  # Will hold the edited/created question on save

        self.title("Редактирование вопроса" if question else "Новый вопрос")
        self.geometry("750x700")
        self.configure(bg=Colors.BG)
        self.transient(parent)
        self.grab_set()

        self.center_window()
        self._build_ui()

        if question:
            self._load_question(question)

    def center_window(self):
        self.update_idletasks()
        w, h = 750, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─── UI Build ───

    def _build_ui(self):
        # Scrollable frame for all content
        canvas = tk.Canvas(self, bg=Colors.BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview, bg=Colors.SURFACE)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        content = scroll_frame

        # ─── ID + Type row ───
        top_row = tk.Frame(content, bg=Colors.BG)
        top_row.pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.XL, Spacing.MD))

        # ID (auto or editable for scenario)
        tk.Label(top_row, text="ID:", font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_PRIMARY).pack(side=tk.LEFT)
        if self.question:
            id_text = str(self.question.get("id", ""))
            tk.Label(top_row, text=id_text, font=Fonts.BODY_LARGE, bg=Colors.BG,
                     fg=Colors.TEXT_SECONDARY).pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XL))
            self._id_value = id_text
        else:
            if self.scenario_mode:
                self.id_var = tk.StringVar()
                entry = tk.Entry(top_row, textvariable=self.id_var, font=Fonts.BODY,
                                 width=8, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
                                 relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY)
                id_frame = tk.Frame(top_row, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=32)
                id_frame.pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XL))
                id_frame.pack_propagate(False)
                entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM)
            else:
                next_id = self._next_available_id()
                tk.Label(top_row, text=str(next_id), font=Fonts.BODY_LARGE, bg=Colors.BG,
                         fg=Colors.TEXT_SECONDARY).pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XL))
                self._id_value = str(next_id)

        # Type dropdown
        tk.Label(top_row, text="Тип:", font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_PRIMARY).pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value=QUESTION_TYPES[0])
        type_menu = tk.OptionMenu(top_row, self.type_var, *QUESTION_TYPES)
        type_menu.configure(font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
                            activebackground=Colors.PRIMARY_BG, relief=tk.FLAT, bd=0,
                            highlightthickness=0, padx=8, pady=2)
        type_menu["menu"].configure(font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY)
        type_menu.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        self.type_var.trace_add("write", lambda *a: self._on_type_change())

        # ─── Question text ───
        tk.Label(content, text="Текст вопроса:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.MD, Spacing.XS))

        q_text_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=60)
        q_text_frame.pack(fill=tk.X, padx=Spacing.XL)
        q_text_frame.pack_propagate(False)

        self.question_text = tk.Text(
            q_text_frame, font=Fonts.BODY_LARGE, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, height=3, wrap=tk.WORD, insertbackground=Colors.PRIMARY
        )
        self.question_text.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def qf_in(e): q_text_frame.configure(bg=Colors.PRIMARY)
        def qf_out(e): q_text_frame.configure(bg=Colors.BORDER_LIGHT)
        self.question_text.bind("<FocusIn>", qf_in)
        self.question_text.bind("<FocusOut>", qf_out)

        # ─── Options Section ───
        self.options_frame = tk.Frame(content, bg=Colors.BG)
        self.options_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=(Spacing.MD, 0))

        self._build_options_ui()

        # ─── Correct answer section ───
        tk.Label(content, text="Правильный ответ:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.MD, Spacing.XS))

        self.answer_frame = tk.Frame(content, bg=Colors.BG)
        self.answer_frame.pack(fill=tk.X, padx=Spacing.XL)

        # ─── Explanation ───
        tk.Label(content, text="Объяснение:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.MD, Spacing.XS))

        expl_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=50)
        expl_frame.pack(fill=tk.X, padx=Spacing.XL)
        expl_frame.pack_propagate(False)

        self.explanation_text = tk.Text(
            expl_frame, font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, height=2, wrap=tk.WORD, insertbackground=Colors.PRIMARY
        )
        self.explanation_text.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def ef_in(e): expl_frame.configure(bg=Colors.PRIMARY)
        def ef_out(e): expl_frame.configure(bg=Colors.BORDER_LIGHT)
        self.explanation_text.bind("<FocusIn>", ef_in)
        self.explanation_text.bind("<FocusOut>", ef_out)

        # ─── Reference ───
        tk.Label(content, text="Ссылка на регламент (например: п. 2.3):", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.MD, Spacing.XS))

        ref_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=38)
        ref_frame.pack(fill=tk.X, padx=Spacing.XL)
        ref_frame.pack_propagate(False)

        self.ref_var = tk.StringVar()
        ref_entry = tk.Entry(
            ref_frame, textvariable=self.ref_var, font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY
        )
        ref_entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)

        def rf_in(e): ref_frame.configure(bg=Colors.PRIMARY)
        def rf_out(e): ref_frame.configure(bg=Colors.BORDER_LIGHT)
        ref_entry.bind("<FocusIn>", rf_in)
        ref_entry.bind("<FocusOut>", rf_out)

        # ─── Buttons ───
        btn_row = tk.Frame(content, bg=Colors.BG)
        btn_row.pack(fill=tk.X, padx=Spacing.XL, pady=Spacing.XL)

        tk.Button(
            btn_row, text="Сохранить", font=Fonts.BUTTON,
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=24, pady=8,
            command=self._save
        ).pack(side=tk.RIGHT, padx=(Spacing.MD, 0))

        tk.Button(
            btn_row, text="Отмена", font=Fonts.BUTTON,
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=24, pady=8,
            command=self.destroy
        ).pack(side=tk.RIGHT)

        self._on_type_change()

    def _build_options_ui(self):
        """Build the options section (varies by type)."""
        for w in self.options_frame.winfo_children():
            w.destroy()

        qtype = self.type_var.get()

        if qtype == "true_false":
            tk.Label(self.options_frame, text="Для типа «Верно / Неверно» варианты не требуются.",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W, pady=Spacing.SM)
            return

        tk.Label(self.options_frame, text="Варианты ответов:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X)

        # Container with scroll for options
        opt_canvas = tk.Canvas(self.options_frame, bg=Colors.BG, highlightthickness=0, bd=0, height=120)
        opt_scroll = tk.Scrollbar(self.options_frame, orient="vertical", command=opt_canvas.yview, bg=Colors.SURFACE)
        opt_inner = tk.Frame(opt_canvas, bg=Colors.BG)

        opt_inner.bind("<Configure>", lambda e: opt_canvas.configure(scrollregion=opt_canvas.bbox("all")))
        opt_canvas.create_window((0, 0), window=opt_inner, anchor="nw")
        opt_canvas.configure(yscrollcommand=opt_scroll.set)

        opt_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        opt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.opt_inner = opt_inner
        self.opt_canvas = opt_canvas
        self.option_entries = []  # list of StringVars

        # Add initial empty options
        if self.question:
            options = self.question.get("options", [])
            for opt in options:
                self._add_option_entry(opt)
        else:
            for _ in range(3):
                self._add_option_entry("")

        # Add option button
        add_btn = tk.Button(
            self.options_frame, text="+ Добавить вариант", font=("Segoe UI", 9),
            bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=12, pady=4,
            command=lambda: self._add_option_entry("")
        )
        add_btn.pack(pady=(Spacing.SM, 0))

    def _add_option_entry(self, text=""):
        """Add an option entry row."""
        idx = len(self.option_entries)
        row = tk.Frame(self.opt_inner, bg=Colors.BG)
        row.pack(fill=tk.X, pady=Spacing.XS)

        var = tk.StringVar(value=text)

        entry_frame = tk.Frame(row, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=32)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_frame.pack_propagate(False)

        entry = tk.Entry(
            entry_frame, textvariable=var, font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=2)

        def ef_in(e, f=entry_frame): f.configure(bg=Colors.PRIMARY)
        def ef_out(e, f=entry_frame): f.configure(bg=Colors.BORDER_LIGHT)
        entry.bind("<FocusIn>", ef_in)
        entry.bind("<FocusOut>", ef_out)

        # Delete button
        del_btn = tk.Button(
            row, text="✕", font=("Segoe UI", 8),
            bg=Colors.ERROR_BG, fg=Colors.ERROR,
            activebackground=Colors.ERROR, activeforeground=Colors.WHITE,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=6, pady=0,
            command=lambda i=idx: self._remove_option(i)
        )
        del_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        self.option_entries.append((row, var, entry_frame))

        # Scroll to bottom
        self.opt_inner.update_idletasks()
        self.opt_canvas.yview_moveto(1.0)

    def _remove_option(self, idx):
        """Remove an option entry."""
        if len(self.option_entries) <= 2:
            messagebox.showwarning("Внимание", "Должно быть минимум 2 варианта ответа")
            return
        row, var, frame = self.option_entries[idx]
        row.destroy()
        self.option_entries.pop(idx)

    def _on_type_change(self):
        """Handle question type change."""
        # Rebuild options
        self._build_options_ui()
        # Rebuild answer section
        self._rebuild_answer_ui()

    def _rebuild_answer_ui(self):
        """Rebuild the correct answer UI based on type."""
        for w in self.answer_frame.winfo_children():
            w.destroy()

        qtype = self.type_var.get()
        self._answer_widgets = []

        if qtype == "single_choice":
            self._build_answer_single()
        elif qtype == "multiple_choice":
            self._build_answer_multiple()
        elif qtype == "ordering":
            self._build_answer_ordering()
        elif qtype == "true_false":
            self._build_answer_truefalse()

    def _get_options_text(self):
        """Get current option texts."""
        return [var.get() for _, var, _ in self.option_entries if var.get().strip()]

    def _build_answer_single(self):
        """Build single_choice answer selector."""
        self.answer_single_var = tk.IntVar(value=-1)
        options = self._get_options_text()
        if not options:
            tk.Label(self.answer_frame, text="(сначала добавьте варианты ответов)",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_DISABLED).pack(anchor=tk.W)
            return

        for i, opt in enumerate(options):
            row = tk.Frame(self.answer_frame, bg=Colors.BG)
            row.pack(fill=tk.X, pady=Spacing.XS)

            rb = tk.Radiobutton(
                row, text=f"{i}. {opt}", variable=self.answer_single_var, value=i,
                font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.CARD_BG, activebackground=Colors.BG,
                relief=tk.FLAT, bd=0, cursor="hand2"
            )
            rb.pack(anchor=tk.W, padx=Spacing.LG)

    def _build_answer_multiple(self):
        """Build multiple_choice answer selector."""
        self.answer_multi_vars = {}
        options = self._get_options_text()
        if not options:
            tk.Label(self.answer_frame, text="(сначала добавьте варианты ответов)",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_DISABLED).pack(anchor=tk.W)
            return

        for i, opt in enumerate(options):
            var = tk.BooleanVar(value=False)
            self.answer_multi_vars[i] = var
            row = tk.Frame(self.answer_frame, bg=Colors.BG)
            row.pack(fill=tk.X, pady=Spacing.XS)

            cb = tk.Checkbutton(
                row, text=f"{i}. {opt}", variable=var,
                font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.CARD_BG, activebackground=Colors.BG,
                relief=tk.FLAT, bd=0, cursor="hand2"
            )
            cb.pack(anchor=tk.W, padx=Spacing.LG)

    def _build_answer_ordering(self):
        """Build ordering answer selector."""
        self.answer_order_vars = []
        options = self._get_options_text()
        if not options:
            tk.Label(self.answer_frame, text="(сначала добавьте варианты ответов)",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_DISABLED).pack(anchor=tk.W)
            return

        tk.Label(self.answer_frame,
                 text="Расставьте варианты в правильном порядке (стрелками):",
                 font=Fonts.BODY_SMALL, bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W, pady=(0, Spacing.SM))

        list_frame = tk.Frame(self.answer_frame, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_frame.pack(fill=tk.X)

        inner = tk.Frame(list_frame, bg=Colors.CARD_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.order_listbox = tk.Listbox(
            inner, font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG, selectforeground=Colors.PRIMARY,
            activestyle='none', height=6, borderwidth=0, highlightthickness=0, relief=tk.FLAT
        )
        self.order_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        indices = list(range(len(options)))
        for i, idx in enumerate(indices):
            self.order_listbox.insert(tk.END, f"  {i+1}. {options[idx]}")

        btn_frame = tk.Frame(inner, bg=Colors.CARD_BG)
        btn_frame.pack(side=tk.RIGHT, padx=(0, Spacing.MD))

        tk.Button(btn_frame, text="↑", font=("Segoe UI", 12),
                  bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
                  activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
                  cursor="hand2", bd=0, padx=8, pady=2,
                  command=lambda: self._order_move(-1)).pack(pady=Spacing.XS)
        tk.Button(btn_frame, text="↓", font=("Segoe UI", 12),
                  bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
                  activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
                  cursor="hand2", bd=0, padx=8, pady=2,
                  command=lambda: self._order_move(1)).pack(pady=Spacing.XS)

        self.order_listbox.selection_set(0)

    def _order_move(self, direction):
        """Move item up or down in ordering listbox."""
        sel = self.order_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= self.order_listbox.size():
            return

        text = self.order_listbox.get(idx)
        self.order_listbox.delete(idx)
        self.order_listbox.insert(new_idx, text)
        self.order_listbox.selection_set(new_idx)

        # Renumber
        options = self._get_options_text()
        for i in range(self.order_listbox.size()):
            item = self.order_listbox.get(i)
            # Extract the text after "  X. "
            display = item[item.find(". ")+2:] if ". " in item else item
            self.order_listbox.delete(i)
            self.order_listbox.insert(i, f"  {i+1}. {display}")

    def _build_answer_truefalse(self):
        """Build true/false answer selector."""
        self.tf_var = tk.StringVar(value="true")

        for val, label in [("true", "Верно"), ("false", "Неверно")]:
            row = tk.Frame(self.answer_frame, bg=Colors.BG)
            row.pack(fill=tk.X, pady=Spacing.XS)

            rb = tk.Radiobutton(
                row, text=label, variable=self.tf_var, value=val,
                font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.CARD_BG, activebackground=Colors.BG,
                relief=tk.FLAT, bd=0, cursor="hand2"
            )
            rb.pack(anchor=tk.W, padx=Spacing.LG)

    def _load_question(self, q):
        """Load existing question data into UI."""
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", q.get("question", ""))

        # Set type
        qtype = q.get("type", "single_choice")
        if qtype in QUESTION_TYPES:
            self.type_var.set(qtype)

        self._on_type_change()

        # Load options
        options = q.get("options", [])
        if options and qtype != "true_false":
            # Remove default empty entries and add real ones
            for _, var, _ in self.option_entries:
                var.set("")
            # Replace entries
            for i, opt in enumerate(options):
                if i < len(self.option_entries):
                    self.option_entries[i][1].set(opt)
                else:
                    self._add_option_entry(opt)

        # Load correct answer
        correct = q.get("correct_answer")
        if correct is not None:
            if qtype == "single_choice":
                if isinstance(correct, list):
                    correct = correct[0]
                self.answer_single_var = tk.IntVar(value=int(correct))
                self._rebuild_answer_ui()
                self.answer_single_var.set(int(correct))
            elif qtype == "multiple_choice":
                correct_list = correct if isinstance(correct, list) else [correct]
                self._rebuild_answer_ui()
                for idx in correct_list:
                    if int(idx) in self.answer_multi_vars:
                        self.answer_multi_vars[int(idx)].set(True)
            elif qtype == "ordering":
                self._rebuild_answer_ui()
                # Reorder listbox
                correct_order = correct if isinstance(correct, list) else []
                if correct_order and hasattr(self, 'order_listbox'):
                    self.order_listbox.delete(0, tk.END)
                    for i, idx in enumerate(correct_order):
                        if idx < len(options):
                            self.order_listbox.insert(tk.END, f"  {i+1}. {options[idx]}")
            elif qtype == "true_false":
                self._rebuild_answer_ui()
                self.tf_var.set("true" if correct else "false")

        # Explanation
        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.insert("1.0", q.get("explanation", ""))

        # Reference
        self.ref_var.set(q.get("reference", ""))

    def _next_available_id(self):
        """Get next available integer ID."""
        n = 1
        while n in self.existing_ids:
            n += 1
        return n

    def _save(self):
        """Validate and save the question."""
        qtype = self.type_var.get()
        question_text = self.question_text.get("1.0", tk.END).strip()

        if not question_text:
            messagebox.showwarning("Ошибка", "Введите текст вопроса")
            return

        # Build question object
        q = {
            "type": qtype,
            "question": question_text,
            "reference": self.ref_var.get().strip(),
            "explanation": self.explanation_text.get("1.0", tk.END).strip(),
        }

        # Set ID
        if self.question:
            q["id"] = self.question["id"]
        else:
            if self.scenario_mode:
                qid = self.id_var.get().strip() if hasattr(self, 'id_var') else ""
                if not qid:
                    messagebox.showwarning("Ошибка", "Введите ID вопроса")
                    return
                if qid in self.existing_ids:
                    messagebox.showwarning("Ошибка", f"ID '{qid}' уже используется")
                    return
                q["id"] = qid
            else:
                q["id"] = int(self._id_value)

        # Handle type-specific data
        if qtype == "true_false":
            q["correct_answer"] = self.tf_var.get() == "true"
            q["options"] = []
        else:
            options = [var.get().strip() for _, var, _ in self.option_entries if var.get().strip()]
            if len(options) < 2:
                messagebox.showwarning("Ошибка", "Добавьте минимум 2 варианта ответа")
                return
            q["options"] = options

            if qtype == "single_choice":
                val = self.answer_single_var.get()
                if val == -1:
                    messagebox.showwarning("Ошибка", "Выберите правильный ответ")
                    return
                q["correct_answer"] = int(val)

            elif qtype == "multiple_choice":
                selected = [i for i, v in self.answer_multi_vars.items() if v.get()]
                if not selected:
                    messagebox.showwarning("Ошибка", "Выберите хотя бы один правильный ответ")
                    return
                q["correct_answer"] = sorted(selected)

            elif qtype == "ordering":
                if not hasattr(self, 'order_listbox') or self.order_listbox.size() < 2:
                    messagebox.showwarning("Ошибка", "Нужно минимум 2 варианта для сортировки")
                    return
                # Extract the original indices from the listbox order
                order = []
                options_text = q["options"]
                for i in range(self.order_listbox.size()):
                    item = self.order_listbox.get(i)
                    display = item[item.find(". ")+2:] if ". " in item else item
                    if display in options_text:
                        order.append(options_text.index(display))
                if len(order) != len(options_text):
                    messagebox.showwarning("Ошибка", "Ошибка определения порядка ответов")
                    return
                q["correct_answer"] = order

        self.result = q
        self.destroy()


# ─── Scenario Edit Dialog ──────────────────────────────────────────────────

class ScenarioEditDialog(tk.Toplevel):
    """Dialog for creating or editing a scenario with its questions."""

    def __init__(self, parent, scenario=None, existing_ids=None):
        super().__init__(parent)
        self.scenario = scenario
        self.existing_ids = existing_ids or set()
        self.result = None
        self.questions = []

        self.title("Редактирование сценария" if scenario else "Новый сценарий")
        self.geometry("800x700")
        self.configure(bg=Colors.BG)
        self.transient(parent)
        self.grab_set()

        self.center_window()
        self._build_ui()

        if scenario:
            self._load_scenario(scenario)

    def center_window(self):
        self.update_idletasks()
        w, h = 800, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        content = tk.Frame(self, bg=Colors.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

        # ─── ID ───
        id_row = tk.Frame(content, bg=Colors.BG)
        id_row.pack(fill=tk.X, pady=(0, Spacing.MD))

        tk.Label(id_row, text="ID сценария:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY).pack(side=tk.LEFT)

        if self.scenario:
            id_text = str(self.scenario.get("id", ""))
            tk.Label(id_row, text=id_text, font=Fonts.BODY_LARGE, bg=Colors.BG,
                     fg=Colors.TEXT_SECONDARY).pack(side=tk.LEFT, padx=(Spacing.SM, 0))
            self._id_value = id_text
        else:
            self.id_var = tk.StringVar()
            id_entry_frame = tk.Frame(id_row, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=32)
            id_entry_frame.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
            id_entry_frame.pack_propagate(False)
            entry = tk.Entry(
                id_entry_frame, textvariable=self.id_var, font=Fonts.BODY,
                width=8, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
                relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY
            )
            entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM)

        # ─── Title ───
        tk.Label(content, text="Название сценария:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, pady=(0, Spacing.XS))
        title_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=38)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        self.title_var = tk.StringVar()
        title_entry = tk.Entry(
            title_frame, textvariable=self.title_var, font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY
        )
        title_entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)
        def tf_in(e): title_frame.configure(bg=Colors.PRIMARY)
        def tf_out(e): title_frame.configure(bg=Colors.BORDER_LIGHT)
        title_entry.bind("<FocusIn>", tf_in)
        title_entry.bind("<FocusOut>", tf_out)

        # ─── Description ───
        tk.Label(content, text="Описание:", font=Fonts.BODY, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, pady=(Spacing.MD, Spacing.XS))
        desc_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0, height=60)
        desc_frame.pack(fill=tk.X)
        desc_frame.pack_propagate(False)
        self.desc_text = tk.Text(
            desc_frame, font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, height=3, wrap=tk.WORD, insertbackground=Colors.PRIMARY
        )
        self.desc_text.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)
        def df_in(e): desc_frame.configure(bg=Colors.PRIMARY)
        def df_out(e): desc_frame.configure(bg=Colors.BORDER_LIGHT)
        self.desc_text.bind("<FocusIn>", df_in)
        self.desc_text.bind("<FocusOut>", df_out)

        # ─── Questions Section ───
        tk.Label(content, text="Вопросы сценария:", font=Fonts.SUBHEADING, bg=Colors.BG,
                 fg=Colors.TEXT_PRIMARY, anchor=tk.W).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))

        # Questions listbox
        q_list_frame = tk.Frame(content, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        q_list_frame.pack(fill=tk.BOTH, expand=True)

        q_list_inner = tk.Frame(q_list_frame, bg=Colors.CARD_BG)
        q_list_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        q_listbox_frame = tk.Frame(q_list_inner, bg=Colors.CARD_BG)
        q_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        scrollbar = tk.Scrollbar(q_listbox_frame, bg=Colors.SURFACE)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.q_listbox = tk.Listbox(
            q_listbox_frame, font=Fonts.BODY,
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG, selectforeground=Colors.PRIMARY,
            activestyle='none', borderwidth=0, highlightthickness=0, relief=tk.FLAT
        )
        self.q_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.q_listbox.yview)

        # Question action buttons
        q_btn_row = tk.Frame(content, bg=Colors.BG)
        q_btn_row.pack(fill=tk.X, pady=(Spacing.SM, 0))

        def mk_btn(text, cmd, bg=Colors.PRIMARY):
            btn = tk.Button(q_btn_row, text=text, font=("Segoe UI", 9),
                            bg=bg, fg=Colors.WHITE, activebackground=Colors.PRIMARY_LIGHT,
                            relief=tk.FLAT, cursor="hand2", bd=0, padx=12, pady=4,
                            command=cmd)
            btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            return btn

        mk_btn("+ Добавить вопрос", self._add_question, Colors.SUCCESS)
        mk_btn("✎ Редактировать", self._edit_question, Colors.PRIMARY)
        mk_btn("✕ Удалить", self._delete_question, Colors.ERROR)

        # ─── Save/Cancel ───
        btn_row = tk.Frame(content, bg=Colors.BG)
        btn_row.pack(fill=tk.X, pady=(Spacing.LG, 0))

        tk.Button(
            btn_row, text="Сохранить сценарий", font=Fonts.BUTTON,
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=24, pady=8,
            command=self._save
        ).pack(side=tk.RIGHT, padx=(Spacing.MD, 0))

        tk.Button(
            btn_row, text="Отмена", font=Fonts.BUTTON,
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=24, pady=8,
            command=self.destroy
        ).pack(side=tk.RIGHT)

    def _load_scenario(self, s):
        """Load scenario data."""
        self.title_var.set(s.get("title", ""))
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", s.get("description", ""))
        self.questions = deepcopy(s.get("questions", []))
        self._refresh_q_list()

    def _refresh_q_list(self):
        """Refresh the questions listbox."""
        self.q_listbox.delete(0, tk.END)
        for q in self.questions:
            qid = q.get("id", "?")
            qtext = q.get("question", "")[:60]
            qtype = q.get("type", "")
            self.q_listbox.insert(tk.END, f"[{qid}] ({qtype}) {qtext}")

    def _get_existing_qids(self):
        """Get set of existing question IDs in this scenario."""
        return {q.get("id") for q in self.questions if q.get("id")}

    def _add_question(self):
        """Add a new question to the scenario."""
        qids = self._get_existing_qids()
        dialog = QuestionEditDialog(self, question=None, scenario_mode=True, existing_ids=qids)
        self.wait_window(dialog)
        if dialog.result:
            self.questions.append(dialog.result)
            self._refresh_q_list()

    def _edit_question(self):
        """Edit selected question."""
        sel = self.q_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите вопрос для редактирования")
            return
        idx = sel[0]
        other_ids = {q.get("id") for i, q in enumerate(self.questions)
                     if i != idx and q.get("id")}
        dialog = QuestionEditDialog(self, question=self.questions[idx],
                                    scenario_mode=True, existing_ids=other_ids)
        self.wait_window(dialog)
        if dialog.result:
            self.questions[idx] = dialog.result
            self._refresh_q_list()

    def _delete_question(self):
        """Delete selected question."""
        sel = self.q_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите вопрос для удаления")
            return
        idx = sel[0]
        if messagebox.askyesno("Подтверждение", "Удалить выбранный вопрос?"):
            self.questions.pop(idx)
            self._refresh_q_list()

    def _save(self):
        """Validate and save scenario."""
        title = self.title_var.get().strip()
        desc = self.desc_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Ошибка", "Введите название сценария")
            return
        if not desc:
            messagebox.showwarning("Ошибка", "Введите описание сценария")
            return
        if not self.questions:
            messagebox.showwarning("Ошибка", "Добавьте хотя бы один вопрос в сценарий")
            return

        s = {
            "id": self.scenario["id"] if self.scenario else self.id_var.get().strip(),
            "title": title,
            "description": desc,
            "questions": deepcopy(self.questions)
        }

        if not s["id"]:
            messagebox.showwarning("Ошибка", "Введите ID сценария")
            return
        if not self.scenario and s["id"] in self.existing_ids:
            messagebox.showwarning("Ошибка", f"ID '{s['id']}' уже используется")
            return

        self.result = s
        self.destroy()


# ─── Main Manager Window ───────────────────────────────────────────────────

class QuestionManagerWindow(tk.Toplevel):
    """Main management window for questions and scenarios."""

    def __init__(self, parent, on_close=None):
        super().__init__(parent)
        self.parent = parent
        self._on_close = on_close

        self.title("Управление вопросами и сценариями")
        self.geometry("950x650")
        self.configure(bg=Colors.BG)

        self.center_window()
        self._load_data()
        self._build_ui()

        self.protocol("WM_DELETE_WINDOW", self._close)

    def center_window(self):
        self.update_idletasks()
        w, h = 950, 650
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _load_data(self):
        """Load questions and scenarios from JSON files."""
        self.questions = _load_json("questions.json") or []
        scenarios_data = _load_json("test_scenarios.json") or {}
        self.scenarios = scenarios_data.get("test_scenarios", [])

    def _save_questions(self):
        """Save questions to JSON."""
        return _save_json("questions.json", self.questions)

    def _save_scenarios(self):
        """Save scenarios to JSON."""
        return _save_json("test_scenarios.json", {"test_scenarios": self.scenarios})

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=Colors.PRIMARY, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="⚙ Управление вопросами и сценариями",
            font=Fonts.HEADING, bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY
        ).pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.XL)

        # Mode tabs
        tab_frame = tk.Frame(self, bg=Colors.BG, height=44)
        tab_frame.pack(fill=tk.X)
        tab_frame.pack_propagate(False)

        self.tab_questions_btn = tk.Button(
            tab_frame, text="📝 Вопросы", font=Fonts.BUTTON,
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=24, pady=8,
            command=lambda: self._switch_tab("questions")
        )
        self.tab_questions_btn.pack(side=tk.LEFT, padx=(Spacing.XL, 0), pady=Spacing.XS)

        self.tab_scenarios_btn = tk.Button(
            tab_frame, text="🎬 Сценарии", font=Fonts.BUTTON,
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY_BG, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=24, pady=8,
            command=lambda: self._switch_tab("scenarios")
        )
        self.tab_scenarios_btn.pack(side=tk.LEFT, padx=Spacing.SM, pady=Spacing.XS)

        # Content area
        self.content_frame = tk.Frame(self, bg=Colors.BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.MD)

        self._active_tab = "questions"
        self._show_questions()

    def _switch_tab(self, tab):
        """Switch between questions and scenarios tabs."""
        if tab == self._active_tab:
            return
        self._active_tab = tab

        # Update tab button styles
        q_bg = Colors.PRIMARY if tab == "questions" else Colors.SURFACE
        q_fg = Colors.TEXT_ON_PRIMARY if tab == "questions" else Colors.TEXT_PRIMARY
        s_bg = Colors.PRIMARY if tab == "scenarios" else Colors.SURFACE
        s_fg = Colors.TEXT_ON_PRIMARY if tab == "scenarios" else Colors.TEXT_PRIMARY

        self.tab_questions_btn.configure(bg=q_bg, fg=q_fg)
        self.tab_scenarios_btn.configure(bg=s_bg, fg=s_fg)

        # Clear and show
        for w in self.content_frame.winfo_children():
            w.destroy()

        if tab == "questions":
            self._show_questions()
        else:
            self._show_scenarios()

    # ─── Questions Tab ───

    def _show_questions(self):
        """Build questions list UI."""
        left = tk.Frame(self.content_frame, bg=Colors.BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(self.content_frame, bg=Colors.BORDER_LIGHT, width=200)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(Spacing.XL, 0))
        right.pack_propagate(False)

        # Counter
        count_label = tk.Label(left, text=f"Всего вопросов: {len(self.questions)}",
                               font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W)
        count_label.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Question list
        list_outer = tk.Frame(left, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_outer.pack(fill=tk.BOTH, expand=True)

        list_inner = tk.Frame(list_outer, bg=Colors.CARD_BG)
        list_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        listbox_frame = tk.Frame(list_inner, bg=Colors.CARD_BG)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        scrollbar = tk.Scrollbar(listbox_frame, bg=Colors.SURFACE)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.q_listbox = tk.Listbox(
            listbox_frame, font=Fonts.BODY,
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG, selectforeground=Colors.PRIMARY,
            activestyle='none', borderwidth=0, highlightthickness=0, relief=tk.FLAT
        )
        self.q_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.q_listbox.yview)

        self._refresh_q_listbox()

        # Right panel buttons
        tk.Label(right, text="Действия", font=Fonts.SUBHEADING, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_PRIMARY).pack(pady=(Spacing.LG, Spacing.MD))

        self._action_btn(right, "+ Добавить вопрос", Colors.SUCCESS, self._add_question)
        self._action_btn(right, "✎ Редактировать", Colors.PRIMARY, self._edit_question)
        self._action_btn(right, "✕ Удалить", Colors.ERROR, self._delete_question)

        tk.Frame(right, bg=Colors.CARD_BG, height=0).pack(fill=tk.X, pady=Spacing.MD)

        self._action_btn(right, "🔄 Обновить список", Colors.TEXT_SECONDARY, self._refresh)

    def _refresh_q_listbox(self):
        """Refresh the questions listbox."""
        self.q_listbox.delete(0, tk.END)
        for q in self.questions:
            qid = q.get("id", "?")
            qtype = q.get("type", "")
            qtext = q.get("question", "")[:70]
            type_short = {"single_choice": "1из", "multiple_choice": "Nиз",
                           "ordering": "пор", "true_false": "В/Н"}.get(qtype, qtype)
            self.q_listbox.insert(tk.END, f"#{qid} [{type_short}] {qtext}")

    def _action_btn(self, parent, text, color, command):
        """Create an action button."""
        btn = tk.Button(
            parent, text=text, font=("Segoe UI", 10),
            bg=color, fg=Colors.WHITE,
            activebackground=Colors.PRIMARY_LIGHT,
            relief=tk.FLAT, cursor="hand2", bd=0, padx=16, pady=8,
            command=command
        )
        btn.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.XS)

        def be(e): btn.configure(bg=Colors.PRIMARY_LIGHT)
        def bl(e): btn.configure(bg=color)
        btn.bind("<Enter>", be)
        btn.bind("<Leave>", bl)
        return btn

    def _get_existing_qids(self):
        """Get set of existing question IDs."""
        return {q.get("id") for q in self.questions if q.get("id") is not None}

    def _add_question(self):
        """Open dialog to add a new question."""
        existing = self._get_existing_qids()
        dialog = QuestionEditDialog(self, question=None, scenario_mode=False, existing_ids=existing)
        self.wait_window(dialog)
        if dialog.result:
            self.questions.append(dialog.result)
            self._save_questions()
            self._refresh_q_listbox()

    def _edit_question(self):
        """Edit selected question."""
        sel = self.q_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите вопрос для редактирования")
            return
        idx = sel[0]
        if idx >= len(self.questions):
            return

        other_ids = {q.get("id") for i, q in enumerate(self.questions)
                     if i != idx and q.get("id") is not None}
        dialog = QuestionEditDialog(self, question=self.questions[idx],
                                    scenario_mode=False, existing_ids=other_ids)
        self.wait_window(dialog)
        if dialog.result:
            self.questions[idx] = dialog.result
            self._save_questions()
            self._refresh_q_listbox()

    def _delete_question(self):
        """Delete selected question."""
        sel = self.q_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите вопрос для удаления")
            return
        idx = sel[0]
        if idx >= len(self.questions):
            return

        q = self.questions[idx]
        if messagebox.askyesno("Подтверждение",
                               f"Удалить вопрос #{q.get('id')}?\n\n{q.get('question', '')[:80]}"):
            self.questions.pop(idx)
            self._save_questions()
            self._refresh_q_listbox()

    # ─── Scenarios Tab ───

    def _show_scenarios(self):
        """Build scenarios list UI."""
        left = tk.Frame(self.content_frame, bg=Colors.BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(self.content_frame, bg=Colors.BORDER_LIGHT, width=200)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(Spacing.XL, 0))
        right.pack_propagate(False)

        count_label = tk.Label(left, text=f"Всего сценариев: {len(self.scenarios)}",
                               font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W)
        count_label.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Scenario list
        list_outer = tk.Frame(left, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_outer.pack(fill=tk.BOTH, expand=True)

        list_inner = tk.Frame(list_outer, bg=Colors.CARD_BG)
        list_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        listbox_frame = tk.Frame(list_inner, bg=Colors.CARD_BG)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        scrollbar = tk.Scrollbar(listbox_frame, bg=Colors.SURFACE)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.s_listbox = tk.Listbox(
            listbox_frame, font=Fonts.BODY,
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG, selectforeground=Colors.PRIMARY,
            activestyle='none', borderwidth=0, highlightthickness=0, relief=tk.FLAT
        )
        self.s_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.s_listbox.yview)

        self._refresh_s_listbox()

        # Right panel buttons
        tk.Label(right, text="Действия", font=Fonts.SUBHEADING, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_PRIMARY).pack(pady=(Spacing.LG, Spacing.MD))

        self._action_btn(right, "+ Добавить сценарий", Colors.SUCCESS, self._add_scenario)
        self._action_btn(right, "✎ Редактировать", Colors.PRIMARY, self._edit_scenario)
        self._action_btn(right, "✕ Удалить", Colors.ERROR, self._delete_scenario)

        tk.Frame(right, bg=Colors.CARD_BG, height=0).pack(fill=tk.X, pady=Spacing.MD)

        self._action_btn(right, "🔄 Обновить список", Colors.TEXT_SECONDARY, self._refresh)

    def _refresh_s_listbox(self):
        """Refresh scenarios listbox."""
        self.s_listbox.delete(0, tk.END)
        for s in self.scenarios:
            sid = s.get("id", "?")
            title = s.get("title", "")[:70]
            qcount = len(s.get("questions", []))
            self.s_listbox.insert(tk.END, f"{sid} - {title}  [{qcount} вопр.]")

    def _get_existing_sids(self):
        """Get set of existing scenario IDs."""
        return {s.get("id") for s in self.scenarios if s.get("id")}

    def _add_scenario(self):
        """Open dialog to add a new scenario."""
        existing = self._get_existing_sids()
        dialog = ScenarioEditDialog(self, scenario=None, existing_ids=existing)
        self.wait_window(dialog)
        if dialog.result:
            self.scenarios.append(dialog.result)
            self._save_scenarios()
            self._refresh_s_listbox()

    def _edit_scenario(self):
        """Edit selected scenario."""
        sel = self.s_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите сценарий для редактирования")
            return
        idx = sel[0]
        if idx >= len(self.scenarios):
            return

        other_ids = {s.get("id") for i, s in enumerate(self.scenarios)
                     if i != idx and s.get("id")}
        dialog = ScenarioEditDialog(self, scenario=self.scenarios[idx], existing_ids=other_ids)
        self.wait_window(dialog)
        if dialog.result:
            self.scenarios[idx] = dialog.result
            self._save_scenarios()
            self._refresh_s_listbox()

    def _delete_scenario(self):
        """Delete selected scenario."""
        sel = self.s_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите сценарий для удаления")
            return
        idx = sel[0]
        if idx >= len(self.scenarios):
            return

        s = self.scenarios[idx]
        if messagebox.askyesno("Подтверждение",
                               f"Удалить сценарий {s.get('id')}?\n\n{s.get('title', '')}"):
            self.scenarios.pop(idx)
            self._save_scenarios()
            self._refresh_s_listbox()

    def _refresh(self):
        """Reload data from files and refresh UI."""
        self._load_data()
        if self._active_tab == "questions":
            self._refresh_q_listbox()
        else:
            self._refresh_s_listbox()

    def _close(self):
        """Close and notify parent."""
        if self._on_close:
            self._on_close()
        self.destroy()
