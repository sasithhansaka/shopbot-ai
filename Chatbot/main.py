import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

# Load env variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")
SITE_NAME = os.getenv("SITE_NAME")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "tradnet")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "products")

if not OPENROUTER_API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY environment variable not set!")

# Allowed categories for Tradnet
ALLOWED_CATEGORIES = {"sports", "gaming", "mobilephones", "laptops", "earphones","toys"}

# FastAPI app
app = FastAPI()

# MongoDB client and dependency
mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client[DB_NAME]
products_collection = db[COLLECTION_NAME]

class ChatRequest(BaseModel):
    message: str

async def find_product(query: str) -> List[dict]:
    """Find products in allowed categories matching query."""
    regex_query = {"$regex": query, "$options": "i"}
    filter_query = {
        "category": {"$in": list(ALLOWED_CATEGORIES)},
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
        product["_id"] = str(product["_id"])  # Convert ObjectId to string if needed
        results.append(product)
    return results

async def get_allowed_products(limit=10) -> List[dict]:
    """Get a limited number of products in allowed categories."""
    cursor = products_collection.find(
        {"category": {"$in": list(ALLOWED_CATEGORIES)}}
    ).limit(limit)
    results = []
    async for product in cursor:
        product["_id"] = str(product["_id"])
        results.append(product)
    return results

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_query = req.message

    # 1. Check if the query matches a product directly in allowed categories
    products_found = await find_product(user_query)
    if products_found:
        details = []
        for prod in products_found[:10]:  # Limit to 10 results for response
            details.append(
                f"Product: {prod.get('short_title') or prod.get('name')}\n"
                f"Long Title: {prod.get('long_title', '')}\n"
                f"Description: {prod.get('description', '')}\n"
                f"Category: {prod.get('category', '').capitalize()}\n"
                f"Price: ${prod.get('price')}\n"
                f"In Stock: {prod.get('stock')}"
            )
        return {"answer": "\n\n".join(details)}

    # 2. If not, use OpenRouter via OpenAI SDK
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    # Only send a limited product catalog to avoid token overflow
    allowed_products = await get_allowed_products(limit=10)
    allowed_products_json = [
        {
            "short_title": p.get("short_title"),
            "long_title": p.get("long_title"),
            "description": p.get("description"),
            "category": p.get("category"),
            "price": p.get("price"),
            "stock": p.get("stock"),
            "brand": p.get("brand"),
            "discountPercentage": p.get("discountPercentage"),
        }
        for p in allowed_products
    ]

    prompt = (
  "You are Tradnet's official e-commerce chatbot. "
    "All prices are in LKR. "
    "You can answer any questions strictly about products in the following categories: sports, gaming, mobile phones, laptops, earphones, and toys. "
    "You should use all available product information (short_title, long_title, description, brand, category, price, discount, and stock) to answer the user's question as accurately as possible. "
    "This includes understanding product names, abbreviations, variations, brands, and features from the catalog. "
    "If the user's question is about availability, price, stock, discount, features, or anything related to products or these categories, answer clearly and helpfully using information in the catalog below. "
    "If the user asks about a category (e.g. 'Do you have any mobile phones?'), always list the product names in that category from the catalog. Do not give a generic answer like 'all are in stock' or 'yes we have them'. Always mention the actual product names. "
    "If the user asks about a product in an allowed category, but the product is not found in the catalog, reply clearly that the product is not available in current stock. Do not use the general fallback message. For example, if asked about 'PlayStation 5' in gaming and it is not in the catalog, reply: 'PlayStation 5 is not available in our current stock.' "
    "If the user asks about any allowed category (sports, gaming, mobile phones, laptops, earphones, or toys), but there are no products available in that category in the catalog, reply clearly that there are no products available in that category in current stock. For example, if asked 'Do you have any toys for kids?' and there are no toys in the catalog, reply: 'We do not have any toys for kids available in our current stock.' Always use this format for all allowed categories with no available products. "
    "If the question is about a product or category not present in this catalog, or not about products/categories at all, reply politely: "
    "\"I'm sorry, I can only assist with products in our sports, gaming, mobile phones, laptops, earphones, or toys categories that are currently available on Tradnet.\" "
    "Never answer questions about anything else.\n\n"
    "Always answer as a simple description, using easy-to-understand sentences suitable for any customer.\n"
    "Product Catalog:\n{catalog}\n\n"
    "User: {user_query}\n"
    "Chatbot: Reply with a clear, customer-friendly answer based only on the catalog above, or reply with the polite fallback if the question is unrelated."
    )

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": SITE_URL,
                "X-Title": SITE_NAME,
            },
            model="tngtech/deepseek-r1t-chimera:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # Defensive checks
        if not completion or not hasattr(completion, "choices") or not completion.choices:
            print("OpenRouter raw response:", completion)
            return {"answer": "Sorry, I am unable to process your request right now (no choices returned)."}

        choice = completion.choices[0]
        message = getattr(choice, "message", None)
        answer = getattr(message, "content", None) if message else None

        if not answer:
            print("OpenRouter raw response (no content):", completion)
            return {"answer": "Sorry, I am unable to process your request right now (no content returned)."}

        # Extract only the final customer-facing answer (usually the last non-empty line)
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        final_line = lines[-1] if lines else answer.strip()
        return {"answer": final_line}
    except Exception as e:
        print("OpenRouter error:", e)
        return {"answer": "Sorry, I am unable to process your request right now (exception)."}