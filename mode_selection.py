#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized mode selection window with card-based layout.
"""

import tkinter as tk
from tkinter import messagebox
from style_config import Colors, Fonts, Spacing


class ModeSelectionWindow(tk.Toplevel):
    """Modern window for selecting application mode."""

    # Modern card-style button configurations
    MODE_BUTTONS = [
        {
            "title": "Режим изучения",
            "description": "Изучение регламента сопровождения сделок с удобной навигацией",
            "icon": "📖",
            "color": Colors.PRIMARY,
            "color_light": Colors.PRIMARY_BG,
            "attr": "on_study_mode",
        },
        {
            "title": "Режим тестирования",
            "description": "Проверка знаний по вопросам",
            "icon": "      ✍️",
            "color": Colors.SUCCESS,
            "color_light": Colors.PRIMARY_BG,
            "attr": "on_test_mode",
        },
        {
            "title": "Тестирование по сценарию",
            "description": "Проверка знаний по готовым сценариям",
            "icon": "🎯",
            "color": Colors.SECONDARY,
            "color_light": Colors.SECONDARY_BG,
            "attr": "on_scenario_test_mode",
        },
        {
            "title": "Просмотр результатов",
            "description": "Таблица результатов тестирования",
            "icon": "📊",
            "color": Colors.WARNING,
            "color_light": Colors.WARNING_BG,
            "attr": "on_view_results",
        },
        # ─── Editing section ────────────────────────────────────────
        {
            "title": "Редактировать вопросы",
            "description": "Добавление, изменение и удаление вопросов для тестирования",
            "icon": "✏️",
            "color": Colors.PRIMARY_DARK,
            "color_light": Colors.PRIMARY_BG,
            "attr": "on_edit_questions",
            "protected": True,
        },
        {
            "title": "Редактировать сценарии",
            "description": "Добавление, изменение и удаление сценариев и их вопросов",
            "icon": "📝",
            "color": Colors.SECONDARY_DARK,
            "color_light": Colors.SECONDARY_BG,
            "attr": "on_edit_scenarios",
            "protected": True,
        },
    ]

    def __init__(self, parent, on_study_mode, on_test_mode, on_view_results,
                 on_scenario_test_mode=None, on_edit_questions=None,
                 on_edit_scenarios=None):
        super().__init__(parent)
        self.on_study_mode = on_study_mode
        self.on_test_mode = on_test_mode
        self.on_view_results = on_view_results
        self.on_scenario_test_mode = on_scenario_test_mode
        self.on_edit_questions = on_edit_questions
        self.on_edit_scenarios = on_edit_scenarios

        self.title("Система тестирования")
        self.geometry("560x920")
        self.resizable(False, False)
        self.configure(bg=Colors.BG)

        self.center_window()
        self.create_widgets()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

    def center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def quit_app(self):
        """Quit the application."""
        self.master.destroy()

    def _check_password(self):
        """Show password dialog. Returns True if correct."""
        dialog = tk.Toplevel(self)
        dialog.title("Подтверждение")
        dialog.configure(bg=Colors.CARD_BG)
        dialog.resizable(False, False)

        w, h = 380, 200
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.transient(self)
        dialog.grab_set()

        result = {"ok": False}

        tk.Label(
            dialog,
            text="Введите пароль для доступа:",
            font=Fonts.BODY,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
        ).pack(pady=(Spacing.XXL, Spacing.MD), padx=Spacing.XL)

        frame = tk.Frame(dialog, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        frame.pack(fill=tk.X, padx=Spacing.XL, pady=(0, Spacing.LG))

        entry = tk.Entry(
            frame,
            font=Fonts.BODY_LARGE,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, bd=0,
            show="*",
            insertbackground=Colors.PRIMARY,
        )
        entry.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        entry.focus_set()
        entry.bind("<FocusIn>", lambda e: frame.configure(bg=Colors.PRIMARY))
        entry.bind("<FocusOut>", lambda e: frame.configure(bg=Colors.BORDER_LIGHT))

        def on_ok():
            if entry.get() == "admin321":
                result["ok"] = True
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный пароль", parent=dialog)

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=Colors.CARD_BG)
        btn_frame.pack(fill=tk.X, padx=Spacing.XL)

        tk.Button(
            btn_frame, text="Отмена", font=("Segoe UI", 10),
            bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=16, pady=6,
            command=on_cancel,
        ).pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        tk.Button(
            btn_frame, text="OK", font=("Segoe UI", 10, "bold"),
            bg=Colors.PRIMARY, fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT, relief=tk.FLAT,
            cursor="hand2", bd=0, padx=16, pady=6,
            command=on_ok,
        ).pack(side=tk.RIGHT)

        entry.bind("<Return>", lambda e: on_ok())
        dialog.bind("<Escape>", lambda e: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        self.wait_window(dialog)
        return result["ok"]

    def create_widgets(self):
        """Create all window widgets with modern design."""

        # ─── Header with gradient effect ───
        header_frame = tk.Frame(self, bg=Colors.PRIMARY, height=160)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Decorative accent bar
        accent = tk.Frame(header_frame, bg=Colors.PRIMARY_LIGHT, height=4)
        accent.pack(fill=tk.X, side=tk.BOTTOM)

        # App icon area
        icon_label = tk.Label(
            header_frame,
            text="📋",
            font=("Segoe UI", 42),
            bg=Colors.PRIMARY,
            fg="white"
        )
        icon_label.pack(pady=(Spacing.XXL, Spacing.XS))

        # Title
        title_label = tk.Label(
            header_frame,
            text="Система тестирования",
            font=Fonts.TITLE_MEDIUM,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY
        )
        title_label.pack()

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Проверка знаний регламента сопровождения сделок",
            font=Fonts.BODY,
            bg=Colors.PRIMARY,
            fg=Colors.PRIMARY_BG
        )
        subtitle_label.pack(pady=(Spacing.XS, 0))

        # ─── Body with mode cards ───
        body = tk.Frame(self, bg=Colors.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

        # Section hint
        hint = tk.Label(
            body,
            text="Выберите режим работы:",
            font=Fonts.SUBHEADING,
            bg=Colors.BG,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W
        )
        hint.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Mode cards
        for mode in self.MODE_BUTTONS:
            self._create_mode_card(body, mode)

    def _create_mode_card(self, parent, mode):
        """Create a modern clickable mode card."""
        card_outer = tk.Frame(parent, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        card_outer.pack(fill=tk.X, pady=(0, Spacing.MD))

        # Inner card with hover effect
        card_inner = tk.Frame(card_outer, bg=Colors.CARD_BG, bd=0, highlightthickness=0,
                              cursor="hand2")
        card_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Content inside card
        content = tk.Frame(card_inner, bg=Colors.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Top row: icon + title + arrow
        top_row = tk.Frame(content, bg=Colors.CARD_BG)
        top_row.pack(fill=tk.X)

        # Icon in colored circle
        icon_circle = tk.Frame(top_row, bg=mode["color_light"], width=48, height=48,
                               bd=0, highlightthickness=0)
        icon_circle.pack_propagate(False)
        icon_circle.pack(side=tk.LEFT)

        icon_label = tk.Label(
            icon_circle,
            text=mode["icon"],
            font=("Segoe UI", 20),
            bg=mode["color_light"],
            fg=mode["color"]
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Title and description
        text_frame = tk.Frame(top_row, bg=Colors.CARD_BG)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(Spacing.MD, 0))

        card_title = tk.Label(
            text_frame,
            text=mode["title"],
            font=Fonts.SUBHEADING,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        )
        card_title.pack(fill=tk.X)

        card_desc = tk.Label(
            text_frame,
            text=mode["description"],
            font=Fonts.BODY_SMALL,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W,
            wraplength=380,
            justify=tk.LEFT
        )
        card_desc.pack(fill=tk.X)

        # Arrow indicator
        arrow = tk.Label(
            top_row,
            text="→",
            font=("Segoe UI", 18),
            bg=Colors.CARD_BG,
            fg=Colors.BORDER
        )
        arrow.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # ─── Hover & Click Effects ───
        callback = getattr(self, mode["attr"])
        protected = mode.get("protected", False)

        def on_click(e=None):
            if protected and not self._check_password():
                return
            callback()

        def on_enter(e, inner=card_inner, hl_bg=mode["color_light"]):
            inner.configure(bg=hl_bg)
            for child in inner.winfo_children():
                child.configure(bg=hl_bg)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Frame):
                        subchild.configure(bg=hl_bg)
                        for subsub in subchild.winfo_children():
                            if isinstance(subsub, tk.Frame):
                                subsub.configure(bg=hl_bg)
            arrow.configure(fg=mode["color"])

        def on_leave(e, inner=card_inner):
            inner.configure(bg=Colors.CARD_BG)
            for child in inner.winfo_children():
                child.configure(bg=Colors.CARD_BG)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Frame):
                        subchild.configure(bg=Colors.CARD_BG)
                        for subsub in subchild.winfo_children():
                            if isinstance(subsub, tk.Frame):
                                subsub.configure(bg=Colors.CARD_BG)
            arrow.configure(fg=Colors.BORDER)

        # Bind events to all relevant widgets for full-area click
        for widget in [card_inner, content, top_row, text_frame, card_title, card_desc, icon_circle, icon_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
