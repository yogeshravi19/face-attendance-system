import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import Image


def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    """Train LBPH face recognizer from captured images and save model."""
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, ids = getImagesAndLabels(trainimage_path)

        if len(faces) == 0:
            msg = "No training images found — register students first"
            message.configure(text="  ✗  " + msg)
            text_to_speech(msg)
            return

        recognizer.train(faces, np.array(ids))

        # Ensure output directory exists
        label_dir = os.path.dirname(trainimagelabel_path)
        os.makedirs(label_dir, exist_ok=True)
        recognizer.save(trainimagelabel_path)

        res = f"  ✓  Model trained on {len(set(ids))} student(s) — {len(faces)} images"
        message.configure(text=res)
        text_to_speech("Model trained successfully")

    except Exception as e:
        msg = f"Training error: {e}"
        message.configure(text="  ✗  " + msg[:70])
        text_to_speech("Training failed")


def getImagesAndLabels(path):
    """
    Walk TrainingImage/<Enrollment_Name>/<Name_Enrollment_N.jpg>
    and return (face_arrays, enrollment_id_list).
    Filename format: Name_Enrollment_SampleNum.jpg  → index [1] = Enrollment
    """
    faces = []
    ids   = []

    if not os.path.exists(path):
        return faces, ids

    for student_dir in os.listdir(path):
        student_path = os.path.join(path, student_dir)
        if not os.path.isdir(student_path):
            continue
        for fname in os.listdir(student_path):
            if not fname.lower().endswith(".jpg"):
                continue
            img_path = os.path.join(student_path, fname)
            try:
                # filename: Name_Enrollment_N.jpg  → parts[1] = Enrollment
                parts = os.path.splitext(fname)[0].split("_")
                enr_id = int(parts[1])
                pil_img = Image.open(img_path).convert("L")
                img_arr = np.array(pil_img, "uint8")
                faces.append(img_arr)
                ids.append(enr_id)
            except (IndexError, ValueError, Exception):
                # Skip files that don't match naming convention
                continue

    return faces, ids
