import os
import subprocess

def construct_script():
    with open('attendance.py', 'r', encoding='utf-8') as f:
        code = f.read()

    injection = """
def grab_sequence():
    from PIL import ImageGrab
    import time
    
    def snap(win, name):
        win.update()
        time.sleep(1.0)
        x = win.winfo_rootx()
        y = win.winfo_rooty()
        w = win.winfo_width()
        h = win.winfo_height()
        
        if w < 50 or h < 50:
            print(f"Skipping {name} - invalid dimensions. w:{w} h:{h}")
            win.destroy()
            return

        img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        img.save(name)
        print(f"Captured {name}", flush=True)
        win.destroy()

    try:
        # Window 1: Register Student
        TakeImageUI()
        window.update()
        t = [c for c in window.winfo_children() if isinstance(c, Toplevel)][-1]
        snap(t, "reg_student.png")

        # Window 2: Register Subject
        registerSubject.open_register_subject()
        window.update()
        t = [c for c in window.winfo_children() if isinstance(c, Toplevel)][-1]
        snap(t, "reg_subject.png")

        # Window 3: Take Attendance
        automaticAttedance.subjectChoose(lambda m: None)
        window.update()
        t = [c for c in window.winfo_children() if isinstance(c, Toplevel)][-1]
        snap(t, "take_attendance.png")

        # Window 4: View Records
        show_attendance.subjectchoose(lambda m: None)
        window.update()
        t = [c for c in window.winfo_children() if isinstance(c, Toplevel)][-1]
        snap(t, "view_records.png")

    except Exception as e:
        print(f"Error during sequence: {e}")

    print("Sub-windows captured. Terminating...", flush=True)
    window.destroy()

# Wait for main application animations to settle
window.after(2500, grab_sequence)
"""
    
    code = code.replace("window.mainloop()", injection + "\nwindow.mainloop()")

    with open('temp_mega.py', 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == "__main__":
    print("Constructing sequence script...", flush=True)
    construct_script()
    print("Executing graphical sequence grabber...", flush=True)
    subprocess.run(["python", "temp_mega.py"])
    try:
        os.remove("temp_mega.py")
    except:
        pass
    print("Capture complete.", flush=True)
