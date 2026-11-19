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
            def randomInt(self, low, high):
        # required function 2: picks a random integer between the min and max for that level
                return random.randint(low, high)

    def decideOperation(self):
        # required function 3: randomly picks addition or subtraction and returns the character
        return random.choice(["+", "-"])

    def start_quiz(self, level):
        # resets the score and question counter for a fresh 10 question run
        self.level = level
        self.q_num = 0
        self.score = 0
        self.history = []
        self.next_question()

    def next_question(self):
        self.after_id = None
        # once all 10 questions are done, jump to the final results screen
        if self.q_num >= NUM_QUESTIONS:
            self.displayResults(self.score)
            return

        self.q_num += 1
        self.tries = 1
        self.locked = False

        name, low, high = LEVELS[self.level]
        num1 = self.randomInt(low, high)
        num2 = self.randomInt(low, high)
        op = self.decideOperation()

        # work out the real answer now so we can check against it on both attempts
        if op == "+":
            self.answer = num1 + num2
        else:
            self.answer = num1 - num2

        self.displayProblem(num1, op, num2)

    def displayProblem(self, num1, op, num2):
        # required function 4: displays the current arithmetic problem and entry box
        self.clear_body()
        self.problem_text = f"{num1} {op} {num2} ="

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text=f"{LEVELS[self.level][0]}  |  Question {self.q_num} of {NUM_QUESTIONS}",
                 font=(FONT, 11, "bold"), bg=BG, fg=PRIMARY).pack(side="left")
        self.score_label = tk.Label(top, text=f"Score: {self.score}", font=(FONT, 11, "bold"),
                                    bg=BG, fg=TEXT)
        self.score_label.pack(side="right")

        # progress bar fills up as the user moves through the 10 questions
        bar = ttk.Progressbar(self.body, maximum=NUM_QUESTIONS, value=self.q_num - 1)
        bar.pack(fill="x", pady=(0, 14))

        card = tk.Frame(self.body, bg=CARD, padx=24, pady=24)
        card.pack(fill="both", expand=True)

        self.tries_label = tk.Label(card, text="Attempt 1 of 2 (10 points)", font=(FONT, 10),
                                    bg=CARD, fg=PRIMARY)
        self.tries_label.pack(pady=(4, 10))

        tk.Label(card, text=self.problem_text, font=(FONT, 36, "bold"),
                 bg=CARD, fg=TEXT).pack(pady=10)

        row = tk.Frame(card, bg=CARD)
        row.pack(pady=12)
        self.entry = tk.Entry(row, font=(FONT, 18), justify="center", width=10, bg=BG,
                              fg=TEXT, insertbackground=TEXT, relief="flat",
                              highlightthickness=2, highlightbackground=SECONDARY,
                              highlightcolor=PRIMARY)
        self.entry.pack(side="left", padx=(0, 10), ipady=5)
        # put the cursor straight into the box so the user can just type without clicking
        self.entry.focus_set()
        # bind the enter key so pressing Return submits the answer just like the button
        self.entry.bind("<Return>", lambda e: self.check_answer())
        self.submit_btn = self.make_button(row, "Submit", self.check_answer)
        self.submit_btn.pack(side="left")

        self.feedback = tk.Label(card, text="Type your answer and hit Enter", font=(FONT, 11, "bold"),
                                 bg=CARD, fg=TEXT, pady=8)
        self.feedback.pack(side="bottom", fill="x")

    def isCorrect(self, user_answer, correct_answer, tries):
        # required function 5: checks the user answer, updates the feedback label and returns a bool
        if user_answer == correct_answer:
            # 10 points on attempt 1, 5 points on attempt 2
            pts = 10 if tries == 1 else 5
            self.feedback.config(text=f"Correct! +{pts} points", fg=PRIMARY)
            return True
        if tries == 1:
            self.feedback.config(text="Not quite, have one more go for 5 points", fg=WRONG)
        else:
            self.feedback.config(text=f"Wrong again, the answer was {correct_answer}", fg=WRONG)
        return False

