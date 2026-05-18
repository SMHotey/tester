# -*- coding: utf-8 -*-
"""
Question bank manager window.
Allows importing, selecting, and deleting question bank files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from style_config import Colors, Fonts, Spacing
from question_bank_manager import QuestionBankManager


class QuestionBankWindow(tk.Toplevel):
    """Window for managing question banks."""

    def __init__(self, parent, bank_manager, on_back, on_bank_changed=None):
        super().__init__(parent)
        self.bank_manager = bank_manager
        self.on_back = on_back
        self.on_bank_changed = on_bank_changed

        self.title("Управление банками вопросов")
        self.geometry("640x520")
        self.configure(bg=Colors.BG)
        self.resizable(False, False)

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 640) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"640x520+{x}+{y}")

        self.create_widgets()
        self.refresh_list()

        self.protocol("WM_DELETE_WINDOW", self.on_back)

    def create_widgets(self):
        # ─── Header ───────────────────────────────────────────────
        header = tk.Frame(self, bg=Colors.PRIMARY, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Button(
            header,
            text="←  Назад",
            font=("Segoe UI", 11),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=12,
            pady=8,
            command=self.on_back,
        ).pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)

        tk.Label(
            header,
            text="Банки вопросов",
            font=Fonts.HEADING,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY,
        ).pack(side=tk.LEFT, pady=Spacing.MD)

        # ─── Body ─────────────────────────────────────────────────
        body = tk.Frame(self, bg=Colors.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

        # Hint
        tk.Label(
            body,
            text="Выберите активный банк вопросов или импортируйте новый:",
            font=Fonts.BODY,
            bg=Colors.BG,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, Spacing.MD))

        # ─── Listbox with scrollbar ───────────────────────────────
        list_frame = tk.Frame(body, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY_BG,
            selectforeground=Colors.PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            cursor="hand2",
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # ─── Button row ───────────────────────────────────────────
        btn_row = tk.Frame(body, bg=Colors.BG)
        btn_row.pack(fill=tk.X, pady=(Spacing.LG, 0))

        self.btn_import = tk.Button(
            btn_row,
            text="📥  Импортировать",
            font=("Segoe UI", 10),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=14,
            pady=8,
            command=self.on_import,
        )
        self.btn_import.pack(side=tk.LEFT)

        self.btn_activate = tk.Button(
            btn_row,
            text="✓  Сделать активным",
            font=("Segoe UI", 10),
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.SUCCESS_LIGHT,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=14,
            pady=8,
            command=self.on_activate,
        )
        self.btn_activate.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        self.btn_delete = tk.Button(
            btn_row,
            text="🗑  Удалить",
            font=("Segoe UI", 10),
            bg=Colors.ERROR,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.ERROR_LIGHT,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=14,
            pady=8,
            command=self.on_delete,
        )
        self.btn_delete.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        # ─── Status bar ───────────────────────────────────────────
        self.status_label = tk.Label(
            body,
            text="",
            font=Fonts.BODY_SMALL,
            bg=Colors.BG,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(Spacing.MD, 0))

        # Double-click to activate
        self.listbox.bind("<Double-Button-1>", lambda e: self.on_activate())

    def refresh_list(self):
        """Reload the bank list from the manager and update the listbox."""
        self.listbox.delete(0, tk.END)
        banks = self.bank_manager.list_banks()

        if not banks:
            self.listbox.insert(tk.END, "  (нет импортированных банков — используется встроенный)")
            self.listbox.itemconfig(0, fg=Colors.TEXT_DISABLED)
            self.btn_activate.configure(state=tk.DISABLED)
            self.btn_delete.configure(state=tk.DISABLED)
            self.status_label.configure(
                text="Активен: встроенный банк вопросов (из questions.json)"
            )
            return

        self.bank_items = {}  # filename -> index in listbox
        for i, bank in enumerate(banks):
            active_flag = " ★ АКТИВЕН" if bank["active"] else ""
            label = f"  {bank['name']}{active_flag}  ({bank['count']} вопросов)"
            self.listbox.insert(tk.END, label)
            self.bank_items[i] = bank["file"]
            if bank["active"]:
                self.listbox.itemconfig(i, fg=Colors.PRIMARY, bg=Colors.PRIMARY_BG)

        self.btn_activate.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)

        active_name = self.bank_manager.get_active_bank_name()
        if active_name:
            self.status_label.configure(text=f"Активен: {active_name}")
        else:
            self.status_label.configure(text="Активен: встроенный банк вопросов (из questions.json)")

    def _get_selected_filename(self):
        """Return the filename of the currently selected bank, or None."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Внимание", "Выберите банк из списка")
            return None
        idx = sel[0]
        return self.bank_items.get(idx)

    def on_import(self):
        """Open file dialog and import a questions.json file."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с вопросами",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        # Ask for a name
        name_dialog = _BankNameDialog(self, "Название банка")
        self.wait_window(name_dialog.dialog)
        bank_name = name_dialog.result
        if bank_name is None:
            return  # User cancelled

        success, msg = self.bank_manager.import_bank(file_path, name=bank_name)
        if success:
            self.refresh_list()
            self.status_label.configure(text=msg, fg=Colors.SUCCESS)
        else:
            messagebox.showerror("Ошибка импорта", msg)

    def on_activate(self):
        """Set the selected bank as active."""
        filename = self._get_selected_filename()
        if not filename:
            return
        success, msg = self.bank_manager.set_active(filename)
        if success:
            self.refresh_list()
            self.status_label.configure(text=msg, fg=Colors.SUCCESS)
            if self.on_bank_changed:
                self.on_bank_changed()
        else:
            messagebox.showerror("Ошибка", msg)

    def on_delete(self):
        """Delete the selected bank."""
        filename = self._get_selected_filename()
        if not filename:
            return

        # Find the bank name for the confirm dialog
        banks = self.bank_manager.list_banks()
        bank_name = None
        for b in banks:
            if b["file"] == filename:
                bank_name = b["name"]
                break

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить банк «{bank_name}»?\nФайл будет удалён безвозвратно.",
        )
        if not confirm:
            return

        success, msg = self.bank_manager.delete_bank(filename)
        if success:
            self.refresh_list()
            self.status_label.configure(text=msg, fg=Colors.WARNING)
            if self.on_bank_changed:
                self.on_bank_changed()
        else:
            messagebox.showerror("Ошибка", msg)


class _BankNameDialog:
    """Simple modal dialog to enter a bank name."""

    def __init__(self, parent, title):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.configure(bg=Colors.CARD_BG)
        self.dialog.resizable(False, False)
        self.result = None

        w, h = 360, 160
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        tk.Label(
            self.dialog,
            text="Введите название банка вопросов:",
            font=Fonts.BODY,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
        ).pack(pady=(Spacing.XL, Spacing.MD), padx=Spacing.XL)

        self.entry = tk.Entry(
            self.dialog,
            font=Fonts.BODY_LARGE,
            bg=Colors.BG,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            insertbackground=Colors.PRIMARY,
        )
        self.entry.pack(fill=tk.X, padx=Spacing.XL, pady=(0, Spacing.LG))
        self.entry.focus_set()

        btn_frame = tk.Frame(self.dialog, bg=Colors.CARD_BG)
        btn_frame.pack(fill=tk.X, padx=Spacing.XL)

        tk.Button(
            btn_frame,
            text="Отмена",
            font=("Segoe UI", 10),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.BORDER_LIGHT,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=16,
            pady=6,
            command=self.on_cancel,
        ).pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        tk.Button(
            btn_frame,
            text="OK",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            padx=16,
            pady=6,
            command=self.on_ok,
        ).pack(side=tk.RIGHT)

        self.entry.bind("<Return>", lambda e: self.on_ok())
        self.entry.bind("<Escape>", lambda e: self.on_cancel())
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        name = self.entry.get().strip()
        if name:
            self.result = name
            self.dialog.destroy()
        else:
            self.result = ""
            self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()
