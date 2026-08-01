"""
main.py - Climate Change: Learn & Play
------------------------------------------
Run this file to start the app:

    python main.py

Flow: Article page -> Games menu -> pick a game (each has a back button).
"""

import tkinter as tk
import importlib

import theme
import article

WINDOW_W, WINDOW_H = 800, 700

# (button label, module path inside the games package)
GAMES = [
    ("\u267B\ufe0f  Recycle Rush", "games.recycle_sort"),
    ("\u2705  Climate Quiz", "games.climate_quiz"),
    ("\u2600\ufe0f  Renewable Catch", "games.renewable_catch"),
]


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Climate Change: Learn & Play")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg=theme.BG_DARK)
        self.root.resizable(False, False)

        self.container = tk.Frame(root, bg=theme.BG_DARK)
        self.container.pack(fill="both", expand=True)

        self.current_game = None
        self.show_article()

    def clear_container(self):
        if self.current_game is not None and hasattr(self.current_game, "stop"):
            self.current_game.stop()
        self.current_game = None
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_article(self):
        self.clear_container()
        ArticlePage(self.container, self)

    def show_games_menu(self):
        self.clear_container()
        GamesMenuPage(self.container, self)

    def launch_game(self, module_path):
        self.clear_container()
        module = importlib.import_module(module_path)
        self.current_game = module.Game(self.container, self.root, self.show_games_menu)


class ArticlePage:
    def __init__(self, parent, app):
        title = tk.Label(parent, text=article.TITLE, font=theme.FONT_TITLE,
                          fg=theme.ACCENT_GREEN, bg=theme.BG_DARK, wraplength=740,
                          justify="center")
        title.pack(pady=(30, 15), side="top")

        # Pack the button at the BOTTOM first so its space is always reserved,
        # no matter how much room the article text below wants to take up.
        btn = tk.Button(
            parent, text="I've read it - Play the games \u2192", font=theme.FONT_BUTTON,
            fg=theme.BG_DARK, bg=theme.ACCENT_GREEN, activebackground=theme.TEXT_LIGHT,
            activeforeground=theme.BG_DARK, bd=0, padx=18, pady=10, cursor="hand2",
            command=app.show_games_menu)
        btn.pack(pady=20, side="bottom")

        text_frame = tk.Frame(parent, bg=theme.BG_PANEL)
        text_frame.pack(padx=30, pady=5, fill="both", expand=True, side="top")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            text_frame, wrap="word", font=("Segoe UI", 12), bg=theme.BG_PANEL,
            fg=theme.TEXT_LIGHT, bd=0, padx=20, pady=20, relief="flat",
            yscrollcommand=scrollbar.set, cursor="arrow", height=1, width=1)
        text_widget.insert("1.0", article.BODY)
        text_widget.configure(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)


class GamesMenuPage:
    def __init__(self, parent, app):
        theme.build_header(parent, "Games", app.show_article, back_label="\u25c0 Article")

        title = tk.Label(parent, text="Pick a Game", font=theme.FONT_TITLE,
                          fg=theme.ACCENT_GREEN, bg=theme.BG_DARK)
        title.pack(pady=(45, 5))

        subtitle = tk.Label(parent, text="Put what you just read into practice",
                             font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.BG_DARK)
        subtitle.pack(pady=(0, 35))

        btn_frame = tk.Frame(parent, bg=theme.BG_DARK)
        btn_frame.pack()

        colors = [theme.ACCENT_GREEN, theme.ACCENT_BLUE, theme.ACCENT_YELLOW]

        for i, (label, module_path) in enumerate(GAMES):
            color = colors[i % len(colors)]
            btn = tk.Button(
                btn_frame, text=label, font=theme.FONT_BUTTON,
                fg=theme.BG_DARK, bg=color,
                activebackground=theme.TEXT_LIGHT, activeforeground=theme.BG_DARK,
                width=26, height=2, bd=0, relief="flat", cursor="hand2",
                command=lambda m=module_path: app.launch_game(m))
            btn.pack(pady=12)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()