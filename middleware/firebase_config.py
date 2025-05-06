import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred = credentials.Certificate("middleware/service-account-key.json")
    default_app = firebase_admin.initialize_app(cred)