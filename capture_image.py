import csv
import cv2
import os
import sys
import dlib

# Set the working directory to the directory containing your script
os.chdir(r'C:\Users\cairo\Downloads\Telegram Desktop\flask project\flask project\website')

# Ensure the directory is in the Python path
sys.path.append(r'C:\Users\cairo\Downloads\Telegram Desktop\flask project\flask project\website')

# Import your module
import train_image


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def takeImages(user_id, name):
    if is_number(user_id) and name.isalpha():
        shape_predictor_path = r'shape_predictor_68_face_landmarks.dat'
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(shape_predictor_path)
        video_path = "\video for presenation\Untitled design (1).mp4"
        cam = cv2.VideoCapture(video_path)

        sampleNum = 0

        while True:
            ret, img = cam.read()
            if not ret:
                return "Failed to grab frame."

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray) # here we have x,y , top left, bottom right
            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom() # this the compliaction in the haar what makes dlib better

                cv2.rectangle(img, (x1, y1), (x2, y2), (10, 159, 255), 2)

                landmarks = predictor(gray, face)
                for n in range(0, 68): #  this of the landmarks from 0 to 68 which draw the face
                    x = landmarks.part(n).x # we take corrdinates (x,y)
                    y = landmarks.part(n).y
                    cv2.circle(img, (x, y), 3, (0, 255, 0), -1)

                sampleNum += 1
                if not os.path.exists("TrainingImage"):
                    os.makedirs("TrainingImage")
                cv2.imwrite(f"TrainingImage/{name}.{user_id}.{sampleNum}.jpg", gray[y1:y2, x1:x2])

            cv2.imshow("Face", img)

            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 100:
                break

        cam.release()
        cv2.destroyAllWindows()

        if not os.path.exists("StudentDetails"):
            os.makedirs("StudentDetails")

        with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([user_id, name])

        train_image.TrainImages()
        return f"Images Saved for ID: {user_id} Name: {name}"
    
    else:
        if is_number(user_id):
            return "Enter Alphabetical Name"
        if name.isalpha():
            return "Enter Numeric ID"
        return "Invalid ID and Name"
