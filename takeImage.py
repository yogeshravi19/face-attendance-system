import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image

# ─── Base Directory ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    "bg":     "#0A0F1E",
    "panel":  "#0F1629",
    "card":   "#141E35",
    "border": "#1E2D50",
    "accent": "#4F8EF7",
    "green":  "#22C55E",
    "red":    "#EF4444",
    "amber":  "#F59E0B",
    "text":   "#E2E8F0",
    "muted":  "#64748B",
    "white":  "#FFFFFF",
}
FONTS = {
    "h2":    ("Segoe UI", 16, "bold"),
    "body":  ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "btn":   ("Segoe UI", 13, "bold"),
    "mono":  ("Consolas", 12, "bold"),
}

MAX_PHOTOS = 100


def TakeImage(l1, l2, haarcasecade_path, trainimage_path,
              message, err_screen, text_to_speech):
    """
    Open a live camera window (embedded in Tkinter) showing bounding box +
    student info. Automatically captures MAX_PHOTOS face images, then closes.
    All student details are saved to StudentDetails/studentdetails.csv.
    """
    if l1 == "" or l2 == "":
        err_screen()
        t = "Please enter Enrollment Number and Name."
        text_to_speech(t)
        return

    Enrollment = l1.strip()
    Name       = l2.strip()

    # ── Create output folder ──
    directory = Enrollment + "_" + Name
    path = os.path.join(trainimage_path, directory)
    os.makedirs(path, exist_ok=True)

    # ── Open camera ──
    # Prioritize index 1 (to bypass virtual cameras like DroidCam on index 0), with full fallbacks
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cam.isOpened():
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        cam = cv2.VideoCapture(1)
    if not cam.isOpened():
        cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        t = "Cannot open camera. Check that no other app is using it."
        text_to_speech(t)
        try:
            message.configure(text="  ✗  " + t, fg=COLORS["red"])
        except Exception:
            pass
        return

    detector = cv2.CascadeClassifier(haarcasecade_path)

    # ══════════════════════════════════════════════════
    #  Live Camera Popup
    # ══════════════════════════════════════════════════
    popup = tk.Toplevel()
    popup.title(f"Registering: {Name} ({Enrollment})")
    popup.configure(bg=COLORS["bg"])
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)  # disable X button while capturing

    # Header
    hdr = tk.Frame(popup, bg=COLORS["card"], pady=10)
    hdr.pack(fill=X)
    tk.Label(hdr, text=f"📷  Registering: {Name}  [{Enrollment}]",
             bg=COLORS["card"], fg=COLORS["white"], font=FONTS["h2"]).pack()
    tk.Label(hdr, text="Look directly at the camera — keep face in frame",
             bg=COLORS["card"], fg=COLORS["muted"], font=FONTS["small"]).pack(pady=(2, 0))

    # Camera canvas
    CAM_W, CAM_H = 640, 480
    cam_canvas = tk.Label(popup, bg=COLORS["bg"])
    cam_canvas.pack(padx=10, pady=8)

    # Status row
    status_frame = tk.Frame(popup, bg=COLORS["bg"])
    status_frame.pack(fill=X, padx=20, pady=(0, 8))

    # Photo counter badge
    counter_lbl = tk.Label(status_frame,
                           text=f"0 / {MAX_PHOTOS}  photos",
                           bg=COLORS["accent"], fg=COLORS["white"],
                           font=FONTS["mono"], padx=14, pady=6)
    counter_lbl.pack(side=LEFT)

    # Status message
    status_lbl = tk.Label(status_frame,
                          text="  Scanning for face…",
                          bg=COLORS["panel"], fg=COLORS["muted"],
                          font=FONTS["small"], padx=12, pady=6, anchor="w")
    status_lbl.pack(side=LEFT, fill=X, expand=True, padx=(8, 0))

    # Progress bar (manual)
    prog_canvas = tk.Canvas(popup, width=640, height=10,
                            bg=COLORS["panel"], highlightthickness=0)
    prog_canvas.pack(fill=X, padx=10)
    prog_rect = prog_canvas.create_rectangle(0, 0, 0, 10, fill=COLORS["accent"], outline="")

    # Close button (disabled until done)
    close_btn = tk.Button(popup, text="⏳  Capturing…  please wait",
                          state=DISABLED,
                          bg=COLORS["card"], fg=COLORS["muted"],
                          font=FONTS["btn"], bd=0, padx=20, pady=10)
    close_btn.pack(pady=(4, 14))

    sampleNum   = [0]
    done        = [False]
    imgtk_ref   = [None]   # prevent GC

    def finish():
        done[0] = True
        cam.release()
        cv2.destroyAllWindows()
        # Update caller's message label
        res = f"  ✓  {MAX_PHOTOS} images saved for {Name} ({Enrollment}). Now Train the Model."
        try:
            message.configure(text=res, fg=COLORS["green"])
        except Exception:
            pass
        text_to_speech(f"Registration complete for {Name}")
        # Save to CSV
        _save_to_csv(Enrollment, Name)
        # Enable close
        close_btn.configure(text="✓  Close Registration", state=NORMAL,
                            bg=COLORS["green"], fg=COLORS["white"],
                            cursor="hand2", command=popup.destroy)

    def update_frame():
        if done[0]:
            return

        ret, img = cam.read()
        if not ret or img is None:
            popup.after(30, update_frame)
            return

        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5,
                                          minSize=(60, 60))

        for (x, y, w, h) in faces:
            if sampleNum[0] < MAX_PHOTOS:
                sampleNum[0] += 1
                face_img = gray[y: y+h, x: x+w]
                fname = f"{Name}_{Enrollment}_{sampleNum[0]}.jpg"
                cv2.imwrite(os.path.join(path, fname), face_img)

            # Bounding box
            pct = sampleNum[0] / MAX_PHOTOS
            box_color = (0, int(220 * pct), int(120 + 135 * (1 - pct)))
            cv2.rectangle(img, (x, y), (x+w, y+h), box_color, 2)

            # Info label above box
            label_bg = img[max(0, y-30):y, x:x+w]
            cv2.rectangle(img, (x, max(0, y-32)), (x+w, y), box_color, -1)
            cv2.putText(img, f"{Enrollment} - {Name}", (x+4, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Progress bar inside frame
            bar_w = int(w * sampleNum[0] / MAX_PHOTOS)
            cv2.rectangle(img, (x, y+h+2), (x+bar_w, y+h+8), box_color, -1)

        # Resize for display
        display = cv2.resize(img, (CAM_W, CAM_H))
        display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(display)
        imgtk   = ImageTk.PhotoImage(image=pil_img)
        imgtk_ref[0] = imgtk
        cam_canvas.configure(image=imgtk)

        # Update counter + progress
        n = sampleNum[0]
        pct_bar = n / MAX_PHOTOS
        try:
            counter_lbl.configure(
                text=f"{n} / {MAX_PHOTOS}  photos",
                bg=COLORS["green"] if n >= MAX_PHOTOS else COLORS["accent"]
            )
            if n < MAX_PHOTOS:
                status_lbl.configure(text=f"  📸  Capturing face {n}…", fg=COLORS["text"])
            else:
                status_lbl.configure(text="  ✅  All photos captured!", fg=COLORS["green"])
            prog_canvas.coords(prog_rect, 0, 0, int(640 * pct_bar), 10)
        except Exception:
            pass

        if sampleNum[0] >= MAX_PHOTOS and not done[0]:
            finish()
            return

        popup.after(30, update_frame)

    # Start feed
    popup.after(100, update_frame)
    popup.grab_set()


# ══════════════════════════════════════════════════
#  Save student to CSV
# ══════════════════════════════════════════════════
def _save_to_csv(enrollment, name):
    csv_path = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Avoid duplicates
    existing = set()
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for e in df["Enrollment"].astype(str).tolist():
                existing.add(str(e))
        except Exception:
            pass

    if str(enrollment) not in existing:
        with open(csv_path, "a+", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            # Write header if file is empty
            if os.path.getsize(csv_path) == 0:
                writer.writerow(["Enrollment", "Name"])
            writer.writerow([enrollment, name])
