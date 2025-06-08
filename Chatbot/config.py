import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SITE_URL = os.getenv("SITE_URL")
    SITE_NAME = os.getenv("SITE_NAME")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("MONGO_DB_NAME", "tradnet")
    COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "products")
    ALLOWED_CATEGORIES = {"sports", "gaming", "mobilephones", "laptops", "earphones", "toys"}

settings = Settings()
