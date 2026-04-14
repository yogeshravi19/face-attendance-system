import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
import os
import csv
import pandas as pd

BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR     = os.path.join(BASE_DIR, "SubjectsDetails")
SUBJECTS_CSV     = os.path.join(SUBJECTS_DIR, "subjects.csv")
ATTENDANCE_DIR   = os.path.join(BASE_DIR, "Attendance")
FIELDNAMES       = ["SubjectName", "FacultyName", "Slot"]

os.makedirs(SUBJECTS_DIR,   exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# ── Ensure CSV exists with header ──
def _ensure_csv():
    if not os.path.exists(SUBJECTS_CSV) or os.path.getsize(SUBJECTS_CSV) == 0:
        with open(SUBJECTS_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()

_ensure_csv()

C = {
    "bg":      "#050511", "surface": "#0A0B1A", "card": "#0D0E20",
    "card2":   "#151733", "glass":   "#0F1126", "border": "#1D1E3A",
    "border2": "#2A2D5C", "white":   "#FFFFFF", "text":   "#E2E8F0",
    "muted":   "#828CA0", "dim":     "#4A5568",
    "blue":    "#2563EB", "cyan":    "#00F0FF", "teal":   "#0AF5C6",
    "green":   "#00FF66", "red":     "#FF003C", "amber":  "#FFB000",
    "purple":  "#9D4EDD", "pink":    "#FF007F",
}
F = {
    "h1":    ("Segoe UI", 20, "bold"),
    "h2":    ("Segoe UI", 15, "bold"),
    "h3":    ("Segoe UI", 12, "bold"),
    "body":  ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "btn":   ("Segoe UI", 12, "bold"),
    "badge": ("Segoe UI", 8,  "bold"),
    "tbl":   ("Segoe UI", 11),
    "tbl_h": ("Segoe UI", 11, "bold"),
}


# ═══════════════════════════════════════════════
#  PUBLIC: load subject list
# ═══════════════════════════════════════════════
def load_subjects():
    _ensure_csv()
    try:
        df = pd.read_csv(SUBJECTS_CSV)
        return df.to_dict("records")
    except Exception:
        return []


# ═══════════════════════════════════════════════
#  PUBLIC: open the Register Subject window
# ═══════════════════════════════════════════════
def open_register_subject():
    win = tk.Toplevel()
    win.title("NexAttend — Register Subject")
    win.geometry("820x580")
    win.configure(bg=C["bg"])
    win.resizable(False, False)
    win.attributes("-topmost", True)

    # ── Header ──
    hdr = tk.Canvas(win, width=820, height=88, bg=C["bg"], highlightthickness=0)
    hdr.pack(fill=X)
    for i in range(88):
        t = i / 88
        r2 = int(0x07 + t * 6); g2 = int(0x09 + t * 8); b2 = int(0x0F + t * 18)
        hdr.create_line(0, i, 820, i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")
    hdr.create_text(410, 30, text="📚  Register Subjects",
                    fill=C["white"], font=F["h1"], anchor="center")
    hdr.create_text(410, 58, text="Add subjects with slot & faculty details — folders auto-created",
                    fill=C["muted"], font=F["small"], anchor="center")
    accent = ["#1B3A6B","#1D4ED8","#3B82F6","#60A5FA","#3B82F6","#1D4ED8","#1B3A6B"]
    sw = 820 // len(accent)
    for i, col in enumerate(accent):
        hdr.create_line(i*sw, 87, (i+1)*sw, 87, fill=col, width=2)

    body = tk.Frame(win, bg=C["bg"])
    body.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # ── Left: Entry Form ──
    left = tk.Frame(body, bg=C["card"], highlightbackground=C["border2"],
                    highlightthickness=1, width=330)
    left.pack(side=LEFT, fill=Y, padx=(0, 10))
    left.pack_propagate(False)

    tk.Label(left, text="ADD NEW SUBJECT", bg=C["card"], fg=C["blue"],
             font=F["badge"]).pack(anchor="w", padx=18, pady=(18, 8))
    tk.Frame(left, bg=C["border"], height=1).pack(fill=X, padx=18, pady=(0, 12))

    fields = {}
    field_defs = [
        ("SUBJECT NAME",  "SubjectName", C["blue"]),
        ("FACULTY NAME",  "FacultyName", C["cyan"]),
        ("SLOT / TIMING", "Slot",        C["teal"]),
    ]

    slot_suggestions = [
        "A1 (Mon 8:00-9:00)", "A2 (Tue 9:00-10:00)", "B1 (Mon 10:00-11:00)",
        "B2 (Wed 11:00-12:00)", "C1 (Thu 12:00-1:00)", "C2 (Fri 1:00-2:00)",
        "D1 (Mon 2:00-3:00)", "D2 (Tue 3:00-4:00)",
    ]

    for lbl, key, col in field_defs:
        tk.Label(left, text=lbl, bg=C["card"], fg=col,
                 font=F["badge"]).pack(anchor="w", padx=18, pady=(0, 3))
        if key == "Slot":
            v = tk.StringVar()
            combo = ttk.Combobox(left, textvariable=v, values=slot_suggestions,
                                 font=("Segoe UI", 13), state="normal")
            style = ttk.Style()
            style.configure("Custom.TCombobox",
                            fieldbackground=C["glass"], background=C["glass"],
                            foreground=C["white"], insertcolor=C["blue"])
            combo["style"] = "Custom.TCombobox"
            combo.pack(fill=X, padx=18, ipady=7, pady=(0, 14))
            fields[key] = v
        else:
            v = tk.StringVar()
            e = tk.Entry(left, textvariable=v, width=28,
                         bd=0, bg=C["glass"], fg=C["white"],
                         insertbackground=col,
                         font=("Segoe UI", 14),
                         highlightthickness=2,
                         highlightcolor=col,
                         highlightbackground=C["border"])
            e.pack(fill=X, padx=18, ipady=8, pady=(0, 14))
            fields[key] = v

    notif = tk.Label(left, text="  ℹ  Fill all fields and click Add Subject",
                     bg=C["glass"], fg=C["muted"],
                     font=F["small"], anchor="w", padx=12, pady=8)
    notif.pack(fill=X, padx=18, pady=(4, 0))

    # ── Right: Subject Table ──
    right = tk.Frame(body, bg=C["surface"], highlightbackground=C["border2"],
                     highlightthickness=1)
    right.pack(side=LEFT, fill=BOTH, expand=True)

    tk.Label(right, text="REGISTERED SUBJECTS", bg=C["surface"],
             fg=C["purple"], font=F["badge"]).pack(anchor="w", padx=16, pady=(14, 4))
    tk.Frame(right, bg=C["border"], height=1).pack(fill=X, padx=16, pady=(0, 8))

    # Treeview table
    tree_frame = tk.Frame(right, bg=C["surface"])
    tree_frame.pack(fill=BOTH, expand=True, padx=16, pady=(0, 10))

    style2 = ttk.Style()
    style2.theme_use("default")
    style2.configure("VM.Treeview",
                     background=C["card"], foreground=C["text"],
                     rowheight=30, fieldbackground=C["card"],
                     bordercolor=C["border"], borderwidth=0,
                     font=F["tbl"])
    style2.configure("VM.Treeview.Heading",
                     background=C["border2"], foreground=C["purple"],
                     font=F["tbl_h"], relief="flat")
    style2.map("VM.Treeview",
               background=[("selected", C["blue"])],
               foreground=[("selected", C["white"])])

    tree = ttk.Treeview(tree_frame, style="VM.Treeview",
                        columns=("Subject", "Faculty", "Slot"),
                        show="headings", selectmode="browse")
    tree.heading("Subject", text="Subject Name")
    tree.heading("Faculty", text="Faculty Name")
    tree.heading("Slot",    text="Slot / Timing")
    tree.column("Subject", width=140, anchor="w")
    tree.column("Faculty", width=140, anchor="w")
    tree.column("Slot",    width=160, anchor="w")

    vsb2 = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=vsb2.set)
    vsb2.pack(side=RIGHT, fill=Y)
    tree.pack(fill=BOTH, expand=True)

    count_lbl = tk.Label(right, text="0 subjects registered",
                         bg=C["surface"], fg=C["muted"], font=F["small"])
    count_lbl.pack(pady=(0, 6))

    def refresh_table():
        tree.delete(*tree.get_children())
        subs = load_subjects()
        for s in subs:
            tree.insert("", END, values=(s.get("SubjectName",""),
                                         s.get("FacultyName",""),
                                         s.get("Slot","")))
        count_lbl.configure(
            text=f"{len(subs)} subject(s) registered",
            fg=C["green"] if subs else C["muted"]
        )

    refresh_table()

    # ── Add Subject ──
    def add_subject():
        sname = fields["SubjectName"].get().strip()
        fname = fields["FacultyName"].get().strip()
        slot  = fields["Slot"].get().strip()

        if not sname or not fname or not slot:
            notif.configure(text="  ⚠  All three fields are required!", fg=C["amber"])
            return

        # Check duplicate
        existing = [s["SubjectName"].lower() for s in load_subjects()]
        if sname.lower() in existing:
            notif.configure(text=f"  ✗  '{sname}' already registered!", fg=C["red"])
            return

        # Write to CSV
        with open(SUBJECTS_CSV, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({"SubjectName": sname, "FacultyName": fname, "Slot": slot})

        # Create Attendance folder
        folder = os.path.join(ATTENDANCE_DIR, sname)
        os.makedirs(folder, exist_ok=True)

        notif.configure(
            text=f"  ✓  '{sname}' added & folder created", fg=C["green"])

        # Clear fields
        for v in fields.values():
            v.set("")
        refresh_table()

    # ── Delete selected ──
    def delete_subject():
        sel = tree.selection()
        if not sel:
            notif.configure(text="  ⚠  Select a subject to delete", fg=C["amber"])
            return
        val = tree.item(sel[0])["values"]
        sname = val[0]
        subs = load_subjects()
        subs = [s for s in subs if s["SubjectName"] != sname]
        with open(SUBJECTS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(subs)
        notif.configure(text=f"  ✓  '{sname}' removed from registry", fg=C["cyan"])
        refresh_table()

    # ── Button Row ──
    btn_row = tk.Frame(left, bg=C["card"])
    btn_row.pack(fill=X, padx=18, pady=14)

    add_btn = tk.Button(btn_row, text="➕  Add Subject",
                        command=add_subject,
                        bg=C["blue"], fg=C["white"],
                        activebackground="#1D4ED8",
                        font=F["btn"], bd=0, padx=16, pady=9, cursor="hand2")
    add_btn.pack(side=LEFT, padx=(0, 8))

    del_btn = tk.Button(btn_row, text="🗑  Remove",
                        command=delete_subject,
                        bg=C["card2"], fg=C["red"],
                        activebackground=C["border2"],
                        font=F["btn"], bd=0, padx=16, pady=9, cursor="hand2",
                        highlightthickness=1, highlightbackground=C["red"])
    del_btn.pack(side=LEFT)

    add_btn.bind("<Enter>", lambda e: add_btn.configure(bg="#1D4ED8"))
    add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=C["blue"]))
