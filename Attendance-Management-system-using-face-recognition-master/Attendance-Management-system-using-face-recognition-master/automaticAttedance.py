import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font

# ─── Base Directory ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Paths ───
haarcasecade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(BASE_DIR, "TrainingImage")
studentdetail_path = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(BASE_DIR, "Attendance")

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
    "card_title":  ("Segoe UI", 16, "bold"),
    "table":       ("Segoe UI", 12),
    "table_head":  ("Segoe UI", 12, "bold"),
}


def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        now = time.time()
        future = now + 20
        if sub == "":
            t = "Please enter the subject name!"
            text_to_speech(t)
            Notifica.configure(text="  ⚠  " + t, fg=COLORS["accent_amber"])
        else:
            try:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                try:
                    recognizer.read(trainimagelabel_path)
                except:
                    e = "Model not found — please train the model first"
                    Notifica.configure(text="  ✗  " + e, fg=COLORS["accent_red"])
                    text_to_speech(e)
                    return

                facecasCade = cv2.CascadeClassifier(haarcasecade_path)
                df = pd.read_csv(studentdetail_path)
                cam = cv2.VideoCapture(0)
                font_cv = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ["Enrollment", "Name"]
                attendance_df = pd.DataFrame(columns=col_names)

                Notifica.configure(text="  📷  Scanning faces... (20 seconds)",
                                   fg=COLORS["accent_cyan"])
                subject.update()

                while True:
                    ___, im = cam.read()
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        global Id
                        Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                        if conf < 70:
                            global Subject, aa, date, timeStamp
                            Subject = tx.get()
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                            aa = df.loc[df["Enrollment"] == Id]["Name"].values
                            global tt
                            tt = str(Id) + "-" + aa
                            attendance_df.loc[len(attendance_df)] = [Id, aa]
                            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 200, 100), 3)
                            cv2.putText(im, str(tt), (x+h, y), font_cv, 0.8, (0, 255, 200), 2)
                        else:
                            Id = "Unknown"
                            tt = str(Id)
                            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 50, 255), 3)
                            cv2.putText(im, str(tt), (x+h, y), font_cv, 0.8, (0, 50, 255), 2)

                    if time.time() > future:
                        break

                    attendance_df = attendance_df.drop_duplicates(["Enrollment"], keep="first")
                    cv2.imshow("FaceAuth — Scanning...", im)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:
                        break

                ts = time.time()
                attendance_df[date] = 1
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                Hour, Minute, Second = timeStamp.split(":")

                path = os.path.join(attendance_path, Subject)
                if not os.path.exists(path):
                    os.makedirs(path)

                fileName = (
                    f"{path}/"
                    + Subject + "_" + date + "_"
                    + Hour + "-" + Minute + "-" + Second + ".csv"
                )
                attendance_df = attendance_df.drop_duplicates(["Enrollment"], keep="first")
                attendance_df.to_csv(fileName, index=False)

                m = f"✓ Attendance filled for {Subject}"
                Notifica.configure(text="  " + m, fg=COLORS["success"])
                text_to_speech(m)

                cam.release()
                cv2.destroyAllWindows()

                # ─── Show results in styled popup ───
                root = tk.Toplevel()
                root.title(f"Attendance — {Subject}")
                root.configure(background=COLORS["bg_dark"])
                root.attributes("-topmost", True)

                tk.Label(root, text=f"📋  Attendance for {Subject}",
                         bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                         font=FONTS["heading"]).pack(pady=15)

                cs = os.path.join(path, fileName)
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    table_frame = tk.Frame(root, bg=COLORS["bg_dark"])
                    table_frame.pack(padx=20, pady=(0, 20))
                    r = 0
                    for col in reader:
                        c = 0
                        for row in col:
                            is_header = (r == 0)
                            bg = COLORS["bg_card"] if r % 2 == 0 else COLORS["bg_dark"]
                            fg = COLORS["accent_cyan"] if is_header else COLORS["text_primary"]
                            f = FONTS["table_head"] if is_header else FONTS["table"]
                            label = tk.Label(table_frame, width=15, height=1,
                                             fg=fg, font=f, bg=bg, text=row,
                                             relief=tk.FLAT, padx=10, pady=6)
                            label.grid(row=r, column=c, sticky="nsew")
                            c += 1
                        r += 1
                root.mainloop()

            except Exception as ex:
                f = "No face found for attendance"
                Notifica.configure(text="  ✗  " + f, fg=COLORS["accent_red"])
                text_to_speech(f)
                cv2.destroyAllWindows()

    # ═══════════════════════════════════════════════════════════
    #  Subject Chooser Window
    # ═══════════════════════════════════════════════════════════
    subject = tk.Toplevel()
    subject.title("Take Attendance")
    subject.geometry("560x380")
    subject.resizable(False, False)
    subject.configure(background=COLORS["bg_dark"])
    subject.attributes("-topmost", True)

    # Header
    h = tk.Canvas(subject, width=560, height=70,
                  bg=COLORS["bg_dark"], highlightthickness=0)
    h.pack(fill=X)
    h.create_text(280, 25, text="📷  Take Attendance",
                  fill="#ffffff", font=FONTS["heading"])
    h.create_text(280, 52, text="Enter subject name, then start scanning",
                  fill=COLORS["text_secondary"], font=FONTS["small"])
    h.create_line(40, 68, 520, 68, fill=COLORS["border"])

    # Subject Input
    form = tk.Frame(subject, bg=COLORS["bg_dark"])
    form.pack(pady=20, padx=40, fill=X)

    tk.Label(form, text="SUBJECT NAME", bg=COLORS["bg_dark"],
             fg=COLORS["accent_green"], font=("Segoe UI", 10, "bold")).pack(anchor="w")

    tx = tk.Entry(form, width=30, bd=0, bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], insertbackground=COLORS["accent_green"],
                  font=("Segoe UI", 18),
                  highlightthickness=2, highlightcolor=COLORS["accent_green"],
                  highlightbackground=COLORS["border"])
    tx.pack(fill=X, ipady=10, pady=(5, 0))

    # Notification
    Notifica = tk.Label(subject, text="  ℹ  Ready — Enter subject and click Fill Attendance",
                        bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                        font=FONTS["small"], anchor="w", padx=15, pady=8)
    Notifica.pack(fill=X, padx=40, pady=15)

    # Buttons
    btn_frame = tk.Frame(subject, bg=COLORS["bg_dark"])
    btn_frame.pack(pady=5)

    fill_btn = tk.Button(btn_frame, text="▶  Fill Attendance",
                         command=FillAttendance,
                         bg=COLORS["accent_green"], fg="#ffffff",
                         activebackground="#00a844", activeforeground="#ffffff",
                         font=FONTS["button"], bd=0, padx=25, pady=10,
                         cursor="hand2")
    fill_btn.grid(row=0, column=0, padx=10)

    def Attf():
        sub = tx.get()
        if sub == "":
            text_to_speech("Please enter the subject name!")
            Notifica.configure(text="  ⚠  Please enter a subject name first",
                               fg=COLORS["accent_amber"])
        else:
            target = os.path.join(attendance_path, sub)
            if os.path.exists(target):
                os.startfile(target)
            else:
                Notifica.configure(text="  ✗  No records found for this subject",
                                   fg=COLORS["accent_red"])

    sheets_btn = tk.Button(btn_frame, text="📂  Check Sheets",
                           command=Attf,
                           bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                           activebackground=COLORS["bg_card_hover"],
                           font=FONTS["body_bold"], bd=0, padx=25, pady=10,
                           cursor="hand2",
                           highlightthickness=1, highlightbackground=COLORS["border"])
    sheets_btn.grid(row=0, column=1, padx=10)

    # Hover effects
    fill_btn.bind("<Enter>", lambda e: fill_btn.configure(bg="#00a844"))
    fill_btn.bind("<Leave>", lambda e: fill_btn.configure(bg=COLORS["accent_green"]))
    sheets_btn.bind("<Enter>", lambda e: sheets_btn.configure(bg=COLORS["bg_card_hover"]))
    sheets_btn.bind("<Leave>", lambda e: sheets_btn.configure(bg=COLORS["bg_card"]))

    subject.mainloop()
