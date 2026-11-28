import os
import tkinter as tk
from tkinter import messagebox, ttk

BG = "#F4F0E6"
NAVY = "#12263A"
GOLD = "#F4A261"
WHITE = "#FFFFFF"
INK = "#1B2A38"

GRADES = {
    "A": "#1B7F5C",
    "B": "#1F6F8B",
    "C": "#C77D1A",
    "D": "#C85A32",
    "F": "#B8333A",
}

FIELDS = [
    ("code", "Student code (1000 to 9999)"),
    ("name", "Student name"),
    ("cw1", "Coursework 1 (0 to 20)"),
    ("cw2", "Coursework 2 (0 to 20)"),
    ("cw3", "Coursework 3 (0 to 20)"),
    ("exam", "Exam mark (0 to 100)"),
]


class Student:
    # stores a single student's ID, name and assessment marks
    def __init__(self, code, name, cw1, cw2, cw3, exam):
        self.code = code
        self.name = name
        self.cw1 = cw1
        self.cw2 = cw2
        self.cw3 = cw3
        self.exam = exam

    # returns combined coursework mark out of 60
    def cw_total(self):
        return self.cw1 + self.cw2 + self.cw3

    # returns coursework plus exam score out of 160
    def total(self):
        return self.cw_total() + self.exam

    # calculates overall percentage out of 160 total available marks
    def percentage(self):
        # 60 coursework marks + 100 exam marks = 160 total
        return self.total() / 160 * 100

    # maps the overall percentage to a letter grade from A to F
    def grade(self):
        pct = self.percentage()
        if pct >= 70:
            return "A"
        if pct >= 60:
            return "B"
        if pct >= 50:
            return "C"
        if pct >= 40:
            return "D"
        return "F"

    # formats this record back into a comma separated row for studentMarks.txt
    def to_csv(self):
        return f"{self.code},{self.name},{self.cw1},{self.cw2},{self.cw3},{self.exam}"


class StudentManager:
    # sets up the main dashboard window, loads studentMarks.txt and waits for a menu choice
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager")
        self.root.geometry("1160x730")
        self.root.minsize(1020, 660)
        self.root.configure(bg=BG)

        self.students = []
        self.nav_buttons = []
        self.active_tab = -1

        self.data_file = self.get_data_path()
        if os.path.exists(self.data_file):
            self.load_students()
        else:
            messagebox.showwarning("File missing", "Could not find studentMarks.txt, starting empty.")

        self.configure_ttk()
        self.build_sidebar()
        self.build_main()
        # populate the dropdown only and leave the table blank until a menu button is clicked
        self.combo["values"] = [f"{s.code}  {s.name}" for s in self.students]
        self.heading.config(text="Select a menu option on the left")
        self.summary.config(text="Click '1. View all records' to display student records and class summary.")
        self.legend.config(text="Press '1. View all records' to load overview")

    # looks for studentMarks.txt next to this script first then in the resources folder
    def get_data_path(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local = os.path.join(script_dir, "studentMarks.txt")
        if os.path.exists(local):
            return local
        res = os.path.join(script_dir, "..", "A1 - Resources", "studentMarks.txt")
        if os.path.exists(res):
            return os.path.normpath(res)
        return local

    # applies custom clam theme colours to the Treeview table and Combobox
    def configure_ttk(self):
        style = ttk.Style()
        style.theme_use("clam")

        # workaround for a Windows Tk bug where custom Treeview tag colours dont show up
        def fixed_map(opt):
            return [elm for elm in style.map("Treeview", query_opt=opt)
                    if elm[:2] != ("!disabled", "!selected")]

        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                        foreground=INK, rowheight=30, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", background=NAVY, foreground="#FAF8F3",
                        font=("Segoe UI", 10, "bold"), relief="flat", padding=(8, 7))
        style.map("Treeview",
                  foreground=fixed_map("foreground") + [("selected", INK)],
                  background=fixed_map("background") + [("selected", "#FCE3CC")])
        style.map("Treeview.Heading", background=[("active", "#1E3A56")])
        style.configure("TCombobox", fieldbackground=WHITE, background=BG, foreground=INK)
        style.map("TCombobox", fieldbackground=[("readonly", WHITE)], foreground=[("readonly", INK)])

        self.root.option_add("*TCombobox*Listbox.background", WHITE)
        self.root.option_add("*TCombobox*Listbox.foreground", INK)
        self.root.option_add("*TCombobox*Listbox.selectBackground", GOLD)
        self.root.option_add("*TCombobox*Listbox.selectForeground", INK)

    # parses studentMarks.txt into Student objects and skips malformed rows
    def load_students(self):
        self.students = []
        skipped = 0
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        except OSError as err:
            messagebox.showerror("Load error", f"Could not read studentMarks.txt:\n{err}")
            return

        # skip line 1 when it is just the student count header
        if lines and "," not in lines[0]:
            lines = lines[1:]

        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 6:
                skipped += 1
                continue
            try:
                self.students.append(Student(
                    int(parts[0]), parts[1], int(parts[2]),
                    int(parts[3]), int(parts[4]), int(parts[5])
                ))
            except ValueError:
                skipped += 1

        if skipped:
            messagebox.showwarning("Bad data", f"Skipped {skipped} unreadable line(s).")

    # builds the left navigation sidebar containing all 8 menu options
    def build_sidebar(self):
        side = tk.Frame(self.root, bg=NAVY, width=245, padx=16, pady=20)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text="STUDENT", font=("Segoe UI", 18, "bold"), bg=NAVY, fg="#FAF8F3").pack(anchor="w")
        tk.Label(side, text="MANAGER", font=("Segoe UI", 18, "bold"), bg=NAVY, fg=GOLD).pack(anchor="w")
        tk.Label(side, text="Core & Extension Portal", font=("Segoe UI", 9), bg=NAVY,
                 fg="#8FA7BC").pack(anchor="w", pady=(2, 18))
        tk.Frame(side, bg="#26405A", height=1).pack(fill="x", pady=(0, 14))

        menu = [
            ("1. View all records", self.view_all),
            ("2. View one student", self.view_one),
            ("3. Highest total score", self.show_highest),
            ("4. Lowest total score", self.show_lowest),
            ("5. Sort records", self.sort_dialog),
            ("6. Add a student", self.add_dialog),
            ("7. Delete a student", self.delete_student),
            ("8. Update a student", self.update_dialog),
        ]
        for idx, (label, fn) in enumerate(menu):
            btn = tk.Button(side, text=label, font=("Segoe UI", 10, "bold"), bg=NAVY, fg="#FAF8F3",
                            activebackground=GOLD, activeforeground=INK, anchor="w",
                            relief="flat", bd=0, padx=14, pady=9, cursor="hand2", takefocus=0,
                            command=lambda i=idx, f=fn: self.select_menu(i, f))
            btn.pack(fill="x", pady=3)
            btn.bind("<Enter>", lambda e, b=btn, i=idx: b.config(bg="#1E3A56") if i != self.active_tab else None)
            btn.bind("<Leave>", lambda e, b=btn, i=idx: b.config(bg=NAVY) if i != self.active_tab else None)
            self.nav_buttons.append(btn)

        tk.Button(side, text="Quit Application", font=("Segoe UI", 10, "bold"), bg="#1D354D", fg="#DCE6F0",
                  activebackground="#B8333A", activeforeground="#FAF8F3", relief="flat", bd=0,
                  pady=9, cursor="hand2", command=self.root.destroy).pack(side="bottom", fill="x")

    # highlights the active sidebar button and runs its paired menu callback
    def select_menu(self, idx, fn):
        self.active_tab = idx
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.config(bg=GOLD, fg=INK)
            else:
                btn.config(bg=NAVY, fg="#FAF8F3")
        fn()

    # constructs the right hand dashboard with selector bar, table, grade bar and bottom KPI cards
    def build_main(self):
        main = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        main.pack(side="right", fill="both", expand=True)

        bar = tk.Frame(main, bg=WHITE, highlightthickness=1, highlightbackground="#DDD6C7",
                       padx=14, pady=10)
        bar.pack(fill="x", pady=(0, 12))

        tk.Label(bar, text="Pick student:", font=("Segoe UI", 10, "bold"), bg=WHITE, fg=INK).pack(side="left")
        self.combo = ttk.Combobox(bar, state="readonly", width=26, font=("Segoe UI", 10))
        self.combo.pack(side="left", padx=(8, 16))
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.select_menu(1, self.view_one))

        tk.Label(bar, text="Search name / code:", font=("Segoe UI", 10, "bold"), bg=WHITE, fg=INK).pack(side="left")
        self.search = tk.Entry(bar, width=18, font=("Segoe UI", 10), bg=BG, fg=INK,
                               relief="flat", highlightthickness=1, highlightbackground="#DDD6C7",
                               highlightcolor=NAVY)
        self.search.pack(side="left", padx=8, ipady=4)
        self.search.bind("<Return>", lambda e: self.select_menu(1, self.view_one))

        tk.Button(bar, text="Find", font=("Segoe UI", 10, "bold"), bg=NAVY, fg="#FAF8F3",
                  activebackground=GOLD, activeforeground=INK, relief="flat",
                  padx=14, pady=3, cursor="hand2",
                  command=lambda: self.select_menu(1, self.view_one)).pack(side="left")

        self.heading = tk.Label(main, text="", font=("Segoe UI", 13, "bold"), bg=BG, fg=INK)
        self.heading.pack(anchor="w", pady=(0, 6))

        tbl_card = tk.Frame(main, bg=WHITE, highlightthickness=1, highlightbackground="#DDD6C7",
                            padx=6, pady=6)
        tbl_card.pack(fill="both", expand=True)

        cols = ("name", "code", "cw", "exam", "pct", "grade")
        heads = ("Student Name", "Student Number", "Coursework (/60)",
                 "Exam (/100)", "Overall %", "Grade")
        widths = (200, 120, 130, 110, 100, 70)
        self.table = ttk.Treeview(tbl_card, columns=cols, show="headings")
        for c, h, w in zip(cols, heads, widths):
            self.table.heading(c, text=h, anchor="w" if c == "name" else "center")
            self.table.column(c, width=w, anchor="w" if c == "name" else "center", stretch=True)

        for letter, hex_col in GRADES.items():
            self.table.tag_configure(letter, foreground=hex_col)

        scroll = ttk.Scrollbar(tbl_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.sync_row_to_combo)

        self.summary = tk.Label(main, text="", font=("Segoe UI", 11, "bold"), bg=NAVY,
                                fg="#FAF8F3", pady=9, padx=14, anchor="w")
        self.summary.pack(fill="x", pady=(10, 12))

        dist_card = tk.Frame(main, bg=WHITE, highlightthickness=1, highlightbackground="#DDD6C7",
                             padx=14, pady=9)
        dist_card.pack(fill="x", pady=(0, 10))
        dist_top = tk.Frame(dist_card, bg=WHITE)
        dist_top.pack(fill="x", pady=(0, 5))
        tk.Label(dist_top, text="GRADE DISTRIBUTION", font=("Segoe UI", 8, "bold"),
                 bg=WHITE, fg="#5D6D7E").pack(side="left")
        self.legend = tk.Label(dist_top, text="", font=("Segoe UI", 9, "bold"), bg=WHITE, fg=INK)
        self.legend.pack(side="right")
        self.grade_bar = tk.Canvas(dist_card, height=18, bg=BG, highlightthickness=0)
        self.grade_bar.pack(fill="x")
        self.stats_visible = False
        self.grade_bar.bind("<Configure>", lambda e: self.draw_grade_bar() if self.stats_visible else None)

        # give Highest and Lowest wider columns so long student names dont get cut off
        kpi_row = tk.Frame(main, bg=BG)
        kpi_row.pack(fill="x")
        kpi_row.columnconfigure(0, weight=2)
        kpi_row.columnconfigure(1, weight=2)
        kpi_row.columnconfigure(2, weight=4)
        kpi_row.columnconfigure(3, weight=4)

        self.kpi_count, self.kpi_count_sub = self.make_stat_card(kpi_row, 0, "TOTAL STUDENTS", "--", "waiting", NAVY)
        self.kpi_avg, self.kpi_avg_sub = self.make_stat_card(kpi_row, 1, "CLASS AVERAGE", "--", "waiting", GRADES["A"])
        self.kpi_high, self.kpi_high_sub = self.make_stat_card(kpi_row, 2, "HIGHEST SCORE", "--", "", GRADES["B"])
        self.kpi_low, self.kpi_low_sub = self.make_stat_card(kpi_row, 3, "LOWEST SCORE", "--", "", GRADES["F"])

    # builds one two line stat card with a coloured accent stripe on the left
    def make_stat_card(self, parent, col, title, val, sub, stripe):
        outer = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground="#DDD6C7")
        outer.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0 if col == 3 else 6))
        tk.Frame(outer, bg=stripe, width=5).pack(side="left", fill="y")
        inner = tk.Frame(outer, bg=WHITE, padx=12, pady=10)
        inner.pack(side="left", fill="both", expand=True)
        tk.Label(inner, text=title, font=("Segoe UI", 8, "bold"), bg=WHITE, fg="#5D6D7E").pack(anchor="w")
        v_lbl = tk.Label(inner, text=val, font=("Segoe UI", 12, "bold"), bg=WHITE, fg=INK, anchor="w")
        v_lbl.pack(anchor="w", pady=(3, 0))
        s_lbl = tk.Label(inner, text=sub, font=("Segoe UI", 9), bg=WHITE, fg="#5D6D7E", anchor="w")
        s_lbl.pack(anchor="w", pady=(1, 0))
        return v_lbl, s_lbl

    # draws proportional coloured segments on the canvas for each letter grade present
    def draw_grade_bar(self):
        self.grade_bar.delete("all")
        w = max(self.grade_bar.winfo_width(), 200)
        total = len(self.students)
        if total == 0:
            self.legend.config(text="No students yet")
            return

        counts = {g: 0 for g in ("A", "B", "C", "D", "F")}
        for s in self.students:
            counts[s.grade()] += 1

        self.legend.config(text="   |   ".join(f"{g}: {counts[g]}" for g in ("A", "B", "C", "D", "F") if counts[g]))

        x = 0.0
        for g in ("A", "B", "C", "D", "F"):
            if not counts[g]:
                continue
            seg_w = (counts[g] / total) * w
            self.grade_bar.create_rectangle(x, 0, x + seg_w, 18, fill=GRADES[g], outline="")
            if seg_w >= 26:
                self.grade_bar.create_text(x + seg_w / 2, 9, text=g, fill="#FAF8F3", font=("Segoe UI", 8, "bold"))
            x += seg_w

    # updates the dropdown list, KPI cards and grade distribution bar after any data change
    def refresh_stats(self):
        self.stats_visible = True
        self.combo["values"] = [f"{s.code}  {s.name}" for s in self.students]
        self.combo.set("")

        n = len(self.students)
        self.kpi_count.config(text=str(n))
        self.kpi_count_sub.config(text="student" if n == 1 else "students")
        if n == 0:
            self.kpi_avg.config(text="0.00%")
            self.kpi_avg_sub.config(text="no records")
            self.kpi_high.config(text="None")
            self.kpi_high_sub.config(text="")
            self.kpi_low.config(text="None")
            self.kpi_low_sub.config(text="")
        else:
            avg = sum(s.percentage() for s in self.students) / n
            top = max(self.students, key=lambda s: s.total())
            bot = min(self.students, key=lambda s: s.total())
            self.kpi_avg.config(text=f"{avg:.2f}%")
            self.kpi_avg_sub.config(text="out of 160 marks")
            self.kpi_high.config(text=top.name)
            self.kpi_high_sub.config(text=f"{top.percentage():.1f}%  ({top.total()} / 160)")
            self.kpi_low.config(text=bot.name)
            self.kpi_low_sub.config(text=f"{bot.percentage():.1f}%  ({bot.total()} / 160)")

        self.draw_grade_bar()
