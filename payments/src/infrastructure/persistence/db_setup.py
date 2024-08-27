import os

from pymongo import MongoClient

MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "payments")
MONGO_USER = os.getenv("MONGO_USER", "mongo")
MONGO_PASS = os.getenv("MONGO_PASS", "mongo")

client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASS,
)
db = client[MONGO_DB]
payments_collection = db["payments"]
