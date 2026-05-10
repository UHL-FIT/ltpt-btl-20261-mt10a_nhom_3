"""
theme.py – Colour tokens and reusable style helpers.
"""

# ── Palette ────────────────────────────────────────────────────────────────────
PRIMARY        = "#3B82F6"   # blue-500
PRIMARY_HOVER  = "#2563EB"   # blue-600
SECONDARY      = "#10B981"   # emerald-500
DANGER         = "#EF4444"
WARNING        = "#F59E0B"
INFO           = "#6366F1"

# Dark/Light sidebar
SIDEBAR_BG     = ("#F8FAFC", "#0F172A")   # slate-50 / slate-900
SIDEBAR_HOVER  = ("#E2E8F0", "#1E293B")   # slate-200 / slate-800
SIDEBAR_ACTIVE = PRIMARY                  # same color
SIDEBAR_TEXT   = ("#64748B", "#94A3B8")   # slate-500 / slate-400
SIDEBAR_ACTIVE_TEXT = ("#FFFFFF", "#FFFFFF")

# Content backgrounds (light / dark mode)
CONTENT_BG     = ("#F1F5F9", "#111827")   # slate-100 / gray-900
CARD_BG        = ("#FFFFFF", "#1F2937")   # white / gray-800
CARD_BORDER    = ("#E2E8F0", "#374151")   # slate-200 / gray-700
INPUT_BG       = ("#F8FAFC", "#374151")   # slate-50 / gray-700
INPUT_BORDER   = ("#CBD5E1", "#4B5563")   # slate-300 / gray-600

TEXT_PRIMARY   = ("#0F172A", "#F9FAFB")   # slate-900 / gray-50
TEXT_SECONDARY = ("#475569", "#9CA3AF")   # slate-600 / gray-400
TEXT_MUTED     = ("#94A3B8", "#6B7280")   # slate-400 / gray-500

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_FAMILY  = "Segoe UI"
FONT_TITLE   = (FONT_FAMILY, 22, "bold")
FONT_HEADING = (FONT_FAMILY, 15, "bold")
FONT_BODY    = (FONT_FAMILY, 13)
FONT_SMALL   = (FONT_FAMILY, 11)
FONT_LABEL   = (FONT_FAMILY, 12, "bold")

# ── Corner radii & padding ─────────────────────────────────────────────────────
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14
PAD       = 16
PAD_SM    = 8
PAD_LG    = 24

# ── Status colours for BMI ─────────────────────────────────────────────────────
BMI_COLORS = {
    "Thiếu cân":  "#60A5FA",
    "Bình thường":"#34D399",
    "Thừa cân":   "#FBBF24",
    "Béo phì":    "#F87171",
}
