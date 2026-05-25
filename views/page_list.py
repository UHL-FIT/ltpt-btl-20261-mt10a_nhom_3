"""
page_list.py – Patient list page with search, edit, delete.
Uses a CTkScrollableFrame as a table since tksheet may not be installed.
"""

import customtkinter as ctk
from views.theme import *
import controller
import model
from tkinter import filedialog, messagebox,ttk

COLUMNS = ["Mã BN", "Họ tên", "Tuổi", "Giới tính", "Cao (cm)", "Nặng (kg)", "Huyết áp", "BMI", "Loại bệnh"]
COL_WIDTHS = [80, 160, 50, 80, 70, 70, 90, 70, 110]
PAGE_SIZE = 100


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

    # ── Filter bar (right side) ───────────────────────────────────────────────
    filter_frame = ctk.CTkFrame(hdr_inner, fg_color="transparent")
    filter_frame.pack(side="right")

    # Disease filter dropdown
    disease_filter_var = ctk.StringVar(value="Tất cả")
    disease_options = ["Tất cả", "Tim mạch", "Tiểu đường", "Hô hấp", "Tiêu hóa",
                       "Thần kinh", "Xương khớp", "Da liễu", "Khác"]
    known_disease_options = set(disease_options[1:-1])
    
    ctk.CTkLabel(filter_frame, text="Loại bệnh:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    disease_combo = ctk.CTkOptionMenu(
        filter_frame, values=disease_options, variable=disease_filter_var,
        font=FONT_BODY, height=38, width=140,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    disease_combo.pack(side="left", padx=(0, PAD_SM))

    # Search bar
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(
        filter_frame, textvariable=search_var,
        font=FONT_BODY, width=200, height=38,
        fg_color=INPUT_BG, border_color=INPUT_BORDER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    search_entry.pack(side="left", padx=(0, PAD_SM))
    
    # Add hint label overlay
    ctk.CTkLabel(filter_frame, text="🔍  Tìm", font=FONT_BODY, text_color=TEXT_MUTED).pack(side="left", padx=(4, 0))

    # Advanced filter toggle button
    filter_panel_state = {"show": False}
    
    def _toggle_filter_panel():
        filter_panel_state["show"] = not filter_panel_state["show"]
        if filter_panel_state["show"]:
            filter_panel.pack(fill="x", padx=PAD_LG, pady=(0, PAD_SM), after=hdr)
            toggle_btn.configure(text="🔽 Ẩn bộ lọc")
        else:
            filter_panel.pack_forget()
            toggle_btn.configure(text="▶ Hiện bộ lọc")

    toggle_btn = ctk.CTkButton(
        filter_frame, text="▶ Hiện bộ lọc", font=FONT_SMALL, height=38, width=120,
        fg_color=CARD_BG, hover_color=SIDEBAR_HOVER, text_color=TEXT_SECONDARY,
        corner_radius=RADIUS_MD, command=_toggle_filter_panel,
    )
    toggle_btn.pack(side="left", padx=(PAD_SM, 0))

    # ── Advanced Filter Panel ────────────────────────────────────────────────
    filter_panel = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=RADIUS_MD)
    
    filter_inner = ctk.CTkFrame(filter_panel, fg_color="transparent")
    filter_inner.pack(fill="x", padx=PAD, pady=PAD)

    # Age group filter
    age_filter_var = ctk.StringVar(value="Tất cả")
    age_options = ["Tất cả", "<18", "18-40", "41-60", ">60"]
    ctk.CTkLabel(filter_inner, text="Tuổi:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    age_combo = ctk.CTkOptionMenu(
        filter_inner, values=age_options, variable=age_filter_var,
        font=FONT_BODY, height=36, width=110,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    age_combo.pack(side="left", padx=(0, PAD_LG))

    # Gender filter
    gender_filter_var = ctk.StringVar(value="Tất cả")
    gender_options = ["Tất cả", "Nam", "Nữ", "Khác"]
    ctk.CTkLabel(filter_inner, text="Giới tính:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    gender_combo = ctk.CTkOptionMenu(
        filter_inner, values=gender_options, variable=gender_filter_var,
        font=FONT_BODY, height=36, width=110,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    gender_combo.pack(side="left", padx=(0, PAD_LG))

    # BMI filter
    bmi_filter_var = ctk.StringVar(value="Tất cả")
    bmi_options = ["Tất cả", "Thiếu cân", "Bình thường", "Thừa cân", "Béo phì"]
    ctk.CTkLabel(filter_inner, text="BMI:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    bmi_combo = ctk.CTkOptionMenu(
        filter_inner, values=bmi_options, variable=bmi_filter_var,
        font=FONT_BODY, height=36, width=130,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    bmi_combo.pack(side="left", padx=(0, PAD_LG))

    # Apply Blood Pressure filter (Huyết áp)
    bp_filter_var = ctk.StringVar(value="Tất cả")
    bp_options = ["Tất cả", "Bình thường", "Cao huyết áp", "Huyết áp thấp"]
    ctk.CTkLabel(filter_inner, text="Huyết áp:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    bp_combo = ctk.CTkOptionMenu(
        filter_inner, values=bp_options, variable=bp_filter_var,
        font=FONT_BODY, height=36, width=130,
        fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
        text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM,
    )
    bp_combo.pack(side="left", padx=(0, PAD_LG))

    # Weight range (kg)
    ctk.CTkLabel(filter_inner, text="Cân nặng (kg):", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    weight_min_entry = ctk.CTkEntry(
        filter_inner, font=FONT_SMALL, width=60, height=36,
        fg_color=INPUT_BG, border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
        corner_radius=RADIUS_SM, placeholder_text="Min",
    )
    weight_min_entry.pack(side="left", padx=(0, PAD_SM))
    
    ctk.CTkLabel(filter_inner, text="→", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    
    weight_max_entry = ctk.CTkEntry(
        filter_inner, font=FONT_SMALL, width=60, height=36,
        fg_color=INPUT_BG, border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
        corner_radius=RADIUS_SM, placeholder_text="Max",
    )
    weight_max_entry.pack(side="left", padx=(0, PAD_LG))

    # Height range (cm)
    ctk.CTkLabel(filter_inner, text="Chiều cao (cm):", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    height_min_entry = ctk.CTkEntry(
        filter_inner, font=FONT_SMALL, width=60, height=36,
        fg_color=INPUT_BG, border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
        corner_radius=RADIUS_SM, placeholder_text="Min",
    )
    height_min_entry.pack(side="left", padx=(0, PAD_SM))
    
    ctk.CTkLabel(filter_inner, text="→", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_SM))
    
    height_max_entry = ctk.CTkEntry(
        filter_inner, font=FONT_SMALL, width=60, height=36,
        fg_color=INPUT_BG, border_color=INPUT_BORDER, text_color=TEXT_PRIMARY,
        corner_radius=RADIUS_SM, placeholder_text="Max",
    )
    height_max_entry.pack(side="left", padx=(0, PAD_LG))

    # Reset filters button
    def _reset_filters():
        disease_filter_var.set("Tất cả")
        age_filter_var.set("Tất cả")
        gender_filter_var.set("Tất cả")
        bmi_filter_var.set("Tất cả")
        bp_filter_var.set("Tất cả")
        weight_min_entry.delete(0, "end")
        weight_max_entry.delete(0, "end")
        height_min_entry.delete(0, "end")
        height_max_entry.delete(0, "end")
        search_var.set("")
        _schedule_refresh()

    reset_btn = ctk.CTkButton(
        filter_inner, text="↻ Đặt lại", font=FONT_SMALL, height=36, width=90,
        fg_color=DANGER, hover_color="#DC2626", text_color="white",
        corner_radius=RADIUS_MD, command=_reset_filters,
    )
    reset_btn.pack(side="left", padx=(PAD_LG, 0))

    # ── Status bar ───────────────────────────────────────────────────────────
    status_var = ctk.StringVar(value="")
    status_lbl = ctk.CTkLabel(outer, textvariable=status_var, font=FONT_BODY,
                              text_color=SECONDARY, fg_color="transparent",
                              wraplength=1000, justify="left") # wraplength giúp tự xuống dòng
    status_lbl.pack(anchor="w", padx=PAD_LG, pady=(PAD_SM, 0))

    # ── Table header row ─────────────────────────────────────────────────────
    # ── Table Container (Dùng Treeview thay cho Frame) ───────────────────────
    # ── Table Container (Dùng Treeview thay cho Frame) ───────────────────────
    table_container = ctk.CTkFrame(outer, fg_color=CONTENT_BG, corner_radius=0)
    table_container.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_SM))

    def _get_color(color_tuple):
        mode = ctk.get_appearance_mode()
        return color_tuple[1] if mode == "Dark" else color_tuple[0]

    style = ttk.Style()
    style.theme_use("default")
    
    style.configure("Treeview",
                    background=_get_color(CARD_BG),
                    foreground=_get_color(TEXT_PRIMARY),
                    rowheight=35,
                    fieldbackground=_get_color(CARD_BG),
                    borderwidth=0,
                    font=(FONT_FAMILY, 11))
    
    style.map('Treeview', background=[('selected', PRIMARY)])

    style.configure("Treeview.Heading",
                    background=_get_color(SIDEBAR_BG),
                    foreground=_get_color(TEXT_SECONDARY),
                    font=(FONT_FAMILY, 11, "bold"),
                    borderwidth=0)
    style.map("Treeview.Heading", background=[('active', _get_color(SIDEBAR_HOVER))])

    tree = ttk.Treeview(table_container, columns=COLUMNS, show="headings", selectmode="browse")
    
    # 1. Khai báo 2 thanh cuộn
    vsb = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # 2. PACK ĐÚNG THỨ TỰ (Quan trọng: Không dùng Grid nữa để tránh lỗi layout)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)

    # 3. Phân bổ cột tự nhiên: Đẹp trên màn hình to, tự trượt ngang trên màn hình nhỏ
    for col, w in zip(COLUMNS, COL_WIDTHS):
        tree.heading(col, text=col, anchor="center")
        
        # Đặt minwidth = kích thước chuẩn. stretch=True để cột tự dàn đều cho đẹp.
        if col in ["Họ tên", "Loại bệnh"]:
            tree.column(col, width=w, minwidth=w, stretch=True, anchor="w")
        else:
            tree.column(col, width=w, minwidth=w, stretch=True, anchor="center")

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
        ma_bn = selected_id["value"]
        if not messagebox.askyesno(
            "Xác nhận xoá",
            f"Bạn có chắc muốn xoá bệnh nhân '{ma_bn}'?",
            icon="warning",
        ):
            return
        ok, msg = controller.handle_delete_patient(ma_bn, on_success=refresh)
        status_var.set(("✅  " if ok else "❌  ") + msg)
        if ok:
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

    def _export_csv():
        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="benh_nhan_export.csv"
        )
        if file:
            ok, msg = controller.handle_export_csv(file)
            if ok:
                status_var.set(f"✅  {msg}")
            else:
                messagebox.showerror("Lỗi", msg)

    def _import_csv():
        file = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file:
            merge = messagebox.askyesno(
                "Import CSV",
                "Cập nhật dữ liệu đã tồn tại?\n\n"
                "Chọn 'Yes' nếu muốn cập nhật bệnh nhân trùng mã.\n"
                "Chọn 'No' nếu chỉ thêm bệnh nhân mới."
            )
            ok, msg = controller.handle_import_csv(file, merge=merge, on_success=refresh)
            messagebox.showinfo("Kết quả Import", msg if ok else f"Lỗi: {msg}")
            if ok:
                refresh()

    ctk.CTkButton(
        action_bar, text="📥  Import CSV", font=FONT_BODY, height=36, width=140,
        fg_color=SECONDARY, hover_color="#6366F1",
        text_color="white", corner_radius=RADIUS_MD,
        command=_import_csv,
    ).pack(side="left", padx=PAD_SM, pady=PAD_SM)

    ctk.CTkButton(
        action_bar, text="📤  Export CSV", font=FONT_BODY, height=36, width=140,
        fg_color=INFO, hover_color="#0EA5E9",
        text_color="white", corner_radius=RADIUS_MD,
        command=_export_csv,
    ).pack(side="left", pady=PAD_SM)

    count_lbl = ctk.CTkLabel(action_bar, text="", font=FONT_SMALL, text_color=TEXT_MUTED)
    count_lbl.pack(side="right", padx=PAD_LG)

    page_state = {"page": 0}
    current_df = {"df": None}

    next_page_btn = ctk.CTkButton(
        action_bar, text="Sau", font=FONT_SMALL, height=30, width=70,
        fg_color=CARD_BG, hover_color=SIDEBAR_HOVER, text_color=TEXT_SECONDARY,
        corner_radius=RADIUS_MD, command=lambda: _change_page(1),
    )
    next_page_btn.pack(side="right", padx=(PAD_SM, 0), pady=PAD_SM)

    prev_page_btn = ctk.CTkButton(
        action_bar, text="Trước", font=FONT_SMALL, height=30, width=70,
        fg_color=CARD_BG, hover_color=SIDEBAR_HOVER, text_color=TEXT_SECONDARY,
        corner_radius=RADIUS_MD, command=lambda: _change_page(-1),
    )
    prev_page_btn.pack(side="right", padx=(PAD_SM, 0), pady=PAD_SM)

    # ── Render table rows ─────────────────────────────────────────────────────
    row_frames = []

    def _render_rows(df):
        current_df["df"] = df
        
        # 1. Xoá cực nhanh toàn bộ dữ liệu cũ trong bảng
        for item in tree.get_children():
            tree.delete(item)
            
        total = len(df)
        max_page = max((total - 1) // PAGE_SIZE, 0)
        page_state["page"] = min(page_state["page"], max_page)
        start = page_state["page"] * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)

        prev_page_btn.configure(state="normal" if page_state["page"] > 0 else "disabled")
        next_page_btn.configure(state="normal" if page_state["page"] < max_page else "disabled")
        count_lbl.configure(text=f"{start + 1 if total else 0}-{end} / {total}")

        if df.empty:
            return

        display_df = df.iloc[start:end]
        bmi_df = model.bmi_distribution(display_df)
        bmi_map = dict(zip(bmi_df["ma_bn"], bmi_df["bmi"])) if not bmi_df.empty else {}

        # 2. Insert dữ liệu mới
        for _, row in display_df.iterrows():
            ma = str(row["ma_bn"])
            bmi_val = bmi_map.get(ma, "-")
            bmi_str = f"{bmi_val:.1f}" if isinstance(bmi_val, float) else "-"

            values = (
                ma, str(row["ten"]), str(row["tuoi"]),
                str(row["gioi_tinh"]),
                str(row["chieu_cao"]), str(row["can_nang"]),
                str(row["huyet_ap"]), bmi_str, str(row["loai_benh"]),
            )
            
            # Insert trực tiếp vào bảng
            tree.insert("", "end", values=values)

    def _change_page(delta):
        df = current_df["df"]
        if df is None:
            return
        total = len(df)
        max_page = max((total - 1) // PAGE_SIZE, 0)
        page_state["page"] = max(0, min(page_state["page"] + delta, max_page))
        _render_rows(df)

    _current_highlight = {"frame": None}

    # ── Bắt sự kiện Click chọn bệnh nhân ─────────────────────────────────────
    def _on_tree_select(event):
        selected_items = tree.selection()
        if not selected_items:
            selected_id["value"] = None
            status_var.set("")
            return
        
        item = selected_items[0]
        values = tree.item(item, "values")
        if values:
            ma_bn = values[0]  # Cột 0: Mã BN
            ten_bn = values[1] # Cột 1: Họ tên
            loai_benh = values[8] # Cột 8: Loại bệnh
            
            _select(ma_bn) # Giữ nguyên hàm chọn để nút Sửa/Xoá hoạt động
            
            # Ghi đè lại status_var để hiển thị cực kỳ chi tiết
            status_var.set(f"👤 {ma_bn} - {ten_bn}  |  🏥 Chi tiết bệnh: {loai_benh}")

    # Gắn sự kiện khi click/đổi dòng
    tree.bind("<<TreeviewSelect>>", _on_tree_select)

    def refresh():
        kw = search_var.get()
        disease = disease_filter_var.get()
        age_group = age_filter_var.get()
        gender = gender_filter_var.get()
        bmi_filter = bmi_filter_var.get()
        bp_filter = bp_filter_var.get()
        
        # Get search results with diseases
        df = controller.handle_search(kw)
        if not df.empty and "loai_benh" not in df.columns:
            # Add loai_benh column if not present
            diseases_list = []
            for ma_bn in df["ma_bn"]:
                diseases = controller.get_patient_diseases(ma_bn)
                diseases_list.append(", ".join(diseases) if diseases else "")
            df["loai_benh"] = diseases_list
        
        if not df.empty:
            # Apply disease filter
            if disease != "Tất cả":
                if disease == "Khác":
                    def match_other_types(value: str) -> bool:
                        if not value:
                            return False
                        for item in value.split(","):
                            item = item.strip()
                            if not item:
                                continue
                            if item == "Khác" or item not in known_disease_options:
                                return True
                        return False

                    df = df[df["loai_benh"].apply(match_other_types)]
                else:
                    df = df[df["loai_benh"].str.contains(disease, na=False)]
            
            # Apply gender filter
            if gender != "Tất cả":
                df = df[df["gioi_tinh"] == gender]
            
            # Apply age group filter
            if age_group != "Tất cả":
                df["age_grp"] = df["tuoi"].astype(int).apply(model.classify_age_group)
                df = df[df["age_grp"] == age_group]
                df = df.drop("age_grp", axis=1)
            
            # Apply BMI filter
            if bmi_filter != "Tất cả":
                bmi_df = model.bmi_distribution(df)
                if not bmi_df.empty:
                    valid_ma = bmi_df[bmi_df["phan_loai_bmi"] == bmi_filter]["ma_bn"].values
                    df = df[df["ma_bn"].isin(valid_ma)]

            # Apply Blood Pressure filter
            if bp_filter != "Tất cả":
                def _classify_bp(bp_str):
                    try:
                        # Tách lấy chỉ số tâm thu (ví dụ "130" từ "130/85")
                        sys_val = int(str(bp_str).split('/')[0])
                        if sys_val < 90: 
                            return "Huyết áp thấp"
                        elif sys_val >= 130: 
                            return "Cao huyết áp"
                        else: 
                            return "Bình thường"
                    except:
                        return "Không rõ"
                
                # Tạo cột tạm thời để phân loại, lọc, rồi xóa cột đó đi
                df["bp_grp"] = df["huyet_ap"].apply(_classify_bp)
                df = df[df["bp_grp"] == bp_filter]
                df = df.drop("bp_grp", axis=1)
            
            # Apply weight range filter
            try:
                w_min = float(weight_min_entry.get()) if weight_min_entry.get() else 0
                w_max = float(weight_max_entry.get()) if weight_max_entry.get() else float('inf')
                df = df[(df["can_nang"].astype(float) >= w_min) & (df["can_nang"].astype(float) <= w_max)]
            except ValueError:
                pass
            
            # Apply height range filter
            try:
                h_min = float(height_min_entry.get()) if height_min_entry.get() else 0
                h_max = float(height_max_entry.get()) if height_max_entry.get() else float('inf')
                df = df[(df["chieu_cao"].astype(float) >= h_min) & (df["chieu_cao"].astype(float) <= h_max)]
            except ValueError:
                pass
        
        df = df.reset_index(drop=True)
        page_state["page"] = 0
        _render_rows(df)

    refresh_job = {"id": None}  # type: ignore

    def _run_scheduled_refresh():
        refresh_job["id"] = None
        refresh()

    def _schedule_refresh(*_):
        if refresh_job["id"] is not None:
            try:
                outer.after_cancel(refresh_job["id"])
            except Exception:
                pass
        refresh_job["id"] = outer.after(180, _run_scheduled_refresh)  # type: ignore

    # Trigger refresh on any filter change
    search_var.trace_add("write", _schedule_refresh)
    disease_filter_var.trace_add("write", _schedule_refresh)
    age_filter_var.trace_add("write", _schedule_refresh)
    gender_filter_var.trace_add("write", _schedule_refresh)
    bmi_filter_var.trace_add("write", _schedule_refresh)
    weight_min_entry.bind("<KeyRelease>", _schedule_refresh)
    weight_max_entry.bind("<KeyRelease>", _schedule_refresh)
    height_min_entry.bind("<KeyRelease>", _schedule_refresh)
    height_max_entry.bind("<KeyRelease>", _schedule_refresh)
    bp_filter_var.trace_add("write", _schedule_refresh)

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
    
    # Get current diseases for this patient
    current_diseases = controller.get_patient_diseases(ma_bn)

    dialog = ctk.CTkToplevel(parent)
    dialog.title(f"Sửa hồ sơ – {ma_bn}")
    dialog.geometry("540x700")
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
        "lich_su_kham": "Lịch sử khám",
        "lich_su_thuoc": "Lịch sử thuốc",
    }
    widgets = {}
    disease_vars = {}

    for key, label in fields.items():
        ctk.CTkLabel(scroll, text=label, font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(6, 1))
        if key in ("lich_su_kham", "lich_su_thuoc"):
            tb = ctk.CTkTextbox(scroll, height=60, font=FONT_BODY, fg_color=INPUT_BG,
                                border_color=INPUT_BORDER, text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM)  # type: ignore
            tb.insert("0.0", str(patient.get(key, "")))
            tb.pack(fill="x")
            widgets[key] = tb
        elif key == "gioi_tinh":
            opt = ctk.CTkOptionMenu(scroll, values=["Nam", "Nữ", "Khác"], font=FONT_BODY,
                                    fg_color=INPUT_BG, button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
                                    text_color=TEXT_PRIMARY, corner_radius=RADIUS_SM, height=36)  # type: ignore
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
    
    # Disease checkboxes
    ctk.CTkLabel(scroll, text="Loại bệnh", font=FONT_LABEL, text_color=TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(12, 6))
    disease_frame = ctk.CTkFrame(scroll, fg_color=INPUT_BG, border_width=1, 
                                 border_color=INPUT_BORDER, corner_radius=RADIUS_SM)  # type: ignore
    disease_frame.pack(fill="x")
    
    all_diseases = controller.get_all_diseases()
    for disease in all_diseases:
        var = ctk.BooleanVar(value=(disease in current_diseases))
        disease_vars[disease] = var
        checkbox = ctk.CTkCheckBox(disease_frame, text=disease, variable=var,
                                   font=FONT_BODY, text_color=TEXT_PRIMARY,
                                   fg_color=PRIMARY, border_color=INPUT_BORDER,
                                   hover_color=PRIMARY_HOVER, checkmark_color="white")
        checkbox.pack(anchor="w", padx=PAD_SM, pady=4)

    status_var = ctk.StringVar()
    ctk.CTkLabel(dialog, textvariable=status_var, font=FONT_SMALL, text_color=DANGER).pack()

    def _save():
        def _get(w):
            return w.get("0.0", "end").strip() if isinstance(w, ctk.CTkTextbox) else w.get()
        data = {k: _get(v) for k, v in widgets.items()}
        # Add selected diseases
        selected_diseases = [disease for disease, var in disease_vars.items() if var.get()]
        data["loai_benh"] = selected_diseases
        
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
