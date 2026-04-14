import tkinter as tk
from tkinter import *
import os
import csv
import datetime
import pandas as pd
import tkinter.font as tkfont

# ── Project Modules ──
import show_attendance
import takeImage
import trainImage
import automaticAttedance
import registerSubject

# ── Base Directory ──
BASE_DIR               = os.path.dirname(os.path.abspath(__file__))
haarcasecade_path      = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path   = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path        = os.path.join(BASE_DIR, "TrainingImage")
studentdetail_path     = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
attendance_path        = os.path.join(BASE_DIR, "Attendance")

os.makedirs(trainimage_path, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "StudentDetails"), exist_ok=True)
os.makedirs(attendance_path, exist_ok=True)

# ══════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM — VisioMark Premium Dark Theme
# ══════════════════════════════════════════════════════════════════
C = {
    # Backgrounds
    "bg":           "#050511",  # Ultra-deep space blue/black
    "surface":      "#0A0B1A",  # Slightly elevated
    "card":         "#0D0E20",  # Card background
    "card2":        "#151733",  # Card hover state
    "glass":        "#0F1126",  # Input backgrounds

    # Neon Accents
    "blue":         "#2563EB",  # Electric Blue
    "blue_glow":    "#3B82F6",
    "cyan":         "#00F0FF",  # Cyber Cyan
    "teal":         "#0AF5C6",  # Vibrant Teal
    "purple":       "#9D4EDD",  # Neon Purple
    "green":        "#00FF66",  # Matrix Green
    "red":          "#FF003C",  # Laser Red
    "amber":        "#FFB000",  # Sunset Gold
    "pink":         "#FF007F",  # Synthwave Pink

    # Borders
    "border":       "#1D1E3A",
    "border2":      "#2A2D5C",

    # Text
    "white":        "#FFFFFF",
    "text":         "#E2E8F0",
    "muted":        "#828CA0",
    "dim":          "#4A5568",
}

F = {
    "brand":   ("Segoe UI", 32, "bold"),
    "hero":    ("Segoe UI", 13),
    "h1":      ("Segoe UI", 22, "bold"),
    "h2":      ("Segoe UI", 17, "bold"),
    "h3":      ("Segoe UI", 14, "bold"),
    "body":    ("Segoe UI", 12),
    "small":   ("Segoe UI", 10),
    "tiny":    ("Segoe UI", 9),
    "clock":   ("Segoe UI Light", 26),
    "stat_n":  ("Segoe UI", 28, "bold"),
    "stat_l":  ("Segoe UI", 9),
    "badge":   ("Segoe UI", 8, "bold"),
    "btn":     ("Segoe UI", 13, "bold"),
    "card_ic": ("Segoe UI", 38),
    "card_t":  ("Segoe UI", 15, "bold"),
    "card_d":  ("Segoe UI", 10),
}

import pyttsx3
def text_to_speech(msg):
    try:
        e = pyttsx3.init()
        e.say(msg)
        e.runAndWait()
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════
#  CANVAS HELPERS
# ══════════════════════════════════════════════════════════════════
def rrect(canvas, x1, y1, x2, y2, r=16, **kw):
    pts = [
        x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
        x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
        x1, y2, x1, y2-r, x1, y1+r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)

def draw_gradient_line(canvas, x1, y1, x2, y2, colors, width=1):
    steps = len(colors)
    seg   = (x2 - x1) / steps
    for i, col in enumerate(colors):
        sx = x1 + i * seg
        canvas.create_line(sx, y1, sx + seg, y2, fill=col, width=width)


# ══════════════════════════════════════════════════════════════════
#  VALIDATION
# ══════════════════════════════════════════════════════════════════
def testVal(inStr, acttyp):
    if acttyp == "1":
        if not inStr.isdigit():
            return False
    return True

def err_screen():
    w = tk.Toplevel()
    w.geometry("400x130")
    w.title("⚠ Input Required")
    w.configure(bg=C["card"])
    w.resizable(False, False)
    w.attributes("-topmost", True)
    tk.Label(w, text="⚠  Enrollment & Name are required",
             bg=C["card"], fg=C["amber"], font=F["h3"]).pack(pady=(22, 6))
    tk.Button(w, text="  Got It  ", command=w.destroy,
              bg=C["amber"], fg=C["bg"], font=F["btn"],
              bd=0, padx=18, pady=6, cursor="hand2").pack()


# ══════════════════════════════════════════════════════════════════
#  REGISTER STUDENT WINDOW
# ══════════════════════════════════════════════════════════════════
def TakeImageUI():
    win = tk.Toplevel()
    win.title("NexAttend — Register Student")
    win.geometry("680x520")
    win.configure(bg=C["bg"])
    win.resizable(False, False)
    win.attributes("-topmost", True)

    # ── Hero banner ──
    hero = tk.Canvas(win, width=680, height=100, bg=C["bg"], highlightthickness=0)
    hero.pack(fill=X)
    for i in range(100):
        t = i / 100
        r2 = int(0x07 + t * 8)
        g2 = int(0x09 + t * 10)
        b2 = int(0x0F + t * 18)
        hero.create_line(0, i, 680, i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")
    hero.create_text(340, 35, text="👤  Register New Student",
                     fill=C["white"], font=F["h1"], anchor="center")
    hero.create_text(340, 65, text="Capture 100 face images for precise AI training",
                     fill=C["muted"], font=F["small"], anchor="center")
    # Accent line
    for i, col in enumerate(["#1E3A5F","#2563EB","#3B82F6","#60A5FA","#3B82F6","#2563EB","#1E3A5F"]):
        sx = i * (680 // 7)
        hero.create_line(sx, 99, sx + 680//7, 99, fill=col, width=2)

    # ── Card ──
    card_frame = tk.Frame(win, bg=C["card"], highlightbackground=C["border2"],
                          highlightthickness=1)
    card_frame.pack(padx=40, pady=18, fill=BOTH, expand=True)

    # Enrollment
    tk.Label(card_frame, text="ENROLLMENT NUMBER",
             bg=C["card"], fg=C["blue"], font=F["badge"]).pack(anchor="w", padx=24, pady=(20, 4))
    txt1 = tk.Entry(card_frame, width=32, bd=0, bg=C["glass"],
                    fg=C["white"], insertbackground=C["blue"],
                    font=("Segoe UI", 18), validate="key",
                    highlightthickness=2, highlightcolor=C["blue"],
                    highlightbackground=C["border"])
    txt1.pack(fill=X, padx=24, ipady=10, pady=(0, 16))
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Name
    tk.Label(card_frame, text="STUDENT FULL NAME",
             bg=C["card"], fg=C["cyan"], font=F["badge"]).pack(anchor="w", padx=24, pady=(0, 4))
    txt2 = tk.Entry(card_frame, width=32, bd=0, bg=C["glass"],
                    fg=C["white"], insertbackground=C["cyan"],
                    font=("Segoe UI", 18),
                    highlightthickness=2, highlightcolor=C["cyan"],
                    highlightbackground=C["border"])
    txt2.pack(fill=X, padx=24, ipady=10, pady=(0, 16))

    # Notif
    notif = tk.Label(card_frame,
                     text="  ℹ  Fill in the details above and click Take Image",
                     bg=C["glass"], fg=C["muted"],
                     font=F["small"], anchor="w", padx=14, pady=9)
    notif.pack(fill=X, padx=24, pady=(0, 18))

    def take_image():
        takeImage.TakeImage(
            txt1.get(), txt2.get(),
            haarcasecade_path, trainimage_path,
            notif, err_screen, text_to_speech
        )
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path, trainimage_path,
            trainimagelabel_path, notif, text_to_speech
        )

    # Buttons
    btn_row = tk.Frame(card_frame, bg=C["card"])
    btn_row.pack(pady=(0, 20))

    take_btn = tk.Button(btn_row, text="📷   Take Image",
                         command=take_image,
                         bg=C["blue"], fg=C["white"],
                         activebackground=C["blue_glow"],
                         font=F["btn"], bd=0, padx=28, pady=11, cursor="hand2")
    take_btn.grid(row=0, column=0, padx=10)

    train_btn = tk.Button(btn_row, text="🧠   Train Model",
                          command=train_image,
                          bg=C["teal"], fg=C["white"],
                          activebackground="#0F9083",
                          font=F["btn"], bd=0, padx=28, pady=11, cursor="hand2")
    train_btn.grid(row=0, column=1, padx=10)

    take_btn.bind("<Enter>",  lambda e: take_btn.configure(bg=C["blue_glow"]))
    take_btn.bind("<Leave>",  lambda e: take_btn.configure(bg=C["blue"]))
    train_btn.bind("<Enter>", lambda e: train_btn.configure(bg="#0F9083"))
    train_btn.bind("<Leave>", lambda e: train_btn.configure(bg=C["teal"]))
    txt1.focus_set()


# ══════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════
window = Tk()
window.title("NexAttend — AI Attendance System")
window.geometry("1280x720")
window.configure(background=C["bg"])
window.resizable(False, False)

try:
    ico = os.path.join(BASE_DIR, "AMS.ico")
    if os.path.exists(ico):
        window.iconbitmap(ico)
except Exception:
    pass

# ══════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════
HEADER_H = 110
header = tk.Canvas(window, width=1280, height=HEADER_H,
                   bg=C["bg"], highlightthickness=0)
header.place(x=0, y=0)

# Gradient fill
for i in range(HEADER_H):
    t = i / HEADER_H
    r2 = int(0x07 + t * 6)
    g2 = int(0x09 + t * 8)
    b2 = int(0x0F + t * 16)
    header.create_line(0, i, 1280, i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")

# Glowing accent bar at bottom of header
accent_colors = ["#0E2038","#1B4B8C","#2563EB","#3B82F6","#60A5FA",
                 "#3B82F6","#2563EB","#1B4B8C","#0E2038"]
seg_w = 1280 // len(accent_colors)
for i, col in enumerate(accent_colors):
    header.create_line(i*seg_w, HEADER_H-1, (i+1)*seg_w, HEADER_H-1,
                       fill=col, width=2)

# Logo glyph
header.create_oval(44, 22, 88, 66, fill=C["surface"],
                   outline=C["blue"], width=2)
header.create_text(66, 44, text="◉", fill=C["blue"],
                   font=("Segoe UI", 22, "bold"))

# Brand name
header.create_text(104, 34, text="NexAttend",
                   fill=C["white"], font=("Segoe UI", 30, "bold"), anchor="w")
header.create_text(104, 62, text="AI-Powered Face Recognition Attendance System",
                   fill=C["muted"], font=F["hero"], anchor="w")
header.create_text(104, 82, text="MODELS: VIOLA-JONES ALGORITHM (HAAR CASCADE)  ·  LBPH RECOGNIZER",
                   fill=C["cyan"], font=("Segoe UI", 8, "bold"), anchor="w")

# Live clock (top-right)
clock_lbl = header.create_text(1250, 44, text="",
                               fill=C["text"], font=F["clock"], anchor="e")
date_lbl  = header.create_text(1250, 78, text="",
                               fill=C["muted"], font=F["tiny"], anchor="e")

def tick():
    now = datetime.datetime.now()
    header.itemconfig(clock_lbl, text=now.strftime("%H:%M:%S"))
    header.itemconfig(date_lbl,  text=now.strftime("%A,  %d %B %Y"))
    window.after(1000, tick)

tick()

# Separator
tk.Frame(window, bg=C["border"], height=1).place(x=0, y=HEADER_H, width=1280)


# ══════════════════════════════════════════════════════════════════
#  HERO SUBTITLE BANNER
# ══════════════════════════════════════════════════════════════════
banner_y = HEADER_H + 14
banner = tk.Canvas(window, width=1200, height=60,
                   bg=C["bg"], highlightthickness=0)
banner.place(x=40, y=banner_y)
rrect(banner, 0, 0, 1200, 60, r=12,
      fill=C["card"], outline=C["border2"], width=1)
banner.create_line(3, 6, 3, 54, fill=C["blue"], width=3)
banner.create_text(24, 20, text="Welcome to NexAttend",
                   fill=C["white"], font=F["h3"], anchor="w")
banner.create_text(24, 42, text="Register students • Train the AI model • Take attendance in seconds via live face recognition",
                   fill=C["muted"], font=F["small"], anchor="w")

# Model status badge
model_ok      = os.path.exists(trainimagelabel_path)
badge_color   = C["green"] if model_ok else C["red"]
badge_fill    = "#0D2E1E"  if model_ok else "#2E0D0D"   # dark tint — no alpha needed
badge_text    = "  ●  Model READY  " if model_ok else "  ●  Model NOT TRAINED  "
banner.create_rectangle(940, 14, 1185, 46, fill=badge_fill,
                        outline=badge_color, width=1)
banner.create_text(1063, 30, text=badge_text,
                   fill=badge_color, font=("Segoe UI", 10, "bold"))


# ══════════════════════════════════════════════════════════════════
#  FEATURE CARDS
# ══════════════════════════════════════════════════════════════════
CARD_W   = 265
CARD_H   = 240
CARDS_Y  = banner_y + 86
GAP      = 22
START_X  = (1280 - (CARD_W * 4 + GAP * 3)) // 2

CARD_DEF = [
    {
        "icon": "👤", "color": C["blue"], "glow": "#1D4ED8",
        "title": "Register Student",
        "desc": "Capture 100 face images\nfor AI model training",
        "steps": ["Enter Enrollment & Name", "Capture 100 photos", "Train the AI model"],
        "cmd": TakeImageUI,
    },
    {
        "icon": "📚", "color": C["pink"], "glow": "#BE185D",
        "title": "Register Subject",
        "desc": "Add subjects with faculty\nname & time slot",
        "steps": ["Enter subject & faculty", "Choose slot timing", "Folder auto-created"],
        "cmd": registerSubject.open_register_subject,
    },
    {
        "icon": "📷", "color": C["teal"], "glow": "#0F9083",
        "title": "Take Attendance",
        "desc": "Live face recognition scan\nmarks attendance instantly",
        "steps": ["Choose registered subject", "Camera scans 20 seconds", "Saved as dated CSV"],
        "cmd": lambda: automaticAttedance.subjectChoose(text_to_speech),
    },
    {
        "icon": "📊", "color": C["purple"], "glow": "#6D28D9",
        "title": "View Records",
        "desc": "Browse attendance sheets\nwith % analytics",
        "steps": ["Choose registered subject", "View merged records", "Color-coded attendance %"],
        "cmd": lambda: show_attendance.subjectchoose(text_to_speech),
    },
]

import winsound
card_canvases = []

for idx, cd in enumerate(CARD_DEF):
    cx   = START_X + idx * (CARD_W + GAP)
    col  = cd["color"]
    glow = cd["glow"]

    cv  = tk.Canvas(window, width=CARD_W, height=CARD_H,
                    bg=C["bg"], highlightthickness=0, cursor="hand2")
    
    # ── Slide-in Animation ──
    start_y = CARDS_Y + 120
    cv.place(x=cx, y=start_y)
    
    def slide_up(canvas, current_y, target_y, speed=10, cx_val=cx):
        if current_y > target_y:
            next_y = max(target_y, current_y - speed)
            canvas.place(x=cx_val, y=next_y)
            window.after(16, lambda c=canvas, ny=next_y, ty=target_y, sp=speed, x=cx_val: slide_up(c, ny, ty, sp, x))

    window.after(idx * 150 + 200, lambda c=cv, sy=start_y, ty=CARDS_Y, x=cx: slide_up(c, sy, ty, speed=8, cx_val=x))

    def _draw_card(canvas, data, hovered=False):
        canvas.delete("all")
        color  = data["color"]
        glow_c = data["glow"]
        fill   = C["card2"] if hovered else C["card"]
        border = color      if hovered else C["border2"]
        bw     = 2          if hovered else 1

        # Shadow layer
        rrect(canvas, 4, 4, CARD_W-1, CARD_H-1, r=18,
              fill=C["bg"], outline="")
        # Card body
        rrect(canvas, 1, 1, CARD_W-4, CARD_H-4, r=18,
              fill=fill, outline=border, width=bw)
        # Top accent glow strip
        canvas.create_line(30, 2, CARD_W-30, 2, fill=color, width=3 if hovered else 2)
        if hovered:
            canvas.create_line(30, 1, CARD_W-30, 1, fill=glow_c, width=1)

        cx2, cy2, r2 = CARD_W//2, 66, 34
        icon_fill = C["card2"] if hovered else C["card"]
        canvas.create_oval(cx2-r2, cy2-r2, cx2+r2, cy2+r2,
                           fill=icon_fill, outline=color, width=2)
        canvas.create_text(cx2, cy2, text=data["icon"], font=F["card_ic"])

        canvas.create_text(CARD_W//2, 123, text=data["title"],
                           fill=C["white"] if hovered else C["text"],
                           font=F["card_t"])
        for li, line in enumerate(data["desc"].split("\n")):
            canvas.create_text(CARD_W//2, 144 + li*16, text=line,
                               fill=C["muted"], font=F["card_d"])

        step_y0 = 188
        bh = 17
        for si, step in enumerate(data["steps"]):
            sy = step_y0 + si * (bh + 3)
            if sy + bh > CARD_H - 8: break
            canvas.create_text(16, sy + bh//2, text=f"  {si+1}.", fill=color,
                               font=("Segoe UI", 8, "bold"), anchor="w")
            canvas.create_text(36, sy + bh//2, text=step, fill=C["muted"],
                               font=("Segoe UI", 8), anchor="w")

    _draw_card(cv, cd, hovered=False)
    card_canvases.append((cv, col, glow))

    def _bind(canvas, data, cmd):
        def _on_enter(e):
            _draw_card(canvas, data, True)
            try: winsound.Beep(900, 15)
            except: pass
        def _on_leave(e):
            _draw_card(canvas, data, False)
        def _on_click(e):
            try: winsound.Beep(1500, 40)
            except: pass
            cmd()
            
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        canvas.bind("<Button-1>", _on_click)
    _bind(cv, cd, cd["cmd"])


# ══════════════════════════════════════════════════════════════════
#  STATS STRIP
# ══════════════════════════════════════════════════════════════════
STATS_Y = CARDS_Y + CARD_H + 22
stats_canvas = tk.Canvas(window, width=1200, height=72,
                          bg=C["bg"], highlightthickness=0)
stats_canvas.place(x=40, y=STATS_Y)
rrect(stats_canvas, 0, 0, 1200, 72, r=12,
      fill=C["card"], outline=C["border"], width=1)

# compute stats
try:
    df_s        = pd.read_csv(studentdetail_path)
    student_cnt = len(df_s)
except Exception:
    student_cnt = 0

try:
    subs  = [d for d in os.listdir(attendance_path)
             if os.path.isdir(os.path.join(attendance_path, d))]
    sub_cnt = len(subs)
except Exception:
    sub_cnt = 0

model_stat  = ("Trained ✓", C["green"]) if os.path.exists(trainimagelabel_path) \
              else ("Not Trained", C["red"])

STATS = [
    (160,  f"{student_cnt}", "Registered Students",  C["blue"]),
    (400,  f"{sub_cnt}",     "Subjects Tracked",     C["purple"]),
    (640,  model_stat[0],    "Model Status",          model_stat[1]),
    (880,  datetime.datetime.now().strftime("%d %b"),  "Today's Date", C["cyan"]),
    (1060, datetime.datetime.now().strftime("%H:%M"),  "Current Time", C["amber"]),
]

for sx, val, label, color in STATS:
    stats_canvas.create_text(sx, 26, text=val,
                             fill=color, font=F["stat_n"], anchor="center")
    stats_canvas.create_text(sx, 54, text=label.upper(),
                             fill=C["muted"], font=("Segoe UI", 8), anchor="center")
    # Separator
    if sx < 1060:
        stats_canvas.create_line(sx+110, 16, sx+110, 56,
                                 fill=C["border"], width=1)


# ══════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════
footer = tk.Canvas(window, width=1280, height=56,
                   bg=C["bg"], highlightthickness=0)
footer.place(x=0, y=720-56)
footer.create_line(0, 0, 1280, 0, fill=C["border"])

TECH = ["OpenCV", "LBPH Face Recognizer", "Python 3", "NumPy", "Pandas", "Tkinter", "Pillow"]
tech_str = "  ·  ".join(TECH)
footer.create_text(640, 20, text=tech_str,
                   fill=C["dim"], font=("Segoe UI", 8), anchor="center")
footer.create_text(640, 40,
                   text="NexAttend  —  AI-Powered Face Recognition Attendance System  ·  Developed by  Yogesh Ravi M",
                   fill=C["muted"], font=("Segoe UI", 9), anchor="center")

# Exit button
exit_cv = tk.Canvas(footer, width=150, height=34,
                    bg=C["bg"], highlightthickness=0, cursor="hand2")
exit_cv.place(x=1100, y=11)

def _draw_exit(hovered=False):
    exit_cv.delete("all")
    if hovered:
        rrect(exit_cv, 0, 0, 150, 34, r=8, fill=C["red"], outline="")
        exit_cv.create_text(75, 17, text="⏻  Exit",
                            fill=C["white"], font=("Segoe UI", 11, "bold"))
    else:
        rrect(exit_cv, 0, 0, 150, 34, r=8, fill=C["card"],
              outline=C["red"], width=1)
        exit_cv.create_text(75, 17, text="⏻  Exit",
                            fill=C["red"], font=("Segoe UI", 11, "bold"))

_draw_exit()
exit_cv.bind("<Enter>",    lambda e: _draw_exit(True))
exit_cv.bind("<Leave>",    lambda e: _draw_exit(False))
exit_cv.bind("<Button-1>", lambda e: window.destroy())


window.mainloop()
