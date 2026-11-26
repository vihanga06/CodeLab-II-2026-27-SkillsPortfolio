import io
import math
import os
import random
import struct
import subprocess
import wave
import tkinter as tk
from tkinter import messagebox

# winsound is Windows only so fall back silently on macOS or Linux
try:
    import winsound
except ImportError:
    winsound = None

ECHO_BG = "#1C2229"
ECHO_DARK = "#12161B"
SCREEN = "#FFFFFF"
CYAN = "#00CAFF"
ECHO_BLUE = "#0073B1"


# finds randomJokes.txt and splits each line into a (setup, punchline) tuple
def load_jokes():
    folder = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(folder, "randomJokes.txt"),
        os.path.join(folder, "..", "A1 - Resources", "randomJokes.txt"),
        os.path.join(folder, "A1 - Resources", "randomJokes.txt"),
    ]
    joke_file = None
    for path in candidates:
        if os.path.isfile(path):
            joke_file = path
            break

    if not joke_file:
        messagebox.showerror("Missing file", "Could not find randomJokes.txt")
        return []

    jokes = []
    try:
        with open(joke_file, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if "?" not in line:
                    continue
                # split on the first ? only and reattach it onto the setup
                setup, punchline = line.split("?", 1)
                if punchline.strip():
                    jokes.append((setup.strip() + "?", punchline.strip()))
    except OSError as err:
        messagebox.showerror("Read error", f"Could not read randomJokes.txt:\n{err}")
    return jokes


class AlexaJokeApp:
    # sets up the Echo Show window, shuffled joke deck, chimes and animation timers
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa tell me a Joke")
        self.root.geometry("820x600")
        self.root.minsize(760, 560)
        self.root.configure(bg="#E8EEF3")

        self.jokes = load_jokes()
        random.shuffle(self.jokes)
        self.deck_pos = 0
        self.current = None

        self.sound_on = True
        self.speech_proc = None
        self.ring_active = False
        self.ring_angle = 0
        self.status_text = "STANDBY"

        # keep the ring spin loop and punchline typewriter timer separate so they never stack up
        self.ring_job = None
        self.type_job = None

        self.wake_chime = self.build_chime([(523.25, 95), (783.99, 150)])
        self.punch_chime = self.build_chime([(659.25, 85), (987.77, 150)])

        self.setup_ui()
        self.root.bind("<Return>", lambda e: self.next_joke())
        self.root.bind("<space>", self.on_space)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.spin_ring()

    # builds the Amazon Echo header, light ring canvas, white screen card and four buttons
    def setup_ui(self):
        rim = tk.Frame(self.root, bg=CYAN, padx=2, pady=2)
        rim.pack(fill="both", expand=True, padx=24, pady=20)

        body = tk.Frame(rim, bg=ECHO_BG, padx=26, pady=18)
        body.pack(fill="both", expand=True)

        top_strip = tk.Frame(body, bg=ECHO_BG)
        top_strip.pack(fill="x", pady=(0, 4))

        self.sound_btn = tk.Button(top_strip, text="Sound: ON", command=self.toggle_sound,
                                   font=("Segoe UI", 9, "bold"), bg=ECHO_BLUE, fg="#FFFFFF",
                                   activebackground=CYAN, activeforeground="#161E26",
                                   relief="flat", bd=0, padx=12, pady=4, cursor="hand2", takefocus=0)
        self.sound_btn.pack(side="left")

        total = len(self.jokes)
        self.counter_lbl = tk.Label(top_strip, text=f"Joke 00 / {total:02d}",
                                    font=("Consolas", 10, "bold"), bg=ECHO_DARK,
                                    fg=CYAN, padx=12, pady=4)
        self.counter_lbl.pack(side="right")

        self.ring_canvas = tk.Canvas(body, height=96, bg=ECHO_BG, highlightthickness=0)
        self.ring_canvas.pack(fill="x", pady=(0, 14))
        self.ring_canvas.bind("<Configure>", lambda e: self.draw_ring())
        self.draw_ring()

        screen_rim = tk.Frame(body, bg=ECHO_DARK, padx=3, pady=3)
        screen_rim.pack(fill="both", expand=True, pady=(0, 18))

        shell = tk.Frame(screen_rim, bg=SCREEN)
        shell.pack(fill="both", expand=True)
        self.light_bar = tk.Frame(shell, bg=CYAN, height=5)
        self.light_bar.pack(fill="x")

        screen = tk.Frame(shell, bg=SCREEN, padx=36, pady=20)
        screen.pack(fill="both", expand=True)

        self.badge = tk.Label(screen, text="ALEXA  |  READY", font=("Segoe UI", 9, "bold"),
                              bg="#EAF6FC", fg=ECHO_BLUE, padx=12, pady=4)
        self.badge.pack(pady=(0, 16))

        self.setup_label = tk.Label(screen, text="Press 'Alexa tell me a Joke' below to hear a joke!",
                                    font=("Segoe UI", 19, "bold"), bg=SCREEN, fg="#161E26",
                                    wraplength=600, justify="center")
        self.setup_label.pack(fill="x", pady=(6, 16))

        tk.Frame(screen, bg="#D7E6F0", height=2).pack(fill="x", padx=70, pady=4)

        self.punch_label = tk.Label(screen, text="", font=("Segoe UI", 17, "bold"),
                                    bg=SCREEN, fg=ECHO_BLUE, wraplength=600, justify="center")
        self.punch_label.pack(fill="x", pady=(16, 10))

        tk.Label(screen, text="Shortcuts:   Enter = Next Joke    |    Space = Show Punchline",
                 font=("Segoe UI", 9), bg=SCREEN, fg="#6B7B8C").pack(side="bottom", pady=(4, 0))

        deck = tk.Frame(body, bg=ECHO_BG)
        deck.pack(fill="x")

        self.tell_btn, _ = self.make_key(deck, "Alexa tell me a Joke", self.tell_joke,
                                         "#00B8EA", "#0082A8", "#26D5FF", "#0D161E")
        self.tell_btn.master.pack(side="left", padx=(0, 10))

        self.punch_btn, self.punch_edge = self.make_key(deck, "Show Punchline", self.show_punchline,
                                                        ECHO_BLUE, "#004D78", "#0B88CC", "#FFFFFF")
        self.punch_btn.master.pack(side="left", padx=(0, 10))

        self.next_btn, _ = self.make_key(deck, "Next Joke", self.next_joke,
                                         "#2D3742", "#1B2229", "#3D4B59", "#FFFFFF")
        self.next_btn.master.pack(side="left")

        self.quit_btn, _ = self.make_key(deck, "Quit", self.quit_app,
                                         "#3A434D", "#232930", "#C93B3B", "#FFFFFF")
        self.quit_btn.master.pack(side="right")

        self.set_punch_ready(False)
        if not self.jokes:
            self.tell_btn.config(state="disabled", bg="#2A313A", fg="#677482")
            self.next_btn.config(state="disabled", bg="#2A313A", fg="#677482")
            self.setup_label.config(text="No jokes could be loaded from randomJokes.txt.")

    # builds a hardware style button with a darker bottom lip and hover highlight
    def make_key(self, parent, text, cmd, bg, edge, hover_bg, fg):
        holder = tk.Frame(parent, bg=edge)
        btn = tk.Button(holder, text=text, command=cmd, font=("Segoe UI", 10, "bold"),
                        bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
                        disabledforeground="#677482", relief="flat", bd=0,
                        padx=18, pady=10, cursor="hand2", takefocus=0)
        btn.pack(fill="both", expand=True, pady=(0, 4))

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg) if str(btn["state"]) != "disabled" else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=bg) if str(btn["state"]) != "disabled" else None)
        return btn, holder

    # switches Show Punchline between active blue and muted disabled styling
    def set_punch_ready(self, ready):
        if ready:
            self.punch_btn.config(state="normal", bg=ECHO_BLUE, fg="#FFFFFF")
            self.punch_edge.config(bg="#004D78")
        else:
            self.punch_btn.config(state="disabled", bg="#2A313A", fg="#677482")
            self.punch_edge.config(bg="#1C2127")

    # redraws the Echo speaker mesh dots and the cyan blue light ring
    def draw_ring(self):
        c = self.ring_canvas
        c.delete("all")
        w = max(c.winfo_width(), 720)
        mid = w // 2
        cy = 48

        for row_y in (22, 38, 54, 70):
            for x in range(18, mid - 72, 16):
                c.create_oval(x - 2, row_y - 2, x + 2, row_y + 2, fill="#2A333D", outline="")
            for x in range(mid + 72, w - 18, 16):
                c.create_oval(x - 2, row_y - 2, x + 2, row_y + 2, fill="#2A333D", outline="")

        ring_col = "#004C78" if self.ring_active else "#3C4B59"
        c.create_oval(mid - 38, cy - 38, mid + 38, cy + 38,
                      outline=ring_col, width=6, fill=ECHO_DARK)
        if self.ring_active:
            c.create_arc(mid - 38, cy - 38, mid + 38, cy + 38,
                         start=self.ring_angle, extent=115, style="arc",
                         outline=CYAN, width=6)

        c.create_text(mid, cy - 5, text="alexa", font=("Segoe UI", 14, "bold"), fill="#FFFFFF")
        c.create_text(mid, cy + 14, text=self.status_text, font=("Consolas", 7, "bold"),
                      fill=CYAN if self.ring_active else "#8A99A8")

    # single repeating timer that rotates the cyan arc whenever Alexa is active
    def spin_ring(self):
        if self.ring_active:
            self.ring_angle = (self.ring_angle + 18) % 360
            self.draw_ring()
        self.ring_job = self.root.after(45, self.spin_ring)
