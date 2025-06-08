from fastapi import APIRouter
from models import ChatRequest
from Service.product_service import find_product
from Service.ai_service import generate_ai_response, extract_keywords
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
db = mongo_client[settings.DB_NAME]
products_collection = db[settings.COLLECTION_NAME]

@router.post("/chat")
async def chat(req: ChatRequest):
    products_found = await find_product(req.message)
    if products_found:
        details = [
            f"Product: {p.get('short_title') or p.get('name')}\n"
            f"Long Title: {p.get('long_title', '')}\n"
            f"Description: {p.get('description', '')}\n"
            f"Category: {p.get('category', '').capitalize()}\n"
            f"Price: LKR {p.get('price')}\n"
            f"In Stock: {p.get('stock')}"
            for p in products_found[:10]
        ]
        return {"answer": "\n\n".join(details)}
    answer = await generate_ai_response(req.message)
    return {"answer": answer}