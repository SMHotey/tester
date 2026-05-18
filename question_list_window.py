# -*- coding: utf-8 -*-
"""
Question list window.
Full window for browsing questions in the active bank with add/edit/delete.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from style_config import Colors, Fonts, Spacing
from question_editor_window import QuestionEditorWindow


class QuestionListWindow(tk.Toplevel):
    """Window for viewing and editing questions in a question bank."""

    # Column widths
    COL_WIDTHS = {
        "id": 60,
        "type": 140,
        "question": 0,  # stretch
    }

    TYPE_LABELS = {
        "single_choice": "Один ответ",
        "multiple_choice": "Несколько",
        "ordering": "Порядок",
        "true_false": "Верно/Неверно",
    }

    def __init__(self, parent, bank_manager, bank_filename=None, bank_name="",
                 on_back=None, on_bank_changed=None):
        super().__init__(parent)
        self.bank_manager = bank_manager
        self.bank_filename = bank_filename
        self.bank_name = bank_name
        self.on_back = on_back
        self.on_bank_changed = on_bank_changed

        self._questions = []

        self.title(f"Редактор банка: {bank_name}")
        self.geometry("900x600")
        self.configure(bg=Colors.BG)
        self.resizable(True, True)

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 900) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"900x600+{x}+{y}")

        self._create_widgets()
        self._load_questions()

        self.protocol("WM_DELETE_WINDOW", self._on_back)

    # ─── Widgets ────────────────────────────────────────────────────

    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=Colors.PRIMARY, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Button(
            header, text="←  Назад", font=("Segoe UI", 11),
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=12, pady=8,
            command=self._on_back,
        ).pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        tk.Label(
            header, text=self.bank_name, font=Fonts.HEADING,
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
        ).pack(side=tk.LEFT, pady=Spacing.MD)

        # Top bar: search + buttons
        top_bar = tk.Frame(self, bg=Colors.BG)
        top_bar.pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.XL, Spacing.SM))

        # Search
        search_frame = tk.Frame(top_bar, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._apply_filter())
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY,
        )
        search_entry.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        search_entry.insert(0, "")
        search_entry.bind("<FocusIn>", lambda e: search_frame.configure(bg=Colors.PRIMARY))
        search_entry.bind("<FocusOut>", lambda e: search_frame.configure(bg=Colors.BORDER_LIGHT))

        # Placeholder
        self.search_placeholder = tk.Label(
            search_frame, text="🔍  Поиск по тексту вопроса...",
            font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.TEXT_DISABLED,
        )
        self.search_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        def on_search_focus(e):
            self.search_placeholder.place_forget()
        def on_search_blur(e):
            if not self.search_var.get():
                self.search_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        search_entry.bind("<FocusIn>", on_search_focus)
        search_entry.bind("<FocusOut>", on_search_blur)

        # Buttons
        btn_frame = tk.Frame(top_bar, bg=Colors.BG)
        btn_frame.pack(side=tk.RIGHT, padx=(Spacing.MD, 0))

        self.btn_add = tk.Button(
            btn_frame, text="+  Добавить", font=("Segoe UI", 10),
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_add,
        )
        self.btn_add.pack(side=tk.LEFT, padx=(0, Spacing.SM))

        self.btn_edit = tk.Button(
            btn_frame, text="✎  Редактировать", font=("Segoe UI", 10),
            bg=Colors.SUCCESS, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SUCCESS_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_edit,
        )
        self.btn_edit.pack(side=tk.LEFT, padx=(0, Spacing.SM))

        self.btn_delete = tk.Button(
            btn_frame, text="🗑  Удалить", font=("Segoe UI", 10),
            bg=Colors.ERROR, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.ERROR_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_delete,
        )
        self.btn_delete.pack(side=tk.LEFT)

        # Treeview
        list_frame = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=(Spacing.SM, Spacing.XL))

        # Columns
        columns = ("id", "type", "question")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                 selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.column("id", width=self.COL_WIDTHS["id"], anchor=tk.CENTER, minwidth=40)

        self.tree.heading("type", text="Тип")
        self.tree.column("type", width=self.COL_WIDTHS["type"], anchor=tk.CENTER, minwidth=80)

        self.tree.heading("question", text="Текст вопроса")
        self.tree.column("question", width=400, minwidth=200)

        # Tags for striping
        self.tree.tag_configure("even", background=Colors.CARD_BG)
        self.tree.tag_configure("odd", background=Colors.SURFACE)

        # Scrollbar
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Events
        self.tree.bind("<Double-1>", lambda e: self._on_edit())
        self.tree.bind("<Return>", lambda e: self._on_edit())

        # Status bar
        self.status_label = tk.Label(
            self, text="", font=Fonts.BODY_SMALL,
            bg=Colors.BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, padx=Spacing.XL, pady=(0, Spacing.MD))

    # ─── Data ───────────────────────────────────────────────────────

    def _load_questions(self):
        """Load questions from the bank."""
        if not self.bank_filename:
            self._questions = self.bank_manager.load_questions()
        else:
            self._questions = self.bank_manager.load_questions_from_bank(self.bank_filename)
        self._apply_filter()

    def _apply_filter(self):
        """Apply search filter and refresh tree."""
        query = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())

        filtered = []
        if query:
            for q in self._questions:
                if query in q.get("question", "").lower():
                    filtered.append(q)
        else:
            filtered = self._questions

        for i, q in enumerate(filtered):
            tag = "even" if i % 2 == 0 else "odd"
            qid = q.get("id", "")
            qtype = self.TYPE_LABELS.get(q.get("type", ""), q.get("type", ""))
            qtext = q.get("question", "")[:120]
            if len(q.get("question", "")) > 120:
                qtext += "..."
            self.tree.insert("", tk.END, values=(qid, qtype, qtext), tags=(tag,), iid=str(qid))

        total = len(self._questions)
        shown = len(filtered)
        if query:
            self.status_label.config(text=f"Показано {shown} из {total} вопросов")
        else:
            self.status_label.config(text=f"Всего вопросов: {total}")

    def _get_selected_question_id(self):
        """Return the ID of the selected question, or None."""
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        if values:
            return int(values[0]) if values[0] else None
        return None

    def _get_question_by_id(self, qid):
        """Find question dict by ID."""
        for q in self._questions:
            if q.get("id") == qid:
                return q
        return None

    # ─── Actions ────────────────────────────────────────────────────

    def _on_add(self):
        """Add a new question."""
        def on_save(question_dict):
            filename = self.bank_filename if self.bank_filename else self.bank_manager.get_active_bank_filename()
            if not filename:
                filename, _ = self.bank_manager.ensure_active_bank_exists()
                self.bank_filename = filename
            success, msg = self.bank_manager.add_question_to_bank(filename, question_dict)
            if success:
                self._load_questions()
            else:
                messagebox.showerror("Ошибка", msg, parent=self)

        QuestionEditorWindow(self, on_save=on_save)

    def _on_edit(self):
        """Edit the selected question."""
        qid = self._get_selected_question_id()
        if qid is None:
            messagebox.showinfo("Внимание", "Выберите вопрос из списка", parent=self)
            return

        question = self._get_question_by_id(qid)
        if not question:
            return

        def on_save(updated_dict):
            filename = self.bank_filename if self.bank_filename else self.bank_manager.get_active_bank_filename()
            if not filename:
                return
            success, msg = self.bank_manager.update_question_in_bank(filename, qid, updated_dict)
            if success:
                self._load_questions()
            else:
                messagebox.showerror("Ошибка", msg, parent=self)

        QuestionEditorWindow(self, question_dict=question, on_save=on_save)

    def _on_delete(self):
        """Delete the selected question."""
        qid = self._get_selected_question_id()
        if qid is None:
            messagebox.showinfo("Внимание", "Выберите вопрос из списка", parent=self)
            return

        question = self._get_question_by_id(qid)
        qtext = question.get("question", "")[:60] + ("..." if len(question.get("question", "")) > 60 else "")

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить вопрос #{qid}?\n\n{qtext}\n\nID будут перенумерованы.",
            parent=self,
        )
        if not confirm:
            return

        filename = self.bank_filename if self.bank_filename else self.bank_manager.get_active_bank_filename()
        if not filename:
            return

        success, msg = self.bank_manager.delete_question_from_bank(filename, qid)
        if success:
            self._load_questions()
            if self.on_bank_changed:
                self.on_bank_changed()
        else:
            messagebox.showerror("Ошибка", msg, parent=self)

    def _on_back(self):
        if self.on_back:
            self.on_back()
        else:
            self.destroy()
