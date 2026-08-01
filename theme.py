"""
theme.py
--------
Shared eco color palette, fonts, and a reusable header widget used by
the article page, the games menu, and every game screen.
"""

import tkinter as tk

# ---- Eco color palette (forest green / sky blue / sun yellow) ----
BG_DARK = "#0d1f16"        # app background - deep forest
BG_PANEL = "#13291b"       # header / panel background
BG_BOARD = "#0f2419"       # game board background

ACCENT_GREEN = "#4ade80"
ACCENT_BLUE = "#38bdf8"
ACCENT_YELLOW = "#facc15"
ACCENT_RED = "#f87171"     # used sparingly, e.g. fossil-fuel / danger cues

TEXT_LIGHT = "#e6f4ea"
TEXT_MUTED = "#8fae9c"

BUTTON_BG = "#1c3524"
BUTTON_HOVER = "#274a30"

FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 13, "bold")


def build_header(parent, title_text, on_back, back_label="\u25c0 Games"):
    """Standard top bar with a back button and a title. Returns the Frame."""
    header = tk.Frame(parent, bg=BG_PANEL, height=54)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)

    back_btn = tk.Button(
        header, text=back_label, font=FONT_BODY, fg=TEXT_LIGHT,
        bg=BUTTON_BG, activebackground=BUTTON_HOVER, activeforeground=TEXT_LIGHT,
        bd=0, padx=14, pady=6, cursor="hand2", command=on_back)
    back_btn.pack(side="left", padx=14, pady=10)

    title = tk.Label(header, text=title_text, font=FONT_HEADING,
                      fg=ACCENT_GREEN, bg=BG_PANEL)
    title.pack(side="left", padx=6)

    return header
