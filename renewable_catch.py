"""
games/renewable_catch.py - Renewable Catch
------------------------------------------------
Move your collector with LEFT/RIGHT (or A/D). Catch renewable energy
icons (sun, wind, water, plant) for points. Avoid fossil fuel icons
(coal, oil, gas) - catching one costs a life. 3 lives, survive as long
as you can as the pace speeds up.
"""

import tkinter as tk
import random

import theme

WIDTH, HEIGHT = 700, 480
COLLECTOR_W, COLLECTOR_H = 90, 22
ITEM_SIZE = 30
FPS_MS = 16
LIVES = 3
SPAWN_MS_START = 950

# Clean Unicode glyphs (stripped of variation selector \ufe0f for Tkinter compatibility)
GOOD_ITEMS = ["\u2600", "\u26A1", "\U0001F4A7", "\U0001F331"]   # ☀ Sun, ⚡ Power, 💧 Water, 🌱 Seedling
BAD_ITEMS  = ["\U0001F6E2", "\U0001F4A8", "\U0001F525"]         # 🛢 Oil Drum, 💨 Smoke, 🔥 Fire

# Valid Tkinter font definition tuple (Font Family, Size)
EMOJI_FONT = ("Segoe UI Emoji", 22)

class Game:
    def __init__(self, parent, root, on_back):
        self.root = root
        self.on_back = on_back
        self.after_id = None
        self.spawn_after_id = None
        self.bind_ids = []

        theme.build_header(parent, "Renewable Catch", self.on_back)

        self.canvas = tk.Canvas(parent, width=WIDTH, height=HEIGHT,
                                bg=theme.BG_BOARD, highlightthickness=0)
        self.canvas.pack(pady=14)
        self.canvas.focus_set()

        self.info_text = self.canvas.create_text(
            WIDTH / 2, 16, fill=theme.TEXT_LIGHT, font=("Segoe UI", 12, "bold"), text="")
        self.status_text = self.canvas.create_text(
            WIDTH / 2, HEIGHT / 2, fill=theme.ACCENT_GREEN,
            font=("Segoe UI", 18, "bold"), text="", justify="center")

        self.collector_x = WIDTH / 2 - COLLECTOR_W / 2
        self.collector = None

        self.items = []
        self.score = 0
        self.lives = LIVES
        self.fall_speed = 2.6
        self.spawn_delay = SPAWN_MS_START
        self.started = False
        self.game_over = False
        self.move_left = False
        self.move_right = False

        self.bind_keys()
        self.show_start_screen()
        self.tick()

    # ---------- setup ----------
    def show_start_screen(self):
        self.canvas.itemconfig(
            self.status_text,
            text="RENEWABLE CATCH\n\nCatch sun/wind/water/plants, avoid fossil fuels!\nPress SPACE to start")
        self.canvas.itemconfig(self.info_text, text="")

    def start_game(self):
        if self.started:
            return
        self.started = True
        self.game_over = False
        self.score = 0
        self.lives = LIVES
        self.fall_speed = 2.6
        self.spawn_delay = SPAWN_MS_START
        self.canvas.itemconfig(self.status_text, text="")

        for it in self.items:
            self.canvas.delete(it["id"])
        self.items = []

        self.collector_x = WIDTH / 2 - COLLECTOR_W / 2
        if self.collector is not None:
            self.canvas.delete(self.collector)
        y0 = HEIGHT - COLLECTOR_H - 10
        self.collector = self.canvas.create_rectangle(
            self.collector_x, y0, self.collector_x + COLLECTOR_W, y0 + COLLECTOR_H,
            fill=theme.ACCENT_GREEN, outline="")

        self.update_info()
        self.schedule_spawn()

    # ---------- keys ----------
    def bind_keys(self):
        def add(seq, handler):
            fid = self.root.bind(seq, handler)
            self.bind_ids.append((seq, fid))

        add("<space>", lambda e: self.start_game())
        add("<Key-r>", lambda e: self.reset_to_start())
        add("<Key-R>", lambda e: self.reset_to_start())

        add("<KeyPress-Left>", lambda e: self.set_move("left", True))
        add("<KeyRelease-Left>", lambda e: self.set_move("left", False))
        add("<KeyPress-Right>", lambda e: self.set_move("right", True))
        add("<KeyRelease-Right>", lambda e: self.set_move("right", False))
        add("<KeyPress-a>", lambda e: self.set_move("left", True))
        add("<KeyRelease-a>", lambda e: self.set_move("left", False))
        add("<KeyPress-d>", lambda e: self.set_move("right", True))
        add("<KeyRelease-d>", lambda e: self.set_move("right", False))

    def set_move(self, direction, pressed):
        if direction == "left":
            self.move_left = pressed
        else:
            self.move_right = pressed

    def reset_to_start(self):
        if not self.game_over:
            return
        self.started = False
        self.game_over = False
        self.show_start_screen()

    # ---------- spawning ----------
    def schedule_spawn(self):
        self.spawn_item()
        self.spawn_delay = max(320, self.spawn_delay - 12)
        if self.started and not self.game_over:
            self.spawn_after_id = self.root.after(self.spawn_delay, self.schedule_spawn)

    def spawn_item(self):
        is_good = random.random() < 0.65
        emoji = random.choice(GOOD_ITEMS if is_good else BAD_ITEMS)
        x = random.randint(30, WIDTH - 30)
        item_id = self.canvas.create_text(
            x, -20, text=emoji, font=EMOJI_FONT, fill=theme.TEXT_LIGHT
        )
        self.items.append({"id": item_id, "x": x, "y": -20, "good": is_good})
        self.fall_speed = min(7.5, self.fall_speed + 0.04)

    # ---------- loop ----------
    def tick(self):
        if self.started and not self.game_over:
            self.move_collector()
            self.move_items()
            self.update_info()
        self.after_id = self.root.after(FPS_MS, self.tick)

    def move_collector(self):
        dx = (1 if self.move_right else 0) - (1 if self.move_left else 0)
        if dx:
            self.collector_x = min(max(self.collector_x + dx * 7, 0), WIDTH - COLLECTOR_W)
            y0 = HEIGHT - COLLECTOR_H - 10
            self.canvas.coords(self.collector, self.collector_x, y0,
                                self.collector_x + COLLECTOR_W, y0 + COLLECTOR_H)

    def move_items(self):
        remaining = []
        cy0 = HEIGHT - COLLECTOR_H - 10
        for it in self.items:
            it["y"] += self.fall_speed
            self.canvas.coords(it["id"], it["x"], it["y"])

            if cy0 <= it["y"] <= cy0 + COLLECTOR_H and self.collector_x <= it["x"] <= self.collector_x + COLLECTOR_W:
                self.catch_item(it)
                continue
            if it["y"] > HEIGHT:
                self.canvas.delete(it["id"])
                continue
            remaining.append(it)
        self.items = remaining

    def catch_item(self, it):
        self.canvas.delete(it["id"])
        if it["good"]:
            self.score += 10
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.end_game()

    def end_game(self):
        self.game_over = True
        if self.spawn_after_id is not None:
            self.root.after_cancel(self.spawn_after_id)
            self.spawn_after_id = None
        self.canvas.itemconfig(
            self.status_text,
            text=f"Game Over!\nFinal Score: {self.score}\nPress R to try again")

    def update_info(self):
        hearts = "\u2665" * self.lives
        self.canvas.itemconfig(self.info_text, text=f"Score: {self.score}    Lives: {hearts}")

    # ---------- cleanup ----------
    def stop(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.spawn_after_id is not None:
            self.root.after_cancel(self.spawn_after_id)
            self.spawn_after_id = None
        for seq, fid in self.bind_ids:
            self.root.unbind(seq, fid)
        self.bind_ids = []