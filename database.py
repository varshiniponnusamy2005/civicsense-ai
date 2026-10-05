from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

users_collection = db["users"]
complaints_collection = db["complaints"]
departments_collection = db["departments"]
status_history_collection = db["status_history"]
notifications_collection = db["notifications"]

print("MongoDB connected successfully!")