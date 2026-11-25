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
            
# required brief function: picks a random integer inside the chosen difficulty range
    def randomInt(self, lo, hi):
        return random.randint(lo, hi)

    # required brief function: randomly picks addition or subtraction
    def decideOperation(self):
        return random.choice(["+", "-"])

    # resets quiz counters and kicks off question 1 for the picked difficulty
    def start_quiz(self, level):
        self.level = level
        self.q_num = 0
        self.score = 0
        self.results = []
        self.history = []
        self.next_question()

    # generates the next arithmetic sum or jumps to the results screen after 10 questions
    def next_question(self):
        self.next_timer = None
        if self.q_num >= TOTAL_Q:
            self.displayResults(self.score)
            return

        self.q_num += 1
        self.tries = 1
        self.locked = False

        _, lo, hi = LEVELS[self.level]
        a = self.randomInt(lo, hi)
        b = self.randomInt(lo, hi)
        op = self.decideOperation()
        self.answer = a + b if op == "+" else a - b

        self.displayProblem(a, op, b)

    # required brief function: displays the current problem, progress dots and answer entry
    def displayProblem(self, num1, op, num2):
        self.clear_screen()
        self.screen = "quiz"
        self.problem_text = f"{num1} {op} {num2} ="

        top = tk.Frame(self.body, bg=BOARD, height=42)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text=f"{LEVELS[self.level][0]} level", font=(self.ui_font, 11, "bold"),
                 bg=BOARD, fg="#9FB8A7").pack(side="left")
        self.score_lbl = tk.Label(top, text=f"Score  {self.score}", font=(self.chalk_font, 16, "bold"),
                                  bg=BOARD, fg=YELLOW)
        self.score_lbl.pack(side="right")

        self.dots = tk.Canvas(self.body, width=TOTAL_Q * 40, height=44, bg=BOARD, highlightthickness=0)
        self.dots.pack(pady=(4, 0))
        tk.Label(self.body, text=f"Question {self.q_num} of {TOTAL_Q}", font=(self.ui_font, 10),
                 bg=BOARD, fg="#9FB8A7").pack()

        self.prob_lbl = tk.Label(self.body, text=self.problem_text, font=(self.chalk_font, 54, "bold"),
                                 bg=BOARD, fg=CHALK)
        self.prob_lbl.pack(pady=(22, 8))

        self.ans_row = tk.Frame(self.body, bg=BOARD)
        self.ans_row.pack(pady=6)
        self.entry = tk.Entry(self.ans_row, font=(self.chalk_font, 22, "bold"), width=9, justify="center",
                              bg="#163021", fg=CHALK, insertbackground=YELLOW, relief="flat",
                              disabledbackground="#163021", disabledforeground="#9FB8A7",
                              highlightthickness=2, highlightbackground="#9FB8A7", highlightcolor=YELLOW)
        self.entry.pack(side="left", ipady=6, padx=(0, 12))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.check_answer())

        self.submit_btn = self.make_chalk_btn(self.ans_row, "Check", self.check_answer)
        self.submit_btn.master.pack(side="left")

        self.tries_lbl = tk.Label(self.body, text="", font=(self.ui_font, 11, "bold"), bg=BOARD, fg="#9FB8A7")
        self.tries_lbl.pack(pady=(14, 0))
        self.feedback = tk.Label(self.body, text="Type your answer and press Enter",
                                 font=(self.chalk_font, 15), bg=BOARD, fg=CHALK)
        self.feedback.pack(pady=(8, 0))

        self.refresh_tries()
        self.draw_dots()
        self.pulse_dot()

    # updates the remaining attempts indicator and available marks
    def refresh_tries(self):
        if self.tries == 1:
            self.tries_lbl.config(text="Tries left  \u25cf \u25cf     worth 10 points", fg="#9FB8A7")
        else:
            self.tries_lbl.config(text="Tries left  \u25cf \u25cb     worth 5 points", fg=YELLOW)

    # redraws the 10 progress circles coloured by score earned on each question
    def draw_dots(self):
        self.dots.delete("all")
        fills = {10: "#7FD8BE", 5: YELLOW, 0: PINK}
        for i in range(TOTAL_Q):
            x = 20 + i * 40
            if i < len(self.results):
                self.dots.create_oval(x - 11, 11, x + 11, 33, fill=fills[self.results[i]], outline="")
            elif i == self.q_num - 1:
                r = 14 if self.pulse_big else 11
                self.dots.create_oval(x - r, 22 - r, x + r, 22 + r, outline=YELLOW, width=3)
            else:
                self.dots.create_oval(x - 11, 11, x + 11, 33, outline="#9FB8A7", width=2)

    # toggles the active dot radius every 450ms to give a gentle pulsing effect
    def pulse_dot(self):
        self.pulse_big = not self.pulse_big
        self.draw_dots()
        self.pulse_timer = self.root.after(450, self.pulse_dot)

    # required brief function: checks the answer, updates feedback text and returns a bool
    def isCorrect(self, user_answer, correct_answer, tries):
        if user_answer == correct_answer:
            pts = 10 if tries == 1 else 5
            self.feedback.config(text=f"Correct!  +{pts} points", fg="#7FD8BE")
            return True
        if tries == 1:
            self.feedback.config(text="Not quite, have another go for 5 points", fg=PINK)
        else:
            self.feedback.config(text=f"Unlucky, the answer was {correct_answer}", fg=PINK)
        return False

    # validates integer input and handles first try, second try and wrong outcomes
    def check_answer(self):
        if self.locked:
            return
        try:
            guess = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(text="Numbers only please (minus signs are fine)", fg=PINK)
            self.shake_box()
            return

        if self.isCorrect(guess, self.answer, self.tries):
            self.prob_lbl.config(text=f"{self.problem_text} {self.answer}", fg="#7FD8BE")
            pts = 10 if self.tries == 1 else 5
            self.finish_question(guess, pts, 1000)
        elif self.tries == 1:
            self.tries = 2
            self.refresh_tries()
            self.entry.delete(0, tk.END)
            self.shake_box()
        else:
            self.prob_lbl.config(text=f"{self.problem_text} {self.answer}", fg=PINK)
            self.shake_box()
            self.finish_question(guess, 0, 1800)

    # records points and question history then schedules the next question after a short pause
    def finish_question(self, guess, pts, wait_ms):
        # lock straight away so pressing Enter twice cant award points twice
        self.locked = True
        self.submit_btn.config(state="disabled", bg=BOARD)
        self.entry.config(state="disabled")
        self.score += pts
        self.results.append(pts)
        self.history.append((self.q_num, self.problem_text, guess, self.answer, self.tries, pts))
        self.draw_dots()
        self.pop_score()
        self.next_timer = self.root.after(wait_ms, self.next_question)

    # briefly scales the score label up and back down when points are added
    def pop_score(self, step=0):
        sizes = [16, 20, 24, 21, 18, 16]
        self.score_lbl.config(text=f"Score  {self.score}", font=(self.chalk_font, sizes[step], "bold"))
        if step < len(sizes) - 1:
            self.anim_timer = self.root.after(40, self.pop_score, step + 1)

    # nudges the entry row left and right on invalid or wrong answers
    def shake_box(self, step=0):
        offsets = [16, -16, 12, -12, 6, -6, 0]
        dx = offsets[step]
        self.ans_row.pack_configure(padx=(max(dx, 0) * 2, max(-dx, 0) * 2))
        if step < len(offsets) - 1:
            self.anim_timer = self.root.after(35, self.shake_box, step + 1)

    # maps the final score out of 100 to a letter grade
    def get_rank(self, score):
        if score > 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 50:
            return "D"
        return "F"

    # required brief function: shows the final rank, breakdown table and play again prompt
    def displayResults(self, score):
        self.clear_screen()
        self.screen = "results"
        rank = self.get_rank(score)

        old_best = self.best[self.level]
        new_best = old_best is None or score > old_best
        if new_best:
            self.best[self.level] = score

        first = sum(1 for h in self.history if h[5] == 10)
        second = sum(1 for h in self.history if h[5] == 5)
        missed = TOTAL_Q - first - second
        col = "#7FD8BE" if score >= 70 else YELLOW if score >= 50 else PINK

        self.banner = tk.Canvas(self.body, height=180, bg=BOARD, highlightthickness=0)
        self.banner.pack(fill="x")
        self.banner.create_oval(14, 10, 174, 170, outline=col, width=6)
        self.banner.create_text(94, 90, text=rank, font=(self.chalk_font, 46, "bold"), fill=col)
        self.score_txt = self.banner.create_text(206, 48, anchor="w", text="Final score: 0 / 100",
                                                 font=(self.chalk_font, 24, "bold"), fill=CHALK)
        self.banner.create_text(206, 96, anchor="w", font=(self.ui_font, 12), fill="#9FB8A7",
                                text=f"{first} right first time,  {second} on the second go,  {missed} missed")
        best_msg = (f"New best score for {LEVELS[self.level][0]}!" if new_best
                    else f"Your best on {LEVELS[self.level][0]} is still {self.best[self.level]}")
        self.banner.create_text(206, 132, anchor="w", text=best_msg,
                                font=(self.ui_font, 12, "bold"), fill=YELLOW)

        self.count_score(0, score)
        if score > 90:
            self.next_timer = self.root.after(400, self.drop_confetti)

        cols = ("q", "problem", "yours", "answer", "tries", "pts")
        heads = ("Q", "Question", "Your answer", "Right answer", "Attempts", "Points")
        table = ttk.Treeview(self.body, columns=cols, show="headings", height=10, style="Chalk.Treeview")
        for c, h in zip(cols, heads):
            table.heading(c, text=h)
            table.column(c, anchor="center", width=40 if c == "q" else 110)
        table.tag_configure("full", foreground="#7FD8BE")
        table.tag_configure("half", foreground=YELLOW)
        table.tag_configure("zero", foreground=PINK)
        for row in self.history:
            tag = {10: "full", 5: "half", 0: "zero"}[row[5]]
            table.insert("", "end", values=row, tags=(tag,))
        table.pack(fill="both", expand=True, pady=(6, 12))

        bottom = tk.Frame(self.body, bg=BOARD)
        bottom.pack(fill="x")
        tk.Label(bottom, text="Fancy another round?", font=(self.chalk_font, 16, "bold"),
                 bg=BOARD, fg=CHALK).pack(side="left")
        self.make_chalk_btn(bottom, "Quit", self.close_app, colour=PINK).master.pack(side="right")
        self.make_chalk_btn(bottom, "Change level", self.displayMenu, colour="#9FB8A7").master.pack(side="right", padx=8)
        self.make_chalk_btn(bottom, "Play again", lambda: self.start_quiz(self.level), colour="#7FD8BE").master.pack(side="right")

    # counts the displayed final score up from 0 on the results banner
    def count_score(self, current, target):
        self.banner.itemconfig(self.score_txt, text=f"Final score: {current} / 100")
        if current < target:
            self.anim_timer = self.root.after(14, self.count_score, current + 1, target)

    # spawns coloured chalk confetti pieces across the banner for A+ scores
    def drop_confetti(self):
        w = max(self.banner.winfo_width(), 600)
        bits = []
        for _ in range(70):
            x = random.randint(0, w)
            y = random.randint(-140, 0)
            c = random.choice(["#7FD8BE", YELLOW, PINK, CHALK])
            item = self.banner.create_rectangle(x, y, x + 6, y + 10, fill=c, outline="")
            bits.append((item, random.uniform(2.5, 5), random.uniform(-1.5, 1.5)))
        self.animate_confetti(bits, 0)

    # moves each confetti piece downward until 75 frames have passed then clears them
    def animate_confetti(self, bits, frame):
        for item, speed, drift in bits:
            self.banner.move(item, drift, speed)
        if frame < 75:
            self.next_timer = self.root.after(30, self.animate_confetti, bits, frame + 1)
        else:
            for item, _, _ in bits:
                self.banner.delete(item)


if __name__ == "__main__":
    root = tk.Tk()
    app = MathsQuiz(root)
    root.mainloop()
