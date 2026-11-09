import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MONGO_DATABASE")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = client[DATABASE_NAME]

users_collection = db["users"]
feedback_collection = db["feedback"]