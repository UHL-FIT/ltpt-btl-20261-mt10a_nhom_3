"""
page_stats.py – Statistics page with matplotlib charts embedded in CTk.
"""

import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.theme import *
import controller

def _rc(color):
    """Resolve CTk color tuple to current mode string for matplotlib."""
    if isinstance(color, tuple):
        return color[1] if ctk.get_appearance_mode() == "Dark" else color[0]
    return color

plt.rcParams.update({
    "figure.facecolor":  _rc(CONTENT_BG),
    "axes.facecolor":    _rc(CARD_BG),
    "axes.edgecolor":    _rc(CARD_BORDER),
    "axes.labelcolor":   _rc(TEXT_SECONDARY),
    "xtick.color":       _rc(TEXT_MUTED),
    "ytick.color":       _rc(TEXT_MUTED),
    "text.color":        _rc(TEXT_PRIMARY),
    "grid.color":        _rc(CARD_BORDER),
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "font.family":       "DejaVu Sans",
})

CHART_COLORS = [PRIMARY, SECONDARY, WARNING, DANGER, INFO, "#EC4899", "#14B8A6", "#8B5CF6"]


def _stat_card(parent, label: str, value: str, color: str = TEXT_PRIMARY):
    f = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    ctk.CTkLabel(f, text=label, font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w", padx=PAD, pady=(PAD, 0))
    ctk.CTkLabel(f, text=value, font=(FONT_FAMILY, 24, "bold"), text_color=color).pack(anchor="w", padx=PAD, pady=(2, PAD))
    return f


def _embed_figure(parent, fig):
    """Embed a matplotlib figure into a CTk frame."""
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas


def _chart_frame(parent, title: str) -> ctk.CTkFrame:
    outer = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=RADIUS_LG)
    ctk.CTkLabel(outer, text=title, font=FONT_HEADING, text_color=PRIMARY).pack(anchor="w", padx=PAD, pady=(PAD, PAD_SM))
    ctk.CTkFrame(outer, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=PAD, pady=(0, PAD_SM))
    return outer


def make_stats_page(parent):
    """
    Build the statistics page.
    Returns (frame, refresh_fn).
    """
    outer = ctk.CTkFrame(parent, fg_color=CONTENT_BG, corner_radius=0)
    outer.pack(fill="both", expand=True)

    scroll = ctk.CTkScrollableFrame(outer, fg_color=CONTENT_BG, corner_radius=0)
    scroll.pack(fill="both", expand=True)

    # Page header
    hdr = ctk.CTkFrame(scroll, fg_color="transparent")
    hdr.pack(fill="x", padx=PAD_LG, pady=(PAD_LG, PAD))
    ctk.CTkLabel(hdr, text="Thống kê & Phân tích", font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(side="left")
    refresh_btn = ctk.CTkButton(hdr, text="🔄  Làm mới", font=FONT_SMALL,
                                height=34, width=120,
                                fg_color=CARD_BG, hover_color=SIDEBAR_HOVER,
                                text_color=TEXT_SECONDARY, corner_radius=RADIUS_MD,
                                command=lambda: _refresh())
    refresh_btn.pack(side="right")

    # ── KPI cards row ─────────────────────────────────────────────────────────
    kpi_row = ctk.CTkFrame(scroll, fg_color="transparent")
    kpi_row.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    kpi_labels = {}
    kpi_defs = [
        ("tong_bn",        "Tổng bệnh nhân", TEXT_PRIMARY),
        ("trung_binh_tuoi","Tuổi trung bình", SECONDARY),
        ("trung_binh_bmi", "BMI trung bình",  WARNING),
        ("nam",            "Bệnh nhân nam",   INFO),
        ("nu",             "Bệnh nhân nữ",    "#EC4899"),
    ]

    for key, label, color in kpi_defs:
        card = _stat_card(kpi_row, label, "–", color)
        card.pack(side="left", expand=True, fill="both", padx=(0, PAD_SM))
        kpi_labels[key] = card.winfo_children()[1]  # value label

    # ── Charts row 1: BP by age group + Disease frequency ─────────────────────
    charts_row1 = ctk.CTkFrame(scroll, fg_color="transparent")
    charts_row1.pack(fill="x", padx=PAD_LG, pady=(0, PAD))

    bp_frame = _chart_frame(charts_row1, "📈  Huyết áp trung bình theo nhóm tuổi")
    bp_frame.pack(side="left", expand=True, fill="both", padx=(0, PAD_SM))
    bp_chart_holder = ctk.CTkFrame(bp_frame, fg_color="transparent", height=280)
    bp_chart_holder.pack(fill="both", expand=True, padx=PAD_SM, pady=(0, PAD_SM))

    dis_frame = _chart_frame(charts_row1, "🥧  Tần suất theo Loại bệnh")
    dis_frame.pack(side="left", expand=True, fill="both")
    dis_chart_holder = ctk.CTkFrame(dis_frame, fg_color="transparent", height=280)
    dis_chart_holder.pack(fill="both", expand=True, padx=PAD_SM, pady=(0, PAD_SM))

    # ── Charts row 2: BMI distribution ────────────────────────────────────────
    charts_row2 = ctk.CTkFrame(scroll, fg_color="transparent")
    charts_row2.pack(fill="x", padx=PAD_LG, pady=(0, PAD_LG))

    bmi_frame = _chart_frame(charts_row2, "📊  Phân bổ BMI bệnh nhân")
    bmi_frame.pack(fill="both", expand=True)
    bmi_chart_holder = ctk.CTkFrame(bmi_frame, fg_color="transparent", height=260)
    bmi_chart_holder.pack(fill="both", expand=True, padx=PAD_SM, pady=(0, PAD_SM))

    # ── BP table ──────────────────────────────────────────────────────────────
    bp_table_frame = _chart_frame(scroll, "📋  Bảng huyết áp theo nhóm tuổi")
    bp_table_frame.pack(fill="x", padx=PAD_LG, pady=(0, PAD_LG))
    bp_table_holder = ctk.CTkFrame(bp_table_frame, fg_color="transparent")
    bp_table_holder.pack(fill="x", padx=PAD, pady=(0, PAD))

    canvases = {}

    def _clear_holder(holder):
        for w in holder.winfo_children():
            w.destroy()
        if id(holder) in canvases:
            try:
                canvases[id(holder)].get_tk_widget().destroy()
            except Exception:
                pass

    def _draw_bp_chart(df_bp):
        _clear_holder(bp_chart_holder)
        if df_bp.empty:
            ctk.CTkLabel(bp_chart_holder, text="Chưa có dữ liệu huyết áp hợp lệ.",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack(expand=True)
            return
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=96)
        fig.patch.set_facecolor(_rc(CONTENT_BG))
        ax.set_facecolor(_rc(CARD_BG))
        x = range(len(df_bp))
        width = 0.35
        bars1 = ax.bar([i - width/2 for i in x], df_bp["TB Tâm thu (mmHg)"],
                       width=width, label="Tâm thu", color=DANGER, alpha=0.85)
        bars2 = ax.bar([i + width/2 for i in x], df_bp["TB Tâm trương (mmHg)"],
                       width=width, label="Tâm trương", color=INFO, alpha=0.85)
        ax.set_xticks(list(x))
        ax.set_xticklabels(df_bp["Nhóm tuổi"].tolist(), fontsize=10)
        ax.set_ylabel("mmHg", fontsize=10)
        ax.legend(fontsize=9, framealpha=0.2)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        canvas = _embed_figure(bp_chart_holder, fig)
        canvases[id(bp_chart_holder)] = canvas
        plt.close(fig)

    def _draw_disease_chart(df_dis):
        _clear_holder(dis_chart_holder)
        if df_dis.empty:
            ctk.CTkLabel(dis_chart_holder, text="Chưa có dữ liệu.",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack(expand=True)
            return
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=96)
        fig.patch.set_facecolor(_rc(CONTENT_BG))
        colors_pie = CHART_COLORS[:len(df_dis)]
        wedges, texts, autotexts = ax.pie(
            df_dis["Số lượt"], labels=df_dis["Loại bệnh"],
            autopct="%1.1f%%", colors=colors_pie,
            pctdistance=0.8, startangle=90,
        )
        for t in texts:
            t.set_color(_rc(TEXT_PRIMARY))
            t.set_fontsize(9)
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(8)
        ax.set_facecolor(_rc(CARD_BG))
        fig.tight_layout()
        canvas = _embed_figure(dis_chart_holder, fig)
        canvases[id(dis_chart_holder)] = canvas
        plt.close(fig)

    def _draw_bmi_chart(df_bmi):
        _clear_holder(bmi_chart_holder)
        if df_bmi.empty:
            ctk.CTkLabel(bmi_chart_holder, text="Chưa có dữ liệu BMI.",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack(expand=True)
            return
        cats = df_bmi["phan_loai_bmi"].value_counts()
        color_map = {k: v for k, v in {
            "Thiếu cân":  "#60A5FA", "Bình thường": "#34D399",
            "Thừa cân":   "#FBBF24", "Béo phì":    "#F87171",
        }.items() if k in cats.index}
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2), dpi=96)
        fig.patch.set_facecolor(_rc(CONTENT_BG))

        # Bar chart by category
        ax1.set_facecolor(_rc(CARD_BG))
        ax1.bar(cats.index, cats.values,
                color=[color_map.get(c, PRIMARY) for c in cats.index], alpha=0.9)
        ax1.set_ylabel("Số bệnh nhân", fontsize=10)
        ax1.set_title("Phân loại BMI", color=_rc(TEXT_PRIMARY), fontsize=11)
        ax1.spines[["top", "right"]].set_visible(False)
        ax1.tick_params(axis="x", labelsize=9)

        # Histogram
        ax2.set_facecolor(_rc(CARD_BG))
        ax2.hist(df_bmi["bmi"], bins=12, color=PRIMARY, alpha=0.8, edgecolor=_rc(CARD_BORDER))
        ax2.set_xlabel("BMI", fontsize=10)
        ax2.set_ylabel("Số bệnh nhân", fontsize=10)
        ax2.set_title("Phân phối BMI", color=_rc(TEXT_PRIMARY), fontsize=11)
        ax2.spines[["top", "right"]].set_visible(False)

        fig.tight_layout()
        canvas = _embed_figure(bmi_chart_holder, fig)
        canvases[id(bmi_chart_holder)] = canvas
        plt.close(fig)

    def _draw_bp_table(df_bp):
        for w in bp_table_holder.winfo_children():
            w.destroy()
        if df_bp.empty:
            ctk.CTkLabel(bp_table_holder, text="Không có dữ liệu.",
                         font=FONT_BODY, text_color=TEXT_MUTED).pack()
            return
        # Header
        header = ctk.CTkFrame(bp_table_holder, fg_color=SIDEBAR_BG, corner_radius=RADIUS_SM, height=32)
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)
        for col in df_bp.columns:
            ctk.CTkLabel(header, text=col, font=(FONT_FAMILY, 11, "bold"),
                         text_color=TEXT_SECONDARY).pack(side="left", expand=True, padx=4)
        # Rows
        for i, row in df_bp.iterrows():
            rf = ctk.CTkFrame(bp_table_holder, fg_color=CARD_BG if i % 2 == 0 else INPUT_BG,
                              corner_radius=RADIUS_SM, height=30)
            rf.pack(fill="x", pady=1)
            rf.pack_propagate(False)
            for val in row:
                ctk.CTkLabel(rf, text=str(val), font=FONT_SMALL, text_color=TEXT_PRIMARY
                             ).pack(side="left", expand=True, padx=4)

    def _refresh():
        plt.rcParams.update({
            "figure.facecolor":  _rc(CONTENT_BG),
            "axes.facecolor":    _rc(CARD_BG),
            "axes.edgecolor":    _rc(CARD_BORDER),
            "axes.labelcolor":   _rc(TEXT_SECONDARY),
            "xtick.color":       _rc(TEXT_MUTED),
            "ytick.color":       _rc(TEXT_MUTED),
            "text.color":        _rc(TEXT_PRIMARY),
            "grid.color":        _rc(CARD_BORDER),
        })
        
        stats = controller.get_summary_stats()
        for key, lbl in kpi_labels.items():
            lbl.configure(text=str(stats.get(key, "–")))

        df_bp  = controller.get_bp_by_age_group()
        df_dis = controller.get_disease_frequency()
        df_bmi = controller.get_bmi_distribution()

        _draw_bp_chart(df_bp)
        _draw_disease_chart(df_dis)
        _draw_bmi_chart(df_bmi)
        _draw_bp_table(df_bp)

    # Initial load
    _refresh()

    return outer, _refresh
