"""
page_list.py – Patient list page with search, edit, delete.
Uses a CTkScrollableFrame as a table since tksheet may not be installed.
"""

import customtkinter as ctk
from views.theme import *
import controller
import model

COLUMNS = ["Mã BN", "Họ tên", "Tuổi", "Giới tính", "Cao (cm)", "Nặng (kg)", "Huyết áp", "BMI", "Loại bệnh"]
COL_WIDTHS = [80, 160, 50, 80, 70, 70, 90, 70, 110]


def make_list_page(parent):
    """
    Build the patient list page.
    Returns (outer_frame, refresh_fn) so the app can trigger refresh.
    """
    outer = ctk.CTkFrame(parent, fg_color=CONTENT_BG, corner_radius=0)
    outer.pack(fill="both", expand=True)

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=0)
    hdr.pack(fill="x")

    hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
    hdr_inner.pack(fill="x", padx=PAD_LG, pady=PAD)

    ctk.CTkLabel(hdr_inner, text="Danh sách bệnh nhân", font=FONT_TITLE,
                 text_color=TEXT_PRIMARY).pack(side="left")

    # Search bar
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(
        hdr_inner, textvariable=search_var,
        placeholder_text="🔍  Tìm theo tên hoặc mã BN...",
        font=FONT_BODY, width=280, height=38,
        fg_color=INPUT_BG, border_color=INPUT_BORDER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    search_entry.pack(side="right")

    # ── Status bar ───────────────────────────────────────────────────────────
    status_var = ctk.StringVar(value="")
    status_lbl = ctk.CTkLabel(outer, textvariable=status_var, font=FONT_SMALL,
                              text_color=TEXT_MUTED, fg_color="transparent")
    status_lbl.pack(anchor="w", padx=PAD_LG, pady=(PAD_SM, 0))

    # ── Table header row ─────────────────────────────────────────────────────
    col_header = ctk.CTkFrame(outer, fg_color=SIDEBAR_BG, corner_radius=0, height=34)
    col_header.pack(fill="x", padx=PAD_LG, pady=(PAD_SM, 0))
    col_header.pack_propagate(False)

    for col, w in zip(COLUMNS, COL_WIDTHS):
        ctk.CTkLabel(
            col_header, text=col, font=(FONT_FAMILY, 11, "bold"),
            text_color=TEXT_SECONDARY, width=w, anchor="w",
        ).pack(side="left", padx=4)

    # ── Table body (scrollable) ────────────────────────────────────────────
    table_frame = ctk.CTkScrollableFrame(
        outer, fg_color=CONTENT_BG, corner_radius=0,
    )
    table_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_SM))

    # ── Bottom action bar ─────────────────────────────────────────────────────
    action_bar = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=0, height=56)
    action_bar.pack(fill="x", side="bottom")
    action_bar.pack_propagate(False)

    selected_id = {"value": None}  # mutable container for selected patient id

    def _select(ma_bn):
        selected_id["value"] = ma_bn
        status_var.set(f"Đã chọn: {ma_bn}")

    def _delete():
        if not selected_id["value"]:
            status_var.set("⚠  Chưa chọn bệnh nhân để xoá!")
            return
        ok, msg = controller.handle_delete_patient(selected_id["value"], on_success=refresh)
        status_var.set(("✅  " if ok else "❌  ") + msg)
        selected_id["value"] = None

    def _edit():
        if not selected_id["value"]:
            status_var.set("⚠  Chưa chọn bệnh nhân để sửa!")
            return
        _open_edit_dialog(outer, selected_id["value"], refresh)

    ctk.CTkButton(
        action_bar, text="✏️  Sửa", font=FONT_BODY, height=36, width=120,
        fg_color=INFO, hover_color="#4F46E5",
        text_color="white", corner_radius=RADIUS_MD,
        command=_edit,
    ).pack(side="left", padx=(PAD_LG, PAD_SM), pady=PAD_SM)

    ctk.CTkButton(
        action_bar, text="🗑  Xoá", font=FONT_BODY, height=36, width=120,
        fg_color=DANGER, hover_color="#DC2626",
        text_color="white", corner_radius=RADIUS_MD,
        command=_delete,
    ).pack(side="left", pady=PAD_SM)

    count_lbl = ctk.CTkLabel(action_bar, text="", font=FONT_SMALL, text_color=TEXT_MUTED)
    count_lbl.pack(side="right", padx=PAD_LG)

    # ── Render table rows ─────────────────────────────────────────────────────
    row_frames = []

    def _render_rows(df):
        nonlocal row_frames
        for f in row_frames:
            f.destroy()
        row_frames.clear()

        if df.empty:
            ctk.CTkLabel(table_frame, text="Không có dữ liệu.",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=PAD_LG)
            return

        bmi_df = model.bmi_distribution(df)
        bmi_map = dict(zip(bmi_df["ma_bn"], bmi_df["bmi"])) if not bmi_df.empty else {}

        for i, row in df.iterrows():
            bg = CARD_BG if i % 2 == 0 else INPUT_BG
            rf = ctk.CTkFrame(table_frame, fg_color=bg, corner_radius=RADIUS_SM, height=38)
            rf.pack(fill="x", pady=1)
            rf.pack_propagate(False)
            row_frames.append(rf)

            ma = str(row["ma_bn"])
            bmi_val = bmi_map.get(ma, "-")
            bmi_str = f"{bmi_val:.1f}" if isinstance(bmi_val, float) else "-"

            values = [
                ma, str(row["ten"]), str(row["tuoi"]),
                str(row["gioi_tinh"]),
                str(row["chieu_cao"]), str(row["can_nang"]),
                str(row["huyet_ap"]), bmi_str, str(row["loai_benh"]),
            ]

            for val, w in zip(values, COL_WIDTHS):
                ctk.CTkLabel(
                    rf, text=val, font=FONT_SMALL,
                    text_color=TEXT_PRIMARY, width=w, anchor="w",
                ).pack(side="left", padx=4)

            # Click to select
            rf.bind("<Button-1>", lambda e, m=ma, f=rf: _on_row_click(m, f))
            for child in rf.winfo_children():
                child.bind("<Button-1>", lambda e, m=ma, f=rf: _on_row_click(m, f))

    _current_highlight = {"frame": None}

    def _on_row_click(ma_bn, frame):
        if _current_highlight["frame"]:
            prev = _current_highlight["frame"]
            try:
                prev.configure(fg_color=prev._orig_color)
            except Exception:
                pass
        _current_highlight["frame"] = frame
        frame._orig_color = frame.cget("fg_color")
        frame.configure(fg_color=PRIMARY)
        _select(ma_bn)

    def refresh():
        kw = search_var.get()
        df = controller.handle_search(kw)
        _render_rows(df)
        count_lbl.configure(text=f"{len(df)} bệnh nhân")

    search_var.trace_add("write", lambda *_: refresh())

    refresh()
    return outer, refresh


# ── Edit dialog ──────────────────────────────────────────────────────────────

def _open_edit_dialog(parent, ma_bn: str, on_saved):
    """Open a Toplevel dialog to edit the selected patient."""
    import pandas as pd

    df = controller.get_patient_list()
    row = df[df["ma_bn"] == ma_bn]
    if row.empty:
        return
    patient = row.iloc[0].to_dict()

    dialog = ctk.CTkToplevel(parent)
    dialog.title(f"Sửa hồ sơ – {ma_bn}")
    dialog.geometry("540x620")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(fg_color=CONTENT_BG)

    ctk.CTkLabel(dialog, text=f"Chỉnh sửa: {patient['ten']}",
                 font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(padx=PAD, pady=(PAD, 0), anchor="w")

    scroll = ctk.CTkScrollableFrame(dialog, fg_color=CONTENT_BG)
    scroll.pack(fill="both", expand=True, padx=PAD, pady=PAD)

    fields = {
        "ten": "Họ và tên", "tuoi": "Tuổi",
        "gioi_tinh": "Giới tính", "chieu_cao": "Chiều cao (cm)",
        "can_nang": "Cân nặng (kg)", "huyet_ap": "Huyết áp",
        "loai_benh": "Loại bệnh", "lich_su_kham": "Lịch sử khám",
        "lich_su_thuoc": "Lịch sử thuốc",
    }
    widgets = {}

    for key, label in fields.items():
        ctk.CTkLabel(scroll, text=label, font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(6, 1))
        if key in ("lich_su_kham", "lich_su_thuoc"):
            tb = ctk.CTkTextbox(scroll, height=60, font=FONT_BODY, fg_color=INPUT_BG,
                                border_color=INPUT_BORDER, text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM)
            tb.insert("0.0", str(patient.get(key, "")))
            tb.pack(fill="x")
            widgets[key] = tb
        elif key == "gioi_tinh":
            opt = ctk.CTkOptionMenu(scroll, values=["Nam", "Nữ", "Khác"], font=FONT_BODY,
                                    fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
                                    text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM, height=36)
            opt.set(str(patient.get(key, "Khác")))
            opt.pack(fill="x")
            widgets[key] = opt
        elif key == "loai_benh":
            opt = ctk.CTkOptionMenu(scroll, values=["Tim mạch", "Tiểu đường", "Hô hấp", "Tiêu hóa",
                                                    "Thần kinh", "Xương khớp", "Da liễu", "Khác"], 
                                    font=FONT_BODY, fg_color=INPUT_BG, button_color=PRIMARY, 
                                    button_hover_color=PRIMARY_HOVER, text_color=TEXT_PRIMARY, 
                                    corner_radius=RADIUS_SM, height=36)
            opt.set(str(patient.get(key, "Khác")))
            opt.pack(fill="x")
            widgets[key] = opt
        else:
            e = ctk.CTkEntry(scroll, font=FONT_BODY, fg_color=INPUT_BG,
                             border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
                             height=36, corner_radius=RADIUS_SM)
            e.insert(0, str(patient.get(key, "")))
            e.pack(fill="x")
            widgets[key] = e

    status_var = ctk.StringVar()
    ctk.CTkLabel(dialog, textvariable=status_var, font=FONT_SMALL, text_color=DANGER).pack()

    def _save():
        def _get(w):
            return w.get("0.0", "end").strip() if isinstance(w, ctk.CTkTextbox) else w.get()
        data = {k: _get(v) for k, v in widgets.items()}
        ok, msg = controller.handle_update_patient(ma_bn, data, on_success=on_saved)
        if ok:
            dialog.destroy()
        else:
            status_var.set(msg)

    btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_row.pack(pady=(0, PAD))
    ctk.CTkButton(btn_row, text="Huỷ", width=100, fg_color=CARD_BG,
                  text_color=TEXT_SECONDARY, hover_color=SIDEBAR_HOVER,
                  command=dialog.destroy, corner_radius=RADIUS_MD).pack(side="left", padx=PAD_SM)
    ctk.CTkButton(btn_row, text="💾  Lưu", width=140, fg_color=PRIMARY,
                  hover_color=PRIMARY_HOVER, text_color="white",
                  command=_save, corner_radius=RADIUS_MD).pack(side="left")
