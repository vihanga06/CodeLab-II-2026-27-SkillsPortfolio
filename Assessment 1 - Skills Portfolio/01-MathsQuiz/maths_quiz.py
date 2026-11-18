# Exercise 1: Maths Quiz (CodeLab II)
import random
import tkinter as tk
from tkinter import ttk

# colours, picked these by trial and error until they looked ok together
BG = "#FBE4D8"
CARD = "#FFF5EC"
PRIMARY = "#522B5B"
SECONDARY = "#DFB6B2"
TEXT = "#2B124C"
WRONG = "#B3202A"

FONT = "Segoe UI"
NUM_QUESTIONS = 10

# name, min and max for each difficulty level
# keeping the ranges in one dictionary means the menu and randomInt stay in sync
LEVELS = {
    1: ("Easy", 1, 9),
    2: ("Moderate", 10, 99),
    3: ("Advanced", 1000, 9999),
}


# the six function names the brief asks for are camelCase, everything else is normal python style
class MathsQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("760x560")
        self.root.minsize(700, 520)
        self.root.configure(bg=BG)

        # quiz state variables, these get reset every time start_quiz runs
        self.level = 1
        self.q_num = 0
        self.score = 0
        self.tries = 1
        self.answer = 0
        self.locked = False
        self.after_id = None
        self.history = []

        # ttk widgets (the results table and progress bar) ignore normal bg arguments
        # so their colours have to be configured through a ttk Style object
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=TEXT, rowheight=24, font=(FONT, 9))
        style.configure("Treeview.Heading", background=SECONDARY, foreground=TEXT,
                        font=(FONT, 9, "bold"))
        style.map("Treeview", background=[("selected", PRIMARY)],
                  foreground=[("selected", CARD)])
        style.configure("Horizontal.TProgressbar", background=PRIMARY,
                        troughcolor=SECONDARY, bordercolor=BG)

        # header stays packed at the top the whole time, only self.body below it gets cleared
        header = tk.Frame(root, bg=PRIMARY, padx=20, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="Maths Quiz", font=(FONT, 16, "bold"),
                 bg=PRIMARY, fg=CARD).pack(side="left")
        tk.Button(header, text="Quit", font=(FONT, 9, "bold"), bg=SECONDARY, fg=TEXT,
                  activebackground=CARD, relief="flat", padx=12, pady=3, cursor="hand2",
                  command=self.quit_app).pack(side="right")
        tk.Button(header, text="Menu", font=(FONT, 9, "bold"), bg=SECONDARY, fg=TEXT,
                  activebackground=CARD, relief="flat", padx=12, pady=3, cursor="hand2",
                  command=self.displayMenu).pack(side="right", padx=(0, 8))

        # main container frame that gets cleared and redrawn when switching screens
        self.body = tk.Frame(root, bg=BG, padx=24, pady=20)
        self.body.pack(fill="both", expand=True)

        self.displayMenu()

    def clear_body(self):
        # cancel any pending root.after timer first so it cant fire after switching screens
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        for w in self.body.winfo_children():
            w.destroy()

    def quit_app(self):
        # clean up the timer before destroying the window so tkinter doesnt complain
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()

    def make_button(self, parent, text, command, primary=True):
        # helper for buttons so i dont have to repeat the same font and colour options everywhere
        bg = PRIMARY if primary else SECONDARY
        fg = CARD if primary else TEXT
        return tk.Button(parent, text=text, command=command, font=(FONT, 11, "bold"),
                         bg=bg, fg=fg, activebackground=TEXT, activeforeground=CARD,
                         relief="flat", padx=16, pady=7, cursor="hand2")

    def displayMenu(self):
        # required function 1: clears the screen and builds the difficulty level menu
        self.clear_body()

        card = tk.Frame(self.body, bg=CARD, padx=30, pady=24)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="DIFFICULTY LEVEL", font=(FONT, 20, "bold"),
                 bg=CARD, fg=TEXT).pack(pady=(10, 4))
        tk.Label(card, text=f"{NUM_QUESTIONS} questions. 10 points for a first try, 5 for a second try.",
                 font=(FONT, 10), bg=CARD, fg=PRIMARY).pack(pady=(0, 24))

        descriptions = {
            1: "single digit numbers (1 to 9)",
            2: "double digit numbers (10 to 99)",
            3: "four digit numbers (1000 to 9999)",
        }
        for num, (name, low, high) in LEVELS.items():
            row = tk.Frame(card, bg=CARD)
            row.pack(fill="x", padx=60, pady=6)
            # n=num captures the current loop number, otherwise all 3 buttons would pass level 3
            btn = self.make_button(row, f"{num}. {name}", lambda n=num: self.start_quiz(n))
            btn.config(width=14)
            btn.pack(side="left")
            tk.Label(row, text=descriptions[num], font=(FONT, 11), bg=CARD,
                     fg=TEXT).pack(side="left", padx=18)
