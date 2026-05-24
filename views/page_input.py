"""
page_input.py – Patient data entry form page.
"""

import customtkinter as ctk
from views.theme import *
import controller
import model


GIOI_TINH_OPTIONS = ["Nam", "Nữ", "Khác"]


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
    error_vars = {}  # field_name -> StringVar for inline errors

    # ══ Card 1: Thông tin cơ bản ═════════════════════════════════════════════
    card1 = _card(scroll, "👤  Thông tin cơ bản")
    card1.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    r1 = _row(card1)
    _label(r1, "Mã bệnh nhân * (ví dụ: BN0001)", col=0, row=0)
    _label(r1, "Họ và tên *", col=1, row=0)
    entries["ma_bn"] = _entry(r1, col=0, row=1)
    entries["ten"]   = _entry(r1, col=1, row=1)
    # Inline error labels for r1
    error_vars["ma_bn"] = ctk.StringVar(value="")
    ctk.CTkLabel(r1, textvariable=error_vars["ma_bn"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=0, sticky="w", padx=(0, 0), pady=(0, 4))
    error_vars["ten"] = ctk.StringVar(value="")
    ctk.CTkLabel(r1, textvariable=error_vars["ten"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=1, sticky="w", padx=(PAD, 0), pady=(0, 4))

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
    entries["gioi_tinh"].set(GIOI_TINH_OPTIONS[0])
    # Inline error for tuổi
    error_vars["tuoi"] = ctk.StringVar(value="")
    ctk.CTkLabel(r2, textvariable=error_vars["tuoi"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=0, sticky="w", padx=(0, 0), pady=(0, 4))

    # ══ Card 2: Chỉ số thể chất ══════════════════════════════════════════════
    card2 = _card(scroll, "⚕️  Chỉ số thể chất")
    card2.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    r3 = _row(card2)
    _label(r3, "Chiều cao (cm) *", col=0, row=0)
    _label(r3, "Cân nặng (kg) *", col=1, row=0)
    entries["chieu_cao"] = _entry(r3, col=0, row=1, placeholder_text="170")
    entries["can_nang"]  = _entry(r3, col=1, row=1, placeholder_text="65")
    # Inline errors for height/weight
    error_vars["chieu_cao"] = ctk.StringVar(value="")
    ctk.CTkLabel(r3, textvariable=error_vars["chieu_cao"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=0, sticky="w", padx=(0, 0), pady=(0, 4))
    error_vars["can_nang"] = ctk.StringVar(value="")
    ctk.CTkLabel(r3, textvariable=error_vars["can_nang"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=1, sticky="w", padx=(PAD, 0), pady=(0, 4))

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
    _label(r4, "Huyết áp (ví dụ: 120/80)", col=0, row=0)
    entries["huyet_ap"] = _entry(r4, col=0, row=1, placeholder_text="120/80")
    error_vars["huyet_ap"] = ctk.StringVar(value="")
    ctk.CTkLabel(r4, textvariable=error_vars["huyet_ap"], font=FONT_SMALL, text_color=DANGER).grid(row=2, column=0, sticky="w", padx=(0, 0), pady=(0, 4))

    # ══ Card 3: Hồ sơ y tế ═══════════════════════════════════════════════════
    card3 = _card(scroll, "📄  Hồ sơ y tế")
    card3.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    # Disease selection with checkboxes
    ctk.CTkLabel(card3, text="Loại bệnh", font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w"
                 ).pack(anchor="w", padx=PAD, pady=(PAD_SM, 4))
    
    diseases_var = {}  # Store checkbox variables
    disease_checkboxes = ctk.CTkFrame(card3, fg_color=INPUT_BG, border_width=1, 
                                      border_color=INPUT_BORDER, corner_radius=RADIUS_SM)
    disease_checkboxes.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
    
    # Get available diseases and create layout
    raw_diseases = controller.get_all_diseases()
    all_diseases = sorted([d for d in raw_diseases if d != "Khác"]) + ["Khác"]

    row_frames = {}
    other_disease_var = ctk.StringVar(value="")

    def _toggle_other_input():
        if diseases_var.get("Khác", ctk.BooleanVar()).get():
            other_disease_entry.configure(state="normal")
        else:
            other_disease_entry.configure(state="disabled")
            other_disease_var.set("")
        _validate_live()

    for i, disease in enumerate(all_diseases):
        row_idx = i // 2
        if row_idx not in row_frames:
            row_frame = ctk.CTkFrame(disease_checkboxes, fg_color="transparent")
            row_frame.pack(fill="x", padx=PAD_SM, pady=3)
            row_frames[row_idx] = row_frame
        else:
            row_frame = row_frames[row_idx]
        
        var = ctk.BooleanVar()
        diseases_var[disease] = var
        display_text = "tâm thần" if disease == "ok" else disease
        checkbox = ctk.CTkCheckBox(row_frame, text=display_text, variable=var,
                                font=FONT_BODY, text_color=TEXT_PRIMARY,
                                fg_color=PRIMARY, border_color=INPUT_BORDER,
                                hover_color=PRIMARY_HOVER, checkmark_color="white",
                                width=150,
                                command=_toggle_other_input if disease == "Khác" else None)
        checkbox.pack(side="left", padx=(0, PAD))
    
    entries["loai_benh"] = diseases_var  # Store for later use

    ctk.CTkLabel(card3, text="Khác (nếu có)", font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w"
                 ).pack(anchor="w", padx=PAD, pady=(PAD_SM, 2))
    other_disease_entry = ctk.CTkEntry(
        card3, textvariable=other_disease_var, placeholder_text="Nhập bệnh khác...",
        font=FONT_BODY, fg_color=INPUT_BG, border_color=INPUT_BORDER,
        text_color=TEXT_PRIMARY, height=38, corner_radius=RADIUS_SM,
    )
    other_disease_entry.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
    other_disease_entry.configure(state="disabled")
    entries["loai_benh_khac"] = other_disease_entry
    # Inline error for other-disease (packed under the entry)
    error_vars["loai_benh_khac"] = ctk.StringVar(value="")
    ctk.CTkLabel(card3, textvariable=error_vars["loai_benh_khac"], font=FONT_SMALL, text_color=DANGER).pack(anchor="w", padx=PAD, pady=(0, 8))

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
        
        form_data = {}
        for k, v in entries.items():
            if k == "loai_benh":
                selected_diseases = []
                for disease, var in v.items():
                    if not var.get():
                        continue
                    if disease == "Khác":
                        other_text = entries["loai_benh_khac"].get().strip()
                        selected_diseases.append(other_text if other_text else disease)
                    else:
                        selected_diseases.append("tâm thần" if disease == "ok" else disease)
                form_data[k] = selected_diseases
            else:
                form_data[k] = _text(v)
        return form_data

    def _validate_live(*_):
        """Validate current form live and show first error (if any) in status banner."""
        data = _collect_form()
        errors = model.validate_patient(data)
        # Clear previous inline errors
        for v in error_vars.values():
            v.set("")
        status_var.set("")
        if not errors:
            return True

        # Map generic error messages to fields when possible
        for msg in errors:
            if "Mã bệnh nhân" in msg or "Mã bệnh" in msg:
                error_vars.get("ma_bn", ctk.StringVar()).set(msg)
            elif "Tên bệnh nhân" in msg or msg.startswith("Tên"):
                error_vars.get("ten", ctk.StringVar()).set(msg)
            elif "Tuổi" in msg:
                error_vars.get("tuoi", ctk.StringVar()).set(msg)
            elif "Chiều cao" in msg or "Chiều cao phải" in msg:
                error_vars.get("chieu_cao", ctk.StringVar()).set(msg)
            elif "Cân nặng" in msg:
                error_vars.get("can_nang", ctk.StringVar()).set(msg)
            elif "Huyết áp" in msg:
                error_vars.get("huyet_ap", ctk.StringVar()).set(msg)
            else:
                # Fallback: show in status banner if we can't map to a field
                status_label.configure(text_color=DANGER)
                status_var.set(f"❌  {msg}")
        return False

    # Attach traces and binds for live validation
    for disease, var in diseases_var.items():
        try:
            var.trace_add("write", lambda *a, d=disease: _validate_live())
        except Exception:
            try:
                var.trace("w", lambda *a, d=disease: _validate_live())
            except Exception:
                pass

    for field in ("lich_su_kham", "lich_su_thuoc"):
        try:
            entries[field].bind("<KeyRelease>", lambda e: _validate_live())
        except Exception:
            pass

    try:
        entries["gioi_tinh"].configure(command=lambda v: _validate_live())
    except Exception:
        pass

    for name in ["ma_bn", "ten", "tuoi", "chieu_cao", "can_nang", "huyet_ap", "loai_benh_khac"]:
        try:
            entries[name].bind("<KeyRelease>", lambda e: _validate_live())
        except Exception:
            pass

    def _clear(keep_status=False):
        for k, w in entries.items():
            if k == "loai_benh":
                # Clear disease checkboxes
                for disease, var in w.items():
                    var.set(False)
                if "loai_benh_khac" in entries:
                    entries["loai_benh_khac"].delete(0, "end")
                    entries["loai_benh_khac"].configure(state="disabled")
            elif isinstance(w, ctk.CTkTextbox):
                w.delete("0.0", "end")
            elif isinstance(w, ctk.CTkEntry):
                w.delete(0, "end")
        entries["gioi_tinh"].set(GIOI_TINH_OPTIONS[0])
        bmi_var.set("")
        if not keep_status:
            status_var.set("")


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
