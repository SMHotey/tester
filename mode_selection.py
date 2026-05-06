#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mode selection window.
"""

import tkinter as tk
from tkinter import ttk


class ModeSelectionWindow(tk.Toplevel):
    """Window for selecting application mode."""

    def __init__(self, parent, on_study_mode, on_test_mode, on_view_results, on_scenario_test_mode=None):
        """Initialize mode selection window."""
        super().__init__(parent)
        self.on_study_mode = on_study_mode
        self.on_test_mode = on_test_mode
        self.on_view_results = on_view_results
        self.on_scenario_test_mode = on_scenario_test_mode

        self.title("Выбор режима работы")
        self.geometry("500x500")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        # Center window
        self.center_window()

        self.create_widgets()

    def center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create window widgets."""
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0")
        title_frame.pack(pady=30)

        title_label = tk.Label(
            title_frame,
            text="Система тестирования",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Проверка знаний регламента сопровождения сделок",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Buttons frame
        buttons_frame = tk.Frame(self, bg="#f0f0f0")
        buttons_frame.pack(expand=True)

        # Study mode button
        study_btn = tk.Button(
            buttons_frame,
            text="📚  Режим изучения",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.on_study_mode
        )
        study_btn.pack(pady=10, fill=tk.X, padx=50)

        # Study mode description
        study_desc = tk.Label(
            buttons_frame,
            text="Изучение регламента сопровождения сделок",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        study_desc.pack(pady=(0, 15))

        # Test mode button
        test_btn = tk.Button(
            buttons_frame,
            text="✏️  Режим тестирования",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.on_test_mode
        )
        test_btn.pack(pady=10, fill=tk.X, padx=50)

        # Test mode description
        test_desc = tk.Label(
            buttons_frame,
            text="Проверка знаний (сценарии 1-40)",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        test_desc.pack(pady=(0, 15))

        # Scenario test mode button - always show
        scenario_test_btn = tk.Button(
            buttons_frame,
            text="🎯  Тестирование по сценарию",
            font=("Arial", 16, "bold"),
            bg="#9C27B0",
            fg="white",
            activebackground="#7B1FA8",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.on_scenario_test_mode
        )
        scenario_test_btn.pack(pady=10, fill=tk.X, padx=50)

        # Scenario test mode description
        scenario_test_desc = tk.Label(
            buttons_frame,
            text="Тестирование по готовым сценариям из test_scenarios.json",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        scenario_test_desc.pack(pady=(0, 15))

        # View results button
        results_btn = tk.Button(
            buttons_frame,
            text="📊  Просмотр результатов",
            font=("Arial", 16, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.on_view_results
        )
        results_btn.pack(pady=10, fill=tk.X, padx=50)

        # Results description
        results_desc = tk.Label(
            buttons_frame,
            text="Таблица результатов тестирования",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        results_desc.pack()
