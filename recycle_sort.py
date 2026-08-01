"""
games/recycle_sort.py - Recycle Rush
-----------------------------------------
Items fall from the top. Move your bin with LEFT/RIGHT (or A/D) and
catch each item in the bin that matches its correct category:
Recycle, Compost, or Trash. Catch it in the wrong bin (or let it fall)
and you lose a life. 3 lives. Score points for correct catches.
"""

import tkinter as tk
import random

import theme

WIDTH, HEIGHT = 700, 480
BIN_W, BIN_H = 110, 60
ITEM_SIZE = 34
FALL_SPEED_START = 2.2
FPS_MS = 16
LIVES = 3
SPAWN_MS_START = 1400

# item -> (emoji, correct category)
ITEMS = [
    ("\U0001F37E", "Recycle"),   # bottle
    ("\U0001F4F0", "Recycle"),   # newspaper
    ("\U0001F96B", "Recycle"),   # can (tin/tray)
    ("\U0001F34C", "Compost"),   # banana
    ("\U0001F34E", "Compost"),   # apple core
    ("\U0001F343", "Compost"),   # leaf/food scrap
    ("\U0001F50B", "Trash"),     # battery (not recyclable curbside)
    ("\U0001FA92", "Trash"),     # toothbrush
    ("\U0001F37F", "Trash"),     # chip bag
]

BINS = ["Recycle", "Compost", "Trash"]

# Bright, high-contrast palette just for this game (independent of the
# app's dark shared theme, so this screen pops with vivid colors).
BOARD_BG = "#FFF6DA"        # warm bright background
TEXT_DARK = "#1B2A22"       # dark text for contrast on the light board
INFO_COLOR = "#0D47A1"      # vivid blue
STATUS_COLOR = "#2E7D32"    # vivid green
GAME_OVER_COLOR = "#E64A19"  # vivid orange-red

BIN_COLORS = {"Recycle": "#1E88E5", "Compost": "#43A047", "Trash": "#FB8C00"}


class Game:
    def __init__(self, parent, root, on_back):
        self.root = root
        self.on_back = on_back
        self.after_id = None
        self.spawn_after_id = None
        self.bind_ids = []

        theme.build_header(parent, "Recycle Rush", self.go_back)

        self.canvas = tk.Canvas(parent, width=WIDTH, height=HEIGHT,
                                 bg=BOARD_BG, highlightthickness=0)
        self.canvas.pack(pady=14)
        self.canvas.focus_set()

        self.info_text = self.canvas.create_text(
            WIDTH / 2, 16, fill=INFO_COLOR, font=("Segoe UI", 12, "bold"), text="")
        self.status_text = self.canvas.create_text(
            WIDTH / 2, HEIGHT / 2, fill=STATUS_COLOR,
            font=("Segoe UI", 18, "bold"), text="", justify="center")

        self.bin_x = WIDTH / 2 - BIN_W / 2
        self.bin_index = 0
        self.bin_rect = None
        self.bin_label = None

        self.items = []
        self.score = 0
        self.lives = LIVES
        self.fall_speed = FALL_SPEED_START
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
            text="RECYCLE RUSH\n\nCatch items in the right bin!\nPress SPACE to start",
            fill=STATUS_COLOR)
        self.canvas.itemconfig(self.info_text, text="")

    def start_game(self):
        if self.started:
            return
        self.started = True
        self.game_over = False
        self.score = 0
        self.lives = LIVES
        self.fall_speed = FALL_SPEED_START
        self.spawn_delay = SPAWN_MS_START
        self.canvas.itemconfig(self.status_text, text="", fill=STATUS_COLOR)

        for it in self.items:
            self.canvas.delete(it["id"])
            self.canvas.delete(it["circle"])
        self.items = []

        self.bin_index = 1  # start on Compost (middle) for visual centering
        self.bin_x = WIDTH / 2 - BIN_W / 2
        self.draw_bin()
        self.update_info()
        self.schedule_spawn()

    def draw_bin(self):
        if self.bin_rect is not None:
            self.canvas.delete(self.bin_rect)
            self.canvas.delete(self.bin_label)
        cat = BINS[self.bin_index]
        color = BIN_COLORS[cat]
        y0 = HEIGHT - BIN_H - 10
        self.bin_rect = self.canvas.create_rectangle(
            self.bin_x, y0, self.bin_x + BIN_W, y0 + BIN_H, fill=color, outline="")
        self.bin_label = self.canvas.create_text(
            self.bin_x + BIN_W / 2, y0 + BIN_H / 2, text=cat,
            fill="white", font=("Segoe UI", 11, "bold"))

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

        add("<Key-Tab>", lambda e: self.cycle_bin(1))
        add("<Key-Up>", lambda e: self.cycle_bin(-1))
        add("<Key-Down>", lambda e: self.cycle_bin(1))

    def set_move(self, direction, pressed):
        if direction == "left":
            self.move_left = pressed
        else:
            self.move_right = pressed

    def cycle_bin(self, step):
        if not self.started or self.game_over:
            return
        self.bin_index = (self.bin_index + step) % len(BINS)
        self.draw_bin()

    def reset_to_start(self):
        if not self.game_over:
            return
        self.started = False
        self.game_over = False
        self.show_start_screen()

    # ---------- spawning ----------
    def schedule_spawn(self):
        self.spawn_item()
        self.spawn_delay = max(550, self.spawn_delay - 25)
        if self.started and not self.game_over:
            self.spawn_after_id = self.root.after(self.spawn_delay, self.schedule_spawn)

    def spawn_item(self):
        emoji, category = random.choice(ITEMS)
        x = random.randint(40, WIDTH - 40)
        circle_id = self.canvas.create_oval(x - 18, -38, x + 18, -2, fill="white", outline="")
        item_id = self.canvas.create_text(x, -20, text=emoji, font=("Segoe UI Emoji", 22))
        self.items.append({"id": item_id, "circle": circle_id, "x": x, "y": -20, "category": category})
        self.fall_speed = min(6.5, self.fall_speed + 0.03)

    # ---------- loop ----------
    def tick(self):
        if self.started and not self.game_over:
            self.move_bin()
            self.move_items()
            self.update_info()
        self.after_id = self.root.after(FPS_MS, self.tick)

    def move_bin(self):
        dx = (1 if self.move_right else 0) - (1 if self.move_left else 0)
        if dx:
            self.bin_x = min(max(self.bin_x + dx * 6, 0), WIDTH - BIN_W)
            y0 = HEIGHT - BIN_H - 10
            self.canvas.coords(self.bin_rect, self.bin_x, y0, self.bin_x + BIN_W, y0 + BIN_H)
            self.canvas.coords(self.bin_label, self.bin_x + BIN_W / 2, y0 + BIN_H / 2)

    def move_items(self):
        remaining = []
        bin_y0 = HEIGHT - BIN_H - 10
        for it in self.items:
            it["y"] += self.fall_speed
            self.canvas.coords(it["id"], it["x"], it["y"])
            self.canvas.coords(it["circle"], it["x"] - 18, it["y"] - 18, it["x"] + 18, it["y"] + 18)

            if it["y"] >= bin_y0 and it["y"] <= bin_y0 + BIN_H:
                if self.bin_x <= it["x"] <= self.bin_x + BIN_W:
                    self.catch_item(it)
                    continue

            if it["y"] > HEIGHT:
                self.miss_item(it)
                continue

            remaining.append(it)
        self.items = remaining

    def catch_item(self, it):
        self.canvas.delete(it["id"])
        self.canvas.delete(it["circle"])
        correct = it["category"] == BINS[self.bin_index]
        if correct:
            self.score += 10
        else:
            self.lose_life()

    def miss_item(self, it):
        self.canvas.delete(it["id"])
        self.canvas.delete(it["circle"])
        self.lose_life()

    def lose_life(self):
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
            text=f"Game Over!\nFinal Score: {self.score}\nPress R to try again",
            fill=GAME_OVER_COLOR)

    def update_info(self):
        hearts = "\u2665" * self.lives
        self.canvas.itemconfig(
            self.info_text,
            text=f"Score: {self.score}    Lives: {hearts}    (Up/Down or Tab to change bin)")

    def go_back(self):
        self.stop()
        self.on_back()

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