import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountsKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-12fcf-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')
data = {
    "442083":
        {
            "name": "Althamash",
            "major": "Unemployed",
            "starting_year": 2023,
            "total_attendance": 10,
            "standing": "G",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "0007":
        {
            "name": "Shashank Sir",
            "major": "Computer Vision",
            "starting_year": 2008,
            "total_attendance": 10,
            "standing": "S",
            "year": 8,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "130203":
        {
            "name": "Manjunath",
            "major": "Kirket",
            "starting_year": 2020,
            "total_attendance": 2,
            "standing": "S",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "211029":
        {
            "name": "Rahul K",
            "major": "Computer Sinze",
            "starting_year": 2019,
            "total_attendance": 2,
            "standing": "S",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "10323":
        {
            "name": "Tanuja Madam",
            "major": "Computer Science",
            "starting_year": 2005,
            "total_attendance": 0,
            "standing": "S",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}
for key,value in data.items():
    ref.child(key).set(value)

print("Upload Successfull")