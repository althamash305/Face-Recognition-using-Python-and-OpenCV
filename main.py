import os
import pickle
from datetime import datetime
import cv2
import cvzone as drawBox
import face_recognition
import numpy
import firebase_admin
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Firebase Initialization
cred = credentials.Certificate('./serviceAccountsKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-12fcf-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-12fcf.appspot.com"
})
bucket = storage.bucket()

# Open Webcam
cap = cv2.VideoCapture(0)
# Place the webcam feed in its position
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')


folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
# All the images ( of Mode ) are loaded
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(f"{folderModePath}/{path}"))

# Loading Encoding file
print("Loading Encode file")
file = open("EncodedFile.p", 'rb')
encodeListWithIds = pickle.load(file)
file.close()
print("Loaded Encode file")
encodeListKnown, studentIds = encodeListWithIds[0], encodeListWithIds[1]
print("Student Ids", studentIds)
# print("Encoded Lists",encodeListKnown)

# Current Mode type
modeType = 0
# How much time the face is shown for
counter = 0

id = 0
imgStudent = []
while True:
    success, img = cap.read()

    # To reduce the computations the image is resized
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # Converting Colorspace from BGR -> RGB
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Finding Location of face
    faceCurFrame = face_recognition.face_locations(imgS)
    # Providing the location of face  from captured image to compare with encoded image
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Set the user image in the background image 
    imgBackground[162:162 + 480, 55:55 + 640] = img
    # Set the mode image in the background image
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    # If there is any face in webcam feed
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            # Matches contains a list of booleans indicating whether the face matches
            # to encoded faces
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            # Provides distances of each face from each face
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(f"Matches {matches}")
            print(f"Face Distance {faceDis}")

            # Minimum distance or closest match
            matchIndex = numpy.argmin(faceDis)
            print("Match Index ", matchIndex)
            if matches[matchIndex] == True:
                y1, x2, y2, x1 = faceLoc
                # Scaling up because we decreased image size before
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                # x1,y1,x2,y2 = 55+x1,162+y1,x2-x1,y2-y1
                bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
                # Draw box 
                imgBackground = drawBox.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                # First time
                if counter == 0:
                    drawBox.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance System by Althamash,Manjunath,Madhu,Manoj,Karthik",imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
            if counter != 0:
                # Downloading data on the first occurence only not all occurences
                if counter == 1:
                    # Get the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    # Get the Image from the storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    # Update data of attendance
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                       "%Y-%m-%d %H:%M:%S")

                    # print(studentInfo['last_attendance_time'])

                    # Diff between Db time and now
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)
                    # For demo purposes 30 seconds else 1 hour or day
                    if secondsElapsed > 30:
                        ref = db.reference(f"Students/{id}")
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if modeType!=3:
                    if counter <= 10:
                    #               which image,   text
                                    # (x,y) loc,   Font
                    #               font Scale,    Color tuple
                        cv2.putText(imgBackground, str(studentInfo['total_attendance'])
                                    , (861, 125), cv2.FONT_HERSHEY_COMPLEX,
                                    1, (255, 255, 255)
                                    )
                        cv2.putText(imgBackground, str(studentInfo['major'])
                                    , (1006, 550), cv2.FONT_HERSHEY_COMPLEX,
                                    0.3, (255, 255, 255)
                                    )
                        cv2.putText(imgBackground, str(id)
                                    , (1006, 493), cv2.FONT_HERSHEY_COMPLEX,
                                    0.5, (255, 255, 255)
                                    )
                        cv2.putText(imgBackground, str(studentInfo['standing'])
                                    , (910, 625), cv2.FONT_HERSHEY_COMPLEX,
                                    0.6, (100, 100, 100)
                                    )
                        cv2.putText(imgBackground, str(studentInfo['year'])
                                    , (1025, 625), cv2.FONT_HERSHEY_COMPLEX,
                                    0.6, (100, 100, 100)
                                    )
                        cv2.putText(imgBackground, str(studentInfo['starting_year'])
                                    , (1125, 625), cv2.FONT_HERSHEY_COMPLEX,
                                    0.6, (100, 100, 100)
                                    )

                        (w, h), _ = cv2.getTextSize(str(studentInfo['name']), cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) / 2
                        # newplace =808+
                        cv2.putText(
                            imgBackground, str(studentInfo['name']),
                            (808 + int(offset), 445), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 100), 1
                        )

                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance System by Althamash,Manjunath,Madhu,Manoj,Karthik", imgBackground)
    cv2.waitKey(1)
