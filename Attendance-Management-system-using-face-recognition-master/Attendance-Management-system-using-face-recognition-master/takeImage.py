import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time

# ─── Base Directory ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# take Image of user
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen, text_to_speech):
    if (l1 == "") and (l2 == ""):
        t = 'Please Enter the your Enrollment Number and Name.'
        text_to_speech(t)
    elif l1 == '':
        t = 'Please Enter the your Enrollment Number.'
        text_to_speech(t)
    elif l2 == "":
        t = 'Please Enter the your Name.'
        text_to_speech(t)
    else:
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                text_to_speech("Cannot open camera")
                message.configure(text="  ✗  Cannot open camera")
                return
            detector = cv2.CascadeClassifier(haarcasecade_path)
            Enrollment = l1
            Name = l2
            sampleNum = 0
            directory = Enrollment + "_" + Name
            path = os.path.join(trainimage_path, directory)
            os.makedirs(path, exist_ok=True)
            while True:
                ret, img = cam.read()
                if not ret or img is None:
                    break
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sampleNum = sampleNum + 1
                    cv2.imwrite(
                        os.path.join(path, Name + "_" + Enrollment + "_" + str(sampleNum) + ".jpg"),
                        gray[y: y + h, x: x + w],
                    )
                    cv2.imshow("Frame", img)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                elif sampleNum > 50:
                    break
            cam.release()
            cv2.destroyAllWindows()
            row = [Enrollment, Name]
            studentdetail_csv = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
            with open(studentdetail_csv, "a+") as csvFile:
                writer = csv.writer(csvFile, delimiter=",")
                writer.writerow(row)
            res = "Images Saved for ER No:" + Enrollment + " Name:" + Name
            message.configure(text=res)
            text_to_speech(res)
        except FileExistsError as F:
            F = "Student Data already exists"
            text_to_speech(F)
