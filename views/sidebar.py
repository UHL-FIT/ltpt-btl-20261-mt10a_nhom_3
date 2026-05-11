"""
sidebar.py – Left navigation sidebar with animated hover effects.
"""

import customtkinter as ctk
from views.theme import *

# Nav items: (icon, label, page_key)
NAV_ITEMS = [
    ("➕", "Nhập liệu",  "input"),
    ("📋", "Danh sách", "list"),
    ("📊", "Thống kê",  "stats"),
    ("ℹ️", "Về ứng dụng", "about"),
]


def make_sidebar(parent, on_navigate):
    """
    Build and return the sidebar frame.
    on_navigate(page_key) is called when a nav button is clicked.
    Returns (frame, set_active_fn) so the controller can highlight the active tab.
    """
    frame = ctk.CTkFrame(parent, width=220, fg_color=SIDEBAR_BG, corner_radius=0)
    frame.pack_propagate(False)

    # ── Logo / App title ──────────────────────────────────────────────────────
    logo_frame = ctk.CTkFrame(frame, fg_color="transparent")
    logo_frame.pack(fill="x", padx=PAD, pady=(PAD_LG, PAD))

    ctk.CTkLabel(
        logo_frame, text="🏥",
        font=(FONT_FAMILY, 32),
        text_color=PRIMARY,
    ).pack(anchor="w")

    ctk.CTkLabel(
        logo_frame, text="Quản lý\nBệnh nhân",
        font=(FONT_FAMILY, 14, "bold"),
        text_color=TEXT_PRIMARY,
        justify="left",
    ).pack(anchor="w")

    # Divider
    ctk.CTkFrame(frame, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=PAD, pady=(PAD, PAD_LG))

    ctk.CTkLabel(
        frame, text="ĐIỀU HƯỚNG",
        font=(FONT_FAMILY, 10, "bold"),
        text_color=TEXT_MUTED,
    ).pack(anchor="w", padx=PAD, pady=(0, PAD_SM))

    # ── Nav buttons ───────────────────────────────────────────────────────────
    buttons = {}

    def make_btn(icon, label, key):
        btn = ctk.CTkButton(
            frame,
            text=f"  {icon}   {label}",
            font=FONT_BODY,
            height=44,
            anchor="w",
            fg_color="transparent",
            text_color=SIDEBAR_TEXT,
            hover_color=SIDEBAR_HOVER,
            corner_radius=RADIUS_MD,
            command=lambda k=key: on_navigate(k),
        )
        btn.pack(fill="x", padx=PAD_SM, pady=2)
        buttons[key] = btn

    for icon, label, key in NAV_ITEMS:
        make_btn(icon, label, key)

    # ── Bottom: theme toggle ──────────────────────────────────────────────────
    ctk.CTkFrame(frame, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=PAD, pady=PAD)

    def toggle_theme():
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

    ctk.CTkButton(
        frame,
        text="  🌓   Đổi giao diện",
        font=FONT_SMALL,
        height=38,
        anchor="w",
        fg_color="transparent",
        text_color=TEXT_MUTED,
        hover_color=SIDEBAR_HOVER,
        corner_radius=RADIUS_MD,
        command=toggle_theme,
    ).pack(fill="x", padx=PAD_SM, pady=2, side="bottom")

    ctk.CTkLabel(
        frame,
        text="v1.0  •  Nhóm 3",
        font=(FONT_FAMILY, 10),
        text_color=TEXT_MUTED,
    ).pack(side="bottom", pady=(0, PAD_SM))

    # ── set_active helper ─────────────────────────────────────────────────────
    def set_active(key: str):
        for k, btn in buttons.items():
            if k == key:
                btn.configure(fg_color=PRIMARY, text_color=SIDEBAR_ACTIVE_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=SIDEBAR_TEXT)

    # Default
    set_active("input")

    return frame, set_active
