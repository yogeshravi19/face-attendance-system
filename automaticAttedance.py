import tkinter as tk
from tkinter import *
import os, cv2
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk

# ─── Base Directory ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Paths ───
haarcasecade_path     = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path  = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path       = os.path.join(BASE_DIR, "TrainingImage")
studentdetail_path    = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
attendance_path       = os.path.join(BASE_DIR, "Attendance")

COLORS = {
    "bg":      "#050511", "panel":   "#0A0B1A", "card":   "#0D0E20",
    "card2":   "#151733", "glass":   "#0F1126", "border": "#1D1E3A",
    "border2": "#2A2D5C", "white":   "#FFFFFF", "text":   "#E2E8F0",
    "muted":   "#828CA0", "dim":     "#4A5568",
    "accent":  "#2563EB", "cyan":    "#00F0FF", "teal":   "#0AF5C6",
    "green":   "#00FF66", "red":     "#FF003C", "amber":  "#FFB000",
    "purple":  "#9D4EDD", "pink":    "#FF007F",
}
FONTS = {
    "h1":    ("Segoe UI", 20, "bold"),
    "h2":    ("Segoe UI", 15, "bold"),
    "h3":    ("Segoe UI", 12, "bold"),
    "body":  ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "btn":   ("Segoe UI", 13, "bold"),
    "badge": ("Segoe UI", 8, "bold"),
    "mono":  ("Consolas", 11, "bold"),
    "tbl":   ("Segoe UI", 11),
    "tbl_h": ("Segoe UI", 11, "bold"),
}

SCAN_SECONDS = 20   # how long to run the camera scan

CAM_W, CAM_H = 640, 480   # display size inside window


def _safe_cfg(widget, **kw):
    try:
        if widget.winfo_exists():
            widget.configure(**kw)
    except Exception:
        pass


def _load_subjects():
    """Load subjects from SubjectsDetails/subjects.csv."""
    csv_path = os.path.join(BASE_DIR, "SubjectsDetails", "subjects.csv")
    subjects = []
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            subjects = df.to_dict("records")
        except Exception:
            pass
    return subjects


def subjectChoose(text_to_speech):

    # ══════════════════════════════════════════════════
    #  Subject Chooser Window
    # ══════════════════════════════════════════════════
    win = tk.Toplevel()
    win.title("NexAttend — Take Attendance")
    win.geometry("720x450")
    win.resizable(False, True)
    win.configure(background=COLORS["bg"])
    win.attributes("-topmost", True)

    # Header
    hdr = tk.Canvas(win, width=720, height=82, bg=COLORS["bg"], highlightthickness=0)
    hdr.pack(fill=X)
    for i in range(82):
        t = i/82; r2=int(0x07+t*6); g2=int(0x09+t*8); b2=int(0x0F+t*18)
        hdr.create_line(0, i, 720, i, fill=f"#{r2:02x}{g2:02x}{b2:02x}")
    hdr.create_text(360, 28, text="📷  Take Attendance",
                    fill=COLORS["white"], font=FONTS["h1"], anchor="center")
    hdr.create_text(360, 54, text="Select a registered subject · camera scans for 20 seconds",
                    fill=COLORS["muted"], font=FONTS["small"], anchor="center")
    accent_cols = ["#0A2040","#1D4ED8","#3B82F6","#60A5FA","#3B82F6","#1D4ED8","#0A2040"]
    sw = 720 // len(accent_cols)
    for i, col in enumerate(accent_cols):
        hdr.create_line(i*sw, 81, (i+1)*sw, 81, fill=col, width=2)

    # ── Subject Picker Card ──
    pick_frame = tk.Frame(win, bg=COLORS["card"],
                          highlightbackground=COLORS["border2"],
                          highlightthickness=1)
    pick_frame.pack(fill=BOTH, expand=True, padx=20, pady=12)

    top_row = tk.Frame(pick_frame, bg=COLORS["card"])
    top_row.pack(fill=X, padx=14, pady=(12, 4))
    tk.Label(top_row, text="SELECT SUBJECT", bg=COLORS["card"],
             fg=COLORS["accent"], font=FONTS["badge"]).pack(side=LEFT)

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
                fg=COLORS["amber"])

    ref_btn = tk.Button(top_row, text="↻  Refresh",
                        command=refresh_list,
                        bg=COLORS["card2"], fg=COLORS["muted"],
                        font=("Segoe UI", 9, "bold"), bd=0,
                        padx=10, pady=3, cursor="hand2")
    ref_btn.pack(side=RIGHT)

    # Treeview
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Sub.Treeview",
                     background=COLORS["glass"], foreground=COLORS["text"],
                     rowheight=32, fieldbackground=COLORS["glass"],
                     bordercolor=COLORS["border"], borderwidth=0,
                     font=FONTS["tbl"])
    style.configure("Sub.Treeview.Heading",
                     background=COLORS["border2"], foreground=COLORS["accent"],
                     font=FONTS["tbl_h"], relief="flat")
    style.map("Sub.Treeview",
              background=[("selected", COLORS["accent"])],
              foreground=[("selected", COLORS["white"])])

    tree_wrap = tk.Frame(pick_frame, bg=COLORS["card"])
    tree_wrap.pack(fill=BOTH, expand=True, padx=14, pady=(0, 8))

    tree = ttk.Treeview(tree_wrap, style="Sub.Treeview",
                        columns=("Subject", "Faculty", "Slot"),
                        show="headings", selectmode="browse", height=6)
    tree.heading("Subject", text="Subject Name")
    tree.heading("Faculty", text="Faculty Name")
    tree.heading("Slot",    text="Slot / Timing")
    tree.column("Subject", width=200, anchor="w")
    tree.column("Faculty", width=200, anchor="w")
    tree.column("Slot",    width=250, anchor="w")

    vsb_t = ttk.Scrollbar(tree_wrap, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=vsb_t.set)
    vsb_t.pack(side=RIGHT, fill=Y)
    tree.pack(fill=BOTH, expand=True)

    # Selected subject label
    sel_frame = tk.Frame(pick_frame, bg=COLORS["card"])
    sel_frame.pack(fill=X, padx=14, pady=(0, 4))
    tk.Label(sel_frame, text="SELECTED:", bg=COLORS["card"],
             fg=COLORS["muted"], font=FONTS["badge"]).pack(side=LEFT)
    sel_lbl = tk.Label(sel_frame, text="  — none —",
                       bg=COLORS["card2"], fg=COLORS["teal"],
                       font=("Segoe UI", 11, "bold"), padx=10, pady=3)
    sel_lbl.pack(side=LEFT, padx=6)

    def on_select(e):
        sel = tree.selection()
        if sel:
            val = tree.item(sel[0])["values"]
            sel_lbl.configure(text=f"  {val[0]}  ·  {val[1]}  ·  {val[2]}")

    tree.bind("<<TreeviewSelect>>", on_select)
    tree.bind("<Double-1>", lambda e: start_scan())

    refresh_list()

    notif = tk.Label(win,
                     text="  ℹ  Click a subject to select, then press Fill Attendance",
                     bg=COLORS["panel"], fg=COLORS["muted"],
                     font=FONTS["small"], anchor="w", padx=14, pady=8)
    notif.pack(fill=X, padx=20, pady=(0, 8))

    # ── subject_var used by start_scan ──
    subject_var = tk.StringVar()

    def _get_selected_subject():
        sel = tree.selection()
        if sel:
            return tree.item(sel[0])["values"][0]
        return ""



    # ══════════════════════════════════════════════════
    #  Camera Scan Window (opened after subject entry)
    # ══════════════════════════════════════════════════
    def start_scan():
        sub = _get_selected_subject()
        if not sub:
            _safe_cfg(notif,
                      text="  ⚠  Please select a subject from the list above!",
                      fg=COLORS["amber"])
            text_to_speech("Please select a subject")
            return

        # Validate model
        if not os.path.exists(trainimagelabel_path):
            msg = "Model not found — register students & train model first"
            _safe_cfg(notif, text="  ✗  " + msg, fg=COLORS["red"])
            text_to_speech(msg)
            return

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(trainimagelabel_path)
        except Exception as e:
            _safe_cfg(notif, text=f"  ✗  Cannot load model: {str(e)[:50]}", fg=COLORS["red"])
            text_to_speech("Cannot load model")
            return

        try:
            df_students = pd.read_csv(studentdetail_path)
        except FileNotFoundError:
            _safe_cfg(notif, text="  ✗  No student records found. Register students first.", fg=COLORS["red"])
            return

        # Open camera
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            # Try index 1 as fallback
            cam = cv2.VideoCapture(1)
        if not cam.isOpened():
            _safe_cfg(notif, text="  ✗  Camera not found. Connect a camera and retry.", fg=COLORS["red"])
            text_to_speech("Camera not found")
            return

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        faceCascade = cv2.CascadeClassifier(haarcasecade_path)
        col_names   = ["Enrollment", "Name"]
        attend_df   = pd.DataFrame(columns=col_names)

        # ── Scan popup ──
        scan_win = tk.Toplevel(win)
        scan_win.title(f"Scanning — {sub}")
        scan_win.configure(bg=COLORS["bg"])
        scan_win.resizable(False, False)
        scan_win.attributes("-topmost", True)
        scan_win.protocol("WM_DELETE_WINDOW", lambda: None)  # block close

        # Banner
        bhdr = tk.Frame(scan_win, bg=COLORS["card"], pady=10)
        bhdr.pack(fill=X)
        tk.Label(bhdr, text=f"📷  Live Scan — {sub.upper()}",
                 bg=COLORS["card"], fg=COLORS["white"], font=FONTS["h2"]).pack()
        sub_status = tk.Label(bhdr, text="Initialising camera…",
                              bg=COLORS["card"], fg=COLORS["muted"], font=FONTS["small"])
        sub_status.pack(pady=(2, 0))

        # Camera frame
        cam_lbl = tk.Label(scan_win, bg=COLORS["bg"])
        cam_lbl.pack(padx=8, pady=6)

        # Stats row
        stat_row = tk.Frame(scan_win, bg=COLORS["bg"])
        stat_row.pack(fill=X, padx=12, pady=(0, 4))

        timer_lbl = tk.Label(stat_row,
                             text=f"⏱  {SCAN_SECONDS}s remaining",
                             bg=COLORS["panel"], fg=COLORS["accent"],
                             font=FONTS["mono"], padx=14, pady=6)
        timer_lbl.pack(side=LEFT)

        found_lbl = tk.Label(stat_row,
                             text="  👤  0 student(s) detected",
                             bg=COLORS["panel"], fg=COLORS["muted"],
                             font=FONTS["small"], padx=14, pady=6, anchor="w")
        found_lbl.pack(side=LEFT, fill=X, expand=True, padx=(6, 0))

        # Progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Scan.Horizontal.TProgressbar",
                        troughcolor=COLORS["panel"],
                        background=COLORS["accent"],
                        bordercolor=COLORS["border"],
                        lightcolor=COLORS["accent"],
                        darkcolor=COLORS["accent"])
        prog = ttk.Progressbar(scan_win, style="Scan.Horizontal.TProgressbar",
                               orient="horizontal", length=CAM_W + 16,
                               mode="determinate", maximum=SCAN_SECONDS)
        prog.pack(padx=8, pady=(0, 6))

        # Close button (disabled until done)
        close_btn = tk.Button(scan_win, text="⏳  Scanning… please wait",
                              state=DISABLED,
                              bg=COLORS["card"], fg=COLORS["muted"],
                              font=FONTS["btn"], bd=0, padx=20, pady=10)
        close_btn.pack(pady=(0, 12))

        imgtk_ref = [None]
        stopped   = [False]
        start_ts  = time.time()

        def stop_and_save(reason="done"):
            if stopped[0]:
                return
            stopped[0] = True
            cam.release()

            # Save CSV
            attend_df.drop_duplicates(["Enrollment"], keep="first", inplace=True)
            date_s = datetime.datetime.now().strftime("%Y-%m-%d")
            time_s = datetime.datetime.now().strftime("%H-%M-%S")
            sub_folder = os.path.join(attendance_path, sub)
            os.makedirs(sub_folder, exist_ok=True)
            fname = os.path.join(sub_folder, f"{sub}_{date_s}_{time_s}.csv")
            attend_df_out = attend_df.copy()
            attend_df_out[date_s] = 1
            attend_df_out.to_csv(fname, index=False)

            n = len(attend_df)
            msg = f"Attendance saved — {n} student(s) marked for {sub}"
            _safe_cfg(notif, text=f"  ✓  {msg}", fg=COLORS["green"])
            _safe_cfg(sub_status, text="✅  Scan complete", fg=COLORS["green"])
            text_to_speech(msg)

            # Enable close
            _safe_cfg(close_btn,
                      text=f"✓  Close  ({n} student(s) recorded)",
                      state=NORMAL,
                      bg=COLORS["green"], fg=COLORS["white"],
                      cursor="hand2")
            close_btn.configure(command=lambda: [scan_win.destroy(), _show_results(win, sub, fname)])

        def update():
            if stopped[0]:
                return

            elapsed   = time.time() - start_ts
            remaining = max(0, SCAN_SECONDS - elapsed)

            ret, frame = cam.read()
            if not ret or frame is None:
                scan_win.after(30, update)
                return

            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray  = cv2.equalizeHist(gray)
            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2,
                                                 minNeighbors=5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                if conf < 70:
                    rows = df_students.loc[df_students["Enrollment"] == Id]["Name"].values
                    name = rows[0] if len(rows) > 0 else "?"
                    label = f"  {Id} — {name}  "
                    color = (0, 220, 100)   # green — known
                    attend_df.loc[len(attend_df)] = [Id, name]
                else:
                    label = "  Unknown  "
                    color = (0, 80, 255)    # red-blue — unknown

                # Bounding box
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

                # Label background pill
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                cv2.rectangle(frame, (x, y - th - 14), (x + tw + 8, y), color, -1)
                cv2.putText(frame, label, (x + 4, y - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                            cv2.LINE_AA)

                # Mini progress strip inside box
                bar_pct = max(0, 1 - elapsed / SCAN_SECONDS)
                cv2.rectangle(frame, (x, y + h + 2),
                              (x + int(w * bar_pct), y + h + 6), color, -1)

            attend_df.drop_duplicates(["Enrollment"], keep="first", inplace=True)

            # Overlay timer
            cv2.putText(frame, f"⏱ {int(remaining)}s", (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 220, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Subject: {sub}", (10, 56),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)

            # Convert & display
            display = cv2.resize(frame, (CAM_W, CAM_H))
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(display)
            imgtk   = ImageTk.PhotoImage(image=pil_img)
            imgtk_ref[0] = imgtk
            _safe_cfg(cam_lbl, image=imgtk)

            # Update widgets
            n = len(attend_df)
            _safe_cfg(timer_lbl, text=f"⏱  {int(remaining)}s remaining")
            _safe_cfg(found_lbl, text=f"  👤  {n} student(s) detected",
                      fg=COLORS["green"] if n > 0 else COLORS["muted"])
            _safe_cfg(sub_status, text=f"Scanning…  {int(elapsed)}s elapsed")
            try:
                if prog.winfo_exists():
                    prog["value"] = elapsed
            except Exception:
                pass

            if elapsed >= SCAN_SECONDS:
                stop_and_save("timer")
                return

            scan_win.after(30, update)

        scan_win.after(200, update)

    # ══════════════════════════════════════════════════
    #  Results popup after scan closes
    # ══════════════════════════════════════════════════
    def _show_results(parent, subject_name, csv_path):
        if not os.path.exists(csv_path):
            return
        popup = tk.Toplevel(parent)
        popup.title(f"Attendance — {subject_name}")
        popup.configure(bg=COLORS["bg"])
        popup.attributes("-topmost", True)
        popup.resizable(True, True)

        # Header
        hdr2 = tk.Frame(popup, bg=COLORS["card"], pady=12)
        hdr2.pack(fill=X)
        tk.Label(hdr2, text=f"📋  Attendance — {subject_name.upper()}",
                 bg=COLORS["card"], fg=COLORS["white"], font=FONTS["h2"]).pack()
        tk.Label(hdr2, text=datetime.datetime.now().strftime("%d %B %Y  •  %H:%M"),
                 bg=COLORS["card"], fg=COLORS["muted"], font=FONTS["small"]).pack()
        tk.Frame(popup, bg=COLORS["border"], height=1).pack(fill=X)

        # Scrollable table
        wrap = tk.Frame(popup, bg=COLORS["bg"])
        wrap.pack(fill=BOTH, expand=True, padx=16, pady=12)
        vsb = tk.Scrollbar(wrap, orient=VERTICAL)
        hsb = tk.Scrollbar(wrap, orient=HORIZONTAL)
        cnv = tk.Canvas(wrap, bg=COLORS["bg"], highlightthickness=0,
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.configure(command=cnv.yview)
        hsb.configure(command=cnv.xview)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        cnv.pack(side=LEFT, fill=BOTH, expand=True)
        tf = tk.Frame(cnv, bg=COLORS["bg"])
        tf.bind("<Configure>", lambda e: cnv.configure(scrollregion=cnv.bbox("all")))
        cnv.create_window((0, 0), window=tf, anchor="nw")

        try:
            with open(csv_path, newline="") as f:
                for r, row in enumerate(csv.reader(f)):
                    is_hdr = (r == 0)
                    for c, cell in enumerate(row):
                        bg = COLORS["border"] if is_hdr else (COLORS["card"] if r % 2 == 0 else COLORS["panel"])
                        fg = COLORS["accent"] if is_hdr else COLORS["text"]
                        fn = ("Segoe UI", 11, "bold") if is_hdr else ("Segoe UI", 11)
                        tk.Label(tf, text=cell, width=18, height=1,
                                 bg=bg, fg=fg, font=fn, padx=8, pady=5,
                                 relief=FLAT).grid(row=r, column=c, sticky="nsew",
                                                   padx=1, pady=1)
        except Exception as e:
            tk.Label(tf, text=f"Error: {e}", bg=COLORS["bg"],
                     fg=COLORS["red"]).pack()

        tk.Button(popup, text="✓  Close",
                  command=popup.destroy,
                  bg=COLORS["accent"], fg=COLORS["white"],
                  activebackground="#3B70D4",
                  font=FONTS["btn"], bd=0, padx=28, pady=10,
                  cursor="hand2").pack(pady=(4, 14))

    # ══════════════════════════════════════════════════
    #  Open Folder
    # ══════════════════════════════════════════════════
    def open_folder():
        sub = _get_selected_subject()
        target = os.path.join(attendance_path, sub)
        if sub and os.path.exists(target):
            os.startfile(target)
        else:
            _safe_cfg(notif, text="  ✗  No records found for selected subject", fg=COLORS["red"])

    # Buttons
    btn_row = tk.Frame(win, bg=COLORS["bg"])
    btn_row.pack(pady=8)

    fill_btn = tk.Button(btn_row, text="▶  Fill Attendance",
                         command=start_scan,
                         bg=COLORS["green"], fg=COLORS["white"],
                         activebackground="#16A34A",
                         font=FONTS["btn"], bd=0, padx=26, pady=10, cursor="hand2")
    fill_btn.grid(row=0, column=0, padx=10)

    folder_btn = tk.Button(btn_row, text="📂  Open Records",
                           command=open_folder,
                           bg=COLORS["card"], fg=COLORS["text"],
                           activebackground=COLORS["border2"],
                           font=("Segoe UI", 12, "bold"), bd=0, padx=26, pady=10,
                           cursor="hand2",
                           highlightthickness=1, highlightbackground=COLORS["border"])
    folder_btn.grid(row=0, column=1, padx=10)

    fill_btn.bind("<Enter>",   lambda e: fill_btn.configure(bg="#16A34A"))
    fill_btn.bind("<Leave>",   lambda e: fill_btn.configure(bg=COLORS["green"]))
    folder_btn.bind("<Enter>", lambda e: folder_btn.configure(bg=COLORS["border2"]))
    folder_btn.bind("<Leave>", lambda e: folder_btn.configure(bg=COLORS["card"]))

