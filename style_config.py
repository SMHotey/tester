#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Material Design 3 inspired style configuration for the test application.

Provides centralized colors, fonts, and helper functions to create modern-looking
tkinter widgets with hover effects and consistent styling.
"""

import tkinter as tk
from tkinter import ttk


# ─── Color Palette (Material Design 3 inspired) ────────────────────────────

class Colors:
    # Primary blue tones
    PRIMARY = "#1A73E8"        # Main brand color
    PRIMARY_LIGHT = "#4A9AF5"  # Lighter variant for hover
    PRIMARY_DARK = "#1557B0"   # Darker variant for pressed
    PRIMARY_BG = "#E8F0FE"     # Very light primary background

    # Secondary purple tones
    SECONDARY = "#7C3AED"
    SECONDARY_LIGHT = "#9D5CFF"
    SECONDARY_DARK = "#5E2ED5"
    SECONDARY_BG = "#F3EEFF"

    # Success green tones
    SUCCESS = "#16A34A"
    SUCCESS_LIGHT = "#22C55E"
    SUCCESS_DARK = "#15803D"

    # Warning orange tones
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    WARNING_DARK = "#D97706"
    WARNING_BG = "#FFF8E1"

    # Error red tones
    ERROR = "#DC2626"
    ERROR_LIGHT = "#EF4444"
    ERROR_DARK = "#B91C1C"
    ERROR_BG = "#FFEBEE"

    # Neutral tones
    WHITE = "#FFFFFF"
    BG = "#F8F9FA"            # Page background
    CARD_BG = "#FFFFFF"       # Card background
    SURFACE = "#F1F3F4"       # Surface background
    BORDER = "#E0E0E0"        # Border color
    BORDER_LIGHT = "#E8EAED"  # Light border

    # Text colors
    TEXT_PRIMARY = "#202124"  # Primary text
    TEXT_SECONDARY = "#5F6368"  # Secondary text
    TEXT_DISABLED = "#9AA0A6"  # Disabled text
    TEXT_ON_PRIMARY = "#FFFFFF"  # Text on primary colored backgrounds

    # Sidebar
    SIDEBAR_BG = "#FFFFFF"
    SIDEBAR_SELECTED = "#E8F0FE"
    SIDEBAR_HOVER = "#F1F3F4"

    # Progress bar
    PROGRESS_BG = "#E8F0FE"
    PROGRESS_FILL = "#22C55E"  # Green for better visibility (was #1A73E8 blue)


# ─── Font Settings ─────────────────────────────────────────────────────────

class Fonts:
    TITLE_LARGE = ("Segoe UI", 28, "bold")
    TITLE_MEDIUM = ("Segoe UI", 20, "bold")
    TITLE_SMALL = ("Segoe UI", 16, "bold")
    HEADING = ("Segoe UI", 14, "bold")
    SUBHEADING = ("Segoe UI", 12, "bold")
    BODY_LARGE = ("Segoe UI", 12)
    BODY = ("Segoe UI", 11)
    BODY_SMALL = ("Segoe UI", 10)
    CAPTION = ("Segoe UI", 9)
    BUTTON = ("Segoe UI", 12, "bold")
    BUTTON_LARGE = ("Segoe UI", 14, "bold")


# ─── Spacing & Sizing ──────────────────────────────────────────────────────

class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    SECTION = 40


# ─── Border Radius (Visual Only - tkinter doesn't support true border-radius) ──
# We simulate rounded corners with padding and frame nesting

class BorderRadius:
    SM = 4
    MD = 8
    LG = 12
    XL = 16


# ─── Helper Functions ──────────────────────────────────────────────────────

def create_button(parent, text, command, style="primary", size="large",
                  icon=None, width=None, enabled=True):
    """
    Create a modern-styled button with hover effect.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Callback function
        style: 'primary', 'secondary', 'success', 'warning', 'error', 'ghost', 'outline'
        size: 'large', 'medium', 'small'
        icon: Optional emoji/icon string to prepend
        width: Fixed width in pixels (or None for auto)
        enabled: Whether button is initially enabled
    """
    btn_text = f"{icon}  {text}" if icon else text

    color_map = {
        "primary": (Colors.PRIMARY, Colors.PRIMARY_LIGHT, Colors.PRIMARY_DARK),
        "secondary": (Colors.SECONDARY, Colors.SECONDARY_LIGHT, Colors.SECONDARY_DARK),
        "success": (Colors.SUCCESS, Colors.SUCCESS_LIGHT, Colors.SUCCESS_DARK),
        "warning": (Colors.WARNING, Colors.WARNING_LIGHT, Colors.WARNING_DARK),
        "error": (Colors.ERROR, Colors.ERROR_LIGHT, Colors.ERROR_DARK),
        "ghost": (Colors.WHITE, Colors.SURFACE, Colors.SURFACE),
        "outline": (Colors.WHITE, Colors.PRIMARY_BG, Colors.SURFACE),
    }

    size_map = {
        "large": (Fonts.BUTTON_LARGE, 20, 14),
        "medium": (Fonts.BUTTON, 16, 10),
        "small": (("Segoe UI", 10, "bold"), 12, 6),
    }

    bg_color, hover_color, active_color = color_map.get(style, color_map["primary"])
    font, padx_val, pady_val = size_map.get(size, size_map["medium"])
    
    # Determine text color
    if style in ("ghost", "outline"):
        fg_color = Colors.PRIMARY
        if style == "outline":
            btn = tk.Button(
                parent,
                text=btn_text,
                font=font,
                bg=bg_color,
                fg=fg_color,
                activebackground=hover_color,
                activeforeground=fg_color,
                relief=tk.FLAT,
                padx=padx_val,
                pady=pady_val,
                cursor="hand2" if enabled else "arrow",
                state=tk.NORMAL if enabled else tk.DISABLED,
                command=command,
                highlightthickness=1,
                highlightcolor=Colors.PRIMARY,
                highlightbackground=Colors.PRIMARY,
                bd=0
            )
        else:
            btn = tk.Button(
                parent,
                text=btn_text,
                font=font,
                bg=bg_color,
                fg=fg_color,
                activebackground=hover_color,
                activeforeground=fg_color,
                relief=tk.FLAT,
                padx=padx_val,
                pady=pady_val,
                cursor="hand2" if enabled else "arrow",
                state=tk.NORMAL if enabled else tk.DISABLED,
                command=command,
                bd=0
            )
    else:
        btn = tk.Button(
            parent,
            text=btn_text,
            font=font,
            bg=bg_color,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=hover_color,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            padx=padx_val,
            pady=pady_val,
            cursor="hand2" if enabled else "arrow",
            state=tk.NORMAL if enabled else tk.DISABLED,
            command=command,
            bd=0
        )

    # Hover effects
    def on_enter(e):
        if btn.cget('state') != tk.DISABLED:
            if style == "ghost":
                btn.configure(bg=hover_color)
            elif style == "outline":
                btn.configure(bg=hover_color)
            else:
                btn.configure(bg=hover_color)
                # Scale effect
                btn.configure(padx=padx_val + 2, pady=pady_val + 2)

    def on_leave(e):
        if btn.cget('state') != tk.DISABLED:
            if style == "ghost":
                btn.configure(bg=bg_color)
            elif style == "outline":
                btn.configure(bg=bg_color)
            else:
                btn.configure(bg=bg_color)
                btn.configure(padx=padx_val, pady=pady_val)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    if width:
        btn.configure(width=width)

    return btn


def create_card(parent, padding=Spacing.XL, bg=Colors.CARD_BG, **pack_kwargs):
    """
    Create a modern card container with subtle border and shadow-like appearance.
    
    Returns the outer frame (for pack) and the content frame (to place widgets inside).
    """
    # Outer frame provides the border and shadow effect
    outer = tk.Frame(parent, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0)
    
    # Inner frame is the actual content area with padding
    inner = tk.Frame(outer, bg=bg, bd=0, highlightthickness=0)
    inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    # Apply padding to the inner frame
    inner_padded = tk.Frame(inner, bg=bg, bd=0, highlightthickness=0)
    inner_padded.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
    
    outer.pack(**pack_kwargs)
    
    return inner_padded


def create_header(parent, title, bg=Colors.PRIMARY, back_command=None,
                  back_text="← Назад", height=64):
    """
    Create a modern header bar with optional back button.
    
    Returns:
        header_frame: The header frame widget
        back_btn: The back button (or None if not created)
    """
    header_frame = tk.Frame(parent, bg=bg, height=height)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)

    back_btn = None
    if back_command:
        back_btn = tk.Button(
            header_frame,
            text=back_text,
            font=("Segoe UI", 11),
            bg=bg,
            fg=Colors.TEXT_ON_PRIMARY,
            activebackground=Colors.PRIMARY_LIGHT,
            activeforeground=Colors.TEXT_ON_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=back_command,
            bd=0,
            padx=12,
            pady=8
        )
        back_btn.pack(side=tk.LEFT, padx=Spacing.LG, pady=Spacing.MD)
        
        def back_enter(e):
            back_btn.configure(bg=Colors.PRIMARY_LIGHT)
        def back_leave(e):
            back_btn.configure(bg=bg)
        if back_command:
            back_btn.bind("<Enter>", back_enter)
            back_btn.bind("<Leave>", back_leave)

    title_label = tk.Label(
        header_frame,
        text=title,
        font=Fonts.HEADING,
        bg=bg,
        fg=Colors.TEXT_ON_PRIMARY
    )
    title_label.pack(side=tk.LEFT, pady=Spacing.MD, padx=Spacing.LG)

    return header_frame, back_btn


def create_progress_bar(parent, current, total, bg=Colors.PROGRESS_BG,
                        fill_color=Colors.PROGRESS_FILL, height=24, **pack_kwargs):
    """
    Create a modern progress bar with percentage text overlay.
    """
    frame = tk.Frame(parent, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0,
                     height=height)
    frame.pack_propagate(False)
    
    # Fill
    pct = current / total if total > 0 else 0
    fill_width = int(pct * 100)
    
    fill_frame = tk.Frame(frame, bg=fill_color, bd=0, highlightthickness=0)
    fill_frame.place(relwidth=pct, relheight=1.0)
    
    # Text overlay
    text_label = tk.Label(
        frame,
        text=f"{current} из {total}",
        font=("Segoe UI", 10, "bold"),
        bg=Colors.BORDER_LIGHT if pct < 0.5 else fill_color,
        fg=Colors.TEXT_ON_PRIMARY if pct >= 0.5 else Colors.TEXT_PRIMARY
    )
    text_label.place(relx=0.5, rely=0.5, anchor="center")
    
    frame.pack(**pack_kwargs)
    return frame


def create_tag(parent, text, variant="info", **pack_kwargs):
    """
    Create a tag/badge label.
    
    Args:
        variant: 'info', 'success', 'warning', 'error', 'default'
    """
    colors = {
        "info": (Colors.PRIMARY_BG, Colors.PRIMARY),
        "success": (Colors.PRIMARY_BG, Colors.SUCCESS),
        "warning": (Colors.WARNING_BG, Colors.WARNING_DARK),
        "error": (Colors.ERROR_BG, Colors.ERROR),
        "default": (Colors.SURFACE, Colors.TEXT_SECONDARY),
    }
    bg, fg = colors.get(variant, colors["default"])
    
    tag = tk.Label(
        parent,
        text=text,
        font=("Segoe UI", 9, "bold"),
        bg=bg,
        fg=fg,
        padx=10,
        pady=3
    )
    tag.pack(**pack_kwargs)
    return tag


def create_separator(parent, color=Colors.BORDER_LIGHT, height=1, **pack_kwargs):
    """Create a horizontal separator line."""
    sep = tk.Frame(parent, bg=color, height=height, bd=0, highlightthickness=0)
    sep.pack(fill=tk.X, **pack_kwargs)
    return sep


def create_section_title(parent, text, **pack_kwargs):
    """Create a section title with modern styling."""
    title = tk.Label(
        parent,
        text=text,
        font=Fonts.HEADING,
        bg=parent.cget('bg') if parent.cget('bg') else Colors.BG,
        fg=Colors.TEXT_PRIMARY,
        anchor=tk.W
    )
    title.pack(fill=tk.X, **pack_kwargs)
    return title


def create_info_row(parent, label, value, label_width=120, **pack_kwargs):
    """Create a label: value row with consistent spacing."""
    row = tk.Frame(parent, bg=parent.cget('bg') if parent.cget('bg') else Colors.CARD_BG)
    row.pack(fill=tk.X, **pack_kwargs)
    
    lbl = tk.Label(
        row,
        text=label,
        font=("Segoe UI", 11),
        bg=row.cget('bg'),
        fg=Colors.TEXT_SECONDARY,
        width=label_width // 7,  # Approximate character width
        anchor=tk.W
    )
    lbl.pack(side=tk.LEFT)
    
    val = tk.Label(
        row,
        text=str(value),
        font=("Segoe UI", 11, "bold"),
        bg=row.cget('bg'),
        fg=Colors.TEXT_PRIMARY,
        anchor=tk.W
    )
    val.pack(side=tk.LEFT, padx=(Spacing.SM, 0), fill=tk.X, expand=True)
    
    return row, lbl, val


def create_entry(parent, label=None, initial_value="", placeholder="",
                 width=None, **pack_kwargs):
    """
    Create a modern-styled entry with optional label.
    Returns (frame, label_widget, entry_widget).
    """
    frame = tk.Frame(parent, bg=parent.cget('bg') if parent.cget('bg') else Colors.BG)
    frame.pack(fill=tk.X, **pack_kwargs)
    
    label_widget = None
    if label:
        label_widget = tk.Label(
            frame,
            text=label,
            font=Fonts.BODY,
            bg=frame.cget('bg'),
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        )
        label_widget.pack(fill=tk.X, pady=(0, Spacing.XS))
    
    entry_frame = tk.Frame(frame, bg=Colors.BORDER_LIGHT, bd=0, highlightthickness=0,
                           height=40)
    entry_frame.pack(fill=tk.X)
    entry_frame.pack_propagate(False)
    
    entry = tk.Entry(
        entry_frame,
        font=Fonts.BODY_LARGE,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_PRIMARY,
        relief=tk.FLAT,
        bd=0,
        insertbackground=Colors.PRIMARY,
        selectbackground=Colors.PRIMARY_BG,
        selectforeground=Colors.PRIMARY
    )
    entry.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.XS)
    entry.insert(0, initial_value)
    
    # Focus effects
    def on_focus_in(e):
        entry_frame.configure(bg=Colors.PRIMARY)
    
    def on_focus_out(e):
        entry_frame.configure(bg=Colors.BORDER_LIGHT)
    
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
    if width:
        entry.configure(width=width)
    
    return frame, label_widget, entry


def apply_treeview_style():
    """Apply modern styling to ttk.Treeview widget."""
    style = ttk.Style()
    style.theme_use("default")
    
    # Treeview
    style.configure("Treeview",
                    background=Colors.CARD_BG,
                    foreground=Colors.TEXT_PRIMARY,
                    rowheight=40,
                    fieldbackground=Colors.CARD_BG,
                    font=("Segoe UI", 10),
                    borderwidth=0)
    
    style.map("Treeview",
              background=[("selected", Colors.PRIMARY_BG)],
              foreground=[("selected", Colors.PRIMARY)])
    
    # Heading
    style.configure("Treeview.Heading",
                    background=Colors.SURFACE,
                    foreground=Colors.TEXT_PRIMARY,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0,
                    relief=tk.FLAT)
    
    style.map("Treeview.Heading",
              background=[("active", Colors.BORDER_LIGHT)])
    
    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=Colors.SURFACE,
                    bordercolor=Colors.BORDER_LIGHT,
                    arrowcolor=Colors.TEXT_SECONDARY,
                    troughcolor=Colors.BG)


def create_scrollable_frame(parent, bg=None):
    """
    Create a scrollable frame container.
    Returns (canvas, scrollable_frame, scrollbar).
    """
    if bg is None:
        bg = Colors.BG
    
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="inner")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Bind mousewheel for scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    return canvas, scrollable_frame, scrollbar
