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
