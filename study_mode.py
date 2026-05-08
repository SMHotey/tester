#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Окно режима изучения - современный дизайн.
Отображение регламента версии 4.0 с поддержкой секций и подсекций.
"""

import tkinter as tk
from tkinter import ttk

from style_config import Colors, Fonts, Spacing


def _make_card(parent, paned, minsize=200, width=300, bg=Colors.CARD_BG):
    """
    Создаёт видимую карточку для PanedWindow.
    Возвращает контент-фрейм для наполнения.
    """
    outer = tk.Frame(paned, bg="#D0D0D0", bd=0, highlightthickness=0)
    paned.add(outer, minsize=minsize, width=width)

    inner = tk.Frame(outer, bg=bg, bd=0, highlightthickness=0)
    inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    content = tk.Frame(inner, bg=bg, bd=0, highlightthickness=0)
    content.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

    return content


class StudyModeWindow(tk.Toplevel):
    """Окно для изучения регламента версии 4.0."""

    def __init__(self, parent, reglament, on_back=None, on_close=None, section_reference=None):
        super().__init__(parent)
        self.reglament = reglament
        self.on_back = on_back
        self.on_close = on_close
        self.section_reference = section_reference
        self.process_text = None
        self.process_title = None
        self.process_desc = None
        self.steps_text = None
        self.section_indices = {}
        self.selected_line = None
        self.section_line_map = {}  # Maps section_ref to line number

        doc_title = reglament.get("document_title", "Регламент")
        self.title(doc_title)
        self.geometry("1100x700")
        self.configure(bg="#F0F2F5")

        self.center_window()
        self.create_widgets()
        self.load_reglament_structure()
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Open specific section if reference provided
        if self.section_reference:
            self.after(100, lambda: self.open_section_by_reference(self.section_reference))

    def center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = 1100
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Создание виджетов окна."""

        # ─── HEADER ─────────────────────────────────────────
        header = tk.Frame(self, bg="#1A56C4", height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        back_btn = tk.Button(
            header,
            text="←  Назад",
            font=Fonts.BODY,
            bg="#1A56C4",
            fg="white",
            activebackground="#154B8C",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.close_window,
            bd=0,
            padx=20,
            pady=12
        )

        def _enter(e):
            back_btn.configure(bg="#154B8C")

        def _leave(e):
            back_btn.configure(bg="#1A56C4")

        back_btn.bind("<Enter>", _enter)
        back_btn.bind("<Leave>", _leave)

        back_btn.pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        doc_title = self.reglament.get("document_title", "Регламент")
        tk.Label(
            header,
            text=doc_title,
            font=("Segoe UI", 18, "bold"),
            bg="#1A56C4",
            fg="white"
        ).pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.LG)

        # ─── PANED WINDOW ────────────────────────────────────
        paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=8,
            sashrelief=tk.FLAT,
            bg="#C0C0C0",
            showhandle=False
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # ─── LEFT PANEL (карточка) ─────────────────────────
        left_content = _make_card(
            self, paned,
            minsize=200, width=450,
            bg=Colors.CARD_BG
        )

        # Заголовок
        left_hdr = tk.Frame(left_content, bg="#E8ECEF", height=50)
        left_hdr.pack(fill=tk.X)
        left_hdr.pack_propagate(False)

        tk.Label(
            left_hdr,
            text="  Разделы регламента",
            font=("Segoe UI", 11, "bold"),
            bg="#E8ECEF",
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=Spacing.MD)

        # Текстовое поле (заменяет Listbox)
        list_frame = tk.Frame(left_content, bg=Colors.CARD_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, Spacing.SM))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.process_text = tk.Text(
            list_frame,
            font=("Segoe UI", 11),
            yscrollcommand=scrollbar.set,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=Spacing.LG,
            pady=Spacing.SM,
            state=tk.DISABLED,
            height=20,
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2"
        )
        # Right external padding = Spacing.SM (8px) so distance from text to scrollbar
        # equals distance from text to left edge of card (Spacing.SM + Spacing.LG)
        self.process_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, Spacing.SM))
        scrollbar.config(command=self.process_text.yview)

        # Теги
        self.process_text.tag_config("section", spacing1=Spacing.XS, spacing3=Spacing.XS, foreground=Colors.PRIMARY)
        self.process_text.tag_config("separator", foreground="#B0B0B0", justify=tk.CENTER)
        self.process_text.tag_config("selected", background="#D0E8FF", foreground=Colors.PRIMARY)
        self.process_text.tag_config("hover", background="#F0F8FF", foreground=Colors.PRIMARY)
        self.process_text.tag_config("version", font=("Segoe UI", 11, "bold"))

        self.process_text.bind("<Button-1>", self._on_click)
        self.process_text.bind("<Motion>", self._on_hover)
        self.process_text.bind("<Leave>", self._on_leave)

        self._hovered_line = None

        # ─── RIGHT PANEL (карточка) ────────────────────────
        right_content = _make_card(
            self, paned,
            minsize=400, width=680,
            bg=Colors.CARD_BG
        )

        # Заголовок процесса
        title_frame = tk.Frame(right_content, bg="#E8ECEF", height=56)
        title_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
        title_frame.pack_propagate(False)

        self.process_title = tk.Label(
            title_frame,
            text="Выберите раздел слева",
            font=("Segoe UI", 16, "bold"),
            bg="#E8ECEF",
            fg=Colors.TEXT_PRIMARY,
            wraplength=600,
            anchor=tk.W
        )
        self.process_title.pack(pady=Spacing.MD, padx=Spacing.MD, fill=tk.X)

        # Описание
        self.process_desc = tk.Label(
            right_content,
            text="",
            font=("Segoe UI", 11),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            wraplength=600,
            anchor=tk.W
        )
        self.process_desc.pack(pady=(Spacing.SM, Spacing.MD), padx=Spacing.LG, fill=tk.X)

        # Секция шагов
        section_hdr = tk.Frame(right_content, bg="#E8ECEF", bd=0)
        section_hdr.pack(fill=tk.X, pady=(Spacing.SM, 0))

        tk.Label(
            section_hdr,
            text="  Содержание раздела",
            font=("Segoe UI", 11, "bold"),
            bg="#E8ECEF",
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, pady=Spacing.SM, padx=Spacing.MD)

        # Текст шагов
        steps_frame = tk.Frame(right_content, bg=Colors.CARD_BG)
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, Spacing.MD))

        steps_scrollbar = ttk.Scrollbar(steps_frame)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.steps_text = tk.Text(
            steps_frame,
            font=("Segoe UI", 11),
            yscrollcommand=steps_scrollbar.set,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=Spacing.LG,
            pady=Spacing.LG,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        self.steps_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        steps_scrollbar.config(command=self.steps_text.yview)

        # Теги текста
        self.steps_text.tag_config("heading", font=("Segoe UI", 12, "bold"), foreground=Colors.PRIMARY, spacing3=Spacing.SM)
        self.steps_text.tag_config("subheading", font=("Segoe UI", 11, "bold"), foreground="#1A56C4", spacing3=Spacing.XS, spacing1=Spacing.XS)
        self.steps_text.tag_config("warning", foreground=Colors.ERROR, font=("Segoe UI", 10, "bold"))
        self.steps_text.tag_config("info", foreground=Colors.PRIMARY)
        self.steps_text.tag_config("success", foreground=Colors.SUCCESS)
        self.steps_text.tag_config("bullet", lmargin1=Spacing.LG, lmargin2=Spacing.LG + 10, spacing1=Spacing.XS)
        self.steps_text.tag_config("indent", lmargin1=Spacing.LG + 20, lmargin2=Spacing.LG + 30, spacing1=Spacing.XS)
        self.steps_text.tag_config("subindent", lmargin1=Spacing.LG + 40, lmargin2=Spacing.LG + 50, spacing1=Spacing.XS)
        self.steps_text.tag_config("paragraph", spacing1=Spacing.SM)
        self.steps_text.tag_config("example", foreground="#666666", lmargin1=Spacing.LG, lmargin2=Spacing.LG + 10)

    def _on_click(self, event):
        """Обработка клика по тексту."""
        index = self.process_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])

        if self.selected_line:
            self.process_text.tag_remove("selected", f"{self.selected_line}.0", f"{self.selected_line}.end")

        self.selected_line = line_num
        self.process_text.tag_add("selected", f"{line_num}.0", f"{line_num}.end")

        self._section_select(line_num)

    def _section_select(self, line_num):
        """Обработка выбора раздела."""
        item_type, item_index = self.section_indices.get(line_num, (None, None))

        if not item_type or item_type == "separator":
            return

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        if item_type == "section":
            sections = self.reglament.get("sections", [])
            if 0 <= item_index < len(sections):
                self.show_section_details(sections[item_index])

        self.steps_text.config(state=tk.DISABLED)

    def _on_hover(self, event):
        """Обработка наведения мыши на пункт оглавления."""
        index = self.process_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])

        if line_num == self._hovered_line:
            return

        # Убираем предыдущий ховер
        if self._hovered_line:
            self.process_text.tag_remove("hover", f"{self._hovered_line}.0", f"{self._hovered_line}.end")

        self._hovered_line = line_num

        # Проверяем, что это пункт раздела и он не выбран
        item_type, _ = self.section_indices.get(line_num, (None, None))
        if item_type == "section" and line_num != self.selected_line:
            self.process_text.tag_add("hover", f"{line_num}.0", f"{line_num}.end")

    def _on_leave(self, event):
        """Обработка ухода мыши с виджета."""
        if self._hovered_line:
            self.process_text.tag_remove("hover", f"{self._hovered_line}.0", f"{self._hovered_line}.end")
            self._hovered_line = None

    def load_reglament_structure(self):
        """Загрузка структуры регламента в текстовое поле."""
        self.process_text.config(state=tk.NORMAL)
        self.process_text.delete(1.0, tk.END)
        self.section_indices = {}
        self.selected_line = None
        self.section_line_map = {}  # Maps "section_id" -> line number

        line = 1

        # Информация о документе
        version = self.reglament.get("version", "")
        last_updated = self.reglament.get("last_updated", "")
        info_text = f"Версия: {version}"
        if last_updated:
            info_text += f" (обновлено: {last_updated})"
        self.process_text.insert(tk.END, info_text + "\n", ("version", "section"))
        self.process_text.insert(tk.END, "\n")  # Пустая строка после версии
        line += 2

        # Секции
        sections = self.reglament.get("sections", [])
        for i, section in enumerate(sections):
            title = section.get("title", f"Раздел {section.get('id', i+1)}")
            section_id = section.get("id", "")
            display_title = f"{section_id}. {title}" if section_id else title
            self.process_text.insert(tk.END, f"{display_title}\n", "section")
            self.section_indices[line] = ("section", i)
            # Map section_id for lookup (e.g., "2" -> line, "2.1" -> line)
            if section_id:
                self.section_line_map[str(section_id)] = line
                # Also map subsections
                content = section.get("content", [])
                self._map_subsections(content, section_id, line)
            line += 1

        self.process_text.config(state=tk.DISABLED)

    def _map_subsections(self, content, parent_id, parent_line):
        """Recursively map subsections to their line numbers."""
        for item in content:
            if item.get("type") == "subsection":
                title = item.get("title", "")
                # Extract subsection number (e.g., "2.1. Запрос счёта..." -> "2.1")
                import re
                match = re.search(r'(\d+\.\d+)', title)
                if match:
                    subsection_id = match.group(1)
                    self.section_line_map[subsection_id] = parent_line
                    # Store subsection title for lookup
                    self.section_line_map[f"title_{subsection_id}"] = title

    def open_section_by_reference(self, section_ref):
        """Open a specific section based on reference like '2.1'."""
        if not section_ref:
            return

        # Look up the line number for this section
        line = self.section_line_map.get(str(section_ref))
        if line:
            # Simulate click on that line
            self.selected_line = line
            self.process_text.tag_add("selected", f"{line}.0", f"{line}.end")
            self._section_select(line)
        else:
            # Try to find by searching for subsection
            sections = self.reglament.get("sections", [])
            for section in sections:
                section_id = str(section.get("id", ""))
                if section_ref.startswith(section_id):
                    # Main section found, now look for subsection
                    line = self.section_line_map.get(section_id)
                    if line:
                        self.selected_line = line
                        self.process_text.tag_add("selected", f"{line}.0", f"{line}.end")
                        self._section_select(line)
                        break

    def show_section_details(self, section):
        """Отображение деталей раздела."""
        self.process_title.config(text=section.get("title", ""))
        self.process_desc.config(text=f"Раздел {section.get('id', '')}")

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        content = section.get("content", [])
        self._render_content(content)

        self.steps_text.config(state=tk.DISABLED)

    def _render_content(self, content_items):
        """Рекурсивный рендеринг содержимого."""
        for item in content_items:
            item_type = item.get("type", "")

            if item_type == "paragraph":
                text = item.get("text", "")
                self.steps_text.insert(tk.END, text + "\n", "paragraph")

            elif item_type == "subsection":
                title = item.get("title", "")
                self.steps_text.insert(tk.END, f"\n{title}\n", "subheading")
                nested_content = item.get("content", [])
                self._render_content(nested_content)

            elif item_type == "ordered_list":
                title = item.get("title", "")
                if title:
                    self.steps_text.insert(tk.END, f"\n{title}\n", "subheading")
                items = item.get("items", [])
                for idx, list_item in enumerate(items, 1):
                    self._render_list_item(list_item, f"{idx}. ", "bullet")

            elif item_type == "unordered_list":
                title = item.get("title", "")
                if title:
                    self.steps_text.insert(tk.END, f"\n{title}\n", "subheading")
                items = item.get("items", [])
                for list_item in items:
                    self._render_list_item(list_item, "• ", "bullet")

            elif item_type == "example":
                text = item.get("text", "")
                self.steps_text.insert(tk.END, f"\nПример:\n", "subheading")
                self.steps_text.insert(tk.END, text + "\n", "example")

    def _render_list_item(self, item, prefix, tag):
        """Рендеринг элемента списка (может быть строкой или объектом)."""
        if isinstance(item, str):
            self.steps_text.insert(tk.END, f"{prefix}{item}\n", tag)
        elif isinstance(item, dict):
            text = item.get("text", "")
            self.steps_text.insert(tk.END, f"{prefix}{text}\n", tag)

            # Обработка вложенных элементов
            subitems = item.get("subitems", [])
            for subitem in subitems:
                if isinstance(subitem, str):
                    self.steps_text.insert(tk.END, f"    • {subitem}\n", "subindent")
                elif isinstance(subitem, dict):
                    subtext = subitem.get("text", "")
                    self.steps_text.insert(tk.END, f"    • {subtext}\n", "subindent")
                    # Рекурсивно обрабатываем вложенность
                    nested_subitems = subitem.get("subitems", [])
                    for nested in nested_subitems:
                        if isinstance(nested, str):
                            self.steps_text.insert(tk.END, f"        - {nested}\n", "subindent")
                        elif isinstance(nested, dict):
                            self.steps_text.insert(tk.END, f"        - {nested.get('text', '')}\n", "subindent")

            # Обработка details (для ordered_list)
            details = item.get("details", "")
            if details:
                self.steps_text.insert(tk.END, f"    {details}\n", "subindent")

    def close_window(self):
        """Закрытие окна."""
        if self.on_back:
            self.on_back()
        elif self.on_close:
            self.on_close()
        else:
            self.destroy()
