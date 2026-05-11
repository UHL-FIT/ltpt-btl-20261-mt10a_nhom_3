"""
page_about.py – About page with application information.
"""

import customtkinter as ctk
from views.theme import *


def make_about_page(parent):
    """
    Build the About page.
    Returns (frame, refresh_fn).
    """
    outer = ctk.CTkFrame(parent, fg_color=CONTENT_BG, corner_radius=0)
    outer.pack(fill="both", expand=True)

    scroll = ctk.CTkScrollableFrame(outer, fg_color=CONTENT_BG, corner_radius=0)
    scroll.pack(fill="both", expand=True)

    # Page header
    hdr = ctk.CTkFrame(scroll, fg_color="transparent")
    hdr.pack(fill="x", padx=PAD_LG, pady=(PAD_LG, PAD))
    ctk.CTkLabel(hdr, text="Về ứng dụng", font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(side="left")

    # Main info card
    info_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    info_card.pack(fill="x", padx=PAD_LG, pady=PAD)

    # App title
    ctk.CTkLabel(
        info_card,
        text="🏥 Quản lý Hồ sơ Bệnh nhân",
        font=(FONT_FAMILY, 20, "bold"),
        text_color=PRIMARY,
    ).pack(pady=(PAD_LG, PAD_SM))

    # Version
    ctk.CTkLabel(
        info_card,
        text="Phiên bản 1.0",
        font=FONT_LABEL,
        text_color=TEXT_SECONDARY,
    ).pack(pady=PAD_SM)

    # Divider
    ctk.CTkFrame(info_card, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=PAD, pady=PAD)

    # Description
    ctk.CTkLabel(
        info_card,
        text="Mô tả",
        font=FONT_HEADING,
        text_color=PRIMARY,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))

    ctk.CTkLabel(
        info_card,
        text="Ứng dụng quản lý hồ sơ bệnh nhân giúp lưu trữ, quản lý và phân tích thông tin sức khỏe của bệnh nhân một cách hiệu quả. Ứng dụng cung cấp các tính năng nhập liệu, xem danh sách và thống kê dữ liệu.",
        font=FONT_BODY,
        text_color=TEXT_SECONDARY,
        wraplength=600,
        justify="left",
    ).pack(anchor="w", padx=PAD, pady=(0, PAD_LG))

    # Team info card
    team_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    team_card.pack(fill="x", padx=PAD_LG, pady=PAD)

    ctk.CTkLabel(
        team_card,
        text="Nhóm phát triển",
        font=FONT_HEADING,
        text_color=PRIMARY,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))

    ctk.CTkLabel(
        team_card,
        text="Nhóm 3 - Bài tập lớn LTPT (20261)",
        font=FONT_BODY,
        text_color=TEXT_SECONDARY,
    ).pack(anchor="w", padx=PAD, pady=(0, PAD_SM))

    ctk.CTkLabel(
        team_card,
        text="Môn học: Lập Trình Python",
        font=FONT_BODY,
        text_color=TEXT_SECONDARY,
    ).pack(anchor="w", padx=PAD, pady=(0, PAD_LG))

    # Features card
    features_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    features_card.pack(fill="x", padx=PAD_LG, pady=PAD)

    ctk.CTkLabel(
        features_card,
        text="Tính năng chính",
        font=FONT_HEADING,
        text_color=PRIMARY,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))

    features = [
        "➕ Nhập liệu bệnh nhân mới",
        "📋 Xem danh sách bệnh nhân",
        "📊 Thống kê và phân tích dữ liệu",
        "🌓 Chuyển đổi giao diện sáng/tối",
        "💾 Lưu trữ dữ liệu trên cơ sở dữ liệu SQLite",
        "🔍 Tìm kiếm bệnh nhân theo tên hoặc mã bệnh nhân",
        "💾 Import/Export dữ liệu",
    ]

    for feature in features:
        ctk.CTkLabel(
            features_card,
            text=feature,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=PAD, pady=PAD_SM)

    # Footer info
    footer_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    footer_card.pack(fill="x", padx=PAD_LG, pady=PAD, side="bottom")

    ctk.CTkLabel(
        footer_card,
        text="Công nghệ sử dụng",
        font=FONT_HEADING,
        text_color=PRIMARY,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))

    tech_stack = [
        "Python 3.x",
        "CustomTkinter (GUI Framework)",
        "SQLite (Database)",
        "Pandas (Data Analysis)",
        "Matplotlib (Visualization)",
    ]

    for tech in tech_stack:
        ctk.CTkLabel(
            footer_card,
            text=f"• {tech}",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=PAD, pady=PAD_SM)

    ctk.CTkLabel(
        footer_card,
        text="© 2026 Nhóm 3. Tất cả quyền được bảo lưu.",
        font=FONT_SMALL,
        text_color=TEXT_MUTED,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_LG))

    def refresh():
        """Refresh handler (no-op for about page)."""
        pass

    return outer, refresh
