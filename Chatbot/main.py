# import os
# import json
# from fastapi import FastAPI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from openai import OpenAI
# from motor.motor_asyncio import AsyncIOMotorClient
# from typing import List
# from fastapi.middleware.cors import CORSMiddleware  # Add this import at the top


# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# SITE_URL = os.getenv("SITE_URL")
# SITE_NAME = os.getenv("SITE_NAME")
# MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("MONGO_DB_NAME", "tradnet")
# COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "products")

# if not OPENAI_API_KEY:
#     raise EnvironmentError("OPENAI_API_KEY environment variable not set!")

# # Initialize OpenAI client (new SDK format)
# client = OpenAI(api_key=OPENAI_API_KEY)

# # Allowed categories
# ALLOWED_CATEGORIES = {"sports", "gaming", "mobilephones", "laptops", "earphones", "toys"}

# # FastAPI app
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",    # Default React development server
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allows all headers
#     expose_headers=["*"]  # Exposes all headers to the client
# )

# # MongoDB client
# mongo_client = AsyncIOMotorClient(MONGODB_URI)
# db = mongo_client[DB_NAME]
# products_collection = db[COLLECTION_NAME]

# class ChatRequest(BaseModel):
#     message: str

# async def find_product(query: str) -> List[dict]:
#     """Find products in allowed categories matching the query."""
#     regex_query = {"$regex": query, "$options": "i"}
#     filter_query = {
#         "category": {"$in": list(ALLOWED_CATEGORIES)},
#         "$or": [
#             {"short_title": regex_query},
#             {"long_title": regex_query},
#             {"name": regex_query},
#             {"description": regex_query}
#         ]
#     }
#     cursor = products_collection.find(filter_query)
#     results = []
#     async for product in cursor:
#         product["_id"] = str(product["_id"])
#         results.append(product)
#     return results

# async def get_allowed_products(limit=10) -> List[dict]:
#     """Get a limited number of products in allowed categories."""
#     cursor = products_collection.find(
#         {"category": {"$in": list(ALLOWED_CATEGORIES)}}
#     ).limit(limit)
#     results = []
#     async for product in cursor:
#         product["_id"] = str(product["_id"])
#         results.append(product)
#     return results

# @app.post("/chat")
# async def chat_endpoint(req: ChatRequest):
#     user_query = req.message

#     # 1. Try to find a direct match
#     products_found = await find_product(user_query)
#     if products_found:
#         details = []
#         for prod in products_found[:10]:
#             details.append(
#                 f"Product: {prod.get('short_title') or prod.get('name')}\n"
#                 f"Long Title: {prod.get('long_title', '')}\n"
#                 f"Description: {prod.get('description', '')}\n"
#                 f"Category: {prod.get('category', '').capitalize()}\n"
#                 f"Price: LKR {prod.get('price')}\n"
#                 f"In Stock: {prod.get('stock')}"
#             )
#         return {"answer": "\n\n".join(details)}

#     # 2. Use OpenAI GPT-3.5 Turbo if no direct matches
#     try:
#         allowed_products = await get_allowed_products(limit=10)
#         allowed_products_json = [
#             {
#                 "short_title": p.get("short_title"),
#                 "long_title": p.get("long_title"),
#                 "description": p.get("description"),
#                 "category": p.get("category"),
#                 "price": p.get("price"),
#                 "stock": p.get("stock"),
#                 "brand": p.get("brand"),
#                 "discountPercentage": p.get("discountPercentage"),
#             }
#             for p in allowed_products
#         ]

#         catalog = json.dumps(allowed_products_json, indent=2, ensure_ascii=False)

#         # Format prompt with actual catalog and user query
#         formatted_prompt = (
#             "You are Tradnet's official e-commerce chatbot. "
#             "When users ask about you, respond with: "
#             "'My name is TradnetBot, I'm your personal shopping assistant for Tradnet.' ""\n\n"
#             "All prices are in LKR. "
#             "You can answer any questions strictly about products in the following categories: sports, gaming, mobile phones, laptops, earphones, and toys. "
#             "You should use all available product information (short_title, long_title, description, brand, category, price, discount, and stock) to answer the user's question as accurately as possible. "
#             "This includes understanding product names, abbreviations, variations, brands, and features from the catalog. "
#             "If the user's question is about availability, price, stock, discount, features, or anything related to products or these categories, answer clearly and helpfully using information in the catalog below. "
#             "If the user asks about a category (e.g. 'Do you have any mobile phones?'), always list the product names in that category from the catalog. Do not give a generic answer like 'all are in stock' or 'yes we have them'. Always mention the actual product names. "
#             "If the user asks about a product in an allowed category, but the product is not found in the catalog, reply clearly that the product is not available in current stock. For example, if asked about 'PlayStation 5' in gaming and it is not in the catalog, reply: 'PlayStation 5 is not available in our current stock.' "
#             "If the user asks about any allowed category (sports, gaming, mobile phones, laptops, earphones, or toys), but there are no products available in that category in the catalog, reply clearly that there are no products available in that category in current stock. For example, if asked 'Do you have any toys for kids?' and there are no toys in the catalog, reply: 'We do not have any toys for kids available in our current stock.' Always use this format for all allowed categories with no available products. "
#             "If the question is about a product or category not present in this catalog, or not about products/categories at all, reply politely: "
#             "\"I'm sorry, I can only assist with Information that are .\" "
#             "Never answer questions about anything else.\n\n"
#             "Always answer as a simple description, using easy-to-understand sentences suitable for any customer.\n"
#             f"Product Catalog:\n{catalog}\n\n"
#             f"User: {user_query}\n"
#             "Chatbot: Reply with a clear, customer-friendly answer based only on the catalog above, or reply with the polite fallback if the question is unrelated."
#         )

#         # Call OpenAI API with the formatted prompt
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful and accurate e-commerce assistant for Tradnet."},
#                 {"role": "user", "content": formatted_prompt}
#             ],
#             temperature=0.3,
#             max_tokens=500,
#         )

#         answer = response.choices[0].message.content.strip()
#         return {"answer": answer}

#     except Exception as e:
#         print("OpenAI error:", e)
#         return {"answer": "Sorry, I am unable to process your request right now (exception)."}



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routes import router as api_router
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(api_router)