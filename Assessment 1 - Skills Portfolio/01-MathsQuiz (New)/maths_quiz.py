import random
import tkinter as tk
from tkinter import messagebox, ttk

WOOD = "#7A4E2D"
BOARD = "#1E3A2B"
CHALK = "#F4F1E8"
YELLOW = "#F6D365"
PINK = "#F28B82"

TOTAL_Q = 10

LEVELS = {
    1: ("Easy", 1, 9),
    2: ("Moderate", 10, 99),
    3: ("Advanced", 1000, 9999),
}


class MathsQuiz:
    # sets up the main chalkboard window, header bar and initial quiz state
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("880x690")
        self.root.minsize(840, 670)
        self.root.configure(bg=WOOD)

        self.chalk_font = "Segoe Print"
        self.ui_font = "Segoe UI"

        self.level = 1
        self.q_num = 0
        self.score = 0
        self.tries = 1
        self.answer = 0
        self.problem_text = ""
        self.locked = False
        self.results = []
        self.history = []
        self.best = {1: None, 2: None, 3: None}
        self.screen = "menu"
        self.pulse_big = False

        # separate timer ids so we can cancel each after() loop cleanly when switching screens
        self.next_timer = None
        self.pulse_timer = None
        self.anim_timer = None

        # ttk Treeview needs a style because it ignores standard tk bg options
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Chalk.Treeview", background="#163021", fieldbackground="#163021",
                        foreground=CHALK, rowheight=23, font=(self.ui_font, 10), borderwidth=0)
        style.configure("Chalk.Treeview.Heading", background=WOOD, foreground=CHALK,
                        font=(self.ui_font, 10, "bold"), relief="flat")
        style.map("Chalk.Treeview", background=[("selected", WOOD)], foreground=[("selected", CHALK)])
        style.map("Chalk.Treeview.Heading", background=[("active", WOOD)])

        # outer padding lets the wood frame colour show around the green board
        self.board = tk.Frame(root, bg=BOARD, padx=28, pady=18)
        self.board.pack(fill="both", expand=True, padx=14, pady=14)

        header = tk.Frame(self.board, bg=BOARD)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1, uniform="hdr")
        header.columnconfigure(1, weight=2)
        header.columnconfigure(2, weight=1, uniform="hdr")

        self.back_btn = self.make_chalk_btn(header, "Back", self.go_back, small=True)
        self.back_btn.master.grid(row=0, column=0, sticky="w")

        tk.Label(header, text="Maths Quiz", font=(self.chalk_font, 22, "bold"),
                 bg=BOARD, fg=CHALK).grid(row=0, column=1)

        quit_btn = self.make_chalk_btn(header, "Quit", self.close_app, small=True, colour=PINK)
        quit_btn.master.grid(row=0, column=2, sticky="e")

        tk.Frame(self.board, bg="#9FB8A7", height=2).pack(fill="x", pady=(8, 14))

        self.body = tk.Frame(self.board, bg=BOARD)
        self.body.pack(fill="both", expand=True)

        self.root.bind("<Key>", self.handle_key)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.displayMenu()

    # cancels any active after() callbacks before destroying widgets or quitting
    def stop_timers(self):
        for attr in ("next_timer", "pulse_timer", "anim_timer"):
            job = getattr(self, attr)
            if job is not None:
                self.root.after_cancel(job)
                setattr(self, attr, None)

    # wipes the body frame so the next screen can be drawn in its place
    def clear_screen(self):
        self.stop_timers()
        for w in self.body.winfo_children():
            w.destroy()

    # stops timers cleanly and closes the application window
    def close_app(self):
        self.stop_timers()
        self.root.destroy()

    # asks for confirmation mid quiz before returning to the difficulty menu
    def go_back(self):
        if self.screen == "quiz":
            if not messagebox.askyesno("Leave quiz?", "Return to the menu? Current progress will be lost."):
                return
        self.displayMenu()

    # creates a chalk outlined button with a hover fill effect
    def make_chalk_btn(self, parent, text, cmd, small=False, colour=YELLOW):
        # wrapping in a 2px frame draws a crisp border on Windows since button highlight borders get ignored
        wrap = tk.Frame(parent, bg=colour, padx=2, pady=2)
        btn = tk.Button(wrap, text=text, command=cmd, font=(self.ui_font, 10 if small else 13, "bold"),
                        bg=BOARD, fg=colour, activebackground=colour, activeforeground=BOARD,
                        disabledforeground="#9FB8A7", relief="flat", bd=0,
                        padx=14 if small else 24, pady=4 if small else 9, cursor="hand2", takefocus=0)
        btn.pack(fill="both", expand=True)

        def on_enter(_e):
            if str(btn["state"]) != "disabled":
                btn.config(bg=colour, fg=BOARD)

        def on_leave(_e):
            if str(btn["state"]) != "disabled":
                btn.config(bg=BOARD, fg=colour)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # lets the player press 1, 2 or 3 on the menu to start a level quickly
    def handle_key(self, event):
        if self.screen == "menu" and event.char in ("1", "2", "3"):
            self.start_quiz(int(event.char))

    # required brief function: draws the difficulty selection menu
    def displayMenu(self):
        self.clear_screen()
        self.screen = "menu"

        tk.Label(self.body, text="DIFFICULTY LEVEL", font=(self.chalk_font, 28, "bold"),
                 bg=BOARD, fg=YELLOW).pack(pady=(6, 0))
        tk.Label(self.body, text=f"{TOTAL_Q} questions a round.  10 points first try, 5 points second try.",
                 font=(self.ui_font, 11), bg=BOARD, fg="#9FB8A7").pack()
        tk.Label(self.body, text="Click a level or press 1, 2 or 3 on the keyboard",
                 font=(self.ui_font, 10, "italic"), bg=BOARD, fg="#9FB8A7").pack(pady=(2, 22))

        row = tk.Frame(self.body, bg=BOARD)
        row.pack(fill="both", expand=True, pady=(0, 10))
        examples = {1: "4 + 7 =", 2: "45 + 19 =", 3: "4210 - 1875 ="}
        colours = {1: "#7FD8BE", 2: YELLOW, 3: PINK}

        for num, (name, lo, hi) in LEVELS.items():
            row.columnconfigure(num - 1, weight=1, uniform="lvl")
            self.build_level_card(row, num, name, lo, hi, examples[num], colours[num])

    # builds one clickable difficulty card with hover darkening and best score
    def build_level_card(self, parent, num, name, lo, hi, example, colour):
        card = tk.Frame(parent, bg=BOARD, highlightthickness=2, highlightbackground=colour,
                        padx=16, pady=18, cursor="hand2")
        card.grid(row=0, column=num - 1, sticky="nsew", padx=8)

        best = self.best[num]
        best_str = f"Best: {best} / 100" if best is not None else "Best: not played yet"
        labels = [
            tk.Label(card, text=str(num), font=(self.chalk_font, 40, "bold"), fg=colour),
            tk.Label(card, text=name, font=(self.ui_font, 17, "bold"), fg=CHALK),
            tk.Label(card, text=f"numbers from {lo} to {hi}", font=(self.ui_font, 10), fg="#9FB8A7"),
            tk.Label(card, text=example, font=(self.chalk_font, 15), fg=CHALK),
            tk.Label(card, text=best_str, font=(self.ui_font, 10, "bold"), fg=colour),
        ]
        for lbl in labels:
            lbl.config(bg=BOARD, cursor="hand2")
            lbl.pack(pady=(0, 8))

        # n=num binds each loop number so every button starts its own level
        self.make_chalk_btn(card, "Start", lambda n=num: self.start_quiz(n), colour=colour).master.pack(pady=(8, 0))

        def set_bg(bg):
            card.config(bg=bg)
            for lbl in labels:
                lbl.config(bg=bg)

        for w in [card] + labels:
            w.bind("<Button-1>", lambda e, n=num: self.start_quiz(n))
            w.bind("<Enter>", lambda e: set_bg("#163021"))
            w.bind("<Leave>", lambda e: set_bg(BOARD))
