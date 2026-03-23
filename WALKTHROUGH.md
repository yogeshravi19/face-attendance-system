# 🎓 Face Attendance System — Walkthrough

## Prerequisites

1. **Python 3.8+** installed
2. Install required packages:
   ```
   pip install opencv-contrib-python numpy pandas Pillow pyttsx3
   ```
3. A **webcam** connected to your laptop

---

## How to Run

```bash
cd "c:\Users\INDIA\Downloads\Face-Attendance-System\Attendance-Management-system-using-face-recognition-master\Attendance-Management-system-using-face-recognition-master"
python attendance.py
```

The main window will open with **3 cards**: Register Student, Take Attendance, and View Records.

---

## Step-by-Step Usage

### 1️⃣ Register a Student
1. Click **Register Student** card
2. Enter the **Enrollment Number** (digits only) and **Student Name**
3. Click **📷 Take Image** — your webcam will open and capture 50 face images
4. Press **Q** to stop early if needed
5. Click **🧠 Train Model** — this trains the face recognizer on all captured images

> ⚠ You must **Train Model** after registering every new student!

### 2️⃣ Take Attendance
1. Click **Take Attendance** card
2. Enter the **Subject Name** (e.g. `dip`, `dsba`, `math`)
3. Click **▶ Fill Attendance** — webcam opens and scans faces for 20 seconds
4. Recognized students are auto-marked present
5. A CSV file is saved in `Attendance/<subject>/` folder
6. Press **ESC** to stop scanning early

### 3️⃣ View Attendance Records
1. Click **View Records** card
2. Enter the same **Subject Name**
3. Click **📊 View Attendance** — shows a table with attendance percentages
4. Click **📂 Open Folder** to browse raw CSV files

---

## Project Structure

```
├── attendance.py            ← Main app (run this)
├── takeImage.py             ← Captures face images
├── trainImage.py            ← Trains the LBPH recognizer
├── automaticAttedance.py    ← Auto face-recognition attendance
├── show_attendance.py       ← View/calculate attendance reports
├── takemanually.py          ← Manual attendance entry
├── haarcascade_frontalface_default.xml  ← Face detection model
├── TrainingImage/           ← Stored face images per student
├── TrainingImageLabel/      ← Trained model (Trainner.yml)
├── StudentDetails/          ← Student enrollment CSV
└── Attendance/              ← Attendance CSVs per subject
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "Cannot open camera" | Check webcam is connected and not used by another app |
| "Model not found" | Click **Train Model** in Register Student first |
| Red errors in VS Code | Set correct Python interpreter (`Ctrl+Shift+P` → "Python: Select Interpreter") |
| `ModuleNotFoundError` | Run `pip install opencv-contrib-python numpy pandas Pillow pyttsx3` |
