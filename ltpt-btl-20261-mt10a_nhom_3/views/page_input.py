"""
page_input.py – Patient data entry form page.
"""

import customtkinter as ctk
from views.theme import *
import controller


GIOI_TINH_OPTIONS = ["Nam", "Nữ", "Khác"]
LOAI_BENH_OPTIONS = [
    "Tim mạch", "Tiểu đường", "Hô hấp", "Tiêu hóa",
    "Thần kinh", "Xương khớp", "Da liễu", "Khác",
]


def _card(parent, title: str, **kwargs):
    """Return a styled card frame with a title label."""
    outer = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=RADIUS_LG, **kwargs)
    ctk.CTkLabel(
        outer, text=title,
        font=FONT_HEADING, text_color=PRIMARY,
    ).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))
    ctk.CTkFrame(outer, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=PAD, pady=(0, PAD_SM))
    return outer


def _row(parent):
    """Return a horizontal frame for two-column layouts."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=PAD, pady=3)
    f.columnconfigure(0, weight=1)
    f.columnconfigure(1, weight=1)
    return f


def _label(parent, text, col=0, row=0):
    lbl = ctk.CTkLabel(parent, text=text, font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w")
    lbl.grid(row=row, column=col, sticky="w", padx=(0 if col == 0 else PAD, 0), pady=(4, 0))
    return lbl


def _entry(parent, col=0, row=1, **kwargs):
    e = ctk.CTkEntry(
        parent, font=FONT_BODY,
        fg_color=INPUT_BG, border_color=INPUT_BORDER,
        text_color=TEXT_PRIMARY, height=38,
        corner_radius=RADIUS_SM, **kwargs,
    )
    e.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else PAD, 0), pady=(0, 4))
    return e


def make_input_page(parent, on_saved):
    """
    Build the patient input form page.
    on_saved() is called after successful save so other pages can refresh.
    Returns the outer frame.
    """
    # Scrollable container
    scroll = ctk.CTkScrollableFrame(parent, fg_color=CONTENT_BG, corner_radius=0)
    scroll.pack(fill="both", expand=True)

    # ── Page header ──────────────────────────────────────────────────────────
    hdr = ctk.CTkFrame(scroll, fg_color="transparent")
    hdr.pack(fill="x", padx=PAD_LG, pady=(PAD_LG, PAD))
    ctk.CTkLabel(hdr, text="Nhập liệu bệnh nhân", font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
    ctk.CTkLabel(hdr, text="Điền đầy đủ thông tin và nhấn Lưu hồ sơ", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")

    # ── Status banner ─────────────────────────────────────────────────────────
    status_var = ctk.StringVar(value="")
    status_label = ctk.CTkLabel(scroll, textvariable=status_var, font=FONT_BODY,
                                text_color=SECONDARY, fg_color="transparent")
    status_label.pack(fill="x", padx=PAD_LG)

    entries = {}  # field_name -> widget

    # ══ Card 1: Thông tin cơ bản ═════════════════════════════════════════════
    card1 = _card(scroll, "👤  Thông tin cơ bản")
    card1.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    r1 = _row(card1)
    _label(r1, "Mã bệnh nhân *", col=0, row=0)
    _label(r1, "Họ và tên *", col=1, row=0)
    entries["ma_bn"] = _entry(r1, col=0, row=1, placeholder_text="BN0001")
    entries["ten"]   = _entry(r1, col=1, row=1, placeholder_text="Nguyễn Văn A")

    r2 = _row(card1)
    _label(r2, "Tuổi *", col=0, row=0)
    _label(r2, "Giới tính", col=1, row=0)
    entries["tuoi"] = _entry(r2, col=0, row=1, placeholder_text="25")
    entries["gioi_tinh"] = ctk.CTkOptionMenu(
        r2, values=GIOI_TINH_OPTIONS, font=FONT_BODY,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM, height=38,
    )
    entries["gioi_tinh"].grid(row=1, column=1, sticky="ew", padx=(PAD, 0), pady=(0, 4))

    # ══ Card 2: Chỉ số thể chất ══════════════════════════════════════════════
    card2 = _card(scroll, "⚕️  Chỉ số thể chất")
    card2.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    r3 = _row(card2)
    _label(r3, "Chiều cao (cm) *", col=0, row=0)
    _label(r3, "Cân nặng (kg) *", col=1, row=0)
    entries["chieu_cao"] = _entry(r3, col=0, row=1, placeholder_text="170")
    entries["can_nang"]  = _entry(r3, col=1, row=1, placeholder_text="65")

    # BMI preview
    bmi_var = ctk.StringVar(value="")
    bmi_lbl = ctk.CTkLabel(card2, textvariable=bmi_var, font=FONT_BODY,
                           text_color=SECONDARY, fg_color="transparent")
    bmi_lbl.pack(anchor="w", padx=PAD, pady=(0, PAD_SM))

    def _update_bmi(*_):
        result = controller.compute_bmi_preview(
            entries["can_nang"].get(), entries["chieu_cao"].get()
        )
        bmi_var.set(result)

    entries["can_nang"].bind("<KeyRelease>", _update_bmi)
    entries["chieu_cao"].bind("<KeyRelease>", _update_bmi)

    r4 = _row(card2)
    _label(r4, "Huyết áp (mmHg)", col=0, row=0)
    entries["huyet_ap"] = _entry(r4, col=0, row=1, placeholder_text="120/80")

    # ══ Card 3: Hồ sơ y tế ═══════════════════════════════════════════════════
    card3 = _card(scroll, "📄  Hồ sơ y tế")
    card3.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    r5 = _row(card3)
    _label(r5, "Loại bệnh", col=0, row=0)
    entries["loai_benh"] = ctk.CTkOptionMenu(
        r5, values=LOAI_BENH_OPTIONS, font=FONT_BODY,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM, height=38,
    )
    entries["loai_benh"].grid(row=1, column=0, sticky="ew", pady=(0, 4))

    for field, placeholder in [("lich_su_kham", "Ghi chú lịch sử khám..."),
                                ("lich_su_thuoc", "Ghi chú lịch sử dùng thuốc...")]:
        ctk.CTkLabel(card3, text=field.replace("_", " ").title(),
                     font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w"
                     ).pack(anchor="w", padx=PAD, pady=(PAD_SM, 2))
        tb = ctk.CTkTextbox(card3, font=FONT_BODY, fg_color=INPUT_BG,
                            border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
                            height=70, corner_radius=RADIUS_SM)
        tb.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
        tb.insert("0.0", placeholder)
        entries[field] = tb

    # ══ Action bar ═══════════════════════════════════════════════════════════
    action_bar = ctk.CTkFrame(scroll, fg_color="transparent")
    action_bar.pack(fill="x", padx=PAD_LG, pady=(0, PAD_LG))

    def _collect_form() -> dict:
        def _text(w):
            if isinstance(w, ctk.CTkTextbox):
                v = w.get("0.0", "end").strip()
                return v
            return w.get()
        return {k: _text(v) for k, v in entries.items()}

    def _clear(keep_status=False):
        for k, w in entries.items():
            if isinstance(w, ctk.CTkTextbox):
                w.delete("0.0", "end")
            elif isinstance(w, ctk.CTkEntry):
                w.delete(0, "end")
        bmi_var.set("")
        if not keep_status:
            status_var.set("")
        # Auto-fill new ID
        new_id = controller.generate_patient_id()
        entries["ma_bn"].insert(0, new_id)

    def _save():
        data = _collect_form()
        ok, msg = controller.handle_add_patient(data, on_success=on_saved)
        if ok:
            status_label.configure(text_color=SECONDARY)
            status_var.set(f"✅  {msg}")
            _clear(keep_status=True)
        else:
            status_label.configure(text_color=DANGER)
            status_var.set(f"❌  {msg}")

    ctk.CTkButton(
        action_bar, text="🗑  Làm mới", font=FONT_BODY,
        height=44, width=140,
        fg_color=CARD_BG, hover_color=SIDEBAR_HOVER,
        text_color=TEXT_SECONDARY, corner_radius=RADIUS_MD,
        command=_clear,
    ).pack(side="left", padx=(0, PAD_SM))

    ctk.CTkButton(
        action_bar, text="💾  Lưu hồ sơ", font=(FONT_FAMILY, 13, "bold"),
        height=44, width=180,
        fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
        text_color="white", corner_radius=RADIUS_MD,
        command=_save,
    ).pack(side="left")

    # Pre-fill ID
    _clear()

    return scroll
