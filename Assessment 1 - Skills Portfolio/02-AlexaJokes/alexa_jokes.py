# Exercise 2: Alexa tell me a Joke (CodeLab II)
import os
import random
import tkinter as tk
from tkinter import messagebox

# colours for this one, dark green with orange and yellow pops
BG = "#1F3A3D"
CARD = "#2E5559"
PRIMARY = "#FF8552"
PUNCH = "#FFE066"
TEXT = "#FFF9EB"

FONT = "Segoe UI"


def find_file(filename):
    # build paths relative to this python file rather than the terminal working directory
    # checks the exercise folder first and then the resources folder so it never fails with FileNotFoundError
    here = os.path.dirname(os.path.abspath(__file__))
    options = [
        os.path.join(here, filename),
        os.path.join(here, "..", "A1 - Resources", filename),
        os.path.join(here, "A1 - Resources", filename),
    ]
    for path in options:
        if os.path.isfile(path):
            return os.path.normpath(path)
    return None


def load_jokes():
    # reads randomJokes.txt and returns a list of (setup, punchline) tuples
    jokes = []
    path = find_file("randomJokes.txt")
    if path is None:
        messagebox.showerror("File missing", "Could not find randomJokes.txt")
        return jokes

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # skip empty lines or any bad line that is missing the question mark separator
                if "?" not in line:
                    continue
                # maxsplit=1 splits on the first ? only, then we attach the ? back onto the setup
                setup, punchline = line.split("?", 1)
                if punchline.strip() == "":
                    continue
                jokes.append((setup.strip() + "?", punchline.strip()))
    except OSError as err:
        messagebox.showerror("Read error", f"Could not read randomJokes.txt:\n{err}")
    return jokes

class JokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa tell me a Joke")
        self.root.geometry("720x500")
        self.root.minsize(640, 460)
        self.root.configure(bg=BG)

        self.jokes = load_jokes()
        # stores the (setup, punchline) tuple currently on screen, starts as None
        self.current = None

        tk.Label(root, text="Alexa", font=(FONT, 22, "bold"), bg=BG,
                 fg=PRIMARY).pack(pady=(18, 0))
        tk.Label(root, text="your very own joke assistant", font=(FONT, 10),
                 bg=BG, fg=TEXT).pack(pady=(0, 12))

        # central card frame holds the setup label on top and punchline label below it
        card = tk.Frame(root, bg=CARD, padx=30, pady=26)
        card.pack(fill="both", expand=True, padx=30)

        # wraplength=580 wraps long setups onto a second line so text never goes off the edge
        self.setup_label = tk.Label(card, text="Press the button to hear a joke",
                                    font=(FONT, 17, "bold"), bg=CARD, fg=TEXT,
                                    wraplength=580, justify="center")
        self.setup_label.pack(pady=(20, 18))

        # punchline label starts blank and only gets filled when Show Punchline is clicked
        self.punch_label = tk.Label(card, text="", font=(FONT, 15, "bold"), bg=CARD,
                                    fg=PUNCH, wraplength=580, justify="center")
        self.punch_label.pack(pady=10)

        # bottom row with the four buttons required by the brief
        buttons = tk.Frame(root, bg=BG)
        buttons.pack(fill="x", padx=30, pady=18)

        self.tell_btn = self.make_button(buttons, "Alexa tell me a Joke", self.tell_joke, True)
        self.tell_btn.pack(side="left", padx=(0, 8))
        self.punch_btn = self.make_button(buttons, "Show Punchline", self.show_punchline, False)
        self.punch_btn.pack(side="left", padx=(0, 8))
        # Next Joke calls tell_joke as well because both pick a new random joke
        self.next_btn = self.make_button(buttons, "Next Joke", self.tell_joke, False)
        self.next_btn.pack(side="left")
        self.make_button(buttons, "Quit", root.destroy, False).pack(side="right")

        # keep Show Punchline disabled until the user actually asks for a joke
        self.punch_btn.config(state="disabled")
        # if the text file was missing or empty, disable the joke buttons so random.choice cant crash
        if not self.jokes:
            self.tell_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            self.setup_label.config(text="No jokes loaded")

