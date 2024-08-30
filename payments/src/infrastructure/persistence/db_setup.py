from pymongo import MongoClient
from src.config import Config

client = MongoClient(
    host=Config.MONGO_HOST,
    port=Config.MONGO_PORT,
    username=Config.MONGO_USER,
    password=Config.MONGO_PASS,
)
db = client[Config.MONGO_DB]
payments_collection = db["payments"]
