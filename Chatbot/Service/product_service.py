from typing import List
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]
products_collection = db[settings.COLLECTION_NAME]

async def find_product(query: str) -> List[dict]:
    regex_query = {"$regex": query, "$options": "i"}
    filter_query = {
        "category": {"$in": list(settings.ALLOWED_CATEGORIES)},
        "$or": [
            {"short_title": regex_query},
            {"long_title": regex_query},
            {"name": regex_query},
            {"description": regex_query}
        ]
    }
    cursor = products_collection.find(filter_query)
    results = []
    async for product in cursor:
        product["_id"] = str(product["_id"])
        results.append(product)
    return results

async def get_allowed_products(limit=10) -> List[dict]:
    cursor = products_collection.find(
        {
            "category": {"$in": list(settings.ALLOWED_CATEGORIES)},
            "stock": {"$gt": 0},
            "status": "active"
        }
    ).limit(limit)
    results = []
    async for product in cursor:
        product["_id"] = str(product["_id"])
        results.append(product)
    return results