"""
main.py – Application entry point.
Assembles sidebar + content area (MVC root).
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from views.theme import *
from views.sidebar import make_sidebar
from views.page_input import make_input_page
from views.page_list import make_list_page
from views.page_stats import make_stats_page
from views.page_about import make_about_page
import controller


def build_app():
    """Bootstrap the CTk application window."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    controller.initialize_app()

    root = ctk.CTk()
    root.title("Quản lý Hồ sơ Bệnh nhân")
    root.geometry("1280x780")
    root.minsize(900, 600)
    root.configure(fg_color=CONTENT_BG)

    # ── Top-level layout: sidebar | content ───────────────────────────────────
    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True)

    # Content container (right side)
    content_area = ctk.CTkFrame(main_frame, fg_color=CONTENT_BG, corner_radius=0)

    # Pages cache
    # Pages cache
    pages: dict[str, ctk.CTkFrame] = {}
    refresh_fns: dict[str, callable] = {}
    current_page = {"key": None}
    need_refresh = {"list": True, "stats": True}  # Thêm cờ báo hiệu cần load lại data

    # ── Page factory (lazy init) ───────────────────────────────────────────────
    def _on_data_changed():
        """Called after add/delete to propagate refreshes."""
        need_refresh["list"] = True   # Bật cờ báo danh sách cần vẽ lại
        need_refresh["stats"] = True  # Bật cờ báo thống kê cần vẽ lại
        
        current = current_page["key"]
        if current and current != "input" and current in refresh_fns:
            refresh_fns[current]()
            need_refresh[current] = False # Load xong thì tắt cờ đi

    def _get_or_create_page(key: str):
        if key in pages:
            return pages[key]

        if key == "input":
            frame = make_input_page(content_area, on_saved=_on_data_changed)
            pages[key] = frame
            refresh_fns[key] = lambda: None  # no refresh needed for form

        elif key == "list":
            frame, refresh = make_list_page(content_area)
            pages[key] = frame
            refresh_fns[key] = refresh

        elif key == "stats":
            frame, refresh = make_stats_page(content_area)
            pages[key] = frame
            refresh_fns[key] = refresh

        elif key == "about":
            frame, refresh = make_about_page(content_area)
            pages[key] = frame
            refresh_fns[key] = refresh

        return pages[key]

    # ── Navigation ────────────────────────────────────────────────────────────
    def navigate(key: str):
        if current_page["key"] == key:
            return
        # Hide current
        if current_page["key"] and current_page["key"] in pages:
            pages[current_page["key"]].pack_forget()

        current_page["key"] = key
        frame = _get_or_create_page(key)
        frame.pack(fill="both", expand=True)

        # Refresh page data when switching to it
        # Refresh page data when switching to it
        # Chỉ refresh nếu dữ liệu thực sự bị thay đổi (need_refresh = True)
        if key in refresh_fns:
            if need_refresh.get(key, True):
                content_area.after(10, refresh_fns[key]) # Delay 10ms để UI nhảy tab mượt
                need_refresh[key] = False # Đẩy việc load data ra phía sau để UI không bị block

        set_active(key)

    # Build sidebar (after navigate is defined)
    sidebar_frame, set_active = make_sidebar(main_frame, on_navigate=navigate)

    sidebar_frame.pack(side="left", fill="y")
    content_area.pack(side="right", fill="both", expand=True)

    # Default page
    navigate("input")

    root.mainloop()


if __name__ == "__main__":
    build_app()
