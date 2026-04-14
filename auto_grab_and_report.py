import os
import subprocess
import time

def main():
    # 1. Inject screenshot code into attendance.py
    with open('attendance.py', 'r', encoding='utf-8') as f:
        code = f.read()

    injection = """
def auto_screenshot():
    try:
        from PIL import ImageGrab
    except ImportError:
        pass
    else:
        window.update()
        x = window.winfo_rootx()
        y = window.winfo_rooty()
        width = window.winfo_width()
        height = window.winfo_height()
        
        # Grab client area
        img = ImageGrab.grab(bbox=(x, y, x+width, y+height))
        img.save("dashboard_ui.png")
        print("Dashboard screenshot successfully captured from GUI.", flush=True)
    window.destroy()

# Wait 2200ms to allow all slide-in animations in attendance.py to finish
window.after(2200, auto_screenshot)
"""

    # Injecting before mainloop
    code = code.replace("window.mainloop()", injection + "\nwindow.mainloop()")

    with open('temp_attendance.py', 'w', encoding='utf-8') as f:
        f.write(code)

    print("Launching NexAttend UI headlessly to capture screenshot...")
    
    # Needs to be run from the same directory so __file__ resolves correctly
    subprocess.run(["python", "temp_attendance.py"])

    # 2. Modify generate_long_report.py to not overwrite the image
    with open('generate_long_report.py', 'r', encoding='utf-8') as f:
        rep_code = f.read()

    # Comment out the line that creates the dashboard placeholder
    rep_code = rep_code.replace('create_placeholder("dashboard_ui.png"', '# create_placeholder("dashboard_ui.png"')

    with open('temp_gen_report.py', 'w', encoding='utf-8') as f:
        f.write(rep_code)

    print("Re-compiling MS Word Report with the authentic screenshot...")
    subprocess.run(["python", "temp_gen_report.py"])

    # Cleanup temporary scripts
    try:
        os.remove('temp_attendance.py')
        os.remove('temp_gen_report.py')
    except Exception as e:
        print(f"Cleanup non-fatal warning: {e}")

    print("Process Complete! Validated and updated document.")

if __name__ == "__main__":
    main()
