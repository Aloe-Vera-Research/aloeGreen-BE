import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()  # auto reads .env from root

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

data_collection = db["price_data"]
scan_history_collection = db["scan_history"]