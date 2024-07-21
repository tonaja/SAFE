import datetime
import os
import time
import cv2
import pandas as pd
import numpy as np
import dlib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import sys

# Set the working directory to the directory containing your script
os.chdir(r'C:\Users\cairo\Downloads\Telegram Desktop\flask project\flask project\website')

# Ensure the directory is in the Python path
sys.path.append(r'C:\Users\cairo\Downloads\Telegram Desktop\flask project\flask project\website')

def calculate_metrics(true_labels, predicted_labels):
    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, average='weighted')
    recall = recall_score(true_labels, predicted_labels, average='weighted')
    f1 = f1_score(true_labels, predicted_labels, average='weighted')
    return accuracy, precision, recall, f1

def recognize_attendance(time_str):
    # Map of time strings to durations in minutes
    time_map = {
        "1 Hour": 60,
        "1:30 Hours": 90,
        "1:40 Hours": 100,
        "2 Hours": 120,
    }

    if time_str not in time_map:
        return "Invalid time format.", None

    lecture_duration = time_map[time_str]

    # Initialize the LBPH face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read(os.path.join("TrainingImageLabel", "Trainner.yml"))
    except cv2.error as e:
        return f"Error loading face recognizer model: {e}", None

    shape_predictor_path = r'shape_predictor_68_face_landmarks.dat'
    face_recognition_model_path = r'dlib_face_recognition_resnet_model_v1.dat'
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor_path)
    face_recognizer = dlib.face_recognition_model_v1(face_recognition_model_path)

    df = pd.read_csv(os.path.join("StudentDetails", "StudentDetails.csv"))
    df.columns = df.columns.str.strip()  # Strip any extra whitespace from column names

    # Create a dictionary for quick look-up of names by ID
    names_dict = {row['Id']: row['Name'] for _, row in df.iterrows()}

    font = cv2.FONT_HERSHEY_SIMPLEX

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)  # Set the width to 640 pixels
    cam.set(4, 480)  # Set the height to 480 pixels
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    entry_time = {}
    attendance_records = []
    true_labels = []
    predicted_labels = []

    start_time = time.time()

    while True:
        ret, im = cam.read()  # rem boolean value , im actual frame from vid (NumPY)
        if not ret:
            break

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            cv2.rectangle(im, (x1, y1), (x2, y2), (10, 159, 255), 2)

            shape = predictor(gray, face)
            face_img = gray[y1:y2, x1:x2]

            try:
                Id, confidence = recognizer.predict(face_img)
            except cv2.error as e:
                print(f"Error during prediction: {e}")
                continue

            student_name = names_dict.get(Id, "Unknown")

            if confidence < 100:  # threshold (100).
                student_info = df[df['Id'] == Id]
                if not student_info.empty:
                    name = student_info['Name'].values[0]
                    confstr = "  {0}%".format(round(100 - confidence))
                    tt = f"{Id}-{name}"
                else:
                    Id = 'Unknown'
                    tt = str(Id)
                    confstr = "  {0}%".format(round(100 - confidence))
            else:
                Id = 'Unknown'
                tt = str(Id)
                confstr = "  {0}%".format(round(100 - confidence))

            true_labels.append(student_name)
            predicted_labels.append(name if confidence < 100 else "Unknown")

            if (100 - confidence) > 55:
                if Id not in entry_time and Id != 'Unknown':
                    entry_time[Id] = datetime.datetime.now()
                tt = f"{tt} [Pass]"
                cv2.putText(im, str(tt), (x1 + 5, y1 - 5), font, 1, (255, 255, 255), 2)
            else:
                if Id != 'Unknown' and Id in entry_time:
                    exit_time = datetime.datetime.now()
                    attendance_records.append({
                        'Id': Id, 'Name': name, 'Entry Time': entry_time[Id], 'Exit Time': exit_time
                    })
                    del entry_time[Id]
                cv2.putText(im, str(tt), (x1 + 5, y1 - 5), font, 1, (255, 255, 255), 2)

            color = (0, 255, 0) if (100 - confidence) > 67 else (0, 255, 255) if (100 - confidence) > 50 else (0, 0, 255)
            cv2.putText(im, str(confstr), (x1 + 5, y2 - 5), font, 1, color, 1)

        cv2.imshow('Attendance', im)

        if time.time() - start_time > lecture_duration * 60:
            for Id in entry_time:
                exit_time = datetime.datetime.now()
                name = df.loc[df['Id'] == Id]['Name'].values[0]
                attendance_records.append({
                    'Id': Id, 'Name': name, 'Entry Time': entry_time[Id], 'Exit Time': exit_time
                })
            break

        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    if attendance_records:
        attendance = pd.DataFrame(attendance_records, columns=['Id', 'Name', 'Entry Time', 'Exit Time'])

        if not os.path.exists('Attendance'):
            os.makedirs('Attendance')

        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%H-%M-%S')
        attendance_file = f"Attendance{os.sep}Attendance_{date}_{time_str}.csv"
        attendance.to_csv(attendance_file, index=False)

        attendance_percentage = calculate_attendance_percentage(df, attendance, lecture_duration)
        percentage_file = f"Attendance{os.sep}Attendance_Percentage_{date}_{time_str}.csv"
        attendance_percentage.to_csv(percentage_file, index=False)
        accuracy, precision, recall, f1 = calculate_metrics(true_labels, predicted_labels)
        print(f"Accuracy: {accuracy}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F1 Score: {f1}")

        return "Attendance records have been saved.", percentage_file

    return "No attendance records found", None

def calculate_attendance_percentage(student_df, attendance_df, lecture_duration):
    attendance_percentage = []
    for index, row in student_df.iterrows():
        student_id = row['Id']
        student_name = row['Name']
        student_attendance = attendance_df[attendance_df['Id'] == student_id]

        if not student_attendance.empty:
            total_class_duration = sum(
                (row['Exit Time'] - row['Entry Time']).total_seconds() / 60
                for _, row in student_attendance.iterrows()
            ) / 60

            total_possible_duration = lecture_duration / 60
            percentage = (total_class_duration / total_possible_duration) * 100

            if percentage < 50:
                attendance_status = "Short Attendance"
            elif 50 <= percentage < 80:
                attendance_status = "Partial Attendance"
            else:
                attendance_status = "Full Attendance"

            attendance_percentage.append({
                'Id': student_id,
                'Name': student_name,
                'Attendance Percentage': percentage,
                'Attendance Status': attendance_status
            })

    return pd.DataFrame(attendance_percentage)
