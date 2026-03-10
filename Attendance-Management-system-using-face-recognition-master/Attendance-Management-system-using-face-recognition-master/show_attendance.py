import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *

# ═══════════════════════════════════════════════════════════════
#  COLORS — Match main window theme
# ═══════════════════════════════════════════════════════════════
COLORS = {
    "bg_dark":       "#0d1117",
    "bg_card":       "#161b22",
    "bg_card_hover": "#1c2333",
    "accent_cyan":   "#00b4d8",
    "accent_green":  "#00c853",
    "accent_purple": "#7c4dff",
    "accent_red":    "#f85149",
    "accent_amber":  "#ffb300",
    "text_primary":  "#e6edf3",
    "text_secondary":"#8b949e",
    "text_muted":    "#484f58",
    "border":        "#30363d",
    "success":       "#3fb950",
}

FONTS = {
    "heading":     ("Segoe UI", 20, "bold"),
    "body":        ("Segoe UI", 13),
    "body_bold":   ("Segoe UI", 13, "bold"),
    "small":       ("Segoe UI", 11),
    "button":      ("Segoe UI", 14, "bold"),
    "table":       ("Segoe UI", 11),
    "table_head":  ("Segoe UI", 11, "bold"),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
attendance_path = os.path.join(BASE_DIR, "Attendance")


def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject == "":
            t = "Please enter the subject name."
            text_to_speech(t)
            notif.configure(text="  ⚠  " + t, fg=COLORS["accent_amber"])
            return

        subject_path = os.path.join(attendance_path, Subject)
        if not os.path.exists(subject_path):
            notif.configure(text="  ✗  No records found for this subject",
                            fg=COLORS["accent_red"])
            return

        try:
            filenames = glob(os.path.join(subject_path, f"{Subject}*.csv"))
            if not filenames:
                notif.configure(text="  ✗  No CSV files found for this subject",
                                fg=COLORS["accent_red"])
                return

            df = [pd.read_csv(f) for f in filenames]
            newdf = df[0]
            for i in range(1, len(df)):
                newdf = newdf.merge(df[i], how="outer")
            newdf.fillna(0, inplace=True)
            newdf["Attendance"] = 0
            for i in range(len(newdf)):
                newdf["Attendance"].iloc[i] = str(int(round(newdf.iloc[i, 2:-1].mean() * 100))) + '%'

            output_csv = os.path.join(subject_path, "attendance.csv")
            newdf.to_csv(output_csv, index=False)

            # ─── Show styled table ───
            root = tk.Toplevel()
            root.title(f"Attendance Report — {Subject}")
            root.configure(background=COLORS["bg_dark"])
            root.attributes("-topmost", True)
            root.minsize(500, 300)

            # Header
            header = tk.Frame(root, bg=COLORS["bg_dark"])
            header.pack(fill=X, padx=20, pady=(15, 5))

            tk.Label(header, text=f"📊  Attendance Report",
                     bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                     font=FONTS["heading"]).pack(side=LEFT)

            tk.Label(header, text=Subject.upper(),
                     bg=COLORS["accent_purple"], fg="#ffffff",
                     font=("Segoe UI", 10, "bold"),
                     padx=12, pady=3).pack(side=RIGHT)

            # Separator
            tk.Frame(root, bg=COLORS["border"], height=1).pack(fill=X, padx=20, pady=10)

            # Scrollable table
            table_container = tk.Frame(root, bg=COLORS["bg_dark"])
            table_container.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

            canvas = tk.Canvas(table_container, bg=COLORS["bg_dark"],
                               highlightthickness=0)
            scrollbar_y = tk.Scrollbar(table_container, orient=VERTICAL,
                                       command=canvas.yview)
            scrollbar_x = tk.Scrollbar(table_container, orient=HORIZONTAL,
                                       command=canvas.xview)
            table_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

            table_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=table_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set,
                             xscrollcommand=scrollbar_x.set)

            scrollbar_y.pack(side=RIGHT, fill=Y)
            scrollbar_x.pack(side=BOTTOM, fill=X)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)

            with open(output_csv, newline="") as file:
                reader = csv.reader(file)
                r = 0
                for col in reader:
                    c = 0
                    for row in col:
                        is_header = (r == 0)
                        if is_header:
                            bg = COLORS["bg_card"]
                            fg = COLORS["accent_cyan"]
                            f = FONTS["table_head"]
                        else:
                            bg = COLORS["bg_card"] if r % 2 == 0 else COLORS["bg_dark"]
                            fg = COLORS["text_primary"]
                            f = FONTS["table"]

                            # Color the attendance percentage
                            if c == len(col) - 1 and "%" in str(row):
                                try:
                                    pct = int(row.replace("%", ""))
                                    if pct >= 75:
                                        fg = COLORS["success"]
                                    elif pct >= 50:
                                        fg = COLORS["accent_amber"]
                                    else:
                                        fg = COLORS["accent_red"]
                                except:
                                    pass

                        label = tk.Label(table_frame, width=14, height=1,
                                         fg=fg, font=f, bg=bg, text=row,
                                         relief=tk.FLAT, padx=8, pady=5)
                        label.grid(row=r, column=c, sticky="nsew")
                        c += 1
                    r += 1

            notif.configure(text="  ✓  Report generated successfully",
                            fg=COLORS["success"])
            root.mainloop()

        except Exception as ex:
            notif.configure(text=f"  ✗  Error: {str(ex)[:50]}",
                            fg=COLORS["accent_red"])

    # ═══════════════════════════════════════════════════════════
    #  Subject Chooser Window
    # ═══════════════════════════════════════════════════════════
    subject = tk.Toplevel()
    subject.title("View Attendance")
    subject.geometry("560x380")
    subject.resizable(False, False)
    subject.configure(background=COLORS["bg_dark"])
    subject.attributes("-topmost", True)

    # Header
    h = tk.Canvas(subject, width=560, height=70,
                  bg=COLORS["bg_dark"], highlightthickness=0)
    h.pack(fill=X)
    h.create_text(280, 25, text="📊  View Attendance Records",
                  fill="#ffffff", font=FONTS["heading"])
    h.create_text(280, 52, text="Enter subject name to view attendance report",
                  fill=COLORS["text_secondary"], font=FONTS["small"])
    h.create_line(40, 68, 520, 68, fill=COLORS["border"])

    # Subject Input
    form = tk.Frame(subject, bg=COLORS["bg_dark"])
    form.pack(pady=20, padx=40, fill=X)

    tk.Label(form, text="SUBJECT NAME", bg=COLORS["bg_dark"],
             fg=COLORS["accent_purple"], font=("Segoe UI", 10, "bold")).pack(anchor="w")

    tx = tk.Entry(form, width=30, bd=0, bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], insertbackground=COLORS["accent_purple"],
                  font=("Segoe UI", 18),
                  highlightthickness=2, highlightcolor=COLORS["accent_purple"],
                  highlightbackground=COLORS["border"])
    tx.pack(fill=X, ipady=10, pady=(5, 0))

    # Notification
    notif = tk.Label(subject, text="  ℹ  Ready — Enter subject and click View Attendance",
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     font=FONTS["small"], anchor="w", padx=15, pady=8)
    notif.pack(fill=X, padx=40, pady=15)

    # Buttons
    btn_frame = tk.Frame(subject, bg=COLORS["bg_dark"])
    btn_frame.pack(pady=5)

    view_btn = tk.Button(btn_frame, text="📊  View Attendance",
                         command=calculate_attendance,
                         bg=COLORS["accent_purple"], fg="#ffffff",
                         activebackground="#6535e0", activeforeground="#ffffff",
                         font=FONTS["button"], bd=0, padx=25, pady=10,
                         cursor="hand2")
    view_btn.grid(row=0, column=0, padx=10)

    def Attf():
        sub = tx.get()
        if sub == "":
            text_to_speech("Please enter the subject name!")
            notif.configure(text="  ⚠  Please enter a subject name first",
                            fg=COLORS["accent_amber"])
        else:
            target = os.path.join(attendance_path, sub)
            if os.path.exists(target):
                os.startfile(target)
            else:
                notif.configure(text="  ✗  No records found for this subject",
                                fg=COLORS["accent_red"])

    sheets_btn = tk.Button(btn_frame, text="📂  Open Folder",
                           command=Attf,
                           bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                           activebackground=COLORS["bg_card_hover"],
                           font=FONTS["body_bold"], bd=0, padx=25, pady=10,
                           cursor="hand2",
                           highlightthickness=1, highlightbackground=COLORS["border"])
    sheets_btn.grid(row=0, column=1, padx=10)

    # Hover effects
    view_btn.bind("<Enter>", lambda e: view_btn.configure(bg="#6535e0"))
    view_btn.bind("<Leave>", lambda e: view_btn.configure(bg=COLORS["accent_purple"]))
    sheets_btn.bind("<Enter>", lambda e: sheets_btn.configure(bg=COLORS["bg_card_hover"]))
    sheets_btn.bind("<Leave>", lambda e: sheets_btn.configure(bg=COLORS["bg_card"]))

    subject.mainloop()
