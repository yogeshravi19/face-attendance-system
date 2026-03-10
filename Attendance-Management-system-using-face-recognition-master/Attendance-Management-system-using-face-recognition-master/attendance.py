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
import tkinter.font as font
import pyttsx3

# project modules
import show_attendance
import takeImage
import trainImage
import automaticAttedance

# ─── Base Directory ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Paths ───
haarcasecade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(BASE_DIR, "TrainingImage")
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)
studentdetail_path = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(BASE_DIR, "Attendance")

# ═══════════════════════════════════════════════════════════════
#  PREMIUM COLOR PALETTE — Futuristic Dark Theme
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
    "border_light":  "#3d444d",
    "gradient_start":"#0d1117",
    "gradient_end":  "#161b22",
    "btn_hover":     "#1f6feb",
    "success":       "#3fb950",
    "header_bg":     "#0d1117",
}

FONTS = {
    "title":       ("Segoe UI", 28, "bold"),
    "subtitle":    ("Segoe UI", 14),
    "heading":     ("Segoe UI", 20, "bold"),
    "body":        ("Segoe UI", 13),
    "body_bold":   ("Segoe UI", 13, "bold"),
    "small":       ("Segoe UI", 11),
    "tiny":        ("Segoe UI", 9),
    "button":      ("Segoe UI", 14, "bold"),
    "button_lg":   ("Segoe UI", 16, "bold"),
    "card_title":  ("Segoe UI", 18, "bold"),
    "card_desc":   ("Segoe UI", 11),
    "icon":        ("Segoe UI", 36, "bold"),
}


def text_to_speech(user_text):
    try:
        engine = pyttsx3.init()
        engine.say(user_text)
        engine.runAndWait()
    except:
        pass


# ═══════════════════════════════════════════════════════════════
#  HELPER: Rounded Rectangle on Canvas
# ═══════════════════════════════════════════════════════════════
def rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# ═══════════════════════════════════════════════════════════════
#  HELPER: Create a premium hoverable card
# ═══════════════════════════════════════════════════════════════
def create_card(parent, x, y, width, height, icon_text, icon_color,
                title, description, command):
    card = tk.Canvas(parent, width=width, height=height,
                     bg=COLORS["bg_dark"], highlightthickness=0, cursor="hand2")
    card.place(x=x, y=y)

    # Card background
    bg_rect = rounded_rect(card, 2, 2, width - 2, height - 2, radius=18,
                           fill=COLORS["bg_card"], outline=COLORS["border"], width=1)

    # Glow line at top
    card.create_line(30, 3, width - 30, 3, fill=icon_color, width=2)

    # Icon circle background
    cx, cy = width // 2, 65
    r = 35
    card.create_oval(cx - r, cy - r, cx + r, cy + r,
                     fill=COLORS["bg_dark"], outline=icon_color, width=2)
    card.create_text(cx, cy, text=icon_text, fill=icon_color,
                     font=FONTS["icon"])

    # Title
    card.create_text(width // 2, 130, text=title,
                     fill=COLORS["text_primary"], font=FONTS["card_title"])

    # Description
    card.create_text(width // 2, 160, text=description,
                     fill=COLORS["text_secondary"], font=FONTS["card_desc"])

    # Bottom button area
    btn_y1, btn_y2 = height - 60, height - 20
    btn_x1, btn_x2 = 30, width - 30
    btn_rect = rounded_rect(card, btn_x1, btn_y1, btn_x2, btn_y2, radius=12,
                            fill=icon_color, outline="")
    btn_text = card.create_text((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2,
                                text="OPEN →", fill="#ffffff",
                                font=FONTS["body_bold"])

    # Hover effects
    def on_enter(e):
        rounded_rect(card, 2, 2, width - 2, height - 2, radius=18,
                     fill=COLORS["bg_card_hover"], outline=icon_color, width=2)
        card.create_line(30, 3, width - 30, 3, fill=icon_color, width=3)
        card.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=COLORS["bg_dark"], outline=icon_color, width=2)
        card.create_text(cx, cy, text=icon_text, fill=icon_color,
                         font=FONTS["icon"])
        card.create_text(width // 2, 130, text=title,
                         fill="#ffffff", font=FONTS["card_title"])
        card.create_text(width // 2, 160, text=description,
                         fill=COLORS["text_secondary"], font=FONTS["card_desc"])
        rounded_rect(card, btn_x1, btn_y1, btn_x2, btn_y2, radius=12,
                     fill="#ffffff", outline="")
        card.create_text((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2,
                         text="OPEN →", fill=icon_color,
                         font=FONTS["body_bold"])

    def on_leave(e):
        card.delete("all")
        rounded_rect(card, 2, 2, width - 2, height - 2, radius=18,
                     fill=COLORS["bg_card"], outline=COLORS["border"], width=1)
        card.create_line(30, 3, width - 30, 3, fill=icon_color, width=2)
        card.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=COLORS["bg_dark"], outline=icon_color, width=2)
        card.create_text(cx, cy, text=icon_text, fill=icon_color,
                         font=FONTS["icon"])
        card.create_text(width // 2, 130, text=title,
                         fill=COLORS["text_primary"], font=FONTS["card_title"])
        card.create_text(width // 2, 160, text=description,
                         fill=COLORS["text_secondary"], font=FONTS["card_desc"])
        rounded_rect(card, btn_x1, btn_y1, btn_x2, btn_y2, radius=12,
                     fill=icon_color, outline="")
        card.create_text((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2,
                         text="OPEN →", fill="#ffffff",
                         font=FONTS["body_bold"])

    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)
    card.bind("<Button-1>", lambda e: command())

    return card


# ═══════════════════════════════════════════════════════════════
#  ERROR POPUP
# ═══════════════════════════════════════════════════════════════
def err_screen():
    sc1 = tk.Toplevel()
    sc1.geometry("420x140")
    sc1.title("⚠ Warning")
    sc1.configure(background=COLORS["bg_card"])
    sc1.resizable(False, False)
    sc1.attributes("-topmost", True)

    tk.Label(sc1, text="⚠", font=("Segoe UI", 32),
             bg=COLORS["bg_card"], fg=COLORS["accent_amber"]).pack(pady=(10, 0))
    tk.Label(sc1, text="Enrollment & Name are required!",
             fg=COLORS["accent_amber"], bg=COLORS["bg_card"],
             font=FONTS["body_bold"]).pack()
    tk.Button(sc1, text="GOT IT", command=sc1.destroy,
              fg="#ffffff", bg=COLORS["accent_amber"],
              activebackground=COLORS["accent_red"],
              font=FONTS["body_bold"], bd=0, padx=30, pady=5,
              cursor="hand2").pack(pady=10)


def testVal(inStr, acttyp):
    if acttyp == "1":
        if not inStr.isdigit():
            return False
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════
window = Tk()
window.title("FaceAuth — Smart Attendance System")
window.geometry("1280x720")
window.configure(background=COLORS["bg_dark"])
window.resizable(False, False)

# ─── Header Section ───
header = tk.Canvas(window, width=1280, height=140,
                   bg=COLORS["bg_dark"], highlightthickness=0)
header.place(x=0, y=0)

# Header gradient bar
for i in range(140):
    shade = int(13 + (i / 140) * 9)
    r_val = min(shade, 255)
    g_val = min(shade + 6, 255)
    b_val = min(shade + 12, 255)
    color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
    try:
        header.create_line(0, i, 1280, i, fill=color)
    except:
        header.create_line(0, i, 1280, i, fill=COLORS["bg_dark"])

# Accent line
header.create_line(0, 139, 1280, 139, fill=COLORS["border"], width=1)
header.create_line(440, 138, 840, 138, fill=COLORS["accent_cyan"], width=2)

# Logo icon
header.create_text(540, 45, text="◉", fill=COLORS["accent_cyan"],
                   font=("Segoe UI", 30))

# Title
header.create_text(640, 40, text="FaceAuth", fill="#ffffff",
                   font=("Segoe UI", 32, "bold"), anchor="w")

# Subtitle
header.create_text(640, 80, text="Smart Attendance System",
                   fill=COLORS["text_secondary"],
                   font=("Segoe UI", 14), anchor="w")

# Tag
header.create_text(640, 108, text="COMPUTER VISION  •  FACE RECOGNITION  •  DEEP LEARNING",
                   fill=COLORS["text_muted"],
                   font=("Segoe UI", 9), anchor="w")

# ─── Welcome Banner ───
banner = tk.Canvas(window, width=1200, height=80,
                   bg=COLORS["bg_dark"], highlightthickness=0)
banner.place(x=40, y=155)
rounded_rect(banner, 0, 0, 1200, 80, radius=16,
             fill=COLORS["bg_card"], outline=COLORS["border"])

banner.create_text(600, 28, text="Welcome to the Face Recognition Based Attendance Management System",
                   fill=COLORS["text_primary"], font=("Segoe UI", 16, "bold"))
banner.create_text(600, 55, text="Register students, take attendance via face recognition, and view records — all in one place.",
                   fill=COLORS["text_secondary"], font=("Segoe UI", 11))


# ─── Feature Cards ───
CARD_W = 350
CARD_H = 220
CARD_Y = 270
CARD_GAP = 45
start_x = (1280 - (CARD_W * 3 + CARD_GAP * 2)) // 2

# Card 1: Register Student
def TakeImageUI():
    ImageUI = tk.Toplevel()
    ImageUI.title("Register New Student")
    ImageUI.geometry("700x520")
    ImageUI.configure(background=COLORS["bg_dark"])
    ImageUI.resizable(False, False)
    ImageUI.attributes("-topmost", True)

    # Header
    h_canvas = tk.Canvas(ImageUI, width=700, height=80,
                         bg=COLORS["bg_dark"], highlightthickness=0)
    h_canvas.pack(fill=X)
    h_canvas.create_text(350, 25, text="👤  Register New Student",
                         fill="#ffffff", font=FONTS["heading"])
    h_canvas.create_text(350, 55, text="Capture face images for training the recognition model",
                         fill=COLORS["text_secondary"], font=FONTS["small"])
    h_canvas.create_line(50, 78, 650, 78, fill=COLORS["border"])

    # Form Frame
    form = tk.Frame(ImageUI, bg=COLORS["bg_dark"])
    form.pack(pady=20, padx=40, fill=X)

    # Enrollment
    tk.Label(form, text="ENROLLMENT NO.", bg=COLORS["bg_dark"],
             fg=COLORS["accent_cyan"], font=("Segoe UI", 10, "bold")).grid(
        row=0, column=0, sticky="w", pady=(0, 5))

    txt1 = tk.Entry(form, width=30, bd=0, bg=COLORS["bg_card"],
                    fg=COLORS["text_primary"], insertbackground=COLORS["accent_cyan"],
                    font=("Segoe UI", 16), validate="key",
                    highlightthickness=2, highlightcolor=COLORS["accent_cyan"],
                    highlightbackground=COLORS["border"])
    txt1.grid(row=1, column=0, sticky="ew", ipady=8, pady=(0, 20))
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Name
    tk.Label(form, text="STUDENT NAME", bg=COLORS["bg_dark"],
             fg=COLORS["accent_cyan"], font=("Segoe UI", 10, "bold")).grid(
        row=2, column=0, sticky="w", pady=(0, 5))

    txt2 = tk.Entry(form, width=30, bd=0, bg=COLORS["bg_card"],
                    fg=COLORS["text_primary"], insertbackground=COLORS["accent_cyan"],
                    font=("Segoe UI", 16),
                    highlightthickness=2, highlightcolor=COLORS["accent_cyan"],
                    highlightbackground=COLORS["border"])
    txt2.grid(row=3, column=0, sticky="ew", ipady=8, pady=(0, 20))

    form.columnconfigure(0, weight=1)

    # Notification
    notif_frame = tk.Frame(ImageUI, bg=COLORS["bg_card"], highlightthickness=1,
                           highlightbackground=COLORS["border"])
    notif_frame.pack(padx=40, fill=X, pady=(0, 15))

    notif_label = tk.Label(notif_frame, text="  ℹ  Ready — Enter details and click Take Image",
                           bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                           font=FONTS["small"], anchor="w", padx=10, pady=8)
    notif_label.pack(fill=X)

    message = notif_label  # reuse for callbacks

    def take_image():
        l1 = txt1.get()
        l2 = txt2.get()
        takeImage.TakeImage(l1, l2, haarcasecade_path, trainimage_path,
                            message, err_screen, text_to_speech)
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    def train_image():
        trainImage.TrainImage(haarcasecade_path, trainimage_path,
                              trainimagelabel_path, message, text_to_speech)

    # Buttons
    btn_frame = tk.Frame(ImageUI, bg=COLORS["bg_dark"])
    btn_frame.pack(pady=10)

    take_btn = tk.Button(btn_frame, text="📷  Take Image", command=take_image,
                         bg=COLORS["accent_cyan"], fg="#ffffff",
                         activebackground="#0096c7", activeforeground="#ffffff",
                         font=FONTS["button"], bd=0, padx=30, pady=12,
                         cursor="hand2")
    take_btn.grid(row=0, column=0, padx=15)

    train_btn = tk.Button(btn_frame, text="🧠  Train Model", command=train_image,
                          bg=COLORS["accent_green"], fg="#ffffff",
                          activebackground="#00a844", activeforeground="#ffffff",
                          font=FONTS["button"], bd=0, padx=30, pady=12,
                          cursor="hand2")
    train_btn.grid(row=0, column=1, padx=15)

    # Button hover effects
    def btn_enter(btn, hover_color):
        btn.configure(bg=hover_color)
    def btn_leave(btn, orig_color):
        btn.configure(bg=orig_color)

    take_btn.bind("<Enter>", lambda e: btn_enter(take_btn, "#0096c7"))
    take_btn.bind("<Leave>", lambda e: btn_leave(take_btn, COLORS["accent_cyan"]))
    train_btn.bind("<Enter>", lambda e: btn_enter(train_btn, "#00a844"))
    train_btn.bind("<Leave>", lambda e: btn_leave(train_btn, COLORS["accent_green"]))


create_card(window, start_x, CARD_Y, CARD_W, CARD_H,
            "👤", COLORS["accent_cyan"],
            "Register Student", "Capture & train face data",
            TakeImageUI)


# Card 2: Take Attendance
def automatic_attedance():
    automaticAttedance.subjectChoose(text_to_speech)

create_card(window, start_x + CARD_W + CARD_GAP, CARD_Y, CARD_W, CARD_H,
            "📷", COLORS["accent_green"],
            "Take Attendance", "Auto-detect faces & mark",
            automatic_attedance)

# Card 3: View Attendance
def view_attendance():
    show_attendance.subjectchoose(text_to_speech)

create_card(window, start_x + (CARD_W + CARD_GAP) * 2, CARD_Y, CARD_W, CARD_H,
            "📊", COLORS["accent_purple"],
            "View Records", "Browse attendance sheets",
            view_attendance)


# ─── Stats Bar ───
stats = tk.Canvas(window, width=1200, height=65,
                  bg=COLORS["bg_dark"], highlightthickness=0)
stats.place(x=40, y=520)
rounded_rect(stats, 0, 0, 1200, 65, radius=14,
             fill=COLORS["bg_card"], outline=COLORS["border"])

# Count registered students
try:
    df_students = pd.read_csv(studentdetail_path)
    student_count = len(df_students)
except:
    student_count = 0

# Count subjects
try:
    subjects = [d for d in os.listdir(attendance_path)
                if os.path.isdir(os.path.join(attendance_path, d))]
    subject_count = len(subjects)
except:
    subject_count = 0

# Check if model exists
model_status = "Trained ✓" if os.path.exists(trainimagelabel_path) else "Not Trained ✗"
model_color = COLORS["success"] if os.path.exists(trainimagelabel_path) else COLORS["accent_red"]

stat_items = [
    (150, f"👥  {student_count} Students", COLORS["accent_cyan"]),
    (450, f"📚  {subject_count} Subjects", COLORS["accent_purple"]),
    (750, f"🧠  Model: {model_status}", model_color),
    (1050, f"📅  {datetime.datetime.now().strftime('%d %b %Y')}", COLORS["text_secondary"]),
]
for sx, text, color in stat_items:
    stats.create_text(sx, 33, text=text, fill=color, font=FONTS["body_bold"])


# ─── Bottom Section ───
bottom = tk.Canvas(window, width=1280, height=100,
                   bg=COLORS["bg_dark"], highlightthickness=0)
bottom.place(x=0, y=610)

# Powered by text
bottom.create_text(640, 20, text="Powered by OpenCV  •  LBPH Face Recognizer  •  Python",
                   fill=COLORS["text_muted"], font=FONTS["tiny"])

# Exit button
exit_canvas = tk.Canvas(bottom, width=180, height=45,
                        bg=COLORS["bg_dark"], highlightthickness=0, cursor="hand2")
exit_canvas.place(x=550, y=35)

exit_bg = rounded_rect(exit_canvas, 0, 0, 180, 45, radius=12,
                       fill=COLORS["bg_card"], outline=COLORS["accent_red"], width=1)
exit_text = exit_canvas.create_text(90, 23, text="EXIT APPLICATION",
                                    fill=COLORS["accent_red"], font=("Segoe UI", 11, "bold"))

def exit_enter(e):
    exit_canvas.delete("all")
    rounded_rect(exit_canvas, 0, 0, 180, 45, radius=12,
                 fill=COLORS["accent_red"], outline="")
    exit_canvas.create_text(90, 23, text="EXIT APPLICATION",
                            fill="#ffffff", font=("Segoe UI", 11, "bold"))

def exit_leave(e):
    exit_canvas.delete("all")
    rounded_rect(exit_canvas, 0, 0, 180, 45, radius=12,
                 fill=COLORS["bg_card"], outline=COLORS["accent_red"], width=1)
    exit_canvas.create_text(90, 23, text="EXIT APPLICATION",
                            fill=COLORS["accent_red"], font=("Segoe UI", 11, "bold"))

exit_canvas.bind("<Enter>", exit_enter)
exit_canvas.bind("<Leave>", exit_leave)
exit_canvas.bind("<Button-1>", lambda e: window.destroy())


window.mainloop()
