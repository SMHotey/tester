# -*- coding: utf-8 -*-
"""
Scenario editor window.
Browse, add, edit, delete scenarios and their embedded questions.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from style_config import Colors, Fonts, Spacing
from question_editor_window import QuestionEditorWindow
from scenario_manager import ScenarioManager


class ScenarioEditorWindow(tk.Toplevel):
    """Window for managing scenarios and their embedded questions."""

    TYPE_LABELS = {
        "single_choice": "Один ответ",
        "multiple_choice": "Несколько",
        "true_false": "Верно/Неверно",
    }

    def __init__(self, parent, scenario_manager, on_back=None):
        super().__init__(parent)
        self.scenario_manager = scenario_manager
        self.on_back = on_back

        self._scenarios = []
        self._current_scenario = None  # Currently selected scenario dict

        self.title("Редактор сценариев")
        self.geometry("1100x700")
        self.configure(bg=Colors.BG)
        self.resizable(True, True)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1100) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"1100x700+{x}+{y}")

        self._create_widgets()
        self._load_scenarios()

        self.protocol("WM_DELETE_WINDOW", self._on_back)

    # ─── Widgets ────────────────────────────────────────────────────

    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=Colors.SECONDARY, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Button(
            header, text="←  Назад", font=("Segoe UI", 11),
            bg=Colors.SECONDARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SECONDARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=12, pady=8,
            command=self._on_back,
        ).pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        tk.Label(
            header, text="Редактор сценариев", font=Fonts.HEADING,
            bg=Colors.SECONDARY, fg=Colors.TEXT_ON_PRIMARY,
        ).pack(side=tk.LEFT, pady=Spacing.MD)

        # Split pane style: left = scenario list, right = scenario detail
        main_frame = tk.Frame(self, bg=Colors.BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

        # ─── Left panel: scenario list ──────────────────────────────
        left_panel = tk.Frame(main_frame, bg=Colors.BG, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel, text="Сценарии", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        # Scenario list frame
        list_outer = tk.Frame(left_panel, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_outer.pack(fill=tk.BOTH, expand=True)

        self.scenario_tree = ttk.Treeview(
            list_outer, columns=("id", "title"), show="tree",
            selectmode="browse",
        )
        self.scenario_tree.heading("#0", text="Сценарии")
        self.scenario_tree.column("#0", width=350, minwidth=200)

        v_scroll = ttk.Scrollbar(list_outer, orient="vertical", command=self.scenario_tree.yview)
        self.scenario_tree.configure(yscrollcommand=v_scroll.set)
        self.scenario_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Scenario buttons
        sc_btn_frame = tk.Frame(left_panel, bg=Colors.BG)
        sc_btn_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        tk.Button(
            sc_btn_frame, text="+  Сценарий", font=("Segoe UI", 10),
            bg=Colors.SECONDARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SECONDARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=10, pady=4,
            command=self._on_add_scenario,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        tk.Button(
            sc_btn_frame, text="✎", font=("Segoe UI", 10),
            bg=Colors.SUCCESS, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SUCCESS_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=10, pady=4,
            command=self._on_edit_scenario_meta,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        tk.Button(
            sc_btn_frame, text="🗑", font=("Segoe UI", 10),
            bg=Colors.ERROR, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.ERROR_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=10, pady=4,
            command=self._on_delete_scenario,
        ).pack(side=tk.LEFT)

        # Separator
        sep = tk.Frame(main_frame, bg=Colors.BORDER_LIGHT, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.XL)

        # ─── Right panel: scenario detail ───────────────────────────
        right_panel = tk.Frame(main_frame, bg=Colors.BG)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))

        # Scenario info
        self.info_frame = tk.Frame(right_panel, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        self.info_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        tk.Label(
            self.info_frame, text="Сценарий не выбран", font=Fonts.HEADING,
            bg=Colors.CARD_BG, fg=Colors.TEXT_DISABLED,
        ).pack(pady=Spacing.XL)

        # Question list in scenario
        tk.Label(
            right_panel, text="Вопросы сценария:", font=Fonts.SUBHEADING,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, Spacing.SM))

        qlist_outer = tk.Frame(right_panel, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        qlist_outer.pack(fill=tk.BOTH, expand=True)

        self.question_tree = ttk.Treeview(
            qlist_outer, columns=("id", "type", "question"), show="headings",
            selectmode="browse",
        )
        self.question_tree.heading("id", text="ID")
        self.question_tree.column("id", width=50, anchor=tk.CENTER)
        self.question_tree.heading("type", text="Тип")
        self.question_tree.column("type", width=120, anchor=tk.CENTER)
        self.question_tree.heading("question", text="Текст вопроса")
        self.question_tree.column("question", width=300, minwidth=200)

        q_v_scroll = ttk.Scrollbar(qlist_outer, orient="vertical", command=self.question_tree.yview)
        self.question_tree.configure(yscrollcommand=q_v_scroll.set)
        self.question_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        q_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Question buttons
        q_btn_frame = tk.Frame(right_panel, bg=Colors.BG)
        q_btn_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        tk.Button(
            q_btn_frame, text="+  Вопрос", font=("Segoe UI", 10),
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_add_question,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        tk.Button(
            q_btn_frame, text="✎  Редактировать", font=("Segoe UI", 10),
            bg=Colors.SUCCESS, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SUCCESS_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_edit_question,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        tk.Button(
            q_btn_frame, text="🗑  Удалить", font=("Segoe UI", 10),
            bg=Colors.ERROR, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.ERROR_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_delete_question,
        ).pack(side=tk.LEFT)

        # Status
        self.status_label = tk.Label(
            self, text="", font=Fonts.BODY_SMALL,
            bg=Colors.BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, padx=Spacing.XL, pady=(0, Spacing.MD))

        # Events
        self.scenario_tree.bind("<<TreeviewSelect>>", self._on_scenario_select)
        self.scenario_tree.bind("<Double-1>", lambda e: self._on_edit_scenario_meta())
        self.question_tree.bind("<Double-1>", lambda e: self._on_edit_question())

    # ─── Data loading ───────────────────────────────────────────────

    def _load_scenarios(self):
        """Reload scenario list."""
        self._scenarios = self.scenario_manager.load_scenarios()
        self.scenario_tree.delete(*self.scenario_tree.get_children())

        for s in self._scenarios:
            sid = s.get("id", "")
            title = s.get("title", "")
            qcount = len(s.get("questions", []))
            label = f"  {sid}: {title}  ({qcount} вопр.)"
            self.scenario_tree.insert("", tk.END, iid=sid, text=label)

        self.scenario_tree.selection_set(self.scenario_tree.get_children()[:1] or ())
        self._on_scenario_select()

        self.status_label.config(text=f"Всего сценариев: {len(self._scenarios)}")

    def _on_scenario_select(self, *args):
        """Handle scenario selection change."""
        sel = self.scenario_tree.selection()
        if not sel:
            self._current_scenario = None
            self._clear_detail()
            return

        sid = sel[0]
        for s in self._scenarios:
            if s.get("id") == sid:
                self._current_scenario = s
                self._show_scenario_detail(s)
                return

        self._current_scenario = None
        self._clear_detail()

    def _clear_detail(self):
        """Clear the detail panel."""
        for w in self.info_frame.winfo_children():
            w.destroy()
        tk.Label(
            self.info_frame, text="Выберите сценарий", font=Fonts.HEADING,
            bg=Colors.CARD_BG, fg=Colors.TEXT_DISABLED,
        ).pack(pady=Spacing.XL)
        self.question_tree.delete(*self.question_tree.get_children())

    def _show_scenario_detail(self, scenario):
        """Show scenario detail in right panel."""
        for w in self.info_frame.winfo_children():
            w.destroy()

        sid = scenario.get("id", "")
        title = scenario.get("title", "")
        desc = scenario.get("description", "")

        tk.Label(
            self.info_frame, text=f"{sid}: {title}", font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W,
        ).pack(fill=tk.X, padx=Spacing.LG, pady=(Spacing.LG, Spacing.XS))

        desc_label = tk.Label(
            self.info_frame, text=desc, font=Fonts.BODY_SMALL,
            bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W,
            wraplength=500, justify=tk.LEFT,
        )
        desc_label.pack(fill=tk.X, padx=Spacing.LG, pady=(0, Spacing.LG))

        # Reload questions list
        self._load_questions_for_scenario(scenario)

    def _load_questions_for_scenario(self, scenario):
        """Load questions tree for the given scenario."""
        self.question_tree.delete(*self.question_tree.get_children())
        questions = scenario.get("questions", [])

        for i, q in enumerate(questions):
            qid = q.get("id", "")
            qtype = self.TYPE_LABELS.get(q.get("type", ""), q.get("type", ""))
            qtext = q.get("question", "")[:100]
            if len(q.get("question", "")) > 100:
                qtext += "..."
            tag = "even" if i % 2 == 0 else "odd"
            self.question_tree.insert("", tk.END, values=(qid, qtype, qtext),
                                      tags=(tag,), iid=qid)

    # ─── Scenario actions ───────────────────────────────────────────

    def _on_add_scenario(self):
        """Add a new scenario."""
        dialog = _ScenarioMetaDialog(self, title="Новый сценарий")
        self.wait_window(dialog.dialog)
        if dialog.result is None:
            return

        title, desc = dialog.result
        success, msg, sid = self.scenario_manager.add_scenario(title, desc)
        if success:
            self._load_scenarios()
            self.status_label.config(text=msg, fg=Colors.SUCCESS)
        else:
            messagebox.showerror("Ошибка", msg, parent=self)

    def _on_edit_scenario_meta(self):
        """Edit the selected scenario's title and description."""
        if not self._current_scenario:
            messagebox.showinfo("Внимание", "Выберите сценарий", parent=self)
            return

        dialog = _ScenarioMetaDialog(
            self,
            title="Редактировать сценарий",
            initial_title=self._current_scenario.get("title", ""),
            initial_desc=self._current_scenario.get("description", ""),
        )
        self.wait_window(dialog.dialog)
        if dialog.result is None:
            return

        new_title, new_desc = dialog.result
        sid = self._current_scenario["id"]
        success, msg = self.scenario_manager.update_scenario(sid, new_title, new_desc)
        if success:
            self._load_scenarios()
            self.status_label.config(text=msg, fg=Colors.SUCCESS)
        else:
            messagebox.showerror("Ошибка", msg, parent=self)

    def _on_delete_scenario(self):
        """Delete the selected scenario."""
        if not self._current_scenario:
            messagebox.showinfo("Внимание", "Выберите сценарий", parent=self)
            return

        sid = self._current_scenario["id"]
        title = self._current_scenario.get("title", "")
        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить сценарий {sid}: «{title}»?\nЭто действие нельзя отменить.",
            parent=self,
        )
        if not confirm:
            return

        success, msg = self.scenario_manager.delete_scenario(sid)
        if success:
            self._load_scenarios()
            self.status_label.config(text=msg, fg=Colors.WARNING)
        else:
            messagebox.showerror("Ошибка", msg, parent=self)

    # ─── Question actions ───────────────────────────────────────────

    def _on_add_question(self):
        """Add a question to the current scenario."""
        if not self._current_scenario:
            messagebox.showinfo("Внимание", "Выберите сценарий", parent=self)
            return

        def on_save(question_dict):
            sid = self._current_scenario["id"]
            success, msg = self.scenario_manager.add_question_to_scenario(sid, question_dict)
            if success:
                # Reload
                self._current_scenario = self.scenario_manager.get_scenario(sid)
                self._show_scenario_detail(self._current_scenario)
                self._refresh_scenario_list()
                self.status_label.config(text=msg, fg=Colors.SUCCESS)
            else:
                messagebox.showerror("Ошибка", msg, parent=self)

        QuestionEditorWindow(self, on_save=on_save, scenario_mode=True)

    def _on_edit_question(self):
        """Edit the selected question in the current scenario."""
        if not self._current_scenario:
            messagebox.showinfo("Внимание", "Выберите сценарий", parent=self)
            return

        sel = self.question_tree.selection()
        if not sel:
            messagebox.showinfo("Внимание", "Выберите вопрос из списка", parent=self)
            return

        qid = sel[0]
        questions = self._current_scenario.get("questions", [])
        question = None
        for q in questions:
            if q.get("id") == qid:
                question = q
                break

        if not question:
            return

        def on_save(updated_dict):
            sid = self._current_scenario["id"]
            success, msg = self.scenario_manager.update_question_in_scenario(sid, qid, updated_dict)
            if success:
                self._current_scenario = self.scenario_manager.get_scenario(sid)
                self._show_scenario_detail(self._current_scenario)
                self._refresh_scenario_list()
                self.status_label.config(text=msg, fg=Colors.SUCCESS)
            else:
                messagebox.showerror("Ошибка", msg, parent=self)

        QuestionEditorWindow(self, question_dict=question, on_save=on_save, scenario_mode=True)

    def _on_delete_question(self):
        """Delete the selected question from the current scenario."""
        if not self._current_scenario:
            messagebox.showinfo("Внимание", "Выберите сценарий", parent=self)
            return

        sel = self.question_tree.selection()
        if not sel:
            messagebox.showinfo("Внимание", "Выберите вопрос из списка", parent=self)
            return

        qid = sel[0]
        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить вопрос {qid} из сценария?",
            parent=self,
        )
        if not confirm:
            return

        sid = self._current_scenario["id"]
        success, msg = self.scenario_manager.delete_question_from_scenario(sid, qid)
        if success:
            self._current_scenario = self.scenario_manager.get_scenario(sid)
            self._show_scenario_detail(self._current_scenario)
            self._refresh_scenario_list()
            self.status_label.config(text=msg, fg=Colors.WARNING)
        else:
            messagebox.showerror("Ошибка", msg, parent=self)

    def _refresh_scenario_list(self):
        """Refresh the scenario tree item label for current scenario."""
        if not self._current_scenario:
            return
        sid = self._current_scenario["id"]
        title = self._current_scenario.get("title", "")
        qcount = len(self._current_scenario.get("questions", []))
        label = f"  {sid}: {title}  ({qcount} вопр.)"
        if self.scenario_tree.exists(sid):
            self.scenario_tree.item(sid, text=label)

    def _on_back(self):
        if self.on_back:
            self.on_back()
        else:
            self.destroy()


class _ScenarioMetaDialog:
    """Modal dialog for creating/editing scenario title and description."""

    def __init__(self, parent, title="Сценарий", initial_title="", initial_desc=""):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=Colors.CARD_BG)
        self.dialog.resizable(False, False)
        self.result = None

        w, h = 500, 300
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Title
        tk.Label(
            self.dialog, text="Название сценария:", font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W,
        ).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.XL, Spacing.SM))

        title_frame = tk.Frame(self.dialog, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        title_frame.pack(fill=tk.X, padx=Spacing.XL)
        self.title_entry = tk.Entry(
            title_frame, font=Fonts.BODY_LARGE,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, insertbackground=Colors.PRIMARY,
        )
        self.title_entry.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        self.title_entry.insert(0, initial_title)
        self.title_entry.bind("<FocusIn>", lambda e: title_frame.configure(bg=Colors.PRIMARY))
        self.title_entry.bind("<FocusOut>", lambda e: title_frame.configure(bg=Colors.BORDER_LIGHT))

        # Description
        tk.Label(
            self.dialog, text="Описание:", font=Fonts.BODY,
            bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, anchor=tk.W,
        ).pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.LG, Spacing.SM))

        desc_frame = tk.Frame(self.dialog, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        desc_frame.pack(fill=tk.X, padx=Spacing.XL)
        desc_inner = tk.Frame(desc_frame, bg=Colors.BG)
        desc_inner.pack(fill=tk.X, padx=1, pady=1)

        self.desc_text = tk.Text(
            desc_inner, height=4, font=Fonts.BODY,
            bg=Colors.BG, fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0, wrap=tk.WORD,
            insertbackground=Colors.PRIMARY,
        )
        self.desc_text.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        self.desc_text.insert("1.0", initial_desc)
        self.desc_text.bind("<FocusIn>", lambda e: desc_frame.configure(bg=Colors.PRIMARY))
        self.desc_text.bind("<FocusOut>", lambda e: desc_frame.configure(bg=Colors.BORDER_LIGHT))

        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=Colors.CARD_BG)
        btn_frame.pack(fill=tk.X, padx=Spacing.XL, pady=Spacing.XL)

        tk.Button(
            btn_frame, text="Отмена", font=("Segoe UI", 10),
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=16, pady=6,
            command=self._on_cancel,
        ).pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        tk.Button(
            btn_frame, text="Сохранить", font=("Segoe UI", 10, "bold"),
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=16, pady=6,
            command=self._on_save,
        ).pack(side=tk.RIGHT)

        self.title_entry.focus_set()
        self.title_entry.bind("<Return>", lambda e: self.desc_text.focus_set())
        self.desc_text.bind("<Control-Return>", lambda e: self._on_save())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_save(self):
        title = self.title_entry.get().strip()
        desc = self.desc_text.get("1.0", tk.END).strip()
        if not title:
            messagebox.showwarning("Внимание", "Название сценария не может быть пустым", parent=self.dialog)
            return
        self.result = (title, desc)
        self.dialog.destroy()

    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()
