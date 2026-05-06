#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate fixed study_mode.py
"""

content = r"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Окно режима изучения для просмотра регламента.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path


class StudyModeWindow(tk.Toplevel):
    """Окно для изучения регламента."""

    def __init__(self, parent, reglament, on_back=None, on_close=None):
        """Инициализация окна изучения."""
        super().__init__(parent)
        self.reglament = reglament
        self.on_back = on_back
        self.on_close = on_close
        self.process_listbox = None
        self.process_title = None
        self.process_desc = None
        self.steps_text = None

        self.title("Режим изучения - Регламент")
        self.geometry("1100x700")
        self.configure(bg="#f0f0f0")

        self.create_widgets()
        self.load_reglament_structure()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_widgets(self):
        """Создание виджетов окна."""
        # Заголовок
        header_frame = tk.Frame(self, bg="#2196F3", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        back_btn = tk.Button(
            header_frame,
            text="← Назад",
            font=("Arial", 11),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.close_window
        )
        back_btn.pack(side=tk.LEFT, padx=15, pady=15)

        title_label = tk.Label(
            header_frame,
            text="Регламент сопровождения сделок",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, pady=15, padx=20)

        # Изменяемая панель с разделителем
        paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, bg="#f0f0f0")
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - список разделов (изменяемая ширина)
        left_panel = tk.Frame(paned_window, bg="white", relief=tk.RIDGE, bd=2)
        paned_window.add(left_panel, minsize=200, width=400)

        tk.Label(
            left_panel,
            text="Разделы регламента",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(pady=10)

        # Список с полосой прокрутки
        list_frame = tk.Frame(left_panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.process_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            bg="white",
            selectbackground="#2196F3",
            activestyle='dotbox',
            justify=tk.LEFT,
            width=50
        )
        self.process_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_listbox.yview)

        self.process_listbox.bind('<<ListboxSelect>>', self.on_process_select)

        # Правая панель - детали процесса
        right_panel = tk.Frame(paned_window, bg="white", relief=tk.RIDGE, bd=2)
        paned_window.add(right_panel, minsize=400, width=680)

        # Заголовок процесса
        self.process_title = tk.Label(
            right_panel,
            text="Выберите раздел слева",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333",
            wraplength=650,
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.process_title.pack(pady=10, padx=10, fill=tk.X)

        # Описание процесса
        self.process_desc = tk.Label(
            right_panel,
            text="",
            font=("Arial", 10),
            bg="white",
            fg="#666",
            wraplength=650,
            justify=tk.LEFT,
            anchor=tk.W
        )
        self.process_desc.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Фрейм для шагов с полосой прокрутки
        steps_label = tk.Label(
            right_panel,
            text="Содержание раздела:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333",
            anchor=tk.W
        )
        steps_label.pack(pady=(10, 5), padx=10, fill=tk.X)

        steps_frame = tk.Frame(right_panel, bg="white")
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        steps_scrollbar = ttk.Scrollbar(steps_frame)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.steps_text = tk.Text(
            steps_frame,
            font=("Arial", 10),
            yscrollcommand=steps_scrollbar.set,
            bg="white",
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.steps_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        steps_scrollbar.config(command=self.steps_text.yview)

        # Настройка тегов текста
        self.steps_text.tag_config("heading", font=("Arial", 11, "bold"), foreground="#2196F3")
        self.steps_text.tag_config("subheading", font=("Arial", 10, "bold"), foreground="#1976D2")
        self.steps_text.tag_config("warning", foreground="#FF5722")
        self.steps_text.tag_config("info", foreground="#2196F3")
        self.steps_text.tag_config("success", foreground="#4CAF50")
        self.steps_text.tag_config("bullet", lmargin1=20, lmargin2=20)
        self.steps_text.tag_config("indent", lmargin1=40, lmargin2=40)

    def load_reglament_structure(self):
        """Загрузка структуры регламента в список."""
        self.process_listbox.delete(0, tk.END)

        # Глобальные правила
        self.process_listbox.insert(tk.END, "Глобальные правила")
        self.process_listbox.itemconfig(0, {'fg': '#FF5722'})

        # Разделитель
        self.process_listbox.insert(tk.END, "-" * 30)
        self.process_listbox.itemconfig(1, {'fg': '#ccc'})

        # Добавление процессов
        processes = self.reglament.get("processes", [])
        for i, process in enumerate(processes, start=1):
            title = process.get("title", f"Процесс {i}")
            # Перенос длинных названий
            if len(title) > 45:
                title = title[:42] + "..."
            self.process_listbox.insert(tk.END, f"{i}. {title}")

        # Типы документов
        self.process_listbox.insert(tk.END, "-" * 30)
        self.process_listbox.itemconfig(tk.END, {'fg': '#ccc'})

        self.process_listbox.insert(tk.END, "Типы документов")
        last_index = self.process_listbox.size() - 1
        self.process_listbox.itemconfig(last_index, {'fg': '#9C27B0'})

    def on_process_select(self, event):
        """Обработка выбора раздела."""
        selection = self.process_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        selected_text = self.process_listbox.get(index)

        # Очистка правой панели
        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        if "Глобальные правила" in selected_text:
            self.show_global_rules()
        elif "Типы документов" in selected_text:
            self.show_document_types()
        elif "-" in selected_text:
            return  # Разделитель, ничего не делаем
        else:
            # Поиск процесса по индексу
            # Индекс в списке: 0=глобальные, 1=разделитель, 2+=процессы
            process_index = index - 2  # Вычитаем глобальные правила и разделитель
            processes = self.reglament.get("processes", [])
            if 0 <= process_index < len(processes):
                self.show_process_details(processes[process_index])

        self.steps_text.config(state=tk.DISABLED)

    def show_global_rules(self):
        """Отображение глобальных правил."""
        self.process_title.config(text="Глобальные правила")
        self.process_desc.config(text="Общие правила для всех процессов")

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        global_rules = self.reglament.get("global_rules", {})

        # Правило дат
        date_rule = global_rules.get("date_rule", {})
        self.steps_text.insert(tk.END, "ПРАВИЛО ДАТ:\n", "heading")
        self.steps_text.insert(tk.END, date_rule.get("description", "") + "\n\n")

        # Пометка ИП
        ip_mark = global_rules.get("individual_entrepreneur_mark", {})
        self.steps_text.insert(tk.END, "ПОМЕТКА ИП:\n", "heading")
        self.steps_text.insert(tk.END, ip_mark.get("rule", "") + "\n\n")
        self.steps_text.insert(tk.END, "Реализация: ", "subheading")
        self.steps_text.insert(tk.END, ip_mark.get("implementation", ""))

        self.steps_text.config(state=tk.DISABLED)

    def show_process_details(self, process):
        """Отображение деталей процесса."""
        title = process.get("title", "")
        desc = process.get("description", "")

        self.process_title.config(text=title)
        self.process_desc.config(text=desc)

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        # Показать условия если есть
        if "conditions" in process:
            self.steps_text.insert(tk.END, "УСЛОВИЯ:\n", "heading")
            conditions = process["conditions"]
            for key, value in conditions.items():
                self.steps_text.insert(tk.END, f"• {key}: {value}\n", "bullet")
            self.steps_text.insert(tk.END, "\n")

        # Показать ограничения если есть
        if "restrictions" in process:
            self.steps_text.insert(tk.END, "ОГРАНИЧЕНИЯ:\n", "heading")
            for restriction in process["restrictions"]:
                rtype = restriction.get("type", "")
                text = restriction.get("text", "")
                tag = "warning" if rtype in ["warning", "forbidden", "critical_forbidden"] else "info"
                self.steps_text.insert(tk.END, f"[{rtype.upper()}] ", tag)
                self.steps_text.insert(tk.END, f"{text}\n", "bullet")
            self.steps_text.insert(tk.END, "\n")

        # Показать шаги
        steps = process.get("steps", [])
        if steps:
            self.steps_text.insert(tk.END, "ШАГИ ПРОЦЕССА:\n", "heading")

            for step in steps:
                step_num = step.get("id", "")
                step_title = step.get("title", "")
                step_desc = step.get("description", "")

                self.steps_text.insert(tk.END, f"\nШаг {step_num}: {step_title}\n", "subheading")
                self.steps_text.insert(tk.END, f"{step_desc}\n", "indent")

                # Подшаги
                if "substeps" in step:
                    for substep in step["substeps"]:
                        self.steps_text.insert(tk.END, f"  • {substep}\n", "indent")
                    self.steps_text.insert(tk.END, "\n")

                # Чек-лист
                if "checklist" in step:
                    self.steps_text.insert(tk.END, "  Чек-лист:\n", "subheading")
                    for item in step["checklist"]:
                        self.steps_text.insert(tk.END, f"    ✓ {item}\n", "indent")
                    self.steps_text.insert(tk.END, "\n")

                # Варианты
                if "options" in step:
                    self.steps_text.insert(tk.END, "  Варианты:\n", "subheading")
                    for option in step["options"]:
                        self.steps_text.insert(tk.END, f"    • {option}\n", "indent")
                    self.steps_text.insert(tk.END, "\n")

        # Показать правило валидации если есть (интегрировано в раздел)
        if "validation" in process:
            self.steps_text.insert(tk.END, "\nПРАВИЛО ВАЛИДАЦИИ:\n", "heading")
            validation = process["validation"]
            if isinstance(validation, dict):
                for key, value in validation.items():
                    self.steps_text.insert(tk.END, f"• {key}: {value}\n", "bullet")
            else:
                self.steps_text.insert(tk.END, f"{validation}\n", "bullet")

        # Специальное правило
        if "special_rule" in process:
            self.steps_text.insert(tk.END, "\nСПЕЦИАЛЬНОЕ ПРАВИЛО:\n", "heading")
            self.steps_text.insert(tk.END, process["special_rule"], "warning")

        # Сценарии (для замены счета)
        if "scenarios" in process:
            self.steps_text.insert(tk.END, "\nСЦЕНАРИИ:\n", "heading")
            for scenario in process["scenarios"]:
                self.steps_text.insert(tk.END, f"\nСценарий {scenario.get('id', '')}: {scenario.get('title', '')}\n", "subheading")
                self.steps_text.insert(tk.END, f"Условие: {scenario.get('condition', '')}\n", "bullet")
                for step in scenario.get("steps", []):
                    self.steps_text.insert(tk.END, f"  • {step}\n", "indent")

        # Шаблоны писем
        if "templates" in process:
            self.steps_text.insert(tk.END, "\nШАБЛОНЫ ПИСЕМ:\n", "heading")
            templates = process["templates"]
            for key, template in templates.items():
                self.steps_text.insert(tk.END, f"\n{key}:\n", "subheading")
                if isinstance(template, dict):
                    for tkey, tvalue in template.items():
                        self.steps_text.insert(tk.END, f"  {tkey}: {tvalue}\n", "indent")
                else:
                    self.steps_text.insert(tk.END, f"{template}\n", "indent")

        # Правила (для раздела УПД)
        if "rules" in process:
            self.steps_text.insert(tk.END, "\nПРАВИЛА:\n", "heading")
            for rule in process["rules"]:
                title_rule = rule.get("title", "")
                desc_rule = rule.get("description", "")
                self.steps_text.insert(tk.END, f"{title_rule}:\n", "subheading")
                self.steps_text.insert(tk.END, f"  {desc_rule}\n", "indent")

        # Варианты подписания (для раздела УПД)
        if "signing_variants" in process:
            self.steps_text.insert(tk.END, "\nВАРИАНТЫ ПОДПИСАНИЯ:\n", "heading")
            for variant in process["signing_variants"]:
                vtitle = variant.get("title", "")
                vcond = variant.get("condition", "")
                self.steps_text.insert(tk.END, f"\n{variant.get('id', '')}. {vtitle}\n", "subheading")
                self.steps_text.insert(tk.END, f"  Условие: {vcond}\n", "bullet")

                if "requirements" in variant:
                    self.steps_text.insert(tk.END, "  Требования:\n", "subheading")
                    for req in variant["requirements"]:
                        self.steps_text.insert(tk.END, f"    • {req}\n", "indent")

                if "process" in variant:
                    self.steps_text.insert(tk.END, "  Процесс:\n", "subheading")
                    for proc in variant["process"]:
                        self.steps_text.insert(tk.END, f"    • {proc}\n", "indent")

                if "restrictions" in variant:
                    self.steps_text.insert(tk.END, "  Ограничения:\n", "subheading")
                    for res in variant["restrictions"]:
                        rtype = res.get("type", "")
                        rtext = res.get("text", "")
                        tag = "warning" if "forbidden" in rtype else "info"
                        self.steps_text.insert(tk.END, f"    [{rtype.upper()}] ", tag)
                        self.steps_text.insert(tk.END, f"{rtext}\n", "indent")

        # Процедура изменения (для раздела УПД)
        if "changes" in process:
            self.steps_text.insert(tk.END, "\nПРОЦЕДУРА ИЗМЕНЕНИЯ УПД:\n", "heading")
            changes = process["changes"]
            if "procedure" in changes:
                for proc_step in changes["procedure"]:
                    self.steps_text.insert(tk.END, f"• {proc_step}\n", "bullet")
            if "template_type" in changes:
                self.steps_text.insert(tk.END, f"\nШаблон: {changes['template_type']}\n", "subheading")

        self.steps_text.config(state=tk.DISABLED)

    def show_document_types(self):
        """Отображение типов документов."""
        self.process_title.config(text="Типы документов")
        self.process_desc.config(text="Список документов, используемых в регламенте")

        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)

        # Показать типы документов
        doc_types = self.reglament.get("document_types", [])
        for doc in doc_types:
            name = doc.get("name", "")
            doc_id = doc.get("id", "")
            required_for = []
            if doc.get("required_for_production"):
                required_for.append("производство")
            if doc.get("required_for_shipment"):
                required_for.append("отгрузка")
            if doc.get("required_for_closing"):
                required_for.append("закрытие")

            self.steps_text.insert(tk.END, f"Тип: {name}\n", "subheading")
            self.steps_text.insert(tk.END, f"   ID: {doc_id}\n", "indent")
            if required_for:
                self.steps_text.insert(tk.END, f"   Требуется для: {', '.join(required_for)}\n", "indent")
            self.steps_text.insert(tk.END, "\n")

        # Показать правила валидации (интегрировано сюда вместо отдельного раздела)
        validation_rules = self.reglament.get("validation_rules", {})
        if validation_rules:
            self.steps_text.insert(tk.END, "\nПРАВИЛА ВАЛИДАЦИИ:\n", "heading")
            for key, value in validation_rules.items():
                self.steps_text.insert(tk.END, f"{key}:\n", "subheading")
                self.steps_text.insert(tk.END, f"  {value}\n\n", "indent")

        # Показать сроки выполнения
        if "deadline_calculations" in self.reglament:
            self.steps_text.insert(tk.END, "\nСРОКИ ВЫПОЛНЕНИЯ:\n", "heading")
            deadlines = self.reglament["deadline_calculations"]
            for key, value in deadlines.items():
                self.steps_text.insert(tk.END, f"\n{key}:\n", "subheading")
                self.steps_text.insert(tk.END, f"  Дней: {value.get('days', 'N/A')}\n", "indent")
                self.steps_text.insert(tk.END, f"  Отсчитывать от: {value.get('from', 'N/A')}\n", "indent")
                if "warning_threshold" in value:
                    self.steps_text.insert(tk.END, f"  Порог предупреждения: {value['warning_threshold']} дней\n", "indent")

        self.steps_text.config(state=tk.DISABLED)

    def close_window(self):
        """Закрытие окна."""
        if self.on_close:
            self.on_close()
        elif self.on_back:
            self.on_back()
        else:
            self.destroy()
"""

with open(r"C:\Projects\tester\study_mode.py", "w", encoding="utf-8") as f:
    f.write(content)

print("study_mode.py has been written successfully!")
