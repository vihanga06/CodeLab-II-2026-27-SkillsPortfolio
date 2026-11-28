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
        
# keeps the top dropdown synced whenever the user clicks a row in the table
    def sync_row_to_combo(self, _event):
        sel = self.table.selection()
        if not sel:
            return
        code_val = int(sel[0])
        for i, s in enumerate(self.students):
            if s.code == code_val:
                self.combo.current(i)
                break

    # repopulates the Treeview table and footer summary for whichever menu option ran
    def show_rows(self, rows, title, footer):
        self.heading.config(text=title)
        self.table.delete(*self.table.get_children())
        for s in rows:
            pct = s.percentage()
            g = s.grade()
            self.table.insert("", "end", iid=str(s.code), values=(
                s.name, s.code, f"{s.cw_total()} / 60", f"{s.exam} / 100", f"{pct:.2f}%", g
            ), tags=(g,))
        self.summary.config(text=footer)

    # builds the class total and average percentage string for summary views
    def class_summary(self, rows):
        if not rows:
            return "No students in the class"
        avg = sum(s.percentage() for s in rows) / len(rows)
        return f"Total students in class: {len(rows)}     |     Average percentage mark: {avg:.2f}%"

    # matches digits against student code and text against exact or partial student names
    def find_matches(self, query):
        q = query.lower()
        if q.isascii() and q.isdigit():
            return [s for s in self.students if s.code == int(q)]
        exact = [s for s in self.students if s.name.lower() == q]
        if exact:
            return exact
        return [s for s in self.students if q in s.name.lower()]

    # resolves the target student from search box, dropdown or selected table row
    def pick_student(self):
        q = self.search.get().strip()
        if q:
            hits = self.find_matches(q)
            if not hits:
                messagebox.showwarning("Not found", f"No student matches '{q}'.")
                return None
            if len(hits) > 1:
                names = "\n".join(f"{m.code}  {m.name}" for m in hits)
                messagebox.showwarning("Multiple matches", f"Be more specific or use the code:\n\n{names}")
                return None
            return hits[0]

        idx = self.combo.current()
        if idx >= 0:
            return self.students[idx]

        sel = self.table.selection()
        if sel:
            code_val = int(sel[0])
            for s in self.students:
                if s.code == code_val:
                    return s

        messagebox.showinfo("Pick a student", "Select a student from the dropdown, click a row, or type a name/code.")
        return None

    # menu option 1: displays every student record with class summary and refreshes overview stats
    def view_all(self):
        self.refresh_stats()
        self.show_rows(self.students, "All Student Records", self.class_summary(self.students))

    # menu option 2: displays the single selected student record
    def view_one(self):
        s = self.pick_student()
        if s is None:
            return
        self.search.delete(0, tk.END)
        self.show_rows([s], f"Individual Record: {s.name}",
                       f"Student {s.code}  |  Total: {s.total()} / 160  |  Grade: {s.grade()}")

    # shared helper for highest and lowest scores including tied totals
    def show_extreme(self, highest):
        if not self.students:
            messagebox.showinfo("No students", "There are no student records loaded.")
            return
        totals = [s.total() for s in self.students]
        target = max(totals) if highest else min(totals)
        # keep all tied students if more than one shares the top or bottom total
        rows = [s for s in self.students if s.total() == target]
        word = "Highest" if highest else "Lowest"
        self.show_rows(rows, f"{word} Overall Score",
                       f"{word} total mark: {target} / 160 ({target / 160 * 100:.2f}%)")

    # menu option 3: shows the student with the highest overall total
    def show_highest(self):
        self.show_extreme(True)

    # menu option 4: shows the student with the lowest overall total
    def show_lowest(self):
        self.show_extreme(False)

    # creates a modal Toplevel dialog window that blocks the main window until closed
    def open_popup(self, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=WHITE, padx=24, pady=20)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        return win

    # writes the updated line 1 count and all CSV rows back to studentMarks.txt
    def save_students(self):
        out = [str(len(self.students))] + [s.to_csv() for s in self.students]
        try:
            with open(self.data_file, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(out))
            return True
        except OSError as err:
            messagebox.showerror("Save error", f"Could not save studentMarks.txt:\n{err}")
            return False

    # menu option 5: opens a dialog to sort records ascending or descending
    def sort_dialog(self):
        if not self.students:
            messagebox.showinfo("No students", "There are no student records to sort.")
            return
        win = self.open_popup("Sort Student Records")

        tk.Label(win, text="Sort by:", font=("Segoe UI", 10, "bold"), bg=WHITE, fg=INK).grid(row=0, column=0, sticky="w", pady=6)
        sort_box = ttk.Combobox(win, state="readonly", width=22, font=("Segoe UI", 10),
                                values=["Overall percentage", "Student name", "Student number"])
        sort_box.current(0)
        sort_box.grid(row=0, column=1, padx=(12, 0), pady=6)

        order = tk.StringVar(value="desc")
        tk.Radiobutton(win, text="Ascending", variable=order, value="asc", bg=WHITE, fg=INK,
                       activebackground=WHITE, selectcolor=WHITE, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6)
        tk.Radiobutton(win, text="Descending", variable=order, value="desc", bg=WHITE, fg=INK,
                       activebackground=WHITE, selectcolor=WHITE, font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", padx=(12, 0), pady=6)

        def apply_sort():
            choice = sort_box.current()
            if choice == 0:
                key_fn = lambda s: s.percentage()
            elif choice == 1:
                key_fn = lambda s: s.name.lower()
            else:
                key_fn = lambda s: s.code
            desc = order.get() == "desc"
            rows = sorted(self.students, key=key_fn, reverse=desc)
            self.show_rows(rows, f"Sorted by {sort_box.get()} ({'Descending' if desc else 'Ascending'})",
                           self.class_summary(rows))
            win.destroy()

        btns = tk.Frame(win, bg=WHITE)
        btns.grid(row=2, column=0, columnspan=2, pady=(16, 0))
        tk.Button(btns, text="Apply Sort", command=apply_sort, font=("Segoe UI", 10, "bold"),
                  bg=GOLD, fg=INK, relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btns, text="Cancel", command=win.destroy, font=("Segoe UI", 10, "bold"),
                  bg=NAVY, fg="#FAF8F3", relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)

    # checks one input field for valid ranges, commas or duplicate student codes
    def validate_field(self, key, raw, ignore=None):
        text = raw.strip()
        if key == "name":
            if not text:
                return None, "Student name cannot be empty."
            if "," in text:
                return None, "Student name cannot contain commas because the file is comma separated."
            if not any(ch.isalpha() for ch in text):
                return None, "Student name needs at least one letter."
            return text, ""

        # isascii and isdigit reject underscores like 1_000 that int() would otherwise accept
        if not (text.isascii() and text.isdigit()):
            return None, "Please enter a non negative whole number."
        val = int(text)

        if key == "code":
            if val < 1000 or val > 9999:
                return None, "Student code must be between 1000 and 9999."
            for s in self.students:
                if s.code == val and s is not ignore:
                    return None, f"Student code {val} already belongs to {s.name}."
        elif key == "exam":
            if val > 100:
                return None, "Exam mark must be between 0 and 100."
        elif val > 20:
            return None, "Coursework marks must each be between 0 and 20."
        return val, ""

    # menu option 6: opens a validated form to add a new student and save to file
    def add_dialog(self):
        win = self.open_popup("Add Student Record")
        inputs = {}
        for row, (key, label) in enumerate(FIELDS):
            tk.Label(win, text=label, font=("Segoe UI", 10), bg=WHITE, fg=INK).grid(row=row, column=0, sticky="w", pady=6)
            ent = tk.Entry(win, width=24, font=("Segoe UI", 10), bg=BG, fg=INK, relief="flat",
                           highlightthickness=1, highlightbackground="#DDD6C7", highlightcolor=NAVY)
            ent.grid(row=row, column=1, padx=(14, 0), pady=6, ipady=4)
            inputs[key] = ent
        inputs["code"].focus_set()

        def save_new():
            vals = {}
            for key, _ in FIELDS:
                val, err = self.validate_field(key, inputs[key].get())
                if err:
                    messagebox.showerror("Invalid input", err, parent=win)
                    inputs[key].focus_set()
                    return
                vals[key] = val
            stu = Student(vals["code"], vals["name"], vals["cw1"], vals["cw2"], vals["cw3"], vals["exam"])
            self.students.append(stu)
            # undo the append if writing to disk fails so memory matches the file
            if not self.save_students():
                self.students.pop()
                return
            self.refresh_stats()
            self.view_all()
            self.table.selection_set(str(stu.code))
            self.table.see(str(stu.code))
            win.destroy()
            messagebox.showinfo("Saved", f"{stu.name} ({stu.code}) was added to studentMarks.txt.")

        btns = tk.Frame(win, bg=WHITE)
        btns.grid(row=len(FIELDS), column=0, columnspan=2, pady=(16, 0))
        tk.Button(btns, text="Add Student", command=save_new, font=("Segoe UI", 10, "bold"),
                  bg=GOLD, fg=INK, relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btns, text="Cancel", command=win.destroy, font=("Segoe UI", 10, "bold"),
                  bg=NAVY, fg="#FAF8F3", relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)

    # menu option 7: confirms and deletes the chosen student then updates studentMarks.txt
    def delete_student(self):
        s = self.pick_student()
        if s is None:
            return
        if not messagebox.askyesno("Confirm Delete", f"Permanently delete {s.name} ({s.code}) from studentMarks.txt?"):
            return
        idx = self.students.index(s)
        self.students.remove(s)
        if not self.save_students():
            self.students.insert(idx, s)
            return
        self.search.delete(0, tk.END)
        self.refresh_stats()
        self.view_all()
        messagebox.showinfo("Deleted", f"{s.name} ({s.code}) was removed and studentMarks.txt was updated.")

    # menu option 8: opens a sub menu dialog to edit any single field and save to file
    def update_dialog(self):
        s = self.pick_student()
        if s is None:
            return
        win = self.open_popup(f"Update Record: {s.name}")

        preview = tk.Label(win, text="", font=("Segoe UI", 10, "bold"), bg=BG, fg=INK,
                           justify="left", padx=12, pady=8)
        preview.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        def update_preview():
            preview.config(text=f"{s.name} ({s.code})\n"
                                f"CW1: {s.cw1}   CW2: {s.cw2}   CW3: {s.cw3}   |   Exam: {s.exam}   |   {s.percentage():.2f}% ({s.grade()})")
        update_preview()

        tk.Label(win, text="Field to update:", font=("Segoe UI", 10), bg=WHITE, fg=INK).grid(row=1, column=0, sticky="w", pady=6)
        field_box = ttk.Combobox(win, state="readonly", width=26, font=("Segoe UI", 10),
                                 values=[lbl for _, lbl in FIELDS])
        field_box.current(1)
        field_box.grid(row=1, column=1, padx=(14, 0), pady=6)

        tk.Label(win, text="New value:", font=("Segoe UI", 10), bg=WHITE, fg=INK).grid(row=2, column=0, sticky="w", pady=6)
        val_entry = tk.Entry(win, width=28, font=("Segoe UI", 10), bg=BG, fg=INK, relief="flat",
                             highlightthickness=1, highlightbackground="#DDD6C7", highlightcolor=NAVY)
        val_entry.grid(row=2, column=1, padx=(14, 0), pady=6, ipady=4)
        val_entry.focus_set()

        def apply_change():
            key = FIELDS[field_box.current()][0]
            val, err = self.validate_field(key, val_entry.get(), ignore=s)
            if err:
                messagebox.showerror("Invalid input", err, parent=win)
                return
            old = getattr(s, key)
            setattr(s, key, val)
            if not self.save_students():
                setattr(s, key, old)
                return
            self.search.delete(0, tk.END)
            self.refresh_stats()
            self.show_rows([s], f"Updated Record: {s.name}", f"Changes saved to {os.path.basename(self.data_file)}")
            val_entry.delete(0, tk.END)
            update_preview()

        btns = tk.Frame(win, bg=WHITE)
        btns.grid(row=3, column=0, columnspan=2, pady=(16, 0))
        tk.Button(btns, text="Save Change", command=apply_change, font=("Segoe UI", 10, "bold"),
                  bg=GOLD, fg=INK, relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btns, text="Done", command=win.destroy, font=("Segoe UI", 10, "bold"),
                  bg=NAVY, fg="#FAF8F3", relief="flat", padx=18, pady=7, cursor="hand2").pack(side="left", padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManager(root)
    root.mainloop()
