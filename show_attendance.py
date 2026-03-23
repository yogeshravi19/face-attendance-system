import pandas as pd
from glob import glob
import os
import csv
import tkinter as tk
from tkinter import *

# ══════════════════════════════════
#  VisioMark Design System
# ══════════════════════════════════
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
    "body":  ("Segoe UI", 11),
    "small": ("Segoe UI", 10),
    "btn":   ("Segoe UI", 12, "bold"),
    "badge": ("Segoe UI", 8, "bold"),
    "mono":  ("Consolas", 11),
}

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
attendance_path = os.path.join(BASE_DIR, "Attendance")


def rrect(canvas, x1, y1, x2, y2, r=12, **kw):
    pts = [
        x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
        x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
        x1, y2, x1, y2-r, x1, y1+r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


def subjectchoose(text_to_speech):

    def _load_subjects():
        csv_path = os.path.join(BASE_DIR, "SubjectsDetails", "subjects.csv")
        subjects = []
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                subjects = df.to_dict("records")
            except Exception:
                pass
        return subjects

    # ── Main Window ──
    win = tk.Toplevel()
    win.title("NexAttend — Attendance Records")
    win.geometry("680x480")
    win.resizable(False, True)
    win.configure(bg=C["bg"])
    win.attributes("-topmost", True)

    def _get_selected_subject():
        sel = tree.selection()
        if sel:
            return tree.item(sel[0])["values"][0]
        return ""

    def calculate_attendance():
        Subject = _get_selected_subject()
        if not Subject:
            notif.configure(text="  ⚠  Please select a subject from the list", fg=C["amber"])
            text_to_speech("Please select a subject")
            return

        subject_path = os.path.join(attendance_path, Subject)
        if not os.path.exists(subject_path):
            notif.configure(text="  ✗  No records found for this subject", fg=C["red"])
            return

        try:
            filenames = glob(os.path.join(subject_path, f"{Subject}*.csv"))
            if not filenames:
                notif.configure(text="  ✗  No attendance CSV files found", fg=C["red"])
                return

            df     = [pd.read_csv(f) for f in filenames]
            newdf  = df[0]
            for i in range(1, len(df)):
                newdf = newdf.merge(df[i], how="outer")
            newdf.fillna(0, inplace=True)

            # Pandas 3.0 safe vectorised assignment
            newdf["Attendance"] = (
                newdf.iloc[:, 2:].mean(axis=1).mul(100).round().astype(int).astype(str) + "%"
            )

            output_csv = os.path.join(subject_path, "attendance.csv")
            newdf.to_csv(output_csv, index=False)

            notif.configure(text=f"  ✓  Report generated for {Subject}", fg=C["green"])
            _show_report(win, Subject, output_csv, newdf)

        except Exception as ex:
            notif.configure(text=f"  ✗  Error: {str(ex)[:55]}", fg=C["red"])

    # Header
    hdr = tk.Canvas(win, width=680, height=88, bg=C["bg"], highlightthickness=0)
    hdr.pack(fill=X)
    for i in range(88):
        t = i / 88
        r2 = int(0x07 + t * 6); g2 = int(0x09 + t * 8); b2 = int(0x0F + t * 18)
        hdr.create_line(0, i, 680, i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")
    hdr.create_text(340, 32, text="📊  View Attendance Records",
                    fill=C["white"], font=F["h1"], anchor="center")
    hdr.create_text(340, 60, text="Merged report with % attendance  ·  color-coded analysis",
                    fill=C["muted"], font=F["small"], anchor="center")
    for i, col in enumerate(["#2D1B69","#5B21B6","#7C3AED","#8B5CF6","#A78BFA",
                              "#8B5CF6","#7C3AED","#5B21B6","#2D1B69"]):
        sx = i * (680 // 9)
        hdr.create_line(sx, 87, sx + 680//9, 87, fill=col, width=2)

    # ── Subject Picker Card ──
    import tkinter.ttk as ttk
    pick_frame = tk.Frame(win, bg=C["card"],
                          highlightbackground=C["border2"],
                          highlightthickness=1)
    pick_frame.pack(fill=BOTH, expand=True, padx=24, pady=12)

    top_row = tk.Frame(pick_frame, bg=C["card"])
    top_row.pack(fill=X, padx=14, pady=(12, 4))
    tk.Label(top_row, text="SELECT SUBJECT", bg=C["card"],
             fg=C["purple"], font=F["badge"]).pack(side=LEFT)

    def refresh_list():
        tree.delete(*tree.get_children())
        subs = _load_subjects()
        for s in subs:
            tree.insert("", END, values=(s.get("SubjectName", ""),
                                         s.get("FacultyName", ""),
                                         s.get("Slot", "")))
        if not subs:
            notif.configure(
                text="  ⚠  No subjects registered yet — use 'Register Subject' first",
                fg=C["amber"])

    ref_btn = tk.Button(top_row, text="↻  Refresh",
                        command=refresh_list,
                        bg=C["card2"], fg=C["muted"],
                        font=("Segoe UI", 9, "bold"), bd=0,
                        padx=10, pady=3, cursor="hand2")
    ref_btn.pack(side=RIGHT)

    # Treeview
    style = ttk.Style()
    style.theme_use("default")
    style.configure("View.Treeview",
                     background=C["glass"], foreground=C["text"],
                     rowheight=32, fieldbackground=C["glass"],
                     bordercolor=C["border"], borderwidth=0,
                     font=("Segoe UI", 11))
    style.configure("View.Treeview.Heading",
                     background=C["border2"], foreground=C["purple"],
                     font=("Segoe UI", 11, "bold"), relief="flat")
    style.map("View.Treeview",
              background=[("selected", C["purple"])],
              foreground=[("selected", C["white"])])

    tree_wrap = tk.Frame(pick_frame, bg=C["card"])
    tree_wrap.pack(fill=BOTH, expand=True, padx=14, pady=(0, 8))

    tree = ttk.Treeview(tree_wrap, style="View.Treeview",
                        columns=("Subject", "Faculty", "Slot"),
                        show="headings", selectmode="browse", height=5)
    tree.heading("Subject", text="Subject Name")
    tree.heading("Faculty", text="Faculty Name")
    tree.heading("Slot",    text="Slot / Timing")
    tree.column("Subject", width=180, anchor="w")
    tree.column("Faculty", width=180, anchor="w")
    tree.column("Slot",    width=240, anchor="w")

    vsb_t = ttk.Scrollbar(tree_wrap, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=vsb_t.set)
    vsb_t.pack(side=RIGHT, fill=Y)
    tree.pack(fill=BOTH, expand=True)

    # Selected subject label
    sel_frame = tk.Frame(pick_frame, bg=C["card"])
    sel_frame.pack(fill=X, padx=14, pady=(0, 4))
    tk.Label(sel_frame, text="SELECTED:", bg=C["card"],
             fg=C["muted"], font=F["badge"]).pack(side=LEFT)
    sel_lbl = tk.Label(sel_frame, text="  — none —",
                       bg=C["card2"], fg=C["cyan"],
                       font=("Segoe UI", 11, "bold"), padx=10, pady=3)
    sel_lbl.pack(side=LEFT, padx=6)

    def on_select(e):
        sel = tree.selection()
        if sel:
            val = tree.item(sel[0])["values"]
            sel_lbl.configure(text=f"  {val[0]}  ·  {val[1]}")

    tree.bind("<<TreeviewSelect>>", on_select)
    tree.bind("<Double-1>", lambda e: calculate_attendance())


    notif = tk.Label(win, text="  ℹ  Select subject and click View Attendance",
                     bg=C["bg"], fg=C["muted"],
                     font=F["small"], anchor="w", padx=14, pady=4)
    notif.pack(fill=X, padx=32, pady=(0, 6))

    refresh_list()

    # Buttons
    btn_row = tk.Frame(win, bg=C["bg"])
    btn_row.pack(pady=(0, 10))

    def _hover(btn, on_col, off_col):
        btn.bind("<Enter>", lambda e: btn.configure(bg=on_col))
        btn.bind("<Leave>", lambda e: btn.configure(bg=off_col))

    view_btn = tk.Button(btn_row, text="📊  View Attendance",
                         command=calculate_attendance,
                         bg=C["purple"], fg=C["white"],
                         activebackground="#6D28D9", font=F["btn"],
                         bd=0, padx=24, pady=10, cursor="hand2")
    view_btn.grid(row=0, column=0, padx=8)
    _hover(view_btn, "#6D28D9", C["purple"])

    def open_folder():
        sub = _get_selected_subject()
        target = os.path.join(attendance_path, sub)
        if sub and os.path.exists(target):
            os.startfile(target)
        else:
            notif.configure(text="  ✗  No records found for selected subject", fg=C["red"])

    folder_btn = tk.Button(btn_row, text="📂  Open Folder",
                           command=open_folder,
                           bg=C["card"], fg=C["text"],
                           activebackground=C["card2"], font=F["h3"],
                           bd=0, padx=24, pady=10, cursor="hand2",
                           highlightthickness=1, highlightbackground=C["border"])
    folder_btn.grid(row=0, column=1, padx=8)
    _hover(folder_btn, C["card2"], C["card"])



def _show_report(parent, subject, csv_path, newdf):
    """Premium attendance report popup with analytics header."""
    popup = tk.Toplevel(parent)
    popup.title(f"NexAttend — {subject} Report")
    popup.configure(bg=C["bg"])
    popup.attributes("-topmost", True)
    popup.resizable(True, True)

    # ── Stats Header ──
    n_students = len(newdf)
    try:
        pcts = newdf["Attendance"].str.replace("%", "").astype(int)
        avg_att   = pcts.mean()
        above_75  = (pcts >= 75).sum()
        below_75  = (pcts < 75).sum()
    except Exception:
        avg_att = above_75 = below_75 = 0

    hdr2 = tk.Canvas(popup, width=800, height=100, bg=C["bg"], highlightthickness=0)
    hdr2.pack(fill=X)
    for i in range(100):
        t = i/100
        r2=int(0x07+t*6); g2=int(0x09+t*8); b2=int(0x0F+t*18)
        hdr2.create_line(0,i,800,i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")
    hdr2.create_text(24, 32, text=f"📋  {subject.upper()} — Attendance Report",
                     fill=C["white"], font=F["h2"], anchor="w")
    hdr2.create_text(24, 62, text=f"{n_students} students  ·  Avg: {avg_att:.0f}%  ·  "
                     f"≥75%: {above_75}  ·  <75%: {below_75}",
                     fill=C["muted"], font=F["small"], anchor="w")
    # Accent
    for i, col in enumerate(["#2D1B69","#5B21B6","#7C3AED","#8B5CF6","#7C3AED","#5B21B6","#2D1B69"]):
        sx = i * (800//7)
        hdr2.create_line(sx, 99, sx+800//7, 99, fill=col, width=2)

    # Mini stat badges
    badge_data = [
        (660, f"{n_students}", "STUDENTS"),
        (720, f"{avg_att:.0f}%", "AVG ATT."),
        (780, f"{above_75}", "≥75%"),
    ]
    for bx, bv, bl in badge_data:
        hdr2.create_text(bx, 30, text=bv, fill=C["purple"], font=("Segoe UI", 16, "bold"))
        hdr2.create_text(bx, 52, text=bl, fill=C["muted"], font=("Segoe UI", 7))

    tk.Frame(popup, bg=C["border"], height=1).pack(fill=X)

    # ── Scrollable Table ──
    wrap = tk.Frame(popup, bg=C["bg"])
    wrap.pack(fill=BOTH, expand=True, padx=16, pady=12)

    vsb = tk.Scrollbar(wrap, orient=VERTICAL, bg=C["surface"])
    hsb = tk.Scrollbar(wrap, orient=HORIZONTAL, bg=C["surface"])
    cnv = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0,
                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.configure(command=cnv.yview)
    hsb.configure(command=cnv.xview)
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    cnv.pack(side=LEFT, fill=BOTH, expand=True)

    tf = tk.Frame(cnv, bg=C["bg"])
    tf.bind("<Configure>", lambda e: cnv.configure(scrollregion=cnv.bbox("all")))
    cnv.create_window((0, 0), window=tf, anchor="nw")

    try:
        with open(csv_path, newline="") as f:
            rows = list(csv.reader(f))

        for r, row in enumerate(rows):
            is_hdr = (r == 0)
            for c, cell in enumerate(row):
                if is_hdr:
                    bg2 = C["border2"]; fg2 = C["purple"]; fn = F["h3"]
                else:
                    bg2 = C["card"] if r % 2 == 0 else C["glass"]
                    fg2 = C["text"]; fn = F["body"]
                    # Color last column (Attendance %)
                    if c == len(row) - 1 and "%" in str(cell):
                        try:
                            pct = int(cell.replace("%", ""))
                            fg2 = C["green"] if pct >= 75 else C["amber"] if pct >= 50 else C["red"]
                            fn  = F["h3"]
                        except Exception:
                            pass

                label = tk.Label(tf, text=cell, width=16, height=1,
                                 bg=bg2, fg=fg2, font=fn,
                                 padx=10, pady=6, relief=FLAT)
                label.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
    except Exception as ex:
        tk.Label(tf, text=f"Error reading file: {ex}", bg=C["bg"],
                 fg=C["red"], font=F["body"]).pack()

    # Close
    tk.Button(popup, text="✓  Close Report",
              command=popup.destroy,
              bg=C["purple"], fg=C["white"],
              activebackground="#6D28D9",
              font=F["btn"], bd=0, padx=28, pady=10,
              cursor="hand2").pack(pady=(4, 14))
