"""
games/climate_quiz.py - Climate Quiz
------------------------------------------
Multiple-choice quiz testing what you learned from the article. Click
an answer button. Score is shown at the end with a short summary.
"""

import tkinter as tk
import random

import theme

WIDTH, HEIGHT = 700, 480

QUESTIONS = [
    {
        "q": "What is the main reason Earth's atmosphere has warmed rapidly\nsince the industrial era?",
        "options": ["Increased greenhouse gases from human activity", "The sun getting hotter",
                    "Volcanic eruptions", "Ocean currents reversing"],
        "answer": 0,
    },
    {
        "q": "Which of these is a greenhouse gas?",
        "options": ["Nitrogen", "Oxygen", "Carbon dioxide", "Argon"],
        "answer": 2,
    },
    {
        "q": "Which of these is a renewable energy source?",
        "options": ["Coal", "Natural gas", "Wind", "Oil"],
        "answer": 2,
    },
    {
        "q": "What effect does deforestation have on climate change?",
        "options": ["It cools the planet", "It reduces CO2 absorption, adding to warming",
                    "It has no effect", "It only affects local wildlife"],
        "answer": 1,
    },
    {
        "q": "Rising global temperatures are linked to which of the following?",
        "options": ["Fewer storms overall", "More stable sea levels",
                    "Melting glaciers and rising sea levels", "Cooler oceans"],
        "answer": 2,
    },
    {
        "q": "Which everyday action helps reduce greenhouse gas emissions?",
        "options": ["Wasting less food", "Leaving lights on all day",
                    "Burning more fuel", "Clearing forests for farmland"],
        "answer": 0,
    },
    {
        "q": "Why is methane from decomposing food waste a climate concern?",
        "options": ["It's harmless", "It's a potent greenhouse gas",
                    "It only affects soil", "It cools the atmosphere"],
        "answer": 1,
    },
    {
        "q": "The greenhouse effect itself is:",
        "options": ["Entirely man-made and harmful", "A myth",
                    "A natural process that human activity has intensified", "Only found on other planets"],
        "answer": 2,
    },
]


class Game:
    def __init__(self, parent, root, on_back):
        self.root = root
        self.on_back = on_back
        self.bind_ids = []

        theme.build_header(parent, "Climate Quiz", self.go_back)

        self.canvas = tk.Canvas(parent, width=WIDTH, height=HEIGHT,
                                 bg=theme.BG_BOARD, highlightthickness=0)
        self.canvas.pack(pady=14)

        self.question_text = self.canvas.create_text(
            WIDTH / 2, 90, fill=theme.TEXT_LIGHT, font=("Segoe UI", 14, "bold"),
            text="", width=600, justify="center")
        self.progress_text = self.canvas.create_text(
            WIDTH / 2, 30, fill=theme.TEXT_MUTED, font=("Segoe UI", 11), text="")
        self.feedback_text = self.canvas.create_text(
            WIDTH / 2, HEIGHT - 40, fill=theme.ACCENT_GREEN,
            font=("Segoe UI", 12, "bold"), text="")

        self.option_buttons = []
        self.btn_window = tk.Frame(self.canvas, bg=theme.BG_BOARD)
        self.canvas.create_window(WIDTH / 2, 280, window=self.btn_window)

        self.order = []
        self.q_index = 0
        self.score = 0
        self.locked = False

        self.bind_keys()
        self.start_quiz()

    def bind_keys(self):
        fid = self.root.bind("<Key-r>", lambda e: self.start_quiz())
        self.bind_ids.append(("<Key-r>", fid))
        fid = self.root.bind("<Key-R>", lambda e: self.start_quiz())
        self.bind_ids.append(("<Key-R>", fid))

    def start_quiz(self):
        self.order = list(range(len(QUESTIONS)))
        random.shuffle(self.order)
        self.q_index = 0
        self.score = 0
        self.canvas.itemconfig(self.feedback_text, text="")
        self.show_question()

    def show_question(self):
        self.locked = False
        for b in self.option_buttons:
            b.destroy()
        self.option_buttons = []

        if self.q_index >= len(self.order):
            self.show_results()
            return

        q = QUESTIONS[self.order[self.q_index]]
        self.canvas.itemconfig(
            self.progress_text, text=f"Question {self.q_index + 1} of {len(self.order)}   |   Score: {self.score}")
        self.canvas.itemconfig(self.question_text, text=q["q"])
        self.canvas.itemconfig(self.feedback_text, text="")

        opts = list(enumerate(q["options"]))
        random.shuffle(opts)
        for orig_idx, text in opts:
            btn = tk.Button(
                self.btn_window, text=text, font=theme.FONT_BODY, wraplength=380,
                fg=theme.TEXT_LIGHT, bg=theme.BUTTON_BG, activebackground=theme.BUTTON_HOVER,
                activeforeground=theme.TEXT_LIGHT, bd=0, padx=14, pady=10, width=40,
                anchor="w", justify="left", cursor="hand2",
                command=lambda oi=orig_idx, b=None: self.answer(oi))
            btn.pack(pady=6)
            self.option_buttons.append(btn)

    def answer(self, chosen_idx):
        if self.locked:
            return
        self.locked = True
        q = QUESTIONS[self.order[self.q_index]]
        correct = chosen_idx == q["answer"]
        if correct:
            self.score += 1
            self.canvas.itemconfig(self.feedback_text, text="Correct!", fill=theme.ACCENT_GREEN)
        else:
            correct_text = q["options"][q["answer"]]
            self.canvas.itemconfig(
                self.feedback_text, text=f"Not quite - the answer was: {correct_text}",
                fill=theme.ACCENT_RED)
        for b in self.option_buttons:
            b.configure(state="disabled")
        self.root.after(1400, self.advance)

    def advance(self):
        self.q_index += 1
        self.show_question()

    def show_results(self):
        for b in self.option_buttons:
            b.destroy()
        self.option_buttons = []
        self.canvas.itemconfig(self.progress_text, text="")
        total = len(self.order)
        pct = round(self.score / total * 100)
        if pct >= 80:
            comment = "Great job - you really absorbed the article!"
        elif pct >= 50:
            comment = "Good effort - worth a re-read for the rest."
        else:
            comment = "Might be worth revisiting the article."
        self.canvas.itemconfig(
            self.question_text,
            text=f"Quiz complete!\n\nScore: {self.score} / {total} ({pct}%)\n\n{comment}")
        self.canvas.itemconfig(self.feedback_text, text="Press R to try again", fill=theme.ACCENT_BLUE)

    def go_back(self):
        self.stop()
        self.on_back()

    def stop(self):
        for b in self.option_buttons:
            b.destroy()
        self.option_buttons = []
        for seq, fid in self.bind_ids:
            self.root.unbind(seq, fid)
        self.bind_ids = []
