import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

config = {
    "apiKey": "AIzaSyC2qvy80zegkDmLkJM18CSiSj_cz21PWZk",
    "authDomain": "refectory-ai.firebaseapp.com",
    "projectId": "refectory-ai",
    "storageBucket": "refectory-ai.appspot.com",
    "databaseURL": "https://databaseName.firebaseio.com",
    "messagingSenderId": "392671167282",
    "appId": "1:392671167282:web:2b6c38f02676e86de0cd2b",
    "measurementId": "G-S557B9S0FY"
}


if __name__ == '__main__':
    cred = credentials.Certificate('./refectory-ai-firebase-adminsdk-stydr-1a035f2f33.json')
    firebase_admin.initialize_app(cred, config)
    db = firestore.client()
    print("Firebase setup")
