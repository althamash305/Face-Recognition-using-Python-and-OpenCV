import time

import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
# * Why Encoding ->  optimization technique allowing you to serve pictures at a smaller size, loading them faster
# Firebase Initialization
cred = credentials.Certificate('./serviceAccountsKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-12fcf-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendance-12fcf.appspot.com"
})

folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for i,path in enumerate(pathList):
    studentIds.append(path.replace(".png",""))
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    # cv2.imshow("something",imgList[i])

    fileName = f"{folderPath}/{path}"
    bucket = storage.bucket()
    # Creating firebase storage blob and uploading to it
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)

def findEncodings(imagesList):
    encodeList=[]
    for img in imagesList:
        #Change Color Space OpenCv -> BGR Face-recognition -> RGB
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        #Encoding using face-recognition Library
        encode = face_recognition.face_encodings(img)[0]

        encodeList.append(encode)

    return encodeList
print("Encoding Started...")
encodeList = findEncodings(imgList)
encodeListWithIds = [encodeList,studentIds]
print("Encoding Finished")

file = open('EncodedFile.p','wb')
pickle.dump(encodeListWithIds,file)
file.close()
print("File Saved")