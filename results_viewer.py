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

from style_config import Colors, Fonts, Spacing

try:
    from pdf_generator import generate_pdf
except ImportError:
    generate_pdf = None


class ResultsViewerWindow(tk.Toplevel):
    """Window for viewing test results."""

    def __init__(self, parent, results_file, on_back):
        """Initialize results viewer window."""
        super().__init__(parent)
        self.results_file = results_file
        self.on_back = on_back
        self.results = []
        self._hovered_item = None

        self.title("Просмотр результатов тестирования")
        self.geometry("1200x700")
        self.configure(bg=Colors.BG)

        # Center window on screen
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.load_results()
        self.create_widgets()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_back)

    def _on_tree_hover(self, event):
        """Handle mouse hover on treeview rows."""
        item = self.tree.identify_row(event.y)
        if item == self._hovered_item:
            return
        # Remove previous hover
        if self._hovered_item:
            tags = list(self.tree.item(self._hovered_item, "tags"))
            tags = [t for t in tags if t != "hover"]
            self.tree.item(self._hovered_item, tags=tags)
        self._hovered_item = item
        if item:
            tags = list(self.tree.item(item, "tags"))
            if "hover" not in tags:
                tags.append("hover")
            self.tree.item(item, tags=tags)

    def _on_tree_leave(self, event):
        """Handle mouse leave from treeview."""
        if self._hovered_item:
            tags = list(self.tree.item(self._hovered_item, "tags"))
            tags = [t for t in tags if t != "hover"]
            self.tree.item(self._hovered_item, tags=tags)
            self._hovered_item = None

    def _load_reglament_data(self):
        """Load regulation data for study mode access."""
        try:
            reglament_path = Path(self.results_file).parent / "reglament.json"
            if reglament_path.exists():
                with open(reglament_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []

    def load_results(self):
        """Load results from JSON file."""
        self.results = []
        if not Path(self.results_file).exists():
            return
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return
                data = json.loads(content)
                if isinstance(data, list):
                    self.results = data
        except json.JSONDecodeError:
            # Empty or invalid JSON - treat as no results, no error dialog
            pass
        except Exception:
            # Only show error for actual file access problems
            pass

    def create_header_button(self, parent, text, bg, hover_bg, command, side=tk.LEFT):
        """Create a modern header button."""
        btn = tk.Button(
            parent,
            text=text,
            font=Fonts.BODY,
            bg=bg,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=hover_bg,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=command,
            bd=0,
            padx=12,
            pady=8
        )

        def on_enter(e):
            btn.configure(bg=hover_bg)
        def on_leave(e):
            btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.pack(side=side, padx=(0, 10))

        return btn

    def create_widgets(self):
        """Create window widgets with modern design."""
        # ─── Header ───
        header_frame = tk.Frame(self, bg=Colors.WARNING, height=56)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_btn = tk.Button(
            header_frame,
            text="←  Назад",
            font=Fonts.BODY,
            bg=Colors.WARNING,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.WARNING_DARK,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_back,
            bd=0,
            padx=12,
            pady=8
        )

        def back_enter(e):
            back_btn.configure(bg=Colors.WARNING_DARK)
        def back_leave(e):
            back_btn.configure(bg=Colors.WARNING)

        back_btn.bind("<Enter>", back_enter)
        back_btn.bind("<Leave>", back_leave)
        back_btn.pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        title_label = tk.Label(
            header_frame,
            text="Результаты тестирования",
            font=Fonts.HEADING,
            bg=Colors.WARNING,
            fg=Colors.TEXT_ON_PRIMARY
        )
        title_label.pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.LG)

        # ─── Stats card ───
        stats_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        stats_outer.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.LG)

        stats_frame = tk.Frame(stats_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        stats_content = tk.Frame(stats_frame, bg=Colors.CARD_BG)
        stats_content.pack(fill=tk.X, padx=Spacing.XL, pady=Spacing.LG)

        total_tests = len(self.results)
        total_correct = sum(r.get("correct_count", 0) for r in self.results)
        total_questions = sum(r.get("total_questions", 0) for r in self.results)
        avg_score = round((total_correct / total_questions * 100) if total_questions > 0 else 0)

        tk.Label(
            stats_content,
            text="Статистика",
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))

        stats_row = tk.Frame(stats_content, bg=Colors.CARD_BG)
        stats_row.pack(fill=tk.X)

        stat_items = [
            ("Всего тестов", str(total_tests), Colors.PRIMARY),
            ("Всего вопросов", str(total_questions), Colors.TEXT_PRIMARY),
            ("Правильных", str(total_correct), Colors.SUCCESS),
            ("Средний балл", f"{avg_score}%", Colors.WARNING),
        ]

        for label, value, color in stat_items:
            item = tk.Frame(stats_row, bg=Colors.CARD_BG)
            item.pack(side=tk.LEFT, padx=(0, Spacing.XXL))

            tk.Label(
                item,
                text=value,
                font=("Segoe UI", 22, "bold"),
                bg=Colors.CARD_BG,
                fg=color
            ).pack(anchor=tk.W)

            tk.Label(
                item,
                text=label,
                font=Fonts.BODY_SMALL,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_SECONDARY
            ).pack(anchor=tk.W)

        # ─── Buttons ───
        btn_frame = tk.Frame(self, bg=Colors.BG)
        btn_frame.pack(fill=tk.X, padx=Spacing.LG, pady=(0, Spacing.LG))

        self.create_header_button(btn_frame, "Посмотреть неправильные ответы",
                                    Colors.ERROR, Colors.ERROR_DARK, self.view_incorrect_answers)

        self.create_header_button(btn_frame, "Скачать PDF",
                                    Colors.SUCCESS, Colors.SUCCESS_DARK, self.download_pdf)

        self.create_header_button(btn_frame, "Удалить выбранный результат",
                                    Colors.TEXT_SECONDARY, Colors.PRIMARY_DARK,
                                    self.delete_selected)

        # ─── Table ───
        table_outer = tk.Frame(self, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        table_outer.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        table_frame = tk.Frame(table_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        table_content = tk.Frame(table_frame, bg=Colors.CARD_BG)
        table_content.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Create treeview with scrollbars
        tree_frame = tk.Frame(table_content, bg=Colors.CARD_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Apply modern treeview style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=Colors.CARD_BG,
                        foreground=Colors.TEXT_PRIMARY,
                        rowheight=36,
                        fieldbackground=Colors.CARD_BG,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", Colors.PRIMARY_BG)],
                  foreground=[("selected", Colors.PRIMARY)])
        style.configure("Treeview.Heading",
                        background=Colors.SURFACE,
                        foreground=Colors.TEXT_PRIMARY,
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0,
                        relief=tk.FLAT)
        style.map("Treeview.Heading",
                  background=[("active", Colors.BORDER_LIGHT)])

        columns = ("ФИО", "Правильно", "Неправильно", "Всего", "Дата", "Время", "Длительность")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            height=20,
            selectmode="browse"
        )

        col_widths = {
            "ФИО": 200,
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

        # Configure hover tag
        self.tree.tag_configure("hover", background="#F0F8FF")

        # Bind hover events
        self.tree.bind("<Motion>", self._on_tree_hover)
        self.tree.bind("<Leave>", self._on_tree_leave)

        self.populate_table()

        self.tree.bind("<Double-1>", lambda e: self.view_incorrect_answers())

    def populate_table(self):
        """Populate the table with results."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add results
        for i, result in enumerate(self.results):
            start_time = result.get("start_time", "")
            date_str = ""
            time_str = ""
            duration_str = ""

            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time)
                    date_str = dt.strftime("%d.%m.%Y")
                    time_str = dt.strftime("%H:%M")
                except:
                    pass

            duration_seconds = result.get("duration_seconds", 0)
            if duration_seconds:
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                duration_str = f"{minutes}м {seconds}с"

            item_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    f"{result.get('last_name', '')} {result.get('first_name', '')}".strip(),
                    result.get("correct_count", 0),
                    result.get("incorrect_count", 0),
                    result.get("total_questions", 0),
                    date_str,
                    time_str,
                    duration_str
                )
            )

            # Color code based on performance
            correct = result.get("correct_count", 0)
            total = result.get("total_questions", 1)
            ratio = correct / total if total > 0 else 0

            if ratio == 1.0:
                self.tree.item(item_id, tags=("perfect",))
            elif ratio >= 0.7:
                self.tree.item(item_id, tags=("good",))
            else:
                self.tree.item(item_id, tags=("poor",))

        # Configure tags
        self.tree.tag_configure("perfect", background="#E8F5E9")
        self.tree.tag_configure("good", background="#FFF8E1")
        self.tree.tag_configure("poor", background="#FFEBEE")

    def view_incorrect_answers(self):
        """View incorrect answers for selected result."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите результат из таблицы")
            return

        item = selection[0]
        item_index = self.tree.index(item)

        if item_index >= len(self.results):
            return

        result = self.results[item_index]
        details = result.get("details", [])

        incorrect = [d for d in details if not d.get("correct", True)]

        if not incorrect:
            messagebox.showinfo("Информация", "Нет неправильных ответов")
            return

        self.show_incorrect_details(result, incorrect)

    def show_incorrect_details(self, result, incorrect):
        """Show window with incorrect answers."""
        window = tk.Toplevel(self)
        window.title(f"Неправильные ответы - {result.get('last_name')} {result.get('first_name')}")
        window.geometry("900x600")
        window.configure(bg=Colors.BG)

        # Header
        header_frame = tk.Frame(window, bg=Colors.ERROR, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f"✗  Неправильные ответы: {result.get('last_name')} {result.get('first_name')}",
            font=Fonts.HEADING,
            bg=Colors.ERROR,
            fg=Colors.TEXT_ON_PRIMARY
        ).pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.LG)

        close_btn = tk.Button(
            header_frame,
            text="✖  Закрыть",
            font=Fonts.BODY,
            bg=Colors.ERROR_DARK,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.ERROR,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=window.destroy,
            bd=0,
            padx=12,
            pady=6
        )
        close_btn.pack(side=tk.RIGHT, padx=Spacing.LG, pady=Spacing.SM)

        # Content with scrollbar
        canvas = tk.Canvas(window, bg=Colors.BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add incorrect answers
        for i, detail in enumerate(incorrect, 1):
            detail_outer = tk.Frame(scrollable_frame, bg=Colors.BORDER_LIGHT, bd=0,
                                     highlightthickness=0)
            detail_outer.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.SM)

            detail_frame = tk.Frame(detail_outer, bg=Colors.CARD_BG)
            detail_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            detail_content = tk.Frame(detail_frame, bg=Colors.CARD_BG)
            detail_content.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.LG)

            tk.Label(
                detail_content,
                text=f"Вопрос {i}: {detail.get('question', '')}",
                font=Fonts.SUBHEADING,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_PRIMARY,
                wraplength=780,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, Spacing.SM))

            answer_frame = tk.Frame(detail_content, bg=Colors.CARD_BG)
            answer_frame.pack(fill=tk.X, pady=Spacing.XS)

            tk.Label(
                answer_frame,
                text="Ваш ответ: ",
                font=Fonts.BODY,
                bg=Colors.CARD_BG,
                fg=Colors.ERROR
            ).pack(side=tk.LEFT)

            tk.Label(
                answer_frame,
                text=f"{self.format_answer(detail)}",
                font=Fonts.BODY,
                bg=Colors.CARD_BG,
                fg=Colors.ERROR
            ).pack(side=tk.LEFT)

            correct_frame = tk.Frame(detail_content, bg=Colors.CARD_BG)
            correct_frame.pack(fill=tk.X, pady=Spacing.XS)

            tk.Label(
                correct_frame,
                text="Правильный ответ: ",
                font=Fonts.BODY,
                bg=Colors.CARD_BG,
                fg=Colors.SUCCESS
            ).pack(side=tk.LEFT)

            tk.Label(
                correct_frame,
                text=self.format_correct_answer(detail),
                font=Fonts.BODY,
                bg=Colors.CARD_BG,
                fg=Colors.SUCCESS
            ).pack(side=tk.LEFT)

            # Explanation
            expl_outer = tk.Frame(detail_content, bg=Colors.WARNING_BG, bd=0,
                                   highlightthickness=0)
            expl_outer.pack(fill=tk.X, pady=(Spacing.SM, 0))

            expl_frame = tk.Frame(expl_outer, bg=Colors.WARNING_BG)
            expl_frame.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.SM)

            tk.Label(
                expl_frame,
                text="Объяснение:",
                font=("Segoe UI", 10, "bold"),
                bg=Colors.WARNING_BG,
                fg=Colors.TEXT_PRIMARY,
                anchor=tk.W
            ).pack(fill=tk.X)

            # Make explanation clickable if reference exists
            if detail.get("reference"):
                expl_link = tk.Label(
                    expl_frame,
                    text=detail.get("explanation", detail.get("reference", "")),
                    font=("Segoe UI", 10, "underline"),
                    bg=Colors.WARNING_BG,
                    fg=Colors.PRIMARY,
                    cursor="hand2",
                    wraplength=760,
                    justify=tk.LEFT
                )
                expl_link.pack(anchor=tk.W, pady=(Spacing.XS, 0))

                def make_click_handler(d=detail, win=window):
                    def on_click(e):
                        self.open_reglament_from_result(d, win)
                    return on_click

                expl_link.bind("<Button-1>", make_click_handler(detail))
                expl_link.bind("<Enter>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline", "bold")))
                expl_link.bind("<Leave>", lambda e, w=expl_link: w.configure(font=("Segoe UI", 10, "underline")))
            else:
                tk.Label(
                    expl_frame,
                    text=detail.get("explanation", ""),
                    font=("Segoe UI", 10),
                    bg=Colors.WARNING_BG,
                    fg=Colors.TEXT_PRIMARY,
                    wraplength=760,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, pady=(Spacing.XS, 0))

            # Open regulation button
            open_btn = tk.Button(
                detail_content,
                text="📖  Открыть регламент",
                font=("Segoe UI", 9),
                bg=Colors.PRIMARY_BG,
                fg=Colors.PRIMARY,
                activebackground=Colors.PRIMARY,
                activeforeground=Colors.TEXT_ON_PRIMARY,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda d=detail, win=window: self.open_reglament_from_result(d, win),
                bd=0,
                padx=10,
                pady=4
            )

            def open_enter(e, btn=open_btn):
                btn.configure(bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY)
            def open_leave(e, btn=open_btn):
                btn.configure(bg=Colors.PRIMARY_BG, fg=Colors.PRIMARY)

            open_btn.bind("<Enter>", open_enter)
            open_btn.bind("<Leave>", open_leave)
            open_btn.pack(anchor=tk.W, pady=(Spacing.XS, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        window.protocol("WM_DELETE_WINDOW", window.destroy)

    def open_reglament_from_result(self, detail, parent_window=None):
        """Open regulation window from test results."""
        from study_mode import StudyModeWindow
        reglament = self._load_reglament_data()
        section_ref = detail.get("section_ref", "")
        study_window = StudyModeWindow(
            parent_window or self,
            reglament,
            on_close=lambda: None,
            section_reference=section_ref
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
            if correct_answer is True:
                return "Верно"
            elif correct_answer is False:
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

        indices = [self.tree.index(item) for item in selection]
        indices.sort(reverse=True)

        for idx in indices:
            if 0 <= idx < len(self.results):
                del self.results[idx]

        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.populate_table()
            messagebox.showinfo("Успех", "Результат удален")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить результат: {e}")

    def download_pdf(self):
        """Generate and download PDF for selected result."""
        if not generate_pdf:
            messagebox.showerror("Ошибка", "Библиотека reportlab не установлена.\nУстановите: pip install reportlab")
            return

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите результат из таблицы")
            return

        item = selection[0]
        item_index = self.tree.index(item)

        if item_index >= len(self.results):
            return

        result = self.results[item_index]

        try:
            pdf_path = generate_pdf(result, {})
            messagebox.showinfo("Успех", f"PDF сохранен:\n{pdf_path}")

            # Open the PDF file
            import os
            os.startfile(pdf_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {e}")
