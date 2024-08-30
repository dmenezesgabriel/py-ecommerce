import os


class Config:
    MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB = os.getenv("MONGO_DB", "payments")
    MONGO_USER = os.getenv("MONGO_USER", "mongo")
    MONGO_PASS = os.getenv("MONGO_PASS", "mongo")
